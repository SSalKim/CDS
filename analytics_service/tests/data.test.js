import {test} from 'node:test';
import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFileSync} from 'node:fs';
import {cleanEvent,filters,insert,statistics,history,csv} from '../src/data.js';
import {administrator,fingerprint} from '../src/auth.js';
import worker from '../src/worker.js';
import {generateKeyPair,exportJWK,SignJWT} from 'jose';

function database(){
 const sqlite=new DatabaseSync(':memory:');sqlite.exec(readFileSync(new URL('../migrations/0001_events.sql',import.meta.url),'utf8'));
 const db={prepare(sql){let args=[];return {bind(...values){args=values;return this;},async all(){return {results:sqlite.prepare(sql).all(...args)};},async run(){return sqlite.prepare(sql).run(...args);}};},async batch(items){const rows=[];for(const item of items)rows.push(await item.all());return rows;}};
 return db;
}
const now=Date.parse('2026-11-17T08:00:00Z');
function event(extra={}){return cleanEvent({event_id:crypto.randomUUID(),occurred_at:now,outcome:'view',menu:'forecast',region:'asia',model_id:'gfs',model_label:'GFS',product_id:'gph500',product_label:'500 고도',run_utc:'2026-11-17T00:00:00Z',valid_utc:'2026-11-18T00:00:00Z',forecast_hour:24,...extra},now);}
test('TOP deduplicates browser-series across leads and sessions, but separates cycles/regions/users',async()=>{
 const db=database();
 const add=async(visitor,series,extra={})=>insert(db,{...event(extra),visitor_key:visitor.repeat(64),session_key:crypto.randomUUID(),series_key:series}).run();
 await add('a','run1',{forecast_hour:0});await add('a','run1',{forecast_hour:3});await add('a','run1',{forecast_hour:240});await add('b','run1');await add('a','run2',{run_utc:'2026-11-17T06:00:00Z'});await add('a','korea',{region:'hkor'});
 const scope=filters(new URL('https://test/?start=2026-11-17&end=2026-11-17'),now);
 const data=await statistics(db,scope);
 assert.equal(data.overview.views,6);assert.equal(data.overview.users,2);assert.equal(data.overview.series_views,4);
 assert.equal(data.top.find(x=>x.region==='asia').series_views,3);
 assert.equal(data.top.find(x=>x.region==='hkor').series_views,1);
 const first=await history(db,scope,null,2),next=await history(db,scope,first.next,10);
 assert.equal(first.rows.length,2);assert.equal(next.rows.length,4);assert.equal(new Set([...first.rows,...next.rows].map(x=>x.event_id)).size,6);
});
test('server whitelists fields, rejects invalid timestamps, injection and dates; CSV is safe',()=>{
 assert.equal(event({email:'someone@example.com',ip:'1.2.3.4'}).email,undefined);
 assert.throws(()=>event({run_utc:'2026-02-30T00:00:00Z'}));
 assert.throws(()=>event({forecast_hour:-1}));
 assert.throws(()=>filters(new URL('https://test/?model_id=%27%20OR%201=1'),now));
 assert.throws(()=>filters(new URL('https://test/?start=2026-01-01'),now));
 assert.match(csv([{product_label:'=danger'}]),/'=danger/);
});
test('owner authentication fails closed, rejects forged JWT and local-preview on a public host',async()=>{
 assert.equal(await administrator(new Request('https://public.example/admin'),{}),null);
 assert.equal(await administrator(new Request('https://public.example/admin'),{LOCAL_PREVIEW:'true'}),null);
 const env={ADMIN_EMAIL:'owner@example.com',ACCESS_TEAM_DOMAIN:'team.cloudflareaccess.com',ACCESS_AUD:'test'};
 assert.equal(await administrator(new Request('https://public.example/admin',{headers:{'Cf-Access-Jwt-Assertion':'forged'}}),env),null);
 assert.equal((await administrator(new Request('http://127.0.0.1/admin'),{LOCAL_PREVIEW:'true'})).email,'local-preview');
 assert.equal((await fingerprint('secret','client')).length,64);
 assert.notEqual(await fingerprint('secret','a'),await fingerprint('secret','b'));
});
test('API and static dashboard reject anonymous calls; collector validates origin and configuration',async()=>{
 for(const path of ['/admin','/admin/app.js','/admin/api/history','/admin/api/stats']){
  assert.equal((await worker.fetch(new Request('https://test'+path),{})).status,403);
 }
 assert.equal((await worker.fetch(new Request('https://test/collect',{method:'POST'}),{})).status,403);
 assert.equal((await worker.fetch(new Request('https://test/collect',{method:'OPTIONS',headers:{Origin:'https://ssalkim.github.io'}}),{ALLOWED_ORIGINS:'https://ssalkim.github.io'})).status,204);
 assert.equal((await worker.fetch(new Request('https://test/collect',{method:'POST',headers:{Origin:'https://ssalkim.github.io'}}),{ALLOWED_ORIGINS:'https://ssalkim.github.io'})).status,503);
});
test('signed owner JWT succeeds, while wrong audience, expired token and another email fail',async()=>{
 const {publicKey,privateKey}=await generateKeyPair('RS256');
 const jwk={...await exportJWK(publicKey),kid:'test-key',alg:'RS256',use:'sig'};
 const original=globalThis.fetch;
 globalThis.fetch=async url=>{assert.equal(String(url),'https://jwt-test.cloudflareaccess.com/cdn-cgi/access/certs');return new Response(JSON.stringify({keys:[jwk]}));};
 const env={ADMIN_EMAIL:'owner@example.com',ACCESS_TEAM_DOMAIN:'jwt-test.cloudflareaccess.com',ACCESS_AUD:'expected'};
 const sign=(email='owner@example.com',aud='expected',expiry='5m')=>new SignJWT({email}).setProtectedHeader({alg:'RS256',kid:'test-key'}).setIssuer('https://jwt-test.cloudflareaccess.com').setAudience(aud).setIssuedAt().setExpirationTime(expiry).sign(privateKey);
 const check=async token=>administrator(new Request('https://public.example/admin',{headers:{'Cf-Access-Jwt-Assertion':token}}),env);
 try{
  assert.equal((await check(await sign())).email,'owner@example.com');
  assert.equal(await check(await sign('other@example.com')),null);
  assert.equal(await check(await sign('owner@example.com','wrong')),null);
  assert.equal(await check(await sign('owner@example.com','expected',Math.floor(Date.now()/1000)-60)),null);
 }finally{globalThis.fetch=original;}
});
test('retention deletes only records older than the configured limit',async()=>{
 const db=database();await insert(db,{...event({occurred_at:now-1000}),visitor_key:'a',session_key:'b',series_key:'c'}).run();
 await insert(db,{...event(),occurred_at:Date.now()-91*86400000,visitor_key:'a',session_key:'b',series_key:'c'}).run();
 await worker.scheduled({}, {DB:db,RETENTION_DAYS:'90'});
 const rows=await db.prepare('SELECT COUNT(*) AS total FROM events').all();assert.equal(rows.results[0].total,1);
});

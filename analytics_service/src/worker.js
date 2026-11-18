import {administrator,fingerprint} from './auth.js';
import {cleanEvent,filters,insert,statistics,users,history,groupedHistory,saveNickname,csv,RETENTION_DAYS} from './data.js';
import {captureConnection,revealConnections,connectionRetention} from './connection.js';
import {chartImage} from './chart-image.js';

const security={
  'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer',
  'Content-Security-Policy':"default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; font-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
};
const json=(body,status=200,headers={})=>new Response(JSON.stringify(body),{
  status,headers:{...security,'Content-Type':'application/json; charset=utf-8',...headers}
});
const retention=env=>Math.min(90,Math.max(1,Number(env.RETENTION_DAYS)||RETENTION_DAYS));

async function collect(request,env){
  const origin=request.headers.get('Origin');
  const allowed=(env.ALLOWED_ORIGINS||'').split(',').map(x=>x.trim()).filter(Boolean);
  if(!origin || !allowed.includes(origin)) return json({error:'Origin not allowed'},403);
  const cors={'Access-Control-Allow-Origin':origin,'Vary':'Origin',
    'Access-Control-Allow-Methods':'POST, OPTIONS','Access-Control-Allow-Headers':'Content-Type'};
  if(request.method==='OPTIONS') return new Response(null,{status:204,headers:{...security,...cors}});
  if(request.method!=='POST') return json({error:'Method not allowed'},405,cors);
  if(!env.DB || !env.COLLECT_LIMITER || String(env.HMAC_SECRET||'').length<32) return json({error:'Collector unavailable'},503,cors);
  if(!request.headers.get('Content-Type')?.startsWith('application/json')) return json({error:'JSON required'},415,cors);
  // Keep the transient rate-limit key separate from encrypted administrator-only metadata.
  const key=await fingerprint(env.HMAC_SECRET,'rate:'+request.headers.get('CF-Connecting-IP'));
  if(!(await env.COLLECT_LIMITER.limit({key})).success) return json({error:'Rate limited'},429,{...cors,'Retry-After':'60'});
  const reader=request.body?.getReader();
  if(!reader) return json({error:'Empty request'},400,cors);
  let size=0,body='';
  const decoder=new TextDecoder();
  while(true){
    const {done,value}=await reader.read();
    if(done) break;
    size+=value.byteLength;
    if(size>24000){await reader.cancel();return json({error:'Request too large'},413,cors);}
    body+=decoder.decode(value,{stream:true});
  }
  body+=decoder.decode();
  let payload,events;
  try{
    payload=JSON.parse(body);
    if(payload.version!==1 || !/^\d{1,20}\.\d{1,20}$/.test(payload.client_id) ||
      !/^\d{1,20}$/.test(payload.session_id) || !Array.isArray(payload.events) ||
      payload.events.length<1 || payload.events.length>12) throw new Error();
    events=payload.events.map(event=>cleanEvent(event));
  }catch{return json({error:'Invalid event batch'},400,cors);}
  const visitor=await fingerprint(env.HMAC_SECRET,'browser:'+payload.client_id);
  const session=await fingerprint(env.HMAC_SECRET,'session:'+payload.client_id+':'+payload.session_id);
  const connection=await captureConnection(request,env);
  const statements=[];
  for(const event of events){
    const series=await fingerprint(env.HMAC_SECRET,JSON.stringify([event.menu,event.region,event.model_id,
      event.product_id,event.run_utc,event.detail_token]));
    statements.push(insert(env.DB,{...event,visitor_key:visitor,session_key:session,series_key:series,connection_ciphertext:connection}));
  }
  await env.DB.batch(statements);
  return json({accepted:events.length},202,cors);
}

async function admin(request,env){
  const owner=await administrator(request,env);
  if(!owner) return json({error:'Administrator authentication required'},403);
  const url=new URL(request.url);
  const route=url.pathname;
  if(route==='/admin/api/nickname' && request.method==='PUT'){
    if(request.headers.get('Origin')!==url.origin) return json({error:'Origin not allowed'},403);
    if(!env.DB) return json({error:'Database unavailable'},503);
    if(!request.headers.get('Content-Type')?.startsWith('application/json')) return json({error:'JSON required'},415);
    try{
      const body=await request.text();if(body.length>1000) return json({error:'Request too large'},413);
      const value=JSON.parse(body);return json(await saveNickname(env.DB,value.visitor_key,value.nickname));
    }catch{return json({error:'Invalid nickname'},400);}
  }
  if(request.method!=='GET') return json({error:'Method not allowed'},405);
  if(route==='/admin/api/whoami') return json({email:owner.email,retention_days:retention(env),connection_retention_days:connectionRetention(env)});
  if(route.startsWith('/admin/api/')){
    if(!env.DB) return json({error:'Database unavailable'},503);
    let scope;
    try{scope=filters(url,Date.now(),retention(env));}
    catch{return json({error:'Invalid date range or filter'},400);}
    if(route==='/admin/api/stats') return json(await statistics(env.DB,scope));
    if(route==='/admin/api/users') return json({rows:await revealConnections(await users(env.DB,scope),env)});
    if(route==='/admin/api/history'){
      try{const read=url.searchParams.get('group')==='series'?groupedHistory:history;
        const data=await read(env.DB,scope,url.searchParams.get('cursor'));
        return json({...data,rows:await revealConnections(data.rows,env)});}
      catch{return json({error:'History unavailable or invalid cursor'},400);}
    }
    if(route==='/admin/api/export.csv'){
      const data=await history(env.DB,scope,null,5000);
      return new Response(csv(await revealConnections(data.rows,env)),{headers:{...security,'Content-Type':'text/csv; charset=utf-8',
        'Content-Disposition':'attachment; filename="cds-usage.csv"','X-Export-Truncated':data.next?'true':'false'}});
    }
    return json({error:'Not found'},404);
  }
  let asset=route.slice('/admin'.length) || '/';
  if(asset==='/index.html') asset='/';
  if(!['/','/styles.css','/app.js','/icons.bundle.js'].includes(asset)) return json({error:'Not found'},404);
  url.pathname=asset;
  const response=await env.ASSETS.fetch(new Request(url,request));
  const headers=new Headers(response.headers);
  for(const [name,value] of Object.entries(security)) headers.set(name,value);
  return new Response(response.body,{status:response.status,headers});
}

export default {
  async fetch(request,env){
    try{
      const url=new URL(request.url);
      if(url.pathname==='/collect') return await collect(request,env);
      if(url.pathname==='/chart-image') return await chartImage(request,env);
      if(url.pathname==='/health') return json({service:'cds-usage-analytics',version:3});
      if(url.pathname==='/admin' || url.pathname.startsWith('/admin/')) return await admin(request,env);
      return json({error:'Not found'},404);
    }catch{return json({error:'Service temporarily unavailable'},503);}
  },
  async scheduled(controller,env){
    await env.DB.prepare('UPDATE events SET connection_ciphertext = NULL WHERE received_at < ? AND connection_ciphertext IS NOT NULL')
      .bind(Date.now()-connectionRetention(env)*86400000).run();
    await env.DB.prepare('DELETE FROM events WHERE occurred_at < ?')
      .bind(Date.now()-retention(env)*86400000).run();
  }
};

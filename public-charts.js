(function(global){
'use strict';

const MODEL_IDS=new Set(['aifs','gfs','aigfs','cmc','icon']);
const SOURCE_MODEL_IDS=new Set([...MODEL_IDS,'ecmwf','ukmo']);
const COMMON_PRODUCTS=new Set(['gph200','gph500','gph700','ept850','ept925','wnd850','wnd925']);
const ROW_PRODUCTS=new Set([...COMMON_PRODUCTS,'gph300','surfce','acptot','acptot1','acrain','acrain1']);
const DRIVE_HOSTS=new Set(['drive.google.com','drive.usercontent.google.com','lh3.googleusercontent.com']);
const REMOTE_MANIFEST='https://raw.githubusercontent.com/SSalKim/CDS-Public-Charts/main/data/public_charts_manifest.json';
// R2 custom-domain origin with a trailing slash, e.g. 'https://charts.example.com/'.
// Empty keeps the Git manifest as the only source.
const R2_BASE='https://cds4.uzo1o1.party/';
const R2_SCHEMA=2;
const R2_FETCH_CONCURRENCY=6;
const R2_RUN=/^(aifs|gfs|aigfs|cmc|ecmwf|icon|ukmo)\/(\d{10})$/;
const R2_EXTRA_FIELDS=['kma_confirmed_at','kma_reference_hour'];
// Producer object name under charts/{model}/{cycle}/; an alias row names the image it reuses.
const R2_IMAGE=/^(aifs|gfs|aigfs|cmc|ecmwf|icon|ukmo)_(asia|hkor)_([a-z0-9]+)_s(\d{3})_(\d{10})_([a-f0-9]{16})\.webp$/;
const DRIVE_FILE_ID=/^[A-Za-z0-9_-]{1,200}$/;
const ZERO_ACRAIN_CUTOVER='2026111612';
const UKMO_WINTER_CUTOVER='2026111800';
// From this cycle GFS/AIFS/AIGFS run to 360 h and ECMWF 00/12Z continues KMA's images (to 240 h) to 360 h.
const EXTENSION_CUTOVER='2026112212';

// Offset applied to Date.now() when the R2 index shows the device clock is clearly wrong.
let clockOffsetMs=0;

function clockNow(){
return Date.now()+clockOffsetMs;
}

function calibrateClock(generatedAt){
const reference=Date.parse(generatedAt);
if(!Number.isFinite(reference)) return;
const local=Date.now();
// generated_at is always in the past, so a clock behind it is wrong. Between production runs
// the index can be tens of minutes old, so only a clock more than two hours ahead is treated
// as wrong; smaller offsets cannot matter for the 48-hour windows this clock decides.
clockOffsetMs=local<reference-60000 || local>reference+2*3600000 ? reference-local : 0;
}

function driveUrl(fileId){
return `https://drive.usercontent.google.com/download?id=${fileId}&export=view&authuser=0`;
}

function r2BaseFor(location,explicit){
const value=explicit!==undefined ? explicit :
(typeof global.CDS_PUBLIC_CHARTS_R2_BASE==='string' ? global.CDS_PUBLIC_CHARTS_R2_BASE :
(isLocalHost(location) ? '' : R2_BASE));
if(!value) return '';
try{
const url=new URL(value);
const local=['localhost','127.0.0.1','[::1]'].includes(url.hostname);
if(url.protocol!=='https:' && !(local && url.protocol==='http:') || url.search || url.hash ||
url.username || url.password) return '';
return url.href.endsWith('/') ? url.href : url.href+'/';
}catch(error){
return '';
}
}

function isLocalHost(location){
const host=location?.hostname || '';
return ['localhost','127.0.0.1','[::1]','::1'].includes(host) || host.endsWith('.localhost');
}

function isReplacementProduct(modelId,product){
return modelId==='ukmo' && product?.category==='hkor' && ['acptot','acrain'].includes(product.id);
}

function supportsReplacement(modelId,product,runUTC,nowMs=clockNow()){
const month=runUTC?.getUTCMonth?.()+1;
const age=nowMs-runUTC?.getTime?.();
return isReplacementProduct(modelId,product) &&
cycleFromDate(runUTC)>=UKMO_WINTER_CUTOVER && age>=0 && age<=48*3600000 &&
(month>=10 || month<=4) && [0,12].includes(runUTC?.getUTCHours?.());
}

// UKMO and ECMWF public charts (06/18Z, UKMO +156/168 h, ECMWF 00/12Z +252-360 h) are kept for 48 h after
// the cycle. After that only KMA's own images remain: UKMO to +144 h and ECMWF 00/12Z to +240 h.
const PUBLIC_WINDOW_MODELS=new Set(['ukmo','ecmwf']);
const PUBLIC_WINDOW_MS=48*3600000;

function publicWindowCurrent(modelId,runUTC,nowMs=clockNow()){
if(!PUBLIC_WINDOW_MODELS.has(modelId)) return true;
const age=nowMs-runUTC?.getTime?.();
return Number.isFinite(age) && age>=0 && age<=PUBLIC_WINDOW_MS &&
(modelId!=='ukmo' || cycleFromDate(runUTC)>=UKMO_WINTER_CUTOVER);
}

function publicWindowExpired(modelId,runUTC,nowMs=clockNow()){
return PUBLIC_WINDOW_MODELS.has(modelId) && nowMs-runUTC?.getTime?.()>PUBLIC_WINDOW_MS;
}

function ukmoCurrent(runUTC,nowMs=clockNow()){
return publicWindowCurrent('ukmo',runUTC,nowMs);
}

function ukmoFullCatalog(runUTC,forecastHour=0){
return cycleFromDate(runUTC)>=UKMO_WINTER_CUTOVER &&
([6,18].includes(runUTC?.getUTCHours?.()) || forecastHour>144);
}

function isModel(modelId){
return MODEL_IDS.has(modelId);
}

function ecmwfExtension(runUTC,forecastHour){
return Number.isFinite(runUTC?.getTime?.()) && [0,12].includes(runUTC.getUTCHours()) &&
cycleFromDate(runUTC)>=EXTENSION_CUTOVER && forecastHour>240;
}

function usesSource(modelId,runUTC,forecastHour=0){
return isModel(modelId) || (modelId==='ecmwf' &&
Number.isFinite(runUTC?.getTime?.()) && ([6,18].includes(runUTC.getUTCHours()) || ecmwfExtension(runUTC,forecastHour))) ||
(modelId==='ukmo' && ukmoFullCatalog(runUTC,forecastHour));
}

function supportsProduct(modelId,product){
if(!SOURCE_MODEL_IDS.has(modelId) || !['asia','hkor'].includes(product?.category)) return false;
return COMMON_PRODUCTS.has(product.id) ||
(product.category==='asia' ? product.id==='surfce' : ['surfce','acptot','acrain'].includes(product.id));
}

function parseCycle(cycle){
if(typeof cycle!=='string' || !/^\d{10}$/.test(cycle)) return null;
const date=new Date(Date.UTC(Number(cycle.slice(0,4)),Number(cycle.slice(4,6))-1,
Number(cycle.slice(6,8)),Number(cycle.slice(8,10))));
return cycleFromDate(date)===cycle ? date : null;
}

function cycleFromDate(date){
if(!date || typeof date.getTime!=='function' || !Number.isFinite(date.getTime())) return '';
return [date.getUTCFullYear(),date.getUTCMonth()+1,date.getUTCDate(),date.getUTCHours()]
.map((part,index)=>String(part).padStart(index===0?4:2,'0')).join('');
}

function supportsZeroAccumulation(runUTC){
return cycleFromDate(runUTC)>=ZERO_ACRAIN_CUTOVER;
}

function validHour(model,hour,runUTC){
const extended=cycleFromDate(runUTC)>=EXTENSION_CUTOVER;
const maximum=model==='ukmo'?([6,18].includes(runUTC?.getUTCHours?.())?69:168):
model==='ecmwf'?([0,12].includes(runUTC?.getUTCHours?.())&&extended?360:144):
model==='icon'?([6,18].includes(runUTC?.getUTCHours?.())?120:180):
['gfs','aifs','aigfs'].includes(model)&&extended?360:240;
if(!Number.isInteger(hour) || hour<0 || hour>maximum) return false;
if(hour<=84) return hour%(['aifs','aigfs'].includes(model)?6:3)===0;
return hour===90 || hour===96 || (hour>=108 && hour%12===0);
}

function validUrl(value){
try{
const url=new URL(value);
return typeof value==='string' && value===value.trim() && url.protocol==='https:' && DRIVE_HOSTS.has(url.hostname) &&
!url.username && !url.password && !url.port &&
!Array.from(url.searchParams.keys()).some(key=>/^(access_token|refresh_token|api_key|key|token)$/i.test(key)) &&
(url.hostname==='lh3.googleusercontent.com' ? url.pathname.length>1 : !!url.searchParams.get('id'));
}catch(error){
return false;
}
}

function browserImageCandidates(value){
if(!validUrl(value)) return [];
const url=new URL(value);
if(!['drive.google.com','drive.usercontent.google.com'].includes(url.hostname)) return [];
const id=url.searchParams.get('id');
if(!id || !/^[A-Za-z0-9_-]{1,200}$/.test(id)) return [];
return [...new Set([
`https://lh3.googleusercontent.com/d/${encodeURIComponent(id)}=s0`,
value,
`https://drive.google.com/thumbnail?id=${encodeURIComponent(id)}&sz=w2400`
])];
}

function manifestUrl(location=global.location){
return isLocalHost(location)?'data/public_charts_manifest.json':REMOTE_MANIFEST;
}

function createStore({fetchImpl=(...args)=>global.fetch(...args),location=global.location,r2Base}={}){
const r2Origin=r2BaseFor(location,r2Base);
let entries=new Map();
let byRun=new Map();
let leadsByRun=new Map();
let fragments=new Map();
let r2Key='';
let source='';
let signature='';
let revision=0;
let pending=null;
let timer=null;
let lastPollAt=0;
const listeners=new Set();

function notifyChange(){
revision++;
for(const listener of listeners){
try{Promise.resolve(listener()).catch(()=>{});}catch(error){}
}
}

function expireReplacements(){
let changed=false;
for(const [key,row] of entries){
if(publicWindowCurrent(row.model,parseCycle(row.cycle))) continue;
entries.delete(key);
byRun.delete(row.model+'/'+row.cycle);
changed=true;
}
if(changed){
signature=JSON.stringify([...entries].sort(([a],[b])=>a.localeCompare(b)));
notifyChange();
}
return changed;
}

// R2 fragments carry the producer's lead list; the Git manifest falls back to local rules.
function hourAllowed(model,hour,runUTC,leads=leadsByRun){
const runLeads=leads.get(model+'/'+cycleFromDate(runUTC));
return runLeads ? Number.isInteger(hour) && runLeads.has(hour) : validHour(model,hour,runUTC);
}

function replaceManifest(manifest){
const next=new Map();
const conflicts=new Set();
const published=manifest?.models;
const nextLeads=new Map();
for(const [run,leads] of Object.entries(manifest?.leads || {})){
if(R2_RUN.test(run) && Array.isArray(leads)) nextLeads.set(run,new Set(leads.filter(Number.isInteger)));
}
for(const row of Array.isArray(manifest?.charts)?manifest.charts:[]){
if(!row || !SOURCE_MODEL_IDS.has(row.model) || published?.[row.model]?.published!==true ||
!hourAllowed(row.model,row.hour,parseCycle(row.cycle),nextLeads) || !ROW_PRODUCTS.has(row.product) ||
!['asia','hkor'].includes(row.domain) || !(validUrl(row.url) || isR2ImageUrl(row.url))) continue;
const run=parseCycle(row.cycle);
if(!run || !(row.model==='cmc'?[0,12]:[0,6,12,18]).includes(run.getUTCHours())) continue;
if(row.model==='ecmwf' && (!usesSource(row.model,run,row.hour) || row.cycle<'2026111606' || !publicWindowCurrent('ecmwf',run))) continue;
if(row.model==='icon' && row.cycle<'2026111612') continue;
if(row.model==='ukmo'){
if(!ukmoCurrent(run) || !supportsProduct('ukmo',{category:row.domain,id:row.product==='gph300'?'gph200':row.product.replace(/1$/,'')})) continue;
if(!ukmoFullCatalog(run,row.hour) && !supportsReplacement('ukmo',{category:row.domain,id:row.product.replace(/1$/,'')},run)) continue;
if([0,12].includes(run.getUTCHours()) && (!Number.isFinite(Date.parse(row.kma_confirmed_at)) ||
row.hour>144 && row.kma_reference_hour!==144)) continue;
}
if(row.domain==='asia' && ['acptot','acptot1','acrain','acrain1'].includes(row.product)) continue;
if(row.model==='aigfs' && ['acptot1','acrain1'].includes(row.product)) continue;
if(row.hour===0 && ['acrain','acrain1'].includes(row.product) && !supportsZeroAccumulation(run)) continue;
const key=[row.model,row.cycle,row.hour,row.domain,row.product].join('/');
// Only fields the viewer uses, so the Git and R2 sources produce identical snapshots.
const entry={model:row.model,cycle:row.cycle,hour:row.hour,domain:row.domain,
product:row.product,url:row.url,...(validUrl(row.fallback)?{fallback:row.fallback}:{})};
// A conflicting key must not silently select whichever upload was listed last.
if(next.has(key) && JSON.stringify(next.get(key))!==JSON.stringify(entry)) conflicts.add(key);
next.set(key,entry);
}
for(const key of conflicts) next.delete(key);
leadsByRun=nextLeads;
const nextSignature=JSON.stringify([...next].sort(([a],[b])=>a.localeCompare(b)));
if(nextSignature===signature) return false;
signature=nextSignature;
entries=next;
byRun=new Map();
for(const entry of entries.values()){
const key=entry.model+'/'+entry.cycle;
if(!byRun.has(key)) byRun.set(key,[]);
byRun.get(key).push(entry);
}
notifyChange();
return true;
}

function productIds({modelId,product,runUTC,forecastHour=0,variant='normal'}){
if(!supportsProduct(modelId,product) || !Number.isFinite(runUTC?.getTime?.())) return [];
const month=runUTC.getUTCMonth()+1;
if(product.id==='gph200') return [month>=11 || month<=4?'gph300':'gph200'];
if(product.id==='acrain' && forecastHour===0 && !supportsZeroAccumulation(runUTC)) return [];
// Winter precipitation composites start in October, one month before 300 hPa.
const winter=month>=10 || month<=4;
if(product.category==='hkor' && ['surfce','acptot'].includes(product.id)){
return variant==='compare' && winter && modelId!=='aigfs'
?['acptot1']:['acptot','surfce'];
}
if(product.id==='acrain' && variant==='compare' && winter && modelId!=='aigfs') return ['acrain1'];
return [product.id];
}

function resolveUrls(selection){
const {modelId,product,runUTC,forecastHour=0}=selection;
if((!usesSource(modelId,runUTC,forecastHour) && !supportsReplacement(modelId,product,runUTC)) || !hourAllowed(modelId,forecastHour,runUTC) ||
!publicWindowCurrent(modelId,runUTC)) return [];
const cycle=cycleFromDate(runUTC);
if(!parseCycle(cycle) || runUTC.getUTCMinutes() || runUTC.getUTCSeconds() || runUTC.getUTCMilliseconds()) return [];
for(const productId of productIds(selection)){
const entry=entries.get([modelId,cycle,forecastHour,product.category,productId].join('/'));
if(entry) return [entry.url];
}
return [];
}

function replacementFallbacks(value){
let id;
try{id=new URL(value).searchParams.get('id');}catch(error){return [];}
const row=[...entries.values()].find(row=>row.url===value) ||
(id ? [...entries.values()].find(row=>{try{return new URL(row.url).searchParams.get('id')===id;}catch(error){return false;}}) : null);
if(!row) return [];
const result=[];
// An R2 copy that fails to load falls back to the same image on Drive.
if(row.fallback) result.push(...(browserImageCandidates(row.fallback).length?browserImageCandidates(row.fallback):[row.fallback]));
if(row.model==='ukmo' && !ukmoFullCatalog(parseCycle(row.cycle),row.hour)){
const product=row.product.replace(/1$/,'');
result.push(`https://data.kma.go.kr/CHT/GDPS/${row.cycle.slice(0,6)}/${row.cycle.slice(6,8)}/ukum_erly_hkor_${product}_s${String(row.hour).padStart(3,'0')}_${row.cycle}.png`);
}
return result;
}

function readyHours(selection){
const rows=byRun.get(selection.modelId+'/'+cycleFromDate(selection.runUTC)) || [];
return [...new Set(rows.map(row=>row.hour))].filter(hour=>
resolveUrls({...selection,forecastHour:hour}).length>0
).sort((a,b)=>a-b);
}

function readyCycles(modelId,product){
const cycles=new Set();
for(const row of entries.values()){
if(row.model===modelId) cycles.add(row.cycle);
}
return [...cycles].filter(cycle=>!product || readyHours({modelId,product,runUTC:parseCycle(cycle)}).length)
.sort().reverse();
}

function hasPublishedCharts(modelId){
return readyCycles(modelId).length>0;
}

function withTimeout(ms,task){
const controller=typeof global.AbortController==='function'?new global.AbortController():null;
const timeout=controller?global.setTimeout(()=>controller.abort(),ms):null;
return task(controller?{signal:controller.signal}:{}).finally(()=>{
if(timeout!==null) global.clearTimeout(timeout);
});
}

async function fetchJson(url,options){
const response=await fetchImpl(url,{credentials:'omit',...options});
if(!response.ok) throw new Error('HTTP '+response.status);
return response.json();
}

function r2ImageUrl(model,cycle,name){
const match=R2_IMAGE.exec(typeof name==='string'?name:'');
if(!r2Origin || !match || match[1]!==model || match[5]!==cycle) return '';
return `${r2Origin}charts/${model}/${cycle}/${name}`;
}

function isR2ImageUrl(value){
if(!r2Origin || typeof value!=='string' || !value.startsWith(r2Origin+'charts/')) return false;
const parts=value.slice(r2Origin.length+7).split('/');
return parts.length===3 && R2_RUN.test(parts[0]+'/'+parts[1]) && !!r2ImageUrl(parts[0],parts[1],parts[2]);
}

function fragmentRows(model,cycle,fragment){
return fragment.charts.map(item=>{
if(!Array.isArray(item) || item.length<4 || item.length>5 || !DRIVE_FILE_ID.test(String(item[3]))) return null;
// "r2_..." identifies an image stored in R2 alone: it has no Drive file to fall back to.
const r2Only=String(item[3]).startsWith('r2_');
const row={model,cycle,hour:item[0],domain:item[1],product:item[2],url:r2Only?'':driveUrl(item[3])};
const extra=item[4];
if(extra && typeof extra==='object'){
for(const name of R2_EXTRA_FIELDS) if(name in extra) row[name]=extra[name];
// Images copied to R2 load from the custom domain; Drive stays the fallback when it has a copy.
const r2Url=r2ImageUrl(model,cycle,extra.r2);
if(r2Url){if(!r2Only) row.fallback=row.url; row.url=r2Url;}
delete row.r2;
}
return r2Only && !row.url ? null : row;
});
}

// Poll the small index; download only fragments whose revision changed. Throws on any
// inconsistency so the caller can fall back to the Git manifest for this poll.
async function loadR2(options){
const index=await fetchJson(r2Origin+'manifest/index.json',{cache:'no-cache',...options});
if(index?.schema!==R2_SCHEMA || index.images!=='drive' || !index.runs || typeof index.runs!=='object' ||
Array.isArray(index.runs) || !index.models || typeof index.models!=='object') throw new Error('Unsupported R2 index');
const runs=Object.entries(index.runs).filter(([run,item])=>R2_RUN.test(run) &&
/^[a-f0-9]{16}$/.test(String(item?.rev)) && Number.isInteger(item?.count));
const fetched=new Map();
const missing=runs.filter(([run,item])=>fragments.get(run)?.rev!==item.rev);
for(let start=0;start<missing.length;start+=R2_FETCH_CONCURRENCY){
await Promise.all(missing.slice(start,start+R2_FETCH_CONCURRENCY).map(async([run,item])=>{
const [,model,cycle]=run.match(R2_RUN);
const fragment=await fetchJson(`${r2Origin}manifest/runs/${model}/${cycle}.${item.rev}.json`,options);
if(fragment?.schema!==R2_SCHEMA || fragment.model!==model || fragment.cycle!==cycle ||
fragment.images!=='drive' || !Array.isArray(fragment.leads) || !Array.isArray(fragment.charts) ||
fragment.charts.length!==item.count) throw new Error('Invalid R2 fragment');
fetched.set(run,{rev:item.rev,rows:fragmentRows(model,cycle,fragment),leads:fragment.leads});
}));
}
calibrateClock(index.generated_at);
const key=JSON.stringify([index.models,runs.map(([run,item])=>[run,item.rev])]);
// Commit fragments only after every download succeeded.
for(const [run,value] of fetched) fragments.set(run,value);
const live=new Set(runs.map(([run])=>run));
for(const run of [...fragments.keys()]) if(!live.has(run)) fragments.delete(run);
if(key===r2Key && source==='r2') return false;
r2Key=key;
const charts=[];
const leads={};
for(const [run] of runs){
const value=fragments.get(run);
charts.push(...value.rows.filter(Boolean));
leads[run]=value.leads;
}
return replaceManifest({models:index.models,charts,leads});
}

async function loadGit(){
return withTimeout(12000,async options=>{
try{
const baseUrl=manifestUrl(location);
const requestUrl=baseUrl===REMOTE_MANIFEST?`${baseUrl}?t=${Math.floor(Date.now()/15000)}`:baseUrl;
const response=await fetchImpl(requestUrl,{cache:'no-store',credentials:'omit',...options});
if(!response.ok){
return {ok:false,changed:response.status===404?replaceManifest(null):false,source:'git'};
}
let manifest;
try{ manifest=await response.json(); }
catch(error){ return {ok:false,changed:replaceManifest(null),source:'git'}; }
source='git';
r2Key='';
return {ok:true,changed:replaceManifest(manifest),source:'git'};
}catch(error){
return {ok:false,changed:false,source:'git'};
}
});
}

async function load(){
expireReplacements();
if(pending) return pending;
pending=(async()=>{
if(r2Origin){
try{
const changed=await withTimeout(30000,options=>loadR2(options));
source='r2';
return {ok:true,changed,source:'r2'};
}catch(error){
// Images live in R2 alone and the Git manifest is no longer published, so an R2 problem keeps
// the last snapshot; R2 is retried at the next poll.
return {ok:false,changed:false,source:'r2'};
}
}
// Without an R2 origin (local development) the bundled Git manifest is the source.
return loadGit();
})();
try{ return await pending; }
finally{ pending=null; }
}

function stopPolling(){
if(timer!==null) global.clearInterval(timer);
timer=null;
}

function startPolling(onChange,{isActive=()=>false}={}){
if(typeof onChange==='function') listeners.add(onChange);
if(timer===null){
lastPollAt=Date.now();
timer=global.setInterval(()=>{
if(global.document?.visibilityState==='hidden') return;
if(!isActive() && Date.now()-lastPollAt<60000) return;
lastPollAt=Date.now();
return load();
},20000);
}
return load();
}

return {isModel,usesSource,ukmoFullCatalog,ukmoCurrent,publicWindowCurrent,publicWindowExpired,isReplacementProduct,supportsReplacement,supportsProduct,supportsZeroAccumulation,hasPublishedCharts,resolveUrls,replacementFallbacks,readyHours,readyCycles,
load,startPolling,stopPolling,getRevision:()=>revision,getSource:()=>source,getR2Base:()=>r2Origin};
}

global.CDSPublicCharts=Object.assign(createStore(),{createStore,manifestUrl,browserImageCandidates,clockNow});
})(typeof window!=='undefined'?window:globalThis);

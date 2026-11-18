(function(global){
'use strict';

const MODEL_IDS=new Set(['aifs','gfs','aigfs','cmc','icon']);
const SOURCE_MODEL_IDS=new Set([...MODEL_IDS,'ecmwf','ukmo']);
const COMMON_PRODUCTS=new Set(['gph200','gph500','gph700','ept850','ept925','wnd850','wnd925']);
const ROW_PRODUCTS=new Set([...COMMON_PRODUCTS,'gph300','surfce','acptot','acptot1','acrain','acrain1']);
const DRIVE_HOSTS=new Set(['drive.google.com','drive.usercontent.google.com','lh3.googleusercontent.com']);
const REMOTE_MANIFEST='https://raw.githubusercontent.com/SSalKim/CDS-Public-Charts/main/data/public_charts_manifest.json';
const ZERO_ACRAIN_CUTOVER='2026111612';
const UKMO_WINTER_CUTOVER='2026111800';

function isReplacementProduct(modelId,product){
return modelId==='ukmo' && product?.category==='hkor' && ['acptot','acrain'].includes(product.id);
}

function supportsReplacement(modelId,product,runUTC,nowMs=Date.now()){
const month=runUTC?.getUTCMonth?.()+1;
const age=nowMs-runUTC?.getTime?.();
return isReplacementProduct(modelId,product) &&
cycleFromDate(runUTC)>=UKMO_WINTER_CUTOVER && age>=0 && age<=48*3600000 &&
(month>=10 || month<=4) && [0,12].includes(runUTC?.getUTCHours?.());
}

function ukmoCurrent(runUTC,nowMs=Date.now()){
const age=nowMs-runUTC?.getTime?.();
return cycleFromDate(runUTC)>=UKMO_WINTER_CUTOVER && age>=0 && age<=48*3600000;
}

function ukmoFullCatalog(runUTC,forecastHour=0){
return cycleFromDate(runUTC)>=UKMO_WINTER_CUTOVER &&
([6,18].includes(runUTC?.getUTCHours?.()) || forecastHour>144);
}

function isModel(modelId){
return MODEL_IDS.has(modelId);
}

function usesSource(modelId,runUTC,forecastHour=0){
return isModel(modelId) || (modelId==='ecmwf' &&
Number.isFinite(runUTC?.getTime?.()) && [6,18].includes(runUTC.getUTCHours())) ||
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
const maximum=model==='ukmo'?([6,18].includes(runUTC?.getUTCHours?.())?69:168):model==='ecmwf'?144:model==='icon'?([6,18].includes(runUTC?.getUTCHours?.())?120:180):240;
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
const host=location?.hostname || '';
return ['localhost','127.0.0.1','[::1]','::1'].includes(host) || host.endsWith('.localhost')
?'data/public_charts_manifest.json':REMOTE_MANIFEST;
}

function createStore({fetchImpl=(...args)=>global.fetch(...args),location=global.location}={}){
let entries=new Map();
let byRun=new Map();
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
if(row.model!=='ukmo' || ukmoCurrent(parseCycle(row.cycle))) continue;
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

function replaceManifest(manifest){
const next=new Map();
const conflicts=new Set();
const published=manifest?.models;
for(const row of Array.isArray(manifest?.charts)?manifest.charts:[]){
if(!row || !SOURCE_MODEL_IDS.has(row.model) || published?.[row.model]?.published!==true ||
!validHour(row.model,row.hour,parseCycle(row.cycle)) || !ROW_PRODUCTS.has(row.product) ||
!['asia','hkor'].includes(row.domain) || !validUrl(row.url)) continue;
const run=parseCycle(row.cycle);
if(!run || !(row.model==='cmc'?[0,12]:[0,6,12,18]).includes(run.getUTCHours())) continue;
if(row.model==='ecmwf' && (!usesSource(row.model,run) || row.cycle<'2026111606')) continue;
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
const entry={model:row.model,cycle:row.cycle,hour:row.hour,domain:row.domain,
product:row.product,url:row.url,sha256:row.sha256 || '',size:row.size || 0};
// A conflicting key must not silently select whichever upload was listed last.
if(next.has(key) && JSON.stringify(next.get(key))!==JSON.stringify(entry)) conflicts.add(key);
next.set(key,entry);
}
for(const key of conflicts) next.delete(key);
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
if((!usesSource(modelId,runUTC,forecastHour) && !supportsReplacement(modelId,product,runUTC)) || !validHour(modelId,forecastHour,runUTC) ||
modelId==='ukmo' && !ukmoCurrent(runUTC)) return [];
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
if(!id) return [];
const row=[...entries.values()].find(row=>row.model==='ukmo' && !ukmoFullCatalog(parseCycle(row.cycle),row.hour) && new URL(row.url).searchParams.get('id')===id);
if(!row) return [];
const product=row.product.replace(/1$/,'');
return [`https://data.kma.go.kr/CHT/GDPS/${row.cycle.slice(0,6)}/${row.cycle.slice(6,8)}/ukum_erly_hkor_${product}_s${String(row.hour).padStart(3,'0')}_${row.cycle}.png`];
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

async function load(){
expireReplacements();
if(pending) return pending;
pending=(async()=>{
const controller=typeof global.AbortController==='function'?new global.AbortController():null;
const timeout=controller?global.setTimeout(()=>controller.abort(),12000):null;
try{
const baseUrl=manifestUrl(location);
const requestUrl=baseUrl===REMOTE_MANIFEST?`${baseUrl}?t=${Math.floor(Date.now()/15000)}`:baseUrl;
const response=await fetchImpl(requestUrl,{
cache:'no-store',credentials:'omit',...(controller?{signal:controller.signal}:{})
});
if(!response.ok){
return {ok:false,changed:response.status===404?replaceManifest(null):false};
}
let manifest;
try{ manifest=await response.json(); }
catch(error){ return {ok:false,changed:replaceManifest(null)}; }
return {ok:true,changed:replaceManifest(manifest)};
}catch(error){
return {ok:false,changed:false};
}finally{
if(timeout!==null) global.clearTimeout(timeout);
}
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

return {isModel,usesSource,ukmoFullCatalog,ukmoCurrent,isReplacementProduct,supportsReplacement,supportsProduct,supportsZeroAccumulation,hasPublishedCharts,resolveUrls,replacementFallbacks,readyHours,readyCycles,
load,startPolling,stopPolling,getRevision:()=>revision};
}

global.CDSPublicCharts=Object.assign(createStore(),{createStore,manifestUrl,browserImageCandidates});
})(typeof window!=='undefined'?window:globalThis);

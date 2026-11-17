(function(){
'use strict';
const config=window.CDS_USAGE_CONFIG || {};
const queue=[];
let timer=null;
let sending=false;
let identity=null;
let identityAt=0;
let identityPending=null;
let retryAfter=0;
const clean=(value,limit=100)=>typeof value==='string' ? value.trim().slice(0,limit) : '';

function isAllowed(){
try{
return localStorage.getItem('cds.analytics.optout')!=='1' && navigator.globalPrivacyControl!==true &&
navigator.doNotTrack!=='1' && window[`ga-disable-${config.measurementId}`]!==true;
}
catch(error){
return navigator.globalPrivacyControl!==true && navigator.doNotTrack!=='1' && window[`ga-disable-${config.measurementId}`]!==true;
}
}

function setEnabled(enabled){
try{
localStorage.setItem('cds.analytics.optout',enabled ? '0' : '1');
}
catch(error){}
window[`ga-disable-${config.measurementId}`]=!enabled;
if(!enabled){
queue.length=0;
identity=null;
if(timer) clearTimeout(timer);
timer=null;
}
}

function endpoint(){
if(!config.enabled || !config.endpoint) return null;
try{
const url=new URL(config.endpoint,location.href);
return (url.protocol==='https:' || (url.protocol==='http:' && ['localhost','127.0.0.1'].includes(url.hostname))) &&
url.pathname==='/collect' && !url.username && !url.password ? url.href : null;
}
catch(error){return null;}
}

function getTagValue(field){
return new Promise(resolve=>{
let settled=false;
const finish=value=>{if(!settled){settled=true;clearTimeout(timeout);resolve(value);}};
const timeout=setTimeout(()=>finish(null),1800);
try{window.gtag('get',config.measurementId,field,finish);}
catch(error){finish(null);}
});
}

async function getIdentity(){
if(identity && Date.now()-identityAt<120000) return identity;
if(identityPending) return identityPending;
identityPending=(async()=>{
// Reuse Analytics' browser identifier; never create a replacement if Analytics is blocked.
const client=await getTagValue('client_id');
const session=await getTagValue('session_id');
identityPending=null;
if(!/^\d{1,20}\.\d{1,20}$/.test(String(client || '')) || !/^\d{1,20}$/.test(String(session || ''))) return null;
identity={client_id:String(client),session_id:String(session)};
identityAt=Date.now();
return identity;
})();
return identityPending;
}

function deviceClass(){
return window.matchMedia?.('(pointer: coarse)').matches ? (window.innerWidth<768 ? 'mobile' : 'tablet') : 'desktop';
}

function schedule(){
if(!timer && queue.length){timer=setTimeout(()=>{timer=null;void flush();},Math.max(3000,retryAfter-Date.now()));}
}

async function flush(){
const target=endpoint();
if(sending || !queue.length || !target || !isAllowed()) return;
sending=true;
const batch=queue.splice(0,12);
try{
const id=await getIdentity();
if(!id || !isAllowed()) return;
const response=await fetch(target,{method:'POST',credentials:'omit',keepalive:true,
headers:{'Content-Type':'application/json'},body:JSON.stringify({version:1,...id,events:batch})});
if(response.status===429 && isAllowed()){
retryAfter=Date.now()+60000;
queue.unshift(...batch);
queue.splice(100);
}
}
catch(error){/* Telemetry cannot interrupt charts; no persistent offline browsing log. */}
finally{sending=false;schedule();}
}

function record(name,params){
if(!['cds_product_view','cds_product_missing'].includes(name) || !endpoint() || !isAllowed()) return;
if(document.visibilityState==='hidden' || queue.length>=100 || !window.crypto?.randomUUID) return;
const lead=Number(params.forecast_hour);
const event={event_id:crypto.randomUUID(),occurred_at:Date.now(),
outcome:name==='cds_product_view' ? 'view' : 'missing',
menu:clean(params.menu,30),region:clean(params.category,40),product_id:clean(params.product_id,60),
product_label:clean(params.product_label || params.product_name),model_id:clean(params.model_id,50),
model_label:clean(params.model_name,80),run_utc:clean(params.run_utc,30),valid_utc:clean(params.valid_utc,30),
forecast_hour:params.forecast_hour!==undefined && Number.isFinite(lead) ? lead : null,
detail_token:clean(params.detail_token,60),view_context:params.view_context==='compare' ? 'compare' : 'single',
image_source:clean(params.image_source,60),loaded_count:Number(params.loaded_count || 0),
expected_count:Number(params.url_count || 0),load_ms:Number.isFinite(params.load_ms) ? params.load_ms : null,
device_class:deviceClass()};
if(!event.model_id || !event.product_id || !event.region || !event.run_utc) return;
queue.push(event);
schedule();
}

window.addEventListener('pagehide',()=>{void flush();});
document.addEventListener('visibilitychange',()=>{if(document.visibilityState==='hidden') void flush();});
window.CDSUsage={record,flush,isAllowed,setEnabled};
})();

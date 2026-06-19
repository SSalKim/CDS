(function(){
'use strict';

var DEFAULT_DEDUPE_MS=30000;
var STRING_LIMIT=100;
var lastEventAt=new Map();

window.dataLayer=window.dataLayer || [];
window.gtag=window.gtag || function(){
window.dataLayer.push(arguments);
};

function isPlainValue(value){
return (
typeof value==='string' ||
typeof value==='number' ||
typeof value==='boolean'
);
}

function cleanValue(value){
if(value===null || value===undefined){
return undefined;
}

if(typeof value==='number'){
return Number.isFinite(value) ? value : undefined;
}

if(typeof value==='boolean'){
return value ? 'true' : 'false';
}

if(typeof value==='string'){
let trimmed=value.trim();
return trimmed ? trimmed.slice(0,STRING_LIMIT) : undefined;
}

if(Array.isArray(value)){
let joined=value
.map(item=>cleanValue(item))
.filter(item=>item!==undefined)
.join(',');
return joined ? joined.slice(0,STRING_LIMIT) : undefined;
}

if(isPlainValue(value)){
return value;
}

return undefined;
}

function cleanParams(params){
let out={};
Object.keys(params || {}).forEach(key=>{
if(key==='analytics_key'){
return;
}

let value=cleanValue(params[key]);
if(value!==undefined){
out[key]=value;
}
});
return out;
}

function sourceFromUrl(value){
let url=String(value || '').trim();
if(!url){
return 'unknown';
}

try{
let parsed=new URL(url,window.location.href);
let host=parsed.hostname.toLowerCase();
let path=parsed.pathname.toLowerCase();

if(host==='raw.githubusercontent.com'){
return 'github_raw';
}

if(host.endsWith('github.io')){
return 'github_pages';
}

if(host==='drive.google.com' && path.startsWith('/thumbnail')){
return 'drive_thumbnail';
}

if(host==='lh3.googleusercontent.com'){
return 'drive_lh3';
}

if(host==='drive.usercontent.google.com'){
return 'drive_usercontent';
}

if(host.includes('radar.kma.go.kr')){
return 'kma_radar';
}

if(host.includes('nmsc.kma.go.kr')){
return 'kma_satellite';
}

if(host.includes('data.kma.go.kr')){
return 'kma_data';
}

if(host.includes('afso.kma.go.kr')){
return 'kma_afso';
}

if(host===window.location.hostname){
return 'site_local';
}

return host.replace(/^www\./,'').slice(0,60);
}
catch(error){
return 'relative_or_invalid';
}
}

function eventKey(eventName,params){
return [
eventName,
params?.analytics_key ||
params?.product_key ||
params?.radar_key ||
params?.storm_key ||
'generic'
].join('|');
}

function shouldSkipDuplicate(key,dedupeMs){
if(!key || dedupeMs<=0){
return false;
}

let now=Date.now();
let previous=lastEventAt.get(key);
if(previous && now-previous<dedupeMs){
return true;
}

lastEventAt.set(key,now);

if(lastEventAt.size>500){
let cutoff=now-(DEFAULT_DEDUPE_MS*4);
lastEventAt.forEach((value,mapKey)=>{
if(value<cutoff){
lastEventAt.delete(mapKey);
}
});
}

return false;
}

function track(eventName,params,options){
let name=String(eventName || '').trim();
if(!name){
return;
}

let opts=options || {};
let key=opts.key || eventKey(name,params || {});
let dedupeMs=Number.isFinite(Number(opts.dedupeMs)) ? Number(opts.dedupeMs) : DEFAULT_DEDUPE_MS;

if(shouldSkipDuplicate(key,dedupeMs)){
return;
}

let cleaned=cleanParams(params || {});

try{
window.gtag('event',name,cleaned);
}
catch(error){}

if(window.CDS_ANALYTICS_DEBUG && window.console){
window.console.debug('[CDSAnalytics]',name,cleaned);
}
}

window.CDSAnalytics={
track,
trackProductView(params,options){
track('cds_product_view',params,options);
},
trackRadarView(params,options){
track('radar_view',params,options);
},
trackTyphoonView(params,options){
track('vtg_storm_view',params,options);
},
trackTyphoonImageFailure(params,options){
track('vtg_image_load_failed',params,options);
},
sourceFromUrl
};

})();

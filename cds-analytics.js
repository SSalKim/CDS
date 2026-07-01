(function(){
'use strict';

var DEFAULT_DEDUPE_MS=30000;
var STRING_LIMIT=100;
var lastEventAt=new Map();
var lastDistinctViewKey=new Map();
var PRODUCT_GROUP_LABELS={
edit:'편집일기도',
analysis:'분석장',
forecast:'예보장',
hazard:'위험기상',
ensemble:'앙상블'
};

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

function trackDistinctView(eventName,params,options,group,key){
let distinctGroup=String(group || eventName || '').trim();
let distinctKey=String(key || '').trim();
if(distinctGroup && distinctKey){
if(lastDistinctViewKey.get(distinctGroup)===distinctKey){
return;
}
lastDistinctViewKey.set(distinctGroup,distinctKey);
}

track(eventName,params,{
...(options || {}),
key:`${eventName}|${distinctGroup}|${distinctKey}`,
dedupeMs:0
});
}

function withProductHierarchy(params,type){
let out={...(params || {})};
let group='';
let label='';
let variant='';

if(type==='radar'){
group='레이더';
label=out.radar_label || out.radar_product || '';
}
else if(type==='vtg'){
group='태풍모델예측';
label=out.storm_label || out.storm_name || out.storm_key || '';
variant=out.forecast_range || '';
}
else{
group=PRODUCT_GROUP_LABELS[out.menu] || out.menu || '';
label=out.product_label || out.product_name || out.product_id || '';
}

if(group){
out.product_group=group;
}
if(label){
out.product_label=label;
}
if(variant){
out.product_variant=variant;
}
if(group && label){
out.product_name=[group,label,variant].filter(Boolean).join('-');
}

return out;
}

window.CDSAnalytics={
track,
trackProductView(params,options){
let enriched=withProductHierarchy(params,'product');
let compare=enriched.view_context==='compare';
let key=[
enriched.menu || '',
enriched.category || '',
enriched.product_id || '',
compare ? 'compare' : (enriched.model_id || ''),
enriched.detail_token || ''
].join('|');
trackDistinctView('cds_product_view',enriched,options,'cds_product_view',key);
},
trackRadarView(params,options){
let enriched=withProductHierarchy(params,'radar');
let pane=Number(enriched.pane_index || 1);
trackDistinctView(
'radar_view',
enriched,
options,
`radar_view|${pane}`,
enriched.radar_key || enriched.radar_product || enriched.radar_label || 'radar'
);
},
trackTyphoonView(params,options){
let enriched=withProductHierarchy(params,'vtg');
let key=[enriched.storm_key || '',enriched.fcst_hours || ''].join('|');
trackDistinctView('vtg_storm_view',enriched,options,'vtg_storm_view',key);
},
trackTyphoonImageFailure(params,options){
track('vtg_image_load_failed',params,options);
},
sourceFromUrl
};

})();

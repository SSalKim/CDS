/* Forecast archive/status, lead-time, and URL selection helpers. Depends on app.js globals at call time. */

function hasProductArchiveOverride(product,modelId){

return !!(
product &&
(
Object.prototype.hasOwnProperty.call(product.archiveStartByModel || {},modelId) ||
Object.prototype.hasOwnProperty.call(product.archiveEndByModel || {},modelId)
)
);

}


function getEffectiveArchiveRange(modelId,product=null){

let m=MODELS[modelId] || {};

let start=m.archiveStart || null;
let end=m.archiveEnd || null;

/*
산출물별 모델 기간 override가 있으면 models.js 기본값보다 우선한다.
예: 같은 파일명이지만 기간에 따라 um_anal / ecmwf_ra로 나뉘는 경우
*/
if(
product &&
Object.prototype.hasOwnProperty.call(product.archiveStartByModel || {},modelId)
){
start=product.archiveStartByModel[modelId] || null;
}

if(
product &&
Object.prototype.hasOwnProperty.call(product.archiveEndByModel || {},modelId)
){
end=product.archiveEndByModel[modelId] || null;
}

return {start,end};

}


function getEffectiveModelStatus(modelId,date,product=null){

let m=MODELS[modelId];

if(!m){
return {
available:false,
message:`${modelId} 모델 메타데이터가 없습니다.`
};
}

let {start,end}=getEffectiveArchiveRange(
modelId,
product
);

let dateOnly=parseDateOnly(
formatDateInputFromUTCParts(date)
);

if(start && dateOnly < parseDateOnly(start)){
return {
available:false,
message:
`자료 보유기간 이전입니다.\n자료 보유기간: ${start} ~ ${end || '현재'}`
};
}

if(end && dateOnly > parseDateOnly(end)){
return {
available:false,
message:
`운영 종료된 모델입니다.\n자료 보유기간: ${start || '미상'} ~ ${end}`
};
}

/*
주의:
models.js의 getModelStatus()는 product별 archiveStartByModel/archiveEndByModel을 모른다.
product override가 있는 경우에는 legacy getModelStatus를 호출하면
다시 models.js 기본 기간으로 잘못 차단될 수 있으므로 건너뛴다.
*/
if(
!hasProductArchiveOverride(product,modelId) &&
typeof getModelStatus==='function'
){
let legacyStatus=getModelStatus(modelId,dateOnly);

if(legacyStatus && legacyStatus.available===false){
return legacyStatus;
}
}

return {
available:true,
message:''
};

}


function getProductArchiveStatus(product,modelId,date){

if(!product){
return {
available:false,
message:'선택된 산출자료를 찾을 수 없습니다.'
};
}

let start=
product.archiveStartByModel?.[modelId] ||
product.archiveStart ||
null;

let end=
product.archiveEndByModel?.[modelId] ||
product.archiveEnd ||
null;

if(start && date < parseDateOnly(start)){
return {
available:false,
message:makeProductArchiveStartMessage({
modelId,
product,
start
})
};
}

if(end && date > parseDateOnly(end)){
return {
available:false,
message:makeProductArchiveEndMessage({
modelId,
product,
end
})
};
}

return {
available:true,
message:''
};

}


function productUsesForecastHour(){

let patterns=getCurrentPatterns();

return patterns.some(
pattern=>pattern.includes('{fh}')
);

}


function isRunTimeSliderMode(){

return !!(
!modelCompareMode &&
['edit','analysis'].includes(currentMainMenu) &&
!productUsesForecastHour()
);

}

function getCurrentRunCycleStepHours(){

let p=getCurrentProduct();
let date=parseDateOnly(runDate.value || formatDateInputLocal(new Date()));
let cycles=getCyclesForSelection(
currentModel,
p,
date
) || [];

let sorted=[...new Set(cycles.map(Number))]
.filter(h=>!Number.isNaN(h))
.sort((a,b)=>a-b);

if(sorted.length<=1){
return 6;
}

let minStep=24;

for(let i=0;i<sorted.length;i++){
let current=sorted[i];
let next=sorted[(i+1)%sorted.length];
let diff=(next-current+24)%24;
if(diff>0){
minStep=Math.min(minStep,diff);
}
}

return Number.isFinite(minStep) && minStep>0 ? minStep : 6;

}

function buildRunTimeSliderOffsets(){

let step=getCurrentRunCycleStepHours();
let offsets=[];

for(let i=-4;i<=4;i++){
offsets.push(i*step);
}

return offsets;

}

function getRunUTCForForecastIndex(index){

let base=getSelectedUTCDate();

if(isRunTimeSliderMode()){
let offset=Number(currentForecastList[index] ?? 0);
return new Date(base.getTime()+offset*60*60*1000);
}

return base;

}

function getRunTimeOffsetLabel(offset){

let value=Number(offset || 0);

if(value===0){
return '기준';
}

return `${value>0?'+':''}${value}h`;

}


function expandProductSteps(scheme,maxLead){

let out=[];

scheme.forEach(rule=>{

let end=Math.min(rule.end,maxLead);

for(let h=rule.start;h<=end;h+=rule.step){
out.push(h);
}

});

return [...new Set(out)].sort((a,b)=>a-b);

}


function getForecastHoursForCurrentSelection(){

let p=getCurrentProduct();
let utcHour=parseInt(getUTCStamp().slice(8,10),10);
let productScheme=p?.forecastStepByModel?.[currentModel];

if(productScheme){

let modelHours=getForecastHours(
currentModel,
parseDateOnly(runDate.value),
utcHour
) || [0];

let maxLead=Math.max(...modelHours);
return expandProductSteps(productScheme,maxLead);

}

return getForecastHours(
currentModel,
parseDateOnly(runDate.value),
utcHour
) || [0];

}



function buildImageUrlsForForecastIndex(index){

let p=getCurrentProduct();

if(!p){
return [];
}

let runUTC=getRunUTCForForecastIndex(index);
let fhValue=isRunTimeSliderMode()
?0
:(currentForecastList[index] ?? currentForecastList[0] ?? 0);
let detailToken=getCurrentAuxToken();

return makeChartImageUrls({
product:p,
modelId:currentModel,
runUTC,
forecastHour:fhValue,
detailToken
});

}

function buildImageUrlsForDetailValue(detailValue,index=Number(slider.value || 0)){

let p=getCurrentProduct();

if(!p){
return [];
}

let runUTC=getRunUTCForForecastIndex(index);
let fhValue=isRunTimeSliderMode()
?0
:(currentForecastList[index] ?? currentForecastList[0] ?? 0);

return makeChartImageUrls({
product:p,
modelId:currentModel,
runUTC,
forecastHour:fhValue,
detailToken:detailValue
});

}

function getForecastHourAtIndex(index){
return forecastTimelineState.getHour(index);
}


function getForecastLeadLabel(index){

let h=getForecastHourAtIndex(index);

if(isRunTimeSliderMode()){
return getRunTimeOffsetLabel(h);
}

if(!productUsesForecastHour()){
return '단일';
}

return '+'+String(h).padStart(3,'0')+'h';

}


function getValidTimeLabel(index){

let h=getForecastHourAtIndex(index);
let utc=getSelectedUTCDate();
let validUTC=new Date(utc.getTime()+h*60*60*1000);
let display=timeMode==='KST'
?new Date(validUTC.getTime()+9*60*60*1000)
:new Date(validUTC.getTime());

let day=pad2(display.getUTCDate());
let hour=pad2(display.getUTCHours());
return `${day}.${hour}`;

}

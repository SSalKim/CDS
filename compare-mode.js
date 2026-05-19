/* Model comparison mode, comparison timeline, and comparison image rendering helpers. Depends on app.js globals at call time. */

const COMPARE_WINTER_VARIANT_ARCHIVE_START='2020-12-29';
const COMPARE_WINTER_VARIANT_CATEGORY='hkor';
const COMPARE_WINTER_VARIANT_PRODUCTS=new Set(['acptot','acrain','tmerge']);
const COMPARE_HKOR_ACPTOT_REGIONAL_MODELS=new Set(['kim_rdps','kim_ldps']);
const COMPARE_WINTER_VARIANT_UNSUPPORTED_MODELS=new Set(['ukmo','um_ldps']);

function supportsModelCompareInCurrentMenu(){

return !['edit','analysis'].includes(currentMainMenu);

}

function disableModelCompareMode(){

if(!modelCompareMode && !compareModels.length){
return;
}

modelCompareMode=false;
compareModels=[];
stopCompareAnimation();

}

function getCompareLayoutOptions(count=compareModels.length){

let n=Math.max(1,Number(count)||1);

if(n===1){
return [{cols:1,rows:1,label:'1×1',filledCount:1}];
}

if(n===2){
return [
{cols:2,rows:1,label:'2×1',filledCount:2},
{cols:1,rows:2,label:'1×2',filledCount:2}
];
}

if(n===3){
return [
{cols:3,rows:1,label:'3×1',filledCount:3},
{cols:2,rows:2,label:'2×2',filledCount:3},
{cols:1,rows:3,label:'1×3',filledCount:3}
];
}

if(n===4){
return [
{cols:4,rows:1,label:'4×1',filledCount:4},
{cols:3,rows:2,label:'3×2',filledCount:4},
{cols:2,rows:2,label:'2×2',filledCount:4},
{cols:1,rows:4,label:'1×4',filledCount:4}
];
}

if(n===5){
return [
{cols:5,rows:1,label:'5×1',filledCount:5},
{cols:4,rows:2,label:'4×2',filledCount:5},
{cols:3,rows:2,label:'3×2',filledCount:5},
{cols:2,rows:3,label:'2×3',filledCount:5},
{cols:1,rows:5,label:'1×5',filledCount:5}
];
}

if(n===6){
return [
{cols:6,rows:1,label:'6×1',filledCount:6},
{cols:5,rows:2,label:'5×2',filledCount:6},
{cols:4,rows:2,label:'4×2',filledCount:6},
{cols:3,rows:2,label:'3×2',filledCount:6},
{cols:2,rows:3,label:'2×3',filledCount:6},
{cols:1,rows:6,label:'1×6',filledCount:6}
];
}

return [
{cols:Math.min(n,COMPARE_MAX_MODELS),rows:1,label:`${Math.min(n,COMPARE_MAX_MODELS)}×1`,filledCount:n},
{cols:5,rows:Math.ceil(n/5),label:`5×${Math.ceil(n/5)}`,filledCount:n},
{cols:4,rows:Math.ceil(n/4),label:`4×${Math.ceil(n/4)}`,filledCount:n},
{cols:3,rows:Math.ceil(n/3),label:`3×${Math.ceil(n/3)}`,filledCount:n},
{cols:2,rows:Math.ceil(n/2),label:`2×${Math.ceil(n/2)}`,filledCount:n},
{cols:1,rows:n,label:`1×${n}`,filledCount:n}
];

}

function normalizeCompareLayout(){

let options=getCompareLayoutOptions(compareModels.length);

if(compareLayoutMode!=='manual'){
compareLayoutMode='auto';
compareManualLayout=null;
return;
}

if(
!compareManualLayout ||
!options.some(option=>
option.cols===compareManualLayout.cols &&
option.rows===compareManualLayout.rows
)
){
compareManualLayout=options[0] || {cols:1,rows:1,label:'1×1'};
}

}

function getAutoCompareColumns(){

let n=Math.max(1,compareModels.length || 1);
return Math.min(n,3);

}

function getActiveCompareLayout(){

normalizeCompareLayout();

if(compareLayoutMode==='manual' && compareManualLayout){
return compareManualLayout;
}

let cols=getAutoCompareColumns();
return {
cols,
rows:Math.ceil(Math.max(1,compareModels.length || 1)/cols),
label:'자동'
};

}

function renderLayoutMiniGrid(cols,rows,filledCount=null){

let safeCols=Math.max(1,Number(cols)||1);
let safeRows=Math.max(1,Number(rows)||1);
let total=safeCols*safeRows;
let filled=Math.min(
total,
Math.max(0,Number(filledCount ?? total)||0)
);
let cellWidth=safeCols>=5?4:(safeCols>=4?5:6);
let cellHeight=safeRows>=4?3:(safeRows>=3?4:5);
let cells='';

for(let i=0;i<total;i++){
cells+=`<span class="${i<filled?'filled':'empty'}"></span>`;
}

return (
`<span class="layout-mini" `+
`style="--layout-cols:${safeCols};--layout-rows:${safeRows};`+
`--layout-cell-w:${cellWidth}px;--layout-cell-h:${cellHeight}px">`+
`${cells}</span>`
);

}

function isModelCompareActive(){

return !!modelCompareMode;

}

function getModelButtonAllowed(modelId){

if(isModelCompareActive()){
return isModelComparableForCurrentProduct(modelId);
}

return isModelAllowedByCurrentCategory(modelId);

}

function getModelDisplayLabel(modelId){

for(let group of modelGroups){
for(let model of group.models){
if(model[0]===modelId){
return model[1];
}
}
}

return MODELS[modelId]?.name || modelId;

}

function getCompareProductForModel(modelId){

let categoryId=getCategoryIdForModelFiltering(modelId);
let product=getProductByIdInCategory(
categoryId,
currentProduct
);

if(!product || !productSupportsModel(product,modelId)){
return null;
}

return product;

}

function isHkorAcptotCompareProduct(product){

return product?.category===COMPARE_WINTER_VARIANT_CATEGORY &&
product?.id==='acptot';

}

function isHkorWinterVariantProduct(product){

return product?.category===COMPARE_WINTER_VARIANT_CATEGORY &&
COMPARE_WINTER_VARIANT_PRODUCTS.has(product?.id);

}

function shouldUsePrcp3hForHkorAcptotCompare(modelId,product){

return isHkorAcptotCompareProduct(product) &&
COMPARE_HKOR_ACPTOT_REGIONAL_MODELS.has(modelId);

}

function getEffectiveCompareProductForModel(modelId){

let product=getCompareProductForModel(modelId);

if(!product){
return null;
}

if(shouldUsePrcp3hForHkorAcptotCompare(modelId,product)){
return getProductByIdInCategory(product.category,'prcp3h') || product;
}

return product;

}

function isWinterSeasonRunDate(runUTC){

if(!(runUTC instanceof Date) || Number.isNaN(runUTC.getTime())){
return false;
}

let month=runUTC.getUTCMonth()+1;

return month>=11 || month<=4;

}

function hasWinterVariantCompareArchiveStarted(runUTC){

let archiveStart=parseDateOnly(COMPARE_WINTER_VARIANT_ARCHIVE_START);

if(!archiveStart || !(runUTC instanceof Date) || Number.isNaN(runUTC.getTime())){
return false;
}

let runDate=parseDateOnly(formatDateInputFromUTCParts(runUTC));

return !!runDate && runDate>=archiveStart;

}

function shouldUseWinterCompareVariant(modelId,baseProduct,runUTC){

if(COMPARE_WINTER_VARIANT_UNSUPPORTED_MODELS.has(modelId)){
return false;
}

return isHkorWinterVariantProduct(baseProduct) &&
isWinterSeasonRunDate(runUTC) &&
hasWinterVariantCompareArchiveStarted(runUTC);

}

function getWinterCompareVariantPattern(pattern,productId){

if(typeof pattern!=='string'){
return pattern;
}

if(productId==='tmerge'){
if(pattern.includes('tmerge')){
return pattern.replace('tmerge','tmerge1');
}

return pattern.replace('merg','merg1');
}

let token=productId==='prcp3h'?'prcp3h':productId;

return pattern.replace(token,`${token}1`);

}

function getWinterCompareVariantPatterns(product,modelId){

let pattern=product?.patternByModel?.[modelId];
let patterns=Array.isArray(pattern)
?pattern
:[pattern];

return patterns.map(p=>getWinterCompareVariantPattern(p,product?.id));

}

function isModelComparableForCurrentProduct(modelId){

if(!isModelVisibleInCurrentMenu(modelId)){
return false;
}

/*
비교 가능 여부는 “현재 날짜에 실제 이미지가 있느냐”가 아니라
“현재 산출물의 파일 패턴을 이 모델이 지원하느냐”만 본다.
운영 종료, 보유기간 밖, 미지원 cycle, 아직 미생산 같은 상태는
비교 카드 안에서 구체적인 메시지로 표시한다.
*/
return !!getCompareProductForModel(modelId);

}

function getComparableModelsForCurrentProduct(){

let out=[];

getVisibleModelGroups().forEach(group=>{
if(group.hidden){
return;
}

group.models.forEach(model=>{
let modelId=model[0];
if(isModelComparableForCurrentProduct(modelId)){
out.push(modelId);
}
});
});

return out;

}

function normalizeCompareModels(){

let comparable=getComparableModelsForCurrentProduct();
let comparableSet=new Set(comparable);

compareModels=compareModels.filter(modelId=>
comparableSet.has(modelId)
);

if(compareModels.length===0){
if(comparableSet.has(currentModel)){
compareModels=[currentModel];
}
else if(comparable.length){
compareModels=[comparable[0]];
}
}

if(compareModels.length>COMPARE_MAX_MODELS){
compareModels=compareModels.slice(0,COMPARE_MAX_MODELS);
}

normalizeCompareLayout();

return compareModels;

}

function toggleModelCompareMode(){

if(!supportsModelCompareInCurrentMenu()){
disableModelCompareMode();
return;
}

let previousForecastHour=getSelectedForecastHour();

invalidateSelectionAsyncWork({latest:false,aux:false});
modelCompareMode=!modelCompareMode;
stopCompareAnimation();

if(modelCompareMode){

compareModels=[];

if(isModelComparableForCurrentProduct(currentModel)){
compareModels.push(currentModel);
}

let comparable=getComparableModelsForCurrentProduct();

if(compareModels.length===0 && comparable.length){
compareModels.push(comparable[0]);
}

}

refreshView({
updateCategories:false,
updateProducts:true,
updateHours:true,
resetSlider:true,
preserveForecastHour:previousForecastHour,
updateChartAfter:true
});

}

function toggleCompareModel(modelId){

if(!isModelComparableForCurrentProduct(modelId)){
return;
}

let previousForecastHour=getSelectedForecastHour();
let idx=compareModels.indexOf(modelId);

if(idx>=0){
if(compareModels.length<=1){
return;
}
compareModels.splice(idx,1);
}
else{
if(compareModels.length>=COMPARE_MAX_MODELS){
showViewerNotice(`모델 비교는 최대 ${COMPARE_MAX_MODELS}개까지 선택할 수 있습니다.`);
return;
}
compareModels.push(modelId);
}

invalidateSelectionAsyncWork({latest:false,aux:false});

if(!compareModels.includes(currentModel)){
currentModel=compareModels[0] || currentModel;
}

refreshView({
updateCategories:false,
updateProducts:true,
updateHours:true,
resetSlider:true,
preserveForecastHour:previousForecastHour,
updateChartAfter:true
});

}

function renderModelCompareToggle(){

if(!supportsModelCompareInCurrentMenu()){
return null;
}

let section=document.createElement('div');
section.className='model-section model-compare-section';

let btn=document.createElement('button');
btn.type='button';
btn.className='model-compare-toggle'+(modelCompareMode?' active':'');
btn.textContent=modelCompareMode?'모델비교 ON':'모델비교 OFF';
btn.onclick=toggleModelCompareMode;

section.appendChild(btn);
return section;

}

function productUsesForecastHourForModel(product,modelId){

let pattern=product?.patternByModel?.[modelId];
let patterns=Array.isArray(pattern)
?pattern
:[pattern];

return patterns.some(
p=>typeof p==='string' && p.includes('{fh}')
);

}

function getForecastHoursForCompareModel(modelId){

let product=getEffectiveCompareProductForModel(modelId);

if(!product){
return [];
}

let modelStatus=getEffectiveModelStatus(
modelId,
getSelectedUTCDate(),
product
);

if(!modelStatus.available){
return [];
}

let productStatus=getProductArchiveStatus(
product,
modelId,
parseDateOnly(runDate.value)
);

if(!productStatus.available){
return [];
}

let cycleStatus=getCycleSupportStatus(
modelId,
product,
getSelectedUTCDate()
);

if(!cycleStatus.supported){
return [];
}

if(!productUsesForecastHourForModel(product,modelId)){
return [0];
}

let utcHour=parseInt(getUTCStamp().slice(8,10),10);
let modelHours=getForecastHours(
modelId,
parseDateOnly(runDate.value),
utcHour
) || [0];

let productScheme=product?.forecastStepByModel?.[modelId];

if(productScheme){
let maxLead=Math.max(...modelHours);
return expandProductSteps(productScheme,maxLead);
}

return modelHours;

}

function buildCompareForecastData(){

normalizeCompareModels();
compareForecastHourMap=new Map();

let union=new Set();

compareModels.forEach(modelId=>{
let hours=getForecastHoursForCompareModel(modelId);
compareForecastHourMap.set(
modelId,
new Set(hours.map(h=>Number(h)))
);
hours.forEach(h=>union.add(Number(h)));
});

let list=[...union].sort((a,b)=>a-b);

if(!list.length){
list=[0];
}

return list;

}

function compareModelHasForecastHour(modelId,forecastHour){

let set=compareForecastHourMap.get(modelId);

if(!set){
return false;
}

return set.has(Number(forecastHour));

}

function rebuildCompareForecastAxis({
reset=true,
preserveForecastHour=null
}={}){

let oldValue=Number(slider.value || 0);
setCurrentForecastList(buildCompareForecastData());

slider.min=0;
slider.max=currentForecastList.length-1;
slider.step=1;
slider.disabled=currentForecastList.length<=0;

let preservedIndex=getForecastIndexByHour(preserveForecastHour);

if(preservedIndex>=0){
slider.value=String(preservedIndex);
}
else if(reset){
slider.value=0;
}
else{
slider.value=forecastTimelineState.clampIndex(oldValue);
}

updateForecastLabel();
renderCompareForecastTimeline();

}

function getValidTimeLabelForForecastHour(forecastHour){

let h=Number(forecastHour || 0);
let utc=getSelectedUTCDate();
let validUTC=new Date(utc.getTime()+h*60*60*1000);
let display=timeMode==='KST'
?new Date(validUTC.getTime()+9*60*60*1000)
:new Date(validUTC.getTime());

let day=pad2(display.getUTCDate());
let hour=pad2(display.getUTCHours());
return `${day}.${hour}`;

}

function getForecastLeadLabelForHour(forecastHour){

if(isRunTimeSliderMode()){
return getRunTimeOffsetLabel(forecastHour);
}

if(!productUsesForecastHour()){
return '단일';
}

return '+'+String(Number(forecastHour || 0)).padStart(3,'0')+'h';

}

function setCompareForecastIndex(index){

let next=forecastTimelineState.clampIndex(index);

slider.value=String(next);
updateForecastLabel();
updateCompareTimelineActiveLabels();
renderCompareImages();

}

function moveCompareForecastSelection(delta){

let max=(currentForecastList.length || 1)-1;

if(max<=0){
return;
}

let current=Number(slider.value || 0);
let next=current+delta;

if(next<0){
next=max;
}
else if(next>max){
next=0;
}

setCompareForecastIndex(next);

}

function playCompareAnimation(){

playTimelineAnimation();

}

function stopCompareAnimation(){

if(comparePlayTimer){
clearInterval(comparePlayTimer);
comparePlayTimer=null;
}

}

function moveForecastSelectionLoop(delta){

let max=(currentForecastList.length || 1)-1;

if(max<=0 || slider.disabled){
return;
}

let current=Number(slider.value || 0);
let next=current+delta;

if(next<0){
next=max;
}
else if(next>max){
next=0;
}

setForecastIndex(next);

}

function moveTimelineSelection(delta){

if(modelCompareMode){
moveCompareForecastSelection(delta);
return;
}

moveForecastSelectionLoop(delta);

}

function playTimelineAnimation(){

stopCompareAnimation();

comparePlayTimer=setInterval(()=>{
moveTimelineSelection(1);
},COMPARE_PLAY_INTERVAL_MS);

}

function renderTimelinePlaybackControls(){

let prev=document.createElement('button');
prev.type='button';
prev.textContent='‹';
prev.title='이전 이미지';
prev.onclick=()=>moveTimelineSelection(-1);

let play=document.createElement('button');
play.type='button';
play.textContent='▶';
play.title='재생';
play.onclick=playTimelineAnimation;

let stop=document.createElement('button');
stop.type='button';
stop.textContent='■';
stop.title='정지';
stop.onclick=stopCompareAnimation;

let next=document.createElement('button');
next.type='button';
next.textContent='›';
next.title='다음 이미지';
next.onclick=()=>moveTimelineSelection(1);

let playback=document.createElement('div');
playback.className='compare-playback-controls timeline-playback-controls';
playback.appendChild(prev);
playback.appendChild(play);
playback.appendChild(stop);
playback.appendChild(next);

return playback;

}

function focusTimelineForKeyboardControl(){

let active=document.activeElement;
let tag=active?.tagName;

if(
tag==='INPUT' ||
tag==='SELECT' ||
tag==='TEXTAREA'
){
active.blur();
}

if(forecastTimeline){

if(!forecastTimeline.hasAttribute('tabindex')){
forecastTimeline.setAttribute('tabindex','-1');
}

try{
forecastTimeline.focus({preventScroll:true});
}
catch(e){
forecastTimeline.focus();
}

}

}

function bindCompareTimelinePointer(track){

let dragging=false;

function indexFromEvent(e){
let rect=track.getBoundingClientRect();
let x=Math.max(0,Math.min(e.clientX-rect.left,rect.width));
let count=currentForecastList.length || 1;
return Math.max(0,Math.min(count-1,Math.floor((x/rect.width)*count)));
}

function apply(e){
let index=indexFromEvent(e);
setCompareHoverIndex(index);
setCompareForecastIndex(index);
}

track.onpointerdown=e=>{
e.preventDefault();
focusTimelineForKeyboardControl();
dragging=true;
track.setPointerCapture?.(e.pointerId);
apply(e);
};

track.onpointermove=e=>{
if(!dragging){
return;
}
e.preventDefault();
apply(e);
};

track.onpointerup=e=>{
dragging=false;
track.releasePointerCapture?.(e.pointerId);
};

track.onpointercancel=()=>{
dragging=false;
};

}

function buildCompareImageUrlsForModel(modelId,forecastHour){

let baseProduct=getCompareProductForModel(modelId);
let product=getEffectiveCompareProductForModel(modelId);

if(!product){
return [];
}

let runUTC=getSelectedUTCDate();
let detailToken=getCurrentAuxToken();
let patterns=shouldUseWinterCompareVariant(modelId,baseProduct,runUTC)
?getWinterCompareVariantPatterns(product,modelId)
:null;

return makeChartImageUrls({
product,
modelId,
runUTC,
forecastHour,
detailToken,
patterns,
checkAvailability:true
});

}
function getCompareAvailableLeadSummary(modelId){

let hours=getForecastHoursForCompareModel(modelId).map(Number);

if(!hours.length){
return '지원 예측시간: 없음';
}

let min=Math.min(...hours);
let max=Math.max(...hours);
let count=hours.length;

return `지원 예측시간: +${String(min).padStart(3,'0')}h ~ +${String(max).padStart(3,'0')}h (${count}개)`;

}

function getCompareDisplayDateTimeForForecastHour(forecastHour){

let h=Number(forecastHour || 0);
let runUTC=getSelectedUTCDate();
let validUTC=new Date(runUTC.getTime()+h*60*60*1000);
let display=timeMode==='KST'
?new Date(validUTC.getTime()+9*60*60*1000)
:new Date(validUTC.getTime());

return `${formatDateInputFromUTCParts(display)} ${pad2(display.getUTCHours())}:00 ${timeMode}`;

}

function makeCompareExpectedButMissingMessage(modelId,product,forecastHour){

let modelLabel=getModelDisplayLabel(modelId);
let productLabel=getCurrentProductLabel(product);
let leadLabel=getForecastLeadLabelForHour(forecastHour);
let validTime=getCompareDisplayDateTimeForForecastHour(forecastHour);

return (
`${modelLabel}
`+
`${productLabel} / ${validTime} / ${leadLabel}
`+
`모델·산출물·자료시각 조합은 유효하지만 이미지 파일을 찾지 못했습니다.
`+
`가장 최근 cycle이라면 아직 생산 또는 업로드 전일 수 있습니다.`
);

}

function getCompareBlockedMessage(modelId,forecastHour){

let product=getCompareProductForModel(modelId);
let modelLabel=getModelDisplayLabel(modelId);

if(!product){
return `${modelLabel}
현재 선택한 산출자료를 지원하지 않습니다.`;
}

let runUTC=getSelectedUTCDate();

let modelStatus=getEffectiveModelStatus(
modelId,
runUTC,
product
);

if(!modelStatus.available){
return `${modelLabel}
${modelStatus.message}`;
}

let productStatus=getProductArchiveStatus(
product,
modelId,
parseDateOnly(runDate.value)
);

if(!productStatus.available){
return `${modelLabel}
${productStatus.message}`;
}

let cycleStatus=getCycleSupportStatus(
modelId,
product,
runUTC
);

if(!cycleStatus.supported){
return cycleStatus.message;
}

if(
productUsesForecastHourForModel(product,modelId) &&
!compareModelHasForecastHour(modelId,forecastHour)
){
return (
`${modelLabel}
`+
`${getForecastLeadLabelForHour(forecastHour)} 예측시간을 지원하지 않습니다.
`+
getCompareAvailableLeadSummary(modelId)
);
}

return '';

}


function setCompareLayout(mode,layout=null){

compareLayoutMode=mode==='manual'?'manual':'auto';
compareManualLayout=layout;
normalizeCompareLayout();
renderCompareForecastTimeline();
renderCompareImages();

}

function renderCompareLayoutControl(){

normalizeCompareLayout();

let wrap=document.createElement('div');
wrap.className='compare-layout-control';

let activeLayout=getActiveCompareLayout();
let btn=document.createElement('button');
btn.type='button';
btn.className='compare-layout-button';
btn.title='이미지 레이아웃 설정';
btn.innerHTML=(
(compareLayoutMode==='manual'
?renderLayoutMiniGrid(activeLayout.cols,activeLayout.rows,activeLayout.filledCount ?? compareModels.length)
:renderLayoutMiniGrid(getAutoCompareColumns(),Math.ceil(Math.max(1,compareModels.length||1)/getAutoCompareColumns()),compareModels.length))+
`<span>${compareLayoutMode==='manual'?activeLayout.label:'자동'}</span>`
);

let menu=document.createElement('div');
menu.className='compare-layout-menu hidden';

let auto=document.createElement('button');
auto.type='button';
auto.className='compare-layout-option'+(compareLayoutMode==='auto'?' active':'');
auto.innerHTML=renderLayoutMiniGrid(getAutoCompareColumns(),Math.ceil(Math.max(1,compareModels.length||1)/getAutoCompareColumns()),compareModels.length)+'<span>자동</span>';
auto.onclick=(event)=>{
event.stopPropagation();
setCompareLayout('auto',null);
};
menu.appendChild(auto);

getCompareLayoutOptions(compareModels.length).forEach(option=>{
let optionButton=document.createElement('button');
optionButton.type='button';
optionButton.className='compare-layout-option'+(
compareLayoutMode==='manual' &&
compareManualLayout &&
compareManualLayout.cols===option.cols &&
compareManualLayout.rows===option.rows
?' active':'');
optionButton.innerHTML=renderLayoutMiniGrid(option.cols,option.rows,option.filledCount ?? compareModels.length)+`<span>${option.label}</span>`;
optionButton.onclick=(event)=>{
event.stopPropagation();
setCompareLayout('manual',option);
};
menu.appendChild(optionButton);
});

btn.onclick=(event)=>{
event.stopPropagation();
menu.classList.toggle('hidden');
};

wrap.appendChild(btn);
wrap.appendChild(menu);

return wrap;

}

function renderCompareControls(){

let controls=document.createElement('div');
controls.className='compare-controls';

let fitLabel=document.createElement('label');
fitLabel.className='compare-fit-toggle';
let fitCheckbox=document.createElement('input');
fitCheckbox.type='checkbox';
fitCheckbox.checked=compareFitToScreen;
fitCheckbox.onchange=()=>{
compareFitToScreen=fitCheckbox.checked;
renderCompareImages();
};
let fitText=document.createElement('span');
fitText.textContent='화면에 맞춤';
fitLabel.appendChild(fitCheckbox);
fitLabel.appendChild(fitText);

let layoutControl=renderCompareLayoutControl();

let playback=renderTimelinePlaybackControls();

controls.appendChild(fitLabel);
controls.appendChild(layoutControl);
controls.appendChild(playback);

return controls;

}

function renderSingleTimelineControls(){

let controls=document.createElement('div');
controls.className='compare-controls single-controls';

if(typeof renderAnalysisResolutionToggle==='function'){
let resolutionToggle=renderAnalysisResolutionToggle();

if(resolutionToggle){
controls.appendChild(resolutionToggle);
}
}

controls.appendChild(renderTimelinePlaybackControls());

return controls;

}

function clearTimelineTopControls(){

if(!timelineTopControls){
return;
}

timelineTopControls.innerHTML='';
timelineTopControls.classList.add('hidden');

}

function renderTimelineTopControls(){

if(!timelineTopControls){
return;
}

timelineTopControls.innerHTML='';
timelineTopControls.classList.remove('hidden');

timelineTopControls.appendChild(
modelCompareMode
?renderCompareControls()
:renderSingleTimelineControls()
);

}

function updateCompareHoverVisuals(){

if(!forecastTimeline){
return;
}

let list=forecastTimeline.querySelector('.compare-timeline-list');
let isHovering=compareHoverIndex!==null && compareHoverIndex!==undefined;
let activeIndex=Number(slider.value || 0);

if(list){
list.classList.toggle('is-hovering',isHovering);
}

let segments=[...forecastTimeline.querySelectorAll('.compare-segment')];

segments.forEach(seg=>{
seg.classList.remove('hover-sync','hover-time-label','hover-lead-label');
});

if(!isHovering){
return;
}

let sameIndex=segments.filter(seg=>
Number(seg.dataset.index)===Number(compareHoverIndex)
);

sameIndex.forEach(seg=>{
seg.classList.add('hover-sync');
});

/*
현재 선택된 시각 라벨은 항상 노란색 active label로 유지한다.
따라서 hover가 active index 위에 있을 때는 lavender hover label을 별도로 만들지 않는다.
*/
if(Number(compareHoverIndex)===activeIndex){
return;
}

if(sameIndex.length){
sameIndex[0].classList.add('hover-time-label');
sameIndex[sameIndex.length-1].classList.add('hover-lead-label');
}

}

function setCompareHoverIndex(index){

if(index===null || index===undefined){
compareHoverIndex=null;
}
else{
compareHoverIndex=Number(index);
}

updateCompareHoverVisuals();

}

function getTimelineLabelLeftPercent(index,count){

if(count<=1){
return 50;
}

return ((Number(index)+0.5)/count)*100;

}

function createCompareTimelineLabel(type,index,count,forecastHour){

let label=document.createElement('div');
let isTime=type==='time';
label.className='compare-active-label '+(isTime?'compare-active-time':'compare-active-lead');

label.textContent=isTime
?getValidTimeLabelForForecastHour(forecastHour)
:getForecastLeadLabelForHour(forecastHour);

let leftPercent=getTimelineLabelLeftPercent(index,count)+'%';
label.style.left=leftPercent;
label.style.setProperty('--label-left',leftPercent);

return label;

}

function updateCompareTimelineActiveLabels(){

if(!forecastTimeline){
return;
}

let count=currentForecastList.length || 1;
let activeIndex=Number(slider.value || 0);
activeIndex=Math.max(0,Math.min(activeIndex,count-1));
let activeForecastHour=currentForecastList[activeIndex] ?? 0;

let rows=[...forecastTimeline.querySelectorAll('.compare-timeline-row')];

rows.forEach((row,rowIndex)=>{
let isFirstRow=rowIndex===0;
let isLastRow=rowIndex===rows.length-1;

row.querySelectorAll('.compare-segment').forEach(seg=>{
let isActive=Number(seg.dataset.index)===activeIndex;
seg.classList.toggle('active',isActive);
seg.classList.remove('active-time-label','active-lead-label');

if(isActive && isFirstRow){
seg.classList.add('active-time-label');
}

if(isActive && isLastRow){
seg.classList.add('active-lead-label');
}

});
});

forecastTimeline.querySelectorAll('.compare-active-label').forEach(label=>{
label.remove();
});

let tracks=[...forecastTimeline.querySelectorAll('.compare-track')];

if(tracks.length){
tracks[0].appendChild(
createCompareTimelineLabel('time',activeIndex,count,activeForecastHour)
);
tracks[tracks.length-1].appendChild(
createCompareTimelineLabel('lead',activeIndex,count,activeForecastHour)
);
}

updateCompareHoverVisuals();

}

function renderCompareForecastTimeline(){

if(!forecastTimeline){
return;
}

let shell=forecastTimeline.closest('.forecast-shell');
let bar=forecastTimeline.closest('.forecast-bar');

if(shell){
shell.classList.add('compare-active');
}

if(bar){
bar.classList.add('compare-active');
}

forecastTimeline.classList.add('compare-timeline');
forecastTimeline.classList.remove('single-timeline');
forecastTimeline.innerHTML='';

let count=currentForecastList.length || 1;
let activeIndex=Number(slider.value || 0);
activeIndex=Math.max(0,Math.min(activeIndex,count-1));

let list=document.createElement('div');
list.className='compare-timeline-list';

renderTimelineTopControls();

compareHoverIndex=null;

compareModels.forEach((modelId,rowIndex)=>{

let isFirstRow=rowIndex===0;
let isLastRow=rowIndex===compareModels.length-1;

let row=document.createElement('div');
row.className='compare-timeline-row';

let info=document.createElement('div');
info.className='compare-row-info';
info.innerHTML=`<div class="compare-row-model">${getModelDisplayLabel(modelId)}</div>`;

let track=document.createElement('div');
track.className='compare-track';
track.style.gridTemplateColumns=`repeat(${count}, minmax(4px, 1fr))`;

for(let i=0;i<count;i++){
let fh=currentForecastList[i] ?? 0;
let available=compareModelHasForecastHour(modelId,fh);
let seg=document.createElement('button');
seg.type='button';

let classes=[
'compare-segment',
available?'state-available':'state-missing'
];

if(i===activeIndex){
classes.push('active');
if(isFirstRow){classes.push('active-time-label');}
if(isLastRow){classes.push('active-lead-label');}
}

if(i===0){classes.push('edge-start');}
if(i===count-1){classes.push('edge-end');}

seg.className=classes.join(' ');
seg.dataset.index=String(i);
seg.dataset.time=getValidTimeLabelForForecastHour(fh);
seg.dataset.lead=getForecastLeadLabelForHour(fh);
seg.title=`${seg.dataset.time} / ${seg.dataset.lead}`;
seg.onclick=()=>{
focusTimelineForKeyboardControl();
setCompareForecastIndex(i);
};
seg.onmouseenter=()=>setCompareHoverIndex(i);
track.appendChild(seg);
}

let activeForecastHour=currentForecastList[activeIndex] ?? 0;

if(isFirstRow){
track.appendChild(
createCompareTimelineLabel('time',activeIndex,count,activeForecastHour)
);
}

if(isLastRow){
track.appendChild(
createCompareTimelineLabel('lead',activeIndex,count,activeForecastHour)
);
}

track.onmouseleave=()=>setCompareHoverIndex(null);
bindCompareTimelinePointer(track);

row.appendChild(info);
row.appendChild(track);
list.appendChild(row);

});

forecastTimeline.appendChild(list);
updateCompareHoverVisuals();

}

function renderComparePlaceholder(text){

let box=document.createElement('div');
box.className='compare-placeholder';
box.textContent=text;
return box;

}

let compareHeightSyncTimer=null;

function clearCompareImageItemHeights(){

document.querySelectorAll('.compare-image-item').forEach(item=>{
item.style.minHeight='';
});

}

function syncCompareImageItemHeights(){

if(!chartImages.classList.contains('compare-images')){
return;
}

let items=[...chartImages.querySelectorAll('.compare-image-item')];

items.forEach(item=>{
item.style.minHeight='';
});

if(compareLayoutMode!=='auto' || items.length<=1){
return;
}

let maxHeight=0;

items.forEach(item=>{
maxHeight=Math.max(maxHeight,item.offsetHeight);
});

if(maxHeight>0){
items.forEach(item=>{
item.style.minHeight=maxHeight+'px';
});
}

}

function scheduleCompareImageItemHeightSync(){

if(compareHeightSyncTimer){
cancelAnimationFrame(compareHeightSyncTimer);
}

compareHeightSyncTimer=requestAnimationFrame(()=>{
compareHeightSyncTimer=requestAnimationFrame(()=>{
compareHeightSyncTimer=null;
syncCompareImageItemHeights();
});
});

}

async function renderCompareImages(){

let requestId=++forecastDisplayRequest;
let index=Number(slider.value || 0);
let fh=currentForecastList[index] ?? 0;

setViewerLoading(false);
modelStatus.textContent='';
modelStatus.classList.add('hidden');

chartImages.classList.remove('hidden');
chartImages.classList.remove('single-images');
chartImages.classList.add('compare-images');
chartImages.classList.toggle('fit-screen',compareFitToScreen);
chartImages.classList.toggle('fixed-size',!compareFitToScreen);
chartImages.classList.toggle('layout-auto',compareLayoutMode==='auto');
chartImages.classList.toggle('layout-manual',compareLayoutMode==='manual');
chartImages.classList.toggle('compare-single',compareModels.length<=1);

let activeLayout=getActiveCompareLayout();
chartImages.style.setProperty('--compare-columns',String(activeLayout.cols));

if(!compareModels.length){
showViewerMessage('비교할 모델을 선택해 주세요.');
return;
}

let itemPromises=compareModels.map(async modelId=>{

let item=document.createElement('div');
item.className='compare-image-item';

let blockedMessage=getCompareBlockedMessage(modelId,fh);

if(blockedMessage){
item.appendChild(renderComparePlaceholder(blockedMessage));
return item;
}

let product=getCompareProductForModel(modelId);
let urls=buildCompareImageUrlsForModel(modelId,fh);

if(!urls.length){
item.appendChild(renderComparePlaceholder(`${getModelDisplayLabel(modelId)}\n이미지 URL을 생성하지 못했습니다.`));
return item;
}

let stack=document.createElement('div');
stack.className='compare-image-stack';

let prepared=await Promise.all(
urls.map(url=>createDecodedDisplayImage(url))
);

let loadedImages=prepared.filter(Boolean);

loadedImages.forEach(img=>{
stack.appendChild(img);
});

if(!loadedImages.length){
item.appendChild(renderComparePlaceholder(makeCompareExpectedButMissingMessage(modelId,product,fh)));
return item;
}

if(loadedImages.length<urls.length){
let warn=document.createElement('div');
warn.className='compare-inline-warning';
warn.textContent='일부 이미지 로드 실패';
stack.appendChild(warn);
}

item.appendChild(stack);
return item;

});

let items=await Promise.all(itemPromises);

if(requestId!==forecastDisplayRequest){
return;
}

clearCompareImageItemHeights();
chartImages.replaceChildren(...items);
revealPreparedImages(chartImages);
scheduleCompareImageItemHeightSync();

}

function updateCompareChart(){

normalizeCompareModels();

if(!compareModels.length){
resetForecastImageCache();
setForecastLoadStates(['missing']);
showViewerMessage('현재 산출물을 비교할 수 있는 모델이 없습니다.');
return;
}

renderModels();
renderCompareImages();

}

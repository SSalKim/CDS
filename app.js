const modelGrid=document.getElementById('modelGrid');
const productCategory=document.getElementById('productCategory');
const productSelect=document.getElementById('productSelect');
const runDate=document.getElementById('runDate');
const runHour=document.getElementById('runHour');
const slider=document.getElementById('forecastSlider');
const forecastLabel=document.getElementById('forecastLabel');
const chartImages=document.getElementById('chartImages');
const modelStatus=document.getElementById('modelStatus');
const auxSidebar=document.getElementById('auxSidebar');
const auxSidebarTitle=document.getElementById('auxSidebarTitle');
const auxSidebarList=document.getElementById('auxSidebarList');
const mobileAuxTrigger=document.getElementById('mobileAuxTrigger');
const mobileAuxTitle=document.getElementById('mobileAuxTitle');
const mobileAuxValue=document.getElementById('mobileAuxValue');
const mobileAuxBackdrop=document.getElementById('mobileAuxBackdrop');
const mobileAuxClose=document.getElementById('mobileAuxClose');
const mobileAuxSearch=document.getElementById('mobileAuxSearch');
const loadingOverlay=document.getElementById('loadingOverlay');
const kstBtn=document.getElementById('kstBtn');
const utcBtn=document.getElementById('utcBtn');
const nowBtn=document.getElementById('nowBtn');
const forecastTimeline=document.getElementById('forecastTimeline');
const viewerWrap=document.querySelector('.viewer-wrap');
const timelineTopControls=document.getElementById('timelineTopControls');
const appTitleReset=document.getElementById('appTitleReset');
const selectionToast=document.getElementById('selectionToast');

let currentModel='kim_gdps';
let currentProduct='gph500';
const forecastTimelineState=CDSTimelineState.createTimelineState();
let currentForecastList=forecastTimelineState.getForecastList();
let timeMode='KST';
let currentAuxValue=null;
let currentMainMenu='forecast';
let modelCompareMode=false;
let compareModels=[];
let compareForecastHourMap=new Map();
let comparePlayTimer=null;
let compareFitToScreen=true;
let singleFitToScreen=false;
let compareLayoutMode='auto';
let compareManualLayout=null;
let compareHoverIndex=null;
let imageSwapSeq=0;
let imagePreloadSeq=0;
let forecastLoadStates=forecastTimelineState.setLoadStates(['loading']);
let forecastImageCache=forecastTimelineState.getImageCache();
let forecastDisplayRequest=0;
let highResolutionEnabled=false;
let analysisResolutionState=null;
let analysisResolutionCache=new Map();

let auxAvailabilitySeq=0;
let auxAvailabilityCache=new Map();
let auxAvailabilityLoadingKey='';
let auxAvailabilityLoading=false;

const AUX_AVAILABILITY_CONCURRENCY=6;

const IMAGE_PRELOAD_CONCURRENCY=4;
const COMPARE_PLAY_INTERVAL_MS=500;
const COMPARE_MAX_MODELS=6;
const IMAGE_DECODE_TIMEOUT_MS=20000;
const chartImageLoader=CDSChartUtils.createImageLoader({
decodeTimeoutMs:IMAGE_DECODE_TIMEOUT_MS,
cacheLimit:500,
trimTo:250
});
const chartResolvedUrlCache=new Map();

function getOrderedChartUrlCandidates(url){
let candidates=typeof CDSChartUtils.getChartUrlCandidates==='function'
?CDSChartUtils.getChartUrlCandidates(url)
:[url];
let preferred=chartResolvedUrlCache.get(url);

if(preferred && candidates.includes(preferred)){
return [preferred,...candidates.filter(candidate=>candidate!==preferred)];
}

return candidates;
}

const createDecodedDisplayImage=async url=>{
for(let candidate of getOrderedChartUrlCandidates(url)){
let img=await chartImageLoader.createDecodedDisplayImage(candidate);

if(img){
chartResolvedUrlCache.set(url,candidate);
return img;
}
}

return null;
};
const revealPreparedImagesFromLoader=chartImageLoader.revealPreparedImages;

const CURRENT_PRODUCT_EXISTENCE_MODE="all";

const AUTO_CHECK_LATEST_ON_SELECTION_CHANGE=false;

const NOW_LOOKBACK_HOURS=24;
const SST_LOOKBACK_HOURS=48;
const NOW_MAX_CANDIDATES=32;
const NOW_IMAGE_TIMEOUT_MS=7000;
const PRELOAD_IMAGE_TIMEOUT_MS=15000;
const DISPLAY_IMAGE_RETRY_DELAY_MS=500;
const DISPLAY_IMAGE_MAX_RETRIES=2;
const AUTO_CHECK_DEBOUNCE_MS=250;
const QUIET_IMAGE_PROBE_HOSTS=new Set(['dmdw.kma.go.kr','data.kma.go.kr','afso.kma.go.kr']);

let latestSearchSeq=0;
let latestSearchInProgress=false;
let autoCheckTimer=null;
let selectionToastTimer=null;

function showSelectionToast(message){

if(!selectionToast){
return;
}

clearTimeout(selectionToastTimer);
selectionToast.textContent=message;
selectionToast.classList.remove('hidden');
selectionToast.classList.remove('show');
void selectionToast.offsetWidth;
selectionToast.classList.add('show');

selectionToastTimer=setTimeout(()=>{
selectionToast.classList.remove('show');
setTimeout(()=>selectionToast.classList.add('hidden'),180);
},2200);

}


function refreshViewAfterSelectionChange(options={}){

let baseDate=options.analysisBaseDate || getSelectedUTCDate();
let shouldSearchAnalysis=
currentMainMenu==='analysis' &&
!(
typeof isOlderThanAnalysisAutoLatestSearchWindow==='function' &&
isOlderThanAnalysisAutoLatestSearchWindow(baseDate)
);
let preserveForecastHour=options.preserveForecastHour ?? getSelectedTimelineHourForPreserve();
let refreshPromise=refreshView({
...options,
updateChartAfter:shouldSearchAnalysis ? false : options.updateChartAfter!==false
});

if(shouldSearchAnalysis){
Promise.resolve(refreshPromise).then(()=>{
jumpLatestAvailableForCurrentSelection({
silent:false,
preserveForecastHour,
baseDate
});
});
}

return refreshPromise;

}


function invalidateForecastDisplay(){

forecastDisplayRequest++;

}

function getProductExistenceMode(product=getCurrentProduct(),modelId=currentModel){

return (
product?.existenceModeByModel?.[modelId] ||
product?.existenceMode ||
CURRENT_PRODUCT_EXISTENCE_MODE
);

}

function invalidateImagePreload(){

imagePreloadSeq++;

}

function invalidateLatestSearch(){

latestSearchSeq++;
latestSearchInProgress=false;
clearTimeout(autoCheckTimer);

}

function invalidateAuxAvailability(){

auxAvailabilitySeq++;
auxAvailabilityLoading=false;
auxAvailabilityLoadingKey='';

}

function invalidateSelectionAsyncWork({
latest=true,
preload=true,
display=true,
aux=true
}={}){

if(latest){
invalidateLatestSearch();
}

if(preload){
invalidateImagePreload();
}

if(display){
invalidateForecastDisplay();
}

if(aux){
invalidateAuxAvailability();
}

}

function setCurrentForecastList(list){

currentForecastList=forecastTimelineState.setForecastList(list);
return currentForecastList;

}

function setForecastLoadStates(states){

forecastLoadStates=forecastTimelineState.setLoadStates(states);
return forecastLoadStates;

}

function setAllForecastLoadStates(length,state='loading'){

forecastLoadStates=forecastTimelineState.setAllLoadStates(length,state);
return forecastLoadStates;

}

function setForecastLoadState(index,state){

forecastLoadStates=forecastTimelineState.setLoadState(index,state);
return forecastLoadStates;

}

function resetForecastImageCache(){

forecastImageCache=forecastTimelineState.resetImageCache();
return forecastImageCache;

}

function resetAnalysisResolutionState(){

analysisResolutionState=null;

if(typeof renderTimelineTopControls==='function'){
renderTimelineTopControls();
}

}

function setForecastImageCacheEntry(index,value){

forecastTimelineState.setImageCacheEntry(index,value);

}

function getForecastImageCacheEntry(index){

return forecastTimelineState.getImageCacheEntry(index);

}

function setForecastAvailabilityResult(index,{
ok,
urls=[],
baseUrls=[],
quiet=false,
future=false
}={}){

setForecastLoadState(index,ok ? 'available' : 'missing');
setForecastImageCacheEntry(index,{urls,baseUrls,ok,quiet,future});
updateForecastSegmentState(index);

}

/* 특정 드롭다운 영역/지점 선택 보조 패널 */







const AUTO_NOW_ON_STARTUP=true;


function init(){

if(isCatalogValidationEnabled()){
validateCatalog();
}
setToday();
populateProductCategories();
bindMainMenu();

refreshView({
updateCategories:false,
updateProducts:true,
updateHours:true,
resetSlider:true,
updateChartAfter:false
});

bindEvents();

if(AUTO_NOW_ON_STARTUP){

setTimeout(()=>{

jumpLatestAvailableForCurrentSelection({
silent:false
});

},0);

}
else{

updateChart();

}

}


async function refreshView({
updateCategories=false,
updateProducts=true,
updateHours=true,
resetSlider=true,
preserveForecastHour=null,
imageRefreshToken='',
updateChartAfter=true
}={}){

if(updateCategories){
populateProductCategories();
}

syncProductCategoryVisibility();

if(updateHours){
populateHours();
}

if(updateProducts){
renderProductList();
}

syncProductSelectVisibility();
renderModels();
renderAuxSidebar();

rebuildForecastAxis({
reset:resetSlider,
preserveForecastHour
});

/*
관측단열선도처럼 동적 지점 활성화가 필요한 경우
먼저 지점 존재 여부를 검사한 뒤 차트 표출
*/
if(isDynamicAuxAvailabilityEnabled()){

let key=getAuxAvailabilityCacheKey();

if(
auxAvailabilityLoading &&
auxAvailabilityLoadingKey &&
auxAvailabilityLoadingKey!==key
){
invalidateAuxAvailability();
}

if(
auxAvailabilityLoading &&
auxAvailabilityLoadingKey===key
){
return;
}

if(!auxAvailabilityCache.has(key)){
await probeAuxAvailabilityForCurrentSelection({
preserveForecastHour,
imageRefreshToken
});
return;
}

}

if(updateChartAfter){
updateChart({imageRefreshToken});
}

}



function revealPreparedImages(root){

return revealPreparedImagesFromLoader(root);

}

function getAnalyticsUrlSource(urls){
let list=Array.isArray(urls) ? urls : [urls];
let first=list.find(Boolean) || '';
return window.CDSAnalytics?.sourceFromUrl
?window.CDSAnalytics.sourceFromUrl(first)
:'unknown';
}

function getCurrentForecastAnalyticsParams({urls=[],loadedImages=[],viewContext='single'}={}){
let product=typeof getCurrentProduct==='function' ? getCurrentProduct() : null;
let category=typeof getCurrentCategory==='function' ? getCurrentCategory() : product?.category || '';
let modelId=currentModel || '';
let productId=product?.id || currentProduct || '';
let sliderIndex=Number(slider?.value || 0);
let forecastHour=currentForecastList?.[sliderIndex] ?? '';
let detailToken='';

try{
detailToken=typeof getCurrentAuxToken==='function' ? (getCurrentAuxToken() || '') : '';
}
catch(error){
detailToken='';
}

let productKey=[
currentMainMenu || '',
category || '',
productId || '',
modelId || '',
detailToken || ''
].filter(Boolean).join('|');

return {
analytics_key:[productKey,forecastHour,viewContext].filter(value=>value!=='' && value!==undefined).join('|'),
product_key:productKey,
menu:currentMainMenu || '',
category,
product_id:productId,
product_name:product?.label || productId,
model_id:modelId,
model_name:typeof getCurrentModelName==='function' ? getCurrentModelName(modelId) : modelId,
forecast_hour:Number(forecastHour),
detail_token:detailToken,
view_context:viewContext,
image_source:getAnalyticsUrlSource(urls),
url_count:Array.isArray(urls) ? urls.length : 0,
loaded_count:Array.isArray(loadedImages) ? loadedImages.length : 0
};
}

function trackCurrentForecastViewAnalytics(options){
if(!window.CDSAnalytics?.trackProductView){
return;
}

window.CDSAnalytics.trackProductView(
getCurrentForecastAnalyticsParams(options)
);
}


function getSelectedForecastHour(){

if(!productUsesForecastHour()){
return null;
}

let index=Number(slider.value || 0);

return forecastTimelineState.getHour(index);

}

function getSelectedTimelineHourForPreserve(){

if(!currentForecastList || !currentForecastList.length){
return null;
}

let index=forecastTimelineState.clampIndex(Number(slider.value || 0));
let hour=currentForecastList[index];
let numericHour=Number(hour);

return Number.isFinite(numericHour) ? numericHour : null;

}


function getForecastIndexByHour(hour){

return forecastTimelineState.indexOfHour(hour);

}


function makeChartImageUrls({
product,
modelId,
runUTC,
patterns,
forecastHour=0,
detailToken=null,
requireDetailToken=true,
checkAvailability=false
}={}){

let resolvedPatterns=patterns ?? CDSChartUtils.getProductPatternsForDetail(
product,
modelId,
detailToken,
runUTC
);

return CDSChartUtils.makeChartImageUrls({
product,
modelId,
runUTC,
patterns:resolvedPatterns,
forecastHour,
detailToken,
requireDetailToken,
checkAvailability,
models:MODELS,
formatUTCStampFromDate,
parseDateOnly,
formatDateInputFromUTCParts,
getEffectiveModelStatus,
getProductArchiveStatus
});

}

function normalizeRunDateYearInput(){

if(!runDate || !runDate.value){
return;
}

if(typeof normalizeDateInputYearValue==='function'){
normalizeDateInputYearValue(runDate);
return;
}

let match=runDate.value.match(/^(\d{5,})-(\d{2})-(\d{2})$/);

if(match){
runDate.value=`${match[1].slice(0,4)}-${match[2]}-${match[3]}`;
}

}


function rebuildForecastAxis({
reset=true,
preserveForecastHour=null
}={}){

if(modelCompareMode){
rebuildCompareForecastAxis({reset,preserveForecastHour});
return;
}

let p=getCurrentProduct();
let oldValue=Number(slider.value || 0);

/*
모델 자체가 운영 종료/자료 보유기간 밖이면
예측시간 슬라이더도 비활성화한다.
*/
let modelStatusResult=getEffectiveModelStatus(
currentModel,
getSelectedUTCDate(),
p
);

if(!modelStatusResult.available){

setCurrentForecastList([0]);
slider.min=0;
slider.max=0;
slider.step=1;
slider.value=0;
slider.disabled=true;
forecastLabel.textContent='자료 없음';
setForecastLoadStates(['missing']);
renderForecastTimeline();
return;

}

let productStatus=getProductArchiveStatus(
p,
currentModel,
parseDateOnly(runDate.value)
);

if(!productStatus.available){

setCurrentForecastList([0]);
slider.min=0;
slider.max=0;
slider.step=1;
slider.value=0;
slider.disabled=true;
forecastLabel.textContent='자료 없음';
setForecastLoadStates(['missing']);
renderForecastTimeline();
return;

}

if(!productUsesForecastHour()){

if(isRunTimeSliderMode()){
setCurrentForecastList(buildRunTimeSliderOffsets());
slider.min=0;
slider.max=currentForecastList.length-1;
slider.step=1;
slider.disabled=false;
setAllForecastLoadStates(currentForecastList.length,'loading');

if(reset){
let zeroIndex=forecastTimelineState.indexOfHour(0);
slider.value=String(zeroIndex>=0?zeroIndex:0);
}
else{
slider.value=forecastTimelineState.clampIndex(oldValue);
}

updateForecastLabel();
renderForecastTimeline();
return;
}

setCurrentForecastList([0]);
slider.min=0;
slider.max=0;
slider.step=1;
slider.value=0;
slider.disabled=true;
forecastLabel.textContent='단일 이미지';
setForecastLoadStates(['loading']);
renderForecastTimeline();
return;

}

setCurrentForecastList(getForecastHoursForCurrentSelection());

if(!currentForecastList.length){
setCurrentForecastList([0]);
}

slider.min=0;
slider.max=currentForecastList.length-1;
slider.step=1;
slider.disabled=false;

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
renderForecastTimeline();

}


function updateForecastLabel(){

if(modelCompareMode){
let h=currentForecastList[+slider.value] ?? 0;
forecastLabel.textContent=getForecastLeadLabelForHour(h);
return;
}

if(!productUsesForecastHour()){
let h=currentForecastList[+slider.value] ?? 0;
forecastLabel.textContent=isRunTimeSliderMode()
?getRunTimeOffsetLabel(h)
:'단일 이미지';
updateForecastTimelineMarker();
return;
}

let h=currentForecastList[+slider.value] ?? 0;

forecastLabel.textContent='+'+
String(h).padStart(3,'0')+'h';

updateForecastTimelineMarker();

}


function getCurrentCategory(){

if(
isForecastCatalog() &&
getActiveModelSpecificProductCategory()[currentModel]
){
return getActiveModelSpecificProductCategory()[currentModel];
}

let selectableCategories=getSelectableCategories();

return (
productCategory.value ||
selectableCategories[0]?.id ||
'empty'
);

}

function applyCategoryRedirectForCurrentModel(){

if(!isForecastCatalog()){
return false;
}

let redirects=getActiveCategoryRedirectByModel()[currentModel];

if(!redirects){
return false;
}

let currentCategory=productCategory.value;
let nextCategory=redirects[currentCategory];

if(!nextCategory){
return false;
}

/*
대상 category가 실제 1차 드롭다운에 존재할 때만 이동
*/
let exists=getActiveCategories().some(
c=>c.id===nextCategory
);

if(!exists){
return false;
}

productCategory.value=nextCategory;

return true;

}


function setViewerLoading(isLoading,message='이미지 로딩 중'){

if(loadingOverlay){
loadingOverlay.classList.toggle('hidden',!isLoading);
let text=loadingOverlay.querySelector('.loading-text');
if(text){
text.textContent=message;
}
}

if(viewerWrap){

if(isLoading){
viewerWrap.scrollTop=0;
viewerWrap.scrollLeft=0;
}

viewerWrap.classList.toggle('loading-active',!!isLoading);
}

}


function showViewerMessage(message){

setViewerLoading(false);
chartImages.innerHTML='';
chartImages.classList.remove('single-images');
chartImages.classList.add('hidden');
modelStatus.textContent=message;
modelStatus.classList.remove('hidden');

}


function showViewerNotice(message){

modelStatus.textContent=message;
modelStatus.classList.remove('hidden');

}

function makeAnalysisLowResolutionUrls(urls){

return urls.map(url=>
typeof url==='string'
?url.replaceAll('pb4','pa4')
:url
);

}

function makeEditHighResolutionUrls(urls){

return urls.map(url=>
typeof url==='string'
?url.replace(/_(\d{10})(?=\.(?:png|gif)(?:[?#]|$))/i,'_pb4_$1')
:url
);

}

function getChartResolutionVariants(urls){

if(!Array.isArray(urls) || !urls.length){
return null;
}

if(
currentMainMenu==='analysis' &&
urls.some(url=>typeof url==='string' && url.includes('pb4'))
){
return {
highUrls:urls,
lowUrls:makeAnalysisLowResolutionUrls(urls)
};
}

if(currentMainMenu==='edit'){
let highUrls=makeEditHighResolutionUrls(urls);

if(highUrls.some((url,index)=>url!==urls[index])){
return {
highUrls,
lowUrls:urls
};
}
}

return null;

}

function isAnalysisResolutionCandidate(urls){

return !!getChartResolutionVariants(urls);

}

function getAnalysisResolutionCacheKey(urls){

return Array.isArray(urls)
?[currentMainMenu,currentProduct,...urls].join('\n')
:'';

}

async function getAnalysisResolutionInfo(urls){

if(!isAnalysisResolutionCandidate(urls)){
return null;
}

let variants=getChartResolutionVariants(urls);
let key=getAnalysisResolutionCacheKey(urls);

if(analysisResolutionCache.has(key)){
return analysisResolutionCache.get(key);
}

let resolutionPromise=(async()=>{

let [lowExists,highExists]=await Promise.all([
urlsExist(variants.lowUrls),
urlsExist(variants.highUrls)
]);

return {
key,
highUrls:variants.highUrls,
lowUrls:variants.lowUrls,
highExists,
lowExists,
canToggle:lowExists && highExists
};

})();

analysisResolutionCache.set(key,resolutionPromise);

return resolutionPromise;

}

function selectAnalysisResolutionUrls(info,baseUrls){

if(!info){
return baseUrls;
}

if(info.highExists && (highResolutionEnabled || !info.lowExists)){
return info.highUrls;
}

return info.lowUrls;

}

async function resolveAnalysisResolutionUrls(urls,{updateControls=false}={}){

let info=await getAnalysisResolutionInfo(urls);

if(updateControls){
analysisResolutionState=info;

if(typeof renderTimelineTopControls==='function'){
renderTimelineTopControls();
}
}

return selectAnalysisResolutionUrls(info,urls);

}

function renderAnalysisResolutionToggle(){

if(!analysisResolutionState?.canToggle){
return null;
}

let label=document.createElement('label');
label.className='compare-fit-toggle analysis-resolution-toggle';

let checkbox=document.createElement('input');
checkbox.type='checkbox';
checkbox.checked=highResolutionEnabled;
checkbox.onchange=()=>{
highResolutionEnabled=checkbox.checked;
resetForecastImageCache();
renderTimelineTopControls();
displayCurrentForecastImage();
};

let text=document.createElement('span');
text.textContent='고해상도';

label.appendChild(checkbox);
label.appendChild(text);
return label;

}


function isNmscSatelliteUrl(url){

return typeof url==='string' &&
url.includes('nmsc.kma.go.kr/IMG/GK2A');

}

function isNmscEastAsiaUrl(url){

return isNmscSatelliteUrl(url) &&
(url.includes('/EA/') || url.includes('_ea020lc_'));

}

function isNmscKoreaUrl(url){

return isNmscSatelliteUrl(url) &&
(url.includes('/KO/') || url.includes('_ko020lc_'));

}

function isNmscMtDryAirUrl(url){

return isNmscSatelliteUrl(url) &&
(
url.includes('/L2/mT_DAI/') ||
url.includes('gk2a_ami_le2_dai_') ||
url.includes('gk2a_ami_le2_dab-')
);

}

function setSingleImageDisplayMode(){

chartImages.classList.remove('compare-images','fit-screen','fixed-size','layout-auto','layout-manual','compare-single','single-images');
chartImages.classList.add('single-images');
syncSingleImageFitMode();
chartImages.classList.remove('hidden');

}

function syncSingleImageFitMode(){

if(!chartImages?.classList.contains('single-images')){
return;
}

chartImages.classList.toggle('fit-screen',singleFitToScreen);
chartImages.classList.toggle('fixed-size',!singleFitToScreen);

}

function createSingleImageDisplayShell({
nmsc=false,
imageCount=1
}={}){

setSingleImageDisplayMode();

let item=document.createElement('div');
item.className='single-image-item';

let stack=document.createElement('div');
stack.className='single-image-stack';
stack.style.setProperty('--single-image-count',String(Math.max(1,Number(imageCount) || 1)));

if(nmsc){
stack.classList.add('nmsc-image-stack');
}

item.appendChild(stack);
chartImages.replaceChildren(item);

return {item,stack};

}

function syncNmscImagePairHeight(stack){

if(!stack){
return;
}

let koImage=stack.querySelector('img.nmsc-ko-image');

if(!koImage){
return;
}

let height=koImage.naturalHeight || koImage.getBoundingClientRect().height;

if(!height){
return;
}

stack.style.setProperty('--nmsc-pair-height',`${height}px`);
stack.classList.add('nmsc-has-ko-height');

}

function createNmscImageSlot(url){

let slot=document.createElement('div');
slot.className='nmsc-image-slot';

if(isNmscEastAsiaUrl(url)){
slot.classList.add('nmsc-ea-slot');
}

if(isNmscKoreaUrl(url)){
slot.classList.add('nmsc-ko-slot');
}

return slot;

}

function applyNmscMtStackMode(stack,urls){

if(!stack || !Array.isArray(urls) || !urls.some(isNmscMtDryAirUrl)){
return;
}

stack.classList.add('nmsc-mt-stack');

let maxHeight=viewerWrap?.clientHeight
?Math.max(240,viewerWrap.clientHeight-8)
:null;

if(maxHeight){
stack.style.setProperty('--nmsc-mt-max-height',`${maxHeight}px`);
}

}

function renderNmscPreparedImages(urls,preparedImages){

let {stack}=createSingleImageDisplayShell({nmsc:true,imageCount:urls.length});

applyNmscMtStackMode(stack,urls);

if(
urls.some(isNmscEastAsiaUrl) &&
urls.some(isNmscKoreaUrl)
){
stack.classList.add('nmsc-wait-for-ko');
}

urls.forEach((url,index)=>{
let slot=createNmscImageSlot(url);
let img=preparedImages[index];

if(img){
slot.replaceChildren(img);
slot.classList.add('loaded');
}

stack.appendChild(slot);
});

syncNmscImagePairHeight(stack);

if(!stack.classList.contains('nmsc-has-ko-height')){
stack.classList.remove('nmsc-wait-for-ko');
}

revealPreparedImages(chartImages);
return stack;

}

async function showProgressiveCharts(urls,{requestId,attempt=0,hadPreviousImage=false}={}){

let {stack}=createSingleImageDisplayShell({nmsc:true,imageCount:urls.length});
let loadedImages=[];

applyNmscMtStackMode(stack,urls);

if(
urls.some(isNmscEastAsiaUrl) &&
urls.some(isNmscKoreaUrl)
){
stack.classList.add('nmsc-wait-for-ko');
}

let slots=urls.map(url=>{
let slot=createNmscImageSlot(url);
stack.appendChild(slot);
return slot;
});

let jobs=urls.map(async (url,index)=>{
let img=await createDecodedDisplayImage(url);

if(requestId!==forecastDisplayRequest){
return null;
}

if(!img){
return null;
}

loadedImages.push(img);
slots[index].replaceChildren(img);
slots[index].classList.add('loaded');
syncNmscImagePairHeight(stack);
revealPreparedImages(chartImages);
return img;
});

await Promise.all(jobs);

if(requestId!==forecastDisplayRequest){
return;
}

if(loadedImages.length){
syncNmscImagePairHeight(stack);

if(!stack.classList.contains('nmsc-has-ko-height')){
stack.classList.remove('nmsc-wait-for-ko');
}

modelStatus.textContent='';
modelStatus.classList.add('hidden');
setViewerLoading(false);

if(loadedImages.length<urls.length){
let warn=document.createElement('div');
warn.className='compare-inline-warning';
warn.textContent='일부 이미지 로드 실패';
stack.appendChild(warn);
}

trackCurrentForecastViewAnalytics({
urls,
loadedImages,
viewContext:'nmsc_progressive'
});

return;
}

if(attempt<DISPLAY_IMAGE_MAX_RETRIES){

setTimeout(()=>{

if(requestId!==forecastDisplayRequest){
return;
}

showCharts(urls,{attempt:attempt+1});

},DISPLAY_IMAGE_RETRY_DELAY_MS);

return;

}

if(hadPreviousImage){
console.warn('이미지 로드 실패. 이전 화면을 지우고 메시지를 표시합니다:',urls);
}

showViewerMessage(
makeExpectedButMissingMessage()
);

}


async function showCharts(urls,{
attempt=0,
progressiveNmsc=true
}={}){

let requestId=++forecastDisplayRequest;
let hadPreviousImage=!!chartImages.querySelector('img');

modelStatus.textContent='';
modelStatus.classList.add('hidden');

if(!urls || urls.length===0){
showViewerMessage('표출할 이미지 URL이 없습니다.');
return;
}

if(progressiveNmsc && urls.some(isNmscSatelliteUrl)){
await showProgressiveCharts(urls,{requestId,attempt,hadPreviousImage});
return;
}

let displayResult=await CDSImagePipeline.prepareDisplayImages(urls,{
createDisplayImage:createDecodedDisplayImage,
existenceMode:getProductExistenceMode()
});

if(requestId!==forecastDisplayRequest){
return;
}

let loadedImages=displayResult.loadedImages;
let enough=displayResult.enough;
let preparedImages=displayResult.prepared || [];

if(enough){

if(urls.some(isNmscSatelliteUrl)){
let stack=renderNmscPreparedImages(urls,preparedImages);

if(loadedImages.length<urls.length){
let warn=document.createElement('div');
warn.className='compare-inline-warning';
warn.textContent='일부 이미지 로드 실패';
stack.appendChild(warn);
}

modelStatus.textContent='';
modelStatus.classList.add('hidden');
setViewerLoading(false);
trackCurrentForecastViewAnalytics({
urls,
loadedImages,
viewContext:'nmsc_stack'
});
return;
}

let {stack}=createSingleImageDisplayShell({imageCount:loadedImages.length});
loadedImages.forEach(img=>{
stack.appendChild(img);
});

if(loadedImages.length<urls.length){
let warn=document.createElement('div');
warn.className='compare-inline-warning';
warn.textContent='일부 이미지 로드 실패';
stack.appendChild(warn);
}

revealPreparedImages(chartImages);

modelStatus.textContent='';
modelStatus.classList.add('hidden');
setViewerLoading(false);
trackCurrentForecastViewAnalytics({
urls,
loadedImages,
viewContext:'single'
});
return;

}

if(attempt<DISPLAY_IMAGE_MAX_RETRIES){

setTimeout(()=>{

if(requestId!==forecastDisplayRequest){
return;
}

showCharts(urls,{attempt:attempt+1});

},DISPLAY_IMAGE_RETRY_DELAY_MS);

return;

}

if(hadPreviousImage){
console.warn('이미지 로드 실패. 이전 화면을 지우고 메시지를 표시합니다:',urls);
}

showViewerMessage(
makeExpectedButMissingMessage()
);

}


function renderForecastTimeline(){

if(!forecastTimeline){
return;
}

if(modelCompareMode){
renderCompareForecastTimeline();
return;
}

let shell=forecastTimeline.closest('.forecast-shell');
let bar=forecastTimeline.closest('.forecast-bar');

if(shell){shell.classList.add('compare-active');}
if(bar){bar.classList.add('compare-active');}

forecastTimeline.classList.add('compare-timeline','single-timeline');
forecastTimeline.classList.remove('is-single');
chartImages.classList.remove('compare-images','fit-screen','fixed-size','layout-auto','layout-manual','compare-single','single-images');
clearCompareImageItemHeights();

let count=currentForecastList.length || 1;
let activeIndex=Number(slider.value || 0);
activeIndex=Math.max(0,Math.min(activeIndex,count-1));

forecastTimeline.innerHTML='';
forecastTimeline.style.setProperty('--forecast-count',String(count));

let list=document.createElement('div');
list.className='compare-timeline-list single-timeline-list';

renderTimelineTopControls();

let row=document.createElement('div');
row.className='compare-timeline-row single-timeline-row';

let info=document.createElement('div');
info.className='compare-row-info';
info.innerHTML=`<div class="compare-row-model">${getModelDisplayLabel(currentModel)}</div>`;

let track=document.createElement('div');
track.className='compare-track single-forecast-track';
track.style.gridTemplateColumns=`repeat(${count}, minmax(4px, 1fr))`;

compareHoverIndex=null;

for(let i=0;i<count;i++){
let state=forecastTimelineState.getLoadState(i);
let seg=document.createElement('button');
seg.type='button';
let classes=[
'compare-segment',
'forecast-segment',
`state-${state}`
];
if(i===activeIndex){
classes.push('active','active-time-label','active-lead-label');
}
if(i===0){classes.push('edge-start');}
if(i===count-1){classes.push('edge-end');}
seg.className=classes.join(' ');
seg.dataset.index=String(i);
seg.dataset.time=getValidTimeLabel(i);
seg.dataset.lead=getForecastLeadLabel(i);
seg.title=`${seg.dataset.time} / ${seg.dataset.lead}`;
seg.onclick=()=>{
focusTimelineForKeyboardControl();
setForecastIndex(i);
};
seg.onmouseenter=()=>setCompareHoverIndex(i);
track.appendChild(seg);
}

let activeForecastHour=currentForecastList[activeIndex] ?? 0;
track.appendChild(
createCompareTimelineLabel('time',activeIndex,count,activeForecastHour)
);
track.appendChild(
createCompareTimelineLabel('lead',activeIndex,count,activeForecastHour)
);

track.onmouseleave=()=>setCompareHoverIndex(null);
bindForecastTimelinePointer(track);

row.appendChild(info);
row.appendChild(track);
list.appendChild(row);
forecastTimeline.appendChild(list);

}


function updateForecastSegmentState(index){

if(!forecastTimeline){
return;
}

let seg=forecastTimeline.querySelector(`.forecast-segment[data-index="${index}"]`) || forecastTimeline.querySelector(`.compare-segment[data-index="${index}"]`);

if(!seg){
return;
}

seg.classList.remove('state-loading','state-available','state-missing');
seg.classList.add('state-'+forecastTimelineState.getLoadState(index));

}


function updateForecastTimelineMarker(){

if(!forecastTimeline){
return;
}

updateCompareTimelineActiveLabels();

}


function refreshForecastTimelineLabels(){

if(!forecastTimeline){
return;
}

forecastTimeline
.querySelectorAll('.forecast-segment,.compare-segment')
.forEach((seg,i)=>{
seg.dataset.time=getValidTimeLabel(i);
seg.dataset.lead=getForecastLeadLabel(i);
seg.title=`${seg.dataset.time} / ${seg.dataset.lead}`;
});

updateCompareTimelineActiveLabels();

}


function bindForecastTimelinePointer(track){

let dragging=false;

function indexFromEvent(e){
let rect=track.getBoundingClientRect();
let x=Math.max(0,Math.min(e.clientX-rect.left,rect.width));
let count=currentForecastList.length || 1;
return Math.max(0,Math.min(count-1,Math.floor((x/rect.width)*count)));
}

function apply(e){
setForecastIndex(indexFromEvent(e));
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


function setForecastIndex(index){

if(modelCompareMode){
setCompareForecastIndex(index);
return;
}

if(slider.disabled){
return;
}

let next=forecastTimelineState.clampIndex(index);

slider.value=String(next);
updateForecastLabel();
setViewerLoading(forecastTimelineState.getLoadState(next)!=='available','이미지 로딩 중');
displayCurrentForecastImage();

}

function moveForecastSelection(delta){

if(modelCompareMode){
moveCompareForecastSelection(delta);
return;
}

let max=(currentForecastList.length || 1)-1;

if(max<=0 || slider.disabled){
return;
}

let current=Number(slider.value || 0);

setForecastIndex(
current+delta
);

}


async function displayCurrentForecastImage(){

if(modelCompareMode){
renderCompareImages();
return;
}

let index=Number(slider.value || 0);
let cached=getForecastImageCacheEntry(index);
let requestId=forecastDisplayRequest;

if(!selectionIsDisplayable()){
return;
}

if(isRunTimeFrameFuture(index)){
setForecastAvailabilityResult(index,{
ok:false,
urls:[],
baseUrls:[],
quiet:true,
future:true
});
showViewerMessage(makeFutureRunTimeFrameMessage(index));
return;
}

/*
성공 캐시만 신뢰한다.
실패 캐시는 네트워크 지연/timeout일 수 있으므로 현재 선택 이미지는 다시 직접 시도한다.
*/
if(cached?.ok===true && cached?.urls?.length){
let urls=await resolveAnalysisResolutionUrls(
cached.baseUrls || cached.urls,
{updateControls:true}
);

if(requestId!==forecastDisplayRequest){
return;
}

setForecastAvailabilityResult(index,{
ok:true,
urls,
baseUrls:cached.baseUrls || cached.urls
});
showCharts(urls,{progressiveNmsc:false});
return;
}

let wasMissingCache=!!(cached && cached.ok===false);

/*
캐시가 없으면 현재 선택 위치 이미지는 직접 표출 시도한다.
*/
let urls=buildImageUrlsForForecastIndex(index);

if(urls.length){
let displayUrls=await resolveAnalysisResolutionUrls(urls,{updateControls:true});

if(requestId!==forecastDisplayRequest){
return;
}

let imageRefreshToken=wasMissingCache ? String(Date.now()) : '';
let loadUrls=addImageRefreshTokenToUrls(displayUrls,imageRefreshToken);
let exists=await urlsExist(displayUrls,{imageRefreshToken});

if(requestId!==forecastDisplayRequest){
return;
}

if(exists){
setForecastAvailabilityResult(index,{
ok:true,
urls:loadUrls,
baseUrls:urls
});
showCharts(loadUrls);
return;
}

setForecastAvailabilityResult(index,{
ok:false,
urls:loadUrls,
baseUrls:urls
});
showViewerMessage(makeExpectedButMissingMessage());
return;
}

showViewerMessage('표출할 이미지 URL이 없습니다.');

}


function shouldUseQuietImageProbe(url){

try{
let parsed=new URL(url,window.location.href);
return (
QUIET_IMAGE_PROBE_HOSTS.has(parsed.hostname) &&
(
parsed.pathname.startsWith('/map/data/CHT/') ||
parsed.pathname.startsWith('/CHT/') ||
parsed.pathname.startsWith('/data/CHT/')
)
);
}
catch(e){
return false;
}

}


async function quietImageExists(url,timeoutMs=PRELOAD_IMAGE_TIMEOUT_MS){

// Do not use fetch(HEAD) for KMA CHT images.
// data.kma.go.kr and afso.kma.go.kr frequently reject HEAD with 405 and/or
// CORS errors even when normal <img> loading works.  Those rejected probes are
// harmless functionally, but they flood DevTools with red errors.
// Returning null lets the regular image loader try the candidate URL directly.
return null;

}


async function loadImage(url,timeoutMs=PRELOAD_IMAGE_TIMEOUT_MS){

for(let candidate of getOrderedChartUrlCandidates(url)){

if(shouldUseQuietImageProbe(candidate)){
let exists=await quietImageExists(candidate,timeoutMs);

if(exists===false){
continue;
}
}

let result=await chartImageLoader.getDecodedImage(candidate,timeoutMs);

if(result?.ok){
chartResolvedUrlCache.set(url,candidate);
return true;
}

}

return false;

}


async function preloadForecastIndex(index,seq,{
imageRefreshToken=''
}={}){

if(isRunTimeFrameFuture(index)){
return {index,ok:false,urls:[],baseUrls:[],quiet:true,future:true};
}

let baseUrls=buildImageUrlsForForecastIndex(index);

if(!baseUrls.length){
return {index,ok:false,urls:[],baseUrls:[]};
}

let urls=await resolveAnalysisResolutionUrls(
baseUrls,
{updateControls:index===Number(slider.value || 0)}
);

if(seq!==imagePreloadSeq){
return {index,ok:false,urls,baseUrls,cancelled:true};
}

let loadUrls=addImageRefreshTokenToUrls(urls,imageRefreshToken);
let ok=await urlsExist(loadUrls);

if(seq!==imagePreloadSeq){
return {index,ok:false,urls,baseUrls,cancelled:true};
}

if(ok && urls.some(isNmscSatelliteUrl)){
await CDSImagePipeline.prepareDisplayImages(loadUrls,{
createDisplayImage:createDecodedDisplayImage,
existenceMode:getProductExistenceMode()
});

if(seq!==imagePreloadSeq){
return {index,ok:false,urls,baseUrls,cancelled:true};
}
}

return {
index,
ok,
urls:loadUrls,
baseUrls
};

}


async function jumpOlderAvailableRunForMissingSelection(){

if(latestSearchInProgress || modelCompareMode){
return false;
}

if(!shouldJumpOlderAvailableRunForMissingSelection()){
return false;
}

let baseRunUTC=getSelectedUTCDate();

await jumpLatestAvailableForCurrentSelection({
silent:false,
preserveForecastHour:getSelectedTimelineHourForPreserve(),
baseDate:baseRunUTC,
skipRunUTC:baseRunUTC
});

return true;

}

function shouldJumpOlderAvailableRunForMissingSelection(){

let selectedRunUTC=getSelectedUTCDate();

if(!(selectedRunUTC instanceof Date) || Number.isNaN(selectedRunUTC.getTime())){
return false;
}

let product=getCurrentProduct();
let baseDate=getDefaultLatestSearchBaseDate(product);

if(!(baseDate instanceof Date) || Number.isNaN(baseDate.getTime())){
return false;
}

let lookbackHours=getLatestSearchLookbackHours(product);
let selectedAgeHours=(baseDate.getTime()-selectedRunUTC.getTime())/(60*60*1000);

return selectedAgeHours>=0 && selectedAgeHours<=lookbackHours;

}


function getForecastPreloadOrder(count){
let safeCount=Math.max(0,Number(count) || 0);
let defaultOrder=Array.from({length:safeCount},(_,index)=>index);

if(currentMainMenu!=='analysis' || !isRunTimeSliderMode()){
return defaultOrder;
}

let zeroIndex=currentForecastList.findIndex(value=>Number(value)===0);

if(zeroIndex<0){
zeroIndex=Number(slider.value || 0);
}

zeroIndex=Math.max(0,Math.min(safeCount-1,zeroIndex));

let order=[];
for(let i=zeroIndex;i>=0;i--){
order.push(i);
}
for(let i=zeroIndex+1;i<safeCount;i++){
order.push(i);
}

return order;
}


function isRunTimeFrameFuture(index,nowUTC=new Date()){

if(!isRunTimeSliderMode()){
return false;
}

if(!['analysis','edit'].includes(currentMainMenu)){
return false;
}

let runUTC=getRunUTCForForecastIndex(index);

if(!(runUTC instanceof Date) || Number.isNaN(runUTC.getTime())){
return false;
}

// Treat frames later than the current real UTC minute as not-yet-available.
// This prevents expected future analysis/edit frames from creating avoidable
// browser 404/CORS noise when the user searches near real time or presses Now.
let safeNow=new Date(nowUTC.getTime()+60*1000);
return runUTC.getTime()>safeNow.getTime();

}


function makeFutureRunTimeFrameMessage(index=Number(slider.value || 0)){

let runUTC=getRunUTCForForecastIndex(index);
let display=timeMode==='KST'
?new Date(runUTC.getTime()+9*60*60*1000)
:new Date(runUTC.getTime());
let displayDate=formatDateInputFromUTCParts(display);
let displayTime=formatRunTimeValue(display);

return (
`${getCurrentMainMenuLabel()} / ${displayDate} ${displayTime} ${timeMode}
`+
`현재 시각 이후 자료시각입니다. 아직 생산되지 않은 자료라 이미지 요청을 건너뜁니다.`
);

}


async function preloadAllForecastImages({
imageRefreshToken=''
}={}){

let seq=++imagePreloadSeq;
let count=currentForecastList.length || 1;
let priorityIndex=forecastTimelineState.clampIndex(Number(slider.value || 0));
let preloadOrder=getForecastPreloadOrder(count).filter(index=>index!==priorityIndex);
let availableCount=0;
resetForecastImageCache();
setAllForecastLoadStates(count,'loading');
renderForecastTimeline();
setViewerLoading(forecastTimelineState.getLoadState(Number(slider.value || 0))!=='available','이미지 로딩 중');

let applyPreloadResult=(index,result)=>{

if(seq!==imagePreloadSeq || result.cancelled){
return false;
}

if(result.ok){
availableCount++;
}

setForecastLoadState(index,result.ok ? 'available' : 'missing');
setForecastImageCacheEntry(index,{
urls:result.urls,
baseUrls:result.baseUrls,
ok:result.ok,
quiet:!!result.quiet,
future:!!result.future
});
updateForecastSegmentState(index);
return true;

};

let priorityResult=await preloadForecastIndex(priorityIndex,seq,{imageRefreshToken});

if(!applyPreloadResult(priorityIndex,priorityResult)){
return;
}

if(priorityIndex===Number(slider.value || 0)){
await displayCurrentForecastImage();
}

await CDSImagePipeline.runConcurrentRange({
count:preloadOrder.length,
concurrency:IMAGE_PRELOAD_CONCURRENCY,
isCancelled:()=>seq!==imagePreloadSeq,
task:async orderIndex=>{
let i=preloadOrder[orderIndex];
let result=await preloadForecastIndex(i,seq,{imageRefreshToken});

if(!applyPreloadResult(i,result)){
return false;
}

if(i===Number(slider.value || 0)){
displayCurrentForecastImage();
}
}
});

if(seq!==imagePreloadSeq){
return;
}

if(
availableCount===0 &&
await jumpOlderAvailableRunForMissingSelection()
){
return;
}

displayCurrentForecastImage();

}


function getCycleSupportStatus(modelId=currentModel,product=getCurrentProduct(),runUTC=getSelectedUTCDate()){

let runDateOnly=parseDateOnly(
formatDateInputFromUTCParts(runUTC)
);

let cycles=getCyclesForSelection(
modelId,
product,
runDateOnly
) || [];

let cycleHour=getCycleValueFromDate(runUTC);

if(cyclesIncludeValue(cycles,cycleHour)){
return {supported:true,message:''};
}

let modelName=getCurrentModelName(modelId);
let displayRun=timeMode==='KST'
?new Date(runUTC.getTime()+9*60*60*1000)
:new Date(runUTC.getTime());
let displayDate=formatDateInputFromUTCParts(displayRun);
let displayTime=formatRunTimeValue(displayRun);
let supportedText=cycles.length
?cycles.map(h=>{
let shown=timeMode==='KST' ? Number(h)+9 : Number(h);
return formatCycleValue(shown);
}).join(', ')
:'없음';

return {
supported:false,
message:
`${modelName}은(는) ${displayDate} ${displayTime} ${timeMode} 자료시각을 지원하지 않습니다.
`+
`지원 시각: ${supportedText}`
};

}

function makeExpectedButMissingMessage(){

let p=getCurrentProduct();
let modelName=getCurrentModelName();
let productLabel=getCurrentProductLabel(p);
let index=Number(slider.value || 0);
let runUTC=getRunUTCForForecastIndex(index);
let display=timeMode==='KST'
?new Date(runUTC.getTime()+9*60*60*1000)
:new Date(runUTC.getTime());
let displayDate=formatDateInputFromUTCParts(display);
let displayTime=formatRunTimeValue(display);
let lead=getForecastLeadLabel(index);

return (
`${getCurrentMainMenuLabel()} / ${modelName}
`+
`${productLabel} / ${displayDate} ${displayTime} ${timeMode} / ${lead}
`+
`모델·산출물·자료시각 조합은 유효하지만 이미지 파일을 찾지 못했습니다.
`+
`가장 최근 cycle이라면 아직 생산 또는 업로드 전일 수 있습니다.`
);

}

function selectionIsDisplayable(){

let p=getCurrentProduct();

if(!p){
showViewerMessage('선택된 카테고리에서 해당 산출자료를 찾을 수 없습니다.');
return false;
}

let s=getEffectiveModelStatus(
currentModel,
getSelectedUTCDate(),
p
);

if(!s.available){
showViewerMessage(s.message);
return false;
}

let cycleStatus=getCycleSupportStatus(
currentModel,
p,
getSelectedUTCDate()
);

if(!cycleStatus.supported){
showViewerMessage(cycleStatus.message);
return false;
}

if(!p.patternByModel?.[currentModel]){
showViewerMessage(
`${MODELS[currentModel]?.name || currentModel}은(는)
현재 선택한 산출자료를 지원하지 않습니다.`
);
return false;
}

let productStatus=getProductArchiveStatus(
p,
currentModel,
parseDateOnly(runDate.value)
);

if(!productStatus.available){
showViewerMessage(productStatus.message);
return false;
}

if(!MODELS[currentModel]?.folder){
showViewerMessage(
`${MODELS[currentModel]?.name || currentModel}은(는)\n아직 URL 매핑이 등록되지 않았습니다.`
);
return false;
}

let auxConfig=getCurrentAuxConfig();

if(auxConfig && !getCurrentAuxToken()){
showViewerMessage('추가 선택 항목을 선택해 주세요.');
return false;
}

return true;

}


function updateChart({
imageRefreshToken=''
}={}){

invalidateImagePreload();
invalidateForecastDisplay();
resetAnalysisResolutionState();

if(modelCompareMode){
updateCompareChart();
return;
}

chartImages.classList.remove('compare-images','fit-screen','fixed-size','layout-auto','layout-manual','compare-single','single-images');

if(!selectionIsDisplayable()){

resetForecastImageCache();
setForecastLoadStates(['missing']);

setViewerLoading(false);
return;

}

preloadAllForecastImages({imageRefreshToken});

}


function getForecastHoursForProductAtRun(product,modelId,runUTC){

let pattern=product?.patternByModel?.[modelId];

let patterns=Array.isArray(pattern)
?pattern
:[pattern];

let usesForecastHour=patterns.some(
p=>typeof p==='string' && p.includes('{fh}')
);

if(!usesForecastHour){
return [0];
}

let cycleHour=getCycleValueFromDate(runUTC);

let runDateOnly=parseDateOnly(
formatDateInputFromUTCParts(runUTC)
);

let modelHours=getForecastHours(
modelId,
runDateOnly,
cycleHour
) || [0];

let productScheme=
product?.forecastStepByModel?.[modelId];

if(productScheme){

let maxLead=Math.max(...modelHours);

return expandProductSteps(
productScheme,
maxLead
);

}

return modelHours;

}


function buildImageUrlsForCurrentSelectionAtRun(runUTC){

let p=getCurrentProduct();

if(!p){
return [];
}

let forecastHours=getForecastHoursForProductAtRun(
p,
currentModel,
runUTC
);

let fhValue=forecastHours[0] ?? 0;
let detailToken=getCurrentAuxToken();

return makeChartImageUrls({
product:p,
modelId:currentModel,
runUTC,
forecastHour:fhValue,
detailToken,
checkAvailability:true
});

}

async function urlsExist(urls,{
existenceMode=getProductExistenceMode(),
imageRefreshToken=''
}={}){

return CDSImagePipeline.urlsExist(urls,{
loadImage:url=>loadImage(addImageRefreshToken(url,imageRefreshToken)),
existenceMode
});

}

function addImageRefreshToken(url,token){

if(!token || typeof url!=='string'){
return url;
}

let separator=url.includes('?') ? '&' : '?';
return `${url}${separator}_cds_refresh=${encodeURIComponent(token)}`;

}

function addImageRefreshTokenToUrls(urls,token){

if(!token || !Array.isArray(urls)){
return urls;
}

return urls.map(url=>addImageRefreshToken(url,token));

}


async function currentSelectionExistsAtRun(runUTC,{
imageRefreshToken=''
}={}){

let urls=buildImageUrlsForCurrentSelectionAtRun(
runUTC
);

if(!urls || urls.length===0){

return {
exists:false,
urls:[]
};

}

let resolvedUrls=await resolveAnalysisResolutionUrls(urls);
let exists=await urlsExist(resolvedUrls,{imageRefreshToken});

return {
exists,
urls:resolvedUrls
};

}

function isSeaSurfaceTemperatureDailySelection(product=getCurrentProduct()){

return !!(
currentMainMenu==='analysis' &&
product?.category==='ssta' &&
currentModel==='usst'
);

}

function getLatestSearchLookbackHours(product=getCurrentProduct()){

let baseLookback=Math.max(24,Number(NOW_LOOKBACK_HOURS) || 24);

if(currentMainMenu==='analysis'){
baseLookback=Math.max(baseLookback,72);
}

if(isSeaSurfaceTemperatureDailySelection(product)){
return Math.max(baseLookback,SST_LOOKBACK_HOURS);
}

return baseLookback;

}

function getLatestSearchMaxCandidates(lookbackHours){

let hours=Math.max(0,Number(lookbackHours) || 0);

return Math.max(
NOW_MAX_CANDIDATES,
Math.floor(hours)+1
);

}

function getDefaultLatestSearchBaseDate(product=getCurrentProduct()){

let now=new Date();

if(!isSeaSurfaceTemperatureDailySelection(product)){
return now;
}

let kstNow=new Date(now.getTime()+9*60*60*1000);

return new Date(Date.UTC(
kstNow.getUTCFullYear(),
kstNow.getUTCMonth(),
kstNow.getUTCDate()-1,
23,
0,
0,
0
));

}

function getRecentRunCandidates(
modelId,
baseDate=new Date(),
lookbackHours=NOW_LOOKBACK_HOURS,
maxCandidates=NOW_MAX_CANDIDATES
){

let candidates=[];

let base=new Date(baseDate.getTime());
base.setUTCMinutes(base.getUTCMinutes()>=30 ? 30 : 0,0,0);

for(let i=0;i<=lookbackHours*2;i++){

let d=new Date(
base.getTime()-i*30*60*1000
);

let dateOnly=parseDateOnly(
formatDateInputFromUTCParts(d)
);

let cycles=getCyclesForSelection(
modelId,
getCurrentProduct(),
dateOnly
);

let cycleHour=getCycleValueFromDate(d);

if(!cyclesIncludeValue(cycles,cycleHour)){
continue;
}

let status=getEffectiveModelStatus(
modelId,
d
);

if(!status.available){
continue;
}

candidates.push(d);

if(candidates.length>=maxCandidates){
break;
}

}

return candidates;

}

async function jumpLatestAvailableForCurrentSelection({
silent=false,
preserveForecastHour=getSelectedTimelineHourForPreserve(),
preserveValidTimeFromRunUTC=null,
forceImageRefresh=false,
baseDate=null,
skipRunUTC=null
}={}){

let searchId=++latestSearchSeq;
latestSearchInProgress=true;
let imageRefreshToken=forceImageRefresh ? String(Date.now()) : '';
let product=getCurrentProduct();
let lookbackHours=getLatestSearchLookbackHours(product);
let maxCandidates=getLatestSearchMaxCandidates(lookbackHours);
let searchBaseDate=baseDate || getDefaultLatestSearchBaseDate(product);
let skipRunStamp=skipRunUTC ? formatUTCStampFromDate(skipRunUTC) : null;

setViewerLoading(true,'최신 자료 검색 중');

try{

let candidates=getRecentRunCandidates(
currentModel,
searchBaseDate,
lookbackHours,
maxCandidates
);

for(let runUTC of candidates){

if(searchId!==latestSearchSeq){
return false;
}

if(skipRunStamp && formatUTCStampFromDate(runUTC)===skipRunStamp){
continue;
}

let result=await currentSelectionExistsAtRun(
runUTC,
{imageRefreshToken}
);

if(searchId!==latestSearchSeq){
return false;
}

if(result.exists){

let targetForecastHour=preserveForecastHour;

if(
preserveValidTimeFromRunUTC instanceof Date &&
!Number.isNaN(preserveValidTimeFromRunUTC.getTime()) &&
typeof getForecastHourForRunChange==='function'
){
targetForecastHour=getForecastHourForRunChange(
preserveValidTimeFromRunUTC,
runUTC
);
}

setRunControlsToUTC(runUTC);

refreshView({
updateCategories:false,
updateProducts:true,
updateHours:false,
resetSlider:true,
preserveForecastHour:targetForecastHour,
imageRefreshToken,
updateChartAfter:true
});

return true;

}

}

if(!silent){

showViewerMessage(
makeLatestNotFoundMessage()
);

}
else{

updateChart({imageRefreshToken});

}

return false;

}
catch(error){

console.error('최신 자료 검색 중 오류:',error);

if(!silent){
showViewerMessage(
'최신 자료 검색 중 오류가 발생했습니다.\n콘솔 로그를 확인해 주세요.'
);
}

return false;

}
finally{

if(searchId!==latestSearchSeq){
return;
}

latestSearchInProgress=false;
setViewerLoading(false);

}

}




function handleCategoryChange(){

let previousForecastHour=getSelectedTimelineHourForPreserve();

if(getActiveModelSpecificProductCategory()[currentModel]){
return;
}

invalidateSelectionAsyncWork();
let cat=getCurrentCategory();
let products=getActiveProducts();

let hasSameProductInCategory=products.some(
p=>p.category===cat && p.id===currentProduct && p.type!=='header'
);

if(!hasSameProductInCategory){

let firstProduct=getDefaultProductForCategory(cat) || products.find(
p=>p.category===cat && p.type!=='header'
);

if(firstProduct){
currentProduct=firstProduct.id;
}

}

/*
새 category + 새 product 기준으로 지원 가능한 모델로 이동한다.
산출물 선택이 우선이며, 현재 모델 미지원 시에만 안내 후 모델을 바꾼다.
*/
enforceModelRestrictionForCurrentCategory({notify:true});

populateProductCategories();

refreshViewAfterSelectionChange({
updateCategories:false,
updateProducts:true,
updateHours:true,
resetSlider:true,
preserveForecastHour:previousForecastHour,
updateChartAfter:true
});

}


function handleProductChange(event){

let previousForecastHour=getSelectedTimelineHourForPreserve();

if(!event.target.value){
return;
}

currentProduct=event.target.value;

invalidateSelectionAsyncWork();

if(modelCompareMode){
normalizeCompareModels();
}

enforceModelAllowedForCurrentSelection({notify:true});

refreshViewAfterSelectionChange({
updateCategories:true,
updateProducts:true,
updateHours:true,
resetSlider:true,
preserveForecastHour:previousForecastHour,
updateChartAfter:true
});

}



function bindEvents(){

rememberSelectedRunUTC();

if(appTitleReset){

let resetToInitialPage=()=>{
let initialUrl=window.location.origin+window.location.pathname;

if(window.location.href!==initialUrl){
window.location.href=initialUrl;
return;
}

window.location.reload();
};

appTitleReset.onclick=resetToInitialPage;
appTitleReset.onkeydown=e=>{
if(e.key!=='Enter' && e.key!==' '){
return;
}

e.preventDefault();
resetToInitialPage();
};

}

document.addEventListener('click',event=>{
if(!event.target.closest('.compare-layout-control')){
document.querySelectorAll('.compare-layout-menu').forEach(menu=>{
menu.classList.add('hidden');
});
}
});

document.querySelectorAll('[data-shift-hours]').forEach(button=>{
button.onclick=()=>shiftRunTimeByHours(button.dataset.shiftHours);
});

productCategory.onchange=handleCategoryChange;
productSelect.onchange=handleProductChange;
window.addEventListener('resize',syncMobileProductCategoryWidth,{passive:true});
mobileAuxTrigger?.addEventListener('click',openMobileAuxSheet);
mobileAuxClose?.addEventListener('click',closeMobileAuxSheet);
mobileAuxBackdrop?.addEventListener('click',closeMobileAuxSheet);
mobileAuxSearch?.addEventListener('input',filterMobileAuxItems);

if(document.fonts?.ready){
document.fonts.ready.then(syncMobileProductCategoryWidth);
}

slider.addEventListener('input',()=>{

if(slider.disabled){
return;
}

updateForecastLabel();
displayCurrentForecastImage();

});

document.addEventListener('keydown',e=>{

if(e.key==='Escape' && auxSidebar?.classList.contains('mobile-open')){
e.preventDefault();
closeMobileAuxSheet();
return;
}

let active=document.activeElement;
let tag=active?.tagName;

/*
입력창/드롭다운에 포커스가 있을 때는 방향키를 뺏지 않음
*/
if(
tag==='INPUT' ||
tag==='SELECT' ||
tag==='TEXTAREA'
){
return;
}


/*
예측시간 좌우 이동
*/
if(e.key==='ArrowLeft'){

e.preventDefault();
moveForecastSelection(-1);
return;

}

if(e.key==='ArrowRight'){

e.preventDefault();
moveForecastSelection(1);
return;

}


/*
보조 패널 상하 이동
*/
let config=getCurrentAuxConfig();

if(!config){
return;
}

if(e.key==='ArrowUp'){

e.preventDefault();
moveAuxSelection(-1);
return;

}

if(e.key==='ArrowDown'){

e.preventDefault();
moveAuxSelection(1);
return;

}

});

runDate.min='1900-01-01';
runDate.max='2099-12-31';
runDate.onchange=handleRunDateChanged;

if(typeof attachDateInputYearKeyboardFix==='function'){
attachDateInputYearKeyboardFix(runDate);
}
else{
runDate.addEventListener('blur',normalizeRunDateYearInput);
}

runHour.onchange=handleRunHourChanged;

kstBtn.onclick=()=>switchTimeMode('KST');
utcBtn.onclick=()=>switchTimeMode('UTC');
nowBtn.onclick=()=>{

let previousRunUTC=getSelectedUTCDate();

jumpLatestAvailableForCurrentSelection({
silent:false,
preserveValidTimeFromRunUTC:previousRunUTC,
forceImageRefresh:true
});

};

}


function isCatalogValidationEnabled(){

try{
let params=new URLSearchParams(window.location.search);
return params.has('debugCatalog');
}
catch(e){
return false;
}

}


function validateCatalog(){

if(!isCatalogValidationEnabled()){
return;
}

let modelIds=new Set(Object.keys(MODELS || {}));
let categoryIds=new Set(
getActiveCategories()
.filter(c=>!isCategoryHeader(c) && c.id)
.map(c=>c.id)
);

Object.values(getActiveModelSpecificProductCategory() || {}).forEach(c=>{
categoryIds.add(c);
});

let hazardCategories=getSafeGlobal("HAZARD_CATEGORIES",[]);
let ensembleCategories=getSafeGlobal("ENSEMBLE_CATEGORIES",[]);
let analysisCategories=getSafeGlobal("ANALYSIS_CATEGORIES",[]);

let hazardProducts=getSafeGlobal("HAZARD_PRODUCTS",[]);
let ensembleProducts=getSafeGlobal("ENSEMBLE_PRODUCTS",[]);
let analysisProducts=getSafeGlobal("ANALYSIS_PRODUCTS",[]);

[...hazardCategories,...ensembleCategories,...analysisCategories].forEach(c=>{
if(c && c.id){
categoryIds.add(c.id);
}
});

let allProducts=[
...(PRODUCTS || []),
...hazardProducts,
...ensembleProducts,
...analysisProducts
];

let seenProducts=new Set();

allProducts.forEach(p=>{

if(!p.category){
console.warn('category가 없는 product/header:',p);
return;
}

if(!categoryIds.has(p.category)){
console.warn('정의되지 않은 category:',p.category,p.id || p.label);
}

if(p.type==='header'){
return;
}

let key=`${p.category}:${p.id}`;

if(seenProducts.has(key)){
console.warn('중복 product id:',key);
}

seenProducts.add(key);

[
'patternByModel',
'folderByModel',
'archiveStartByModel',
'archiveEndByModel',
'forecastStepByModel'
].forEach(field=>{

if(!p[field]){
return;
}

Object.keys(p[field]).forEach(modelId=>{
if(!modelIds.has(modelId)){
console.warn(`존재하지 않는 modelId in ${field}:`,modelId,key);
}
});

});

let patterns=p.patternByModel || {};
Object.entries(patterns).forEach(([modelId,patternValue])=>{

let list=Array.isArray(patternValue)?patternValue:[patternValue];

list.forEach(pattern=>{
if(typeof pattern!=='string'){
console.warn('pattern이 문자열이 아닙니다:',key,modelId,pattern);
}

let auxRules=getSafeGlobal('AUX_USAGE_RULES',{});
let hasAuxRule=Object.values(auxRules || {}).some(ruleGroup=>{
return !!(
ruleGroup[p.category] ||
ruleGroup[p.id] ||
ruleGroup[p.category+':'+p.id] ||
(p.auxSelectorKey && ruleGroup[p.auxSelectorKey])
);
});

if(
typeof pattern==='string' &&
pattern.includes('{detail}') &&
!hasAuxRule &&
!p.auxSelectorKey
){
console.warn('{detail}이 있지만 보조 패널 설정이 없습니다:',key,modelId,pattern);
}
});

});

});

}


init();

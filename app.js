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
const loadingOverlay=document.getElementById('loadingOverlay');
const kstBtn=document.getElementById('kstBtn');
const utcBtn=document.getElementById('utcBtn');
const nowBtn=document.getElementById('nowBtn');
const forecastTimeline=document.getElementById('forecastTimeline');
const viewerWrap=document.querySelector('.viewer-wrap');

let currentModel='kim_gdps';
let currentProduct='gph500';
let currentForecastList=[];
let timeMode='KST';
let currentAuxValue=null;
let currentMainMenu='forecast';
let imagePreloadSeq=0;
let forecastLoadStates=[];
let forecastImageCache=new Map();
let forecastDisplayRequest=null;

let auxAvailabilitySeq=0;
let auxAvailabilityCache=new Map();
let auxAvailabilityLoadingKey='';
let auxAvailabilityLoading=false;

const AUX_AVAILABILITY_CONCURRENCY=6;

const IMAGE_PRELOAD_CONCURRENCY=2;

const modelGroups=[

{
id:'global',
label:'전지구',
models:[
['kim_gdps','KIM_GDAPS'],
['ukmo','UKUM'],
['ecmwf','ECMWF']
]
},

{
id:'regional',
label:'지역',
models:[
['kim_rdps','KIM_RDAPS']
]
},

{
id:'local',
label:'국지',
models:[
['kim_ldps','KIM_LDAPS']
]
},

{
id:'nowcast',
label:'초단기',
models:[
['kim_klfs','KIM_KLAPS']
]
},

{
id:'gens',
label:'전지구확률',
models:[
['kim_epsg','KIM_EPSG'],
['ecmwf_eps','ECMWF_EPS']
]
},

{
id:'lens',
label:'국지확률',
models:[
['kim_lens','KIM_LENS']
]
},

{
id:'ended',
label:'종료모델',
models:[
['um_gdps','UM_GDAPS'],
['um_rdps','UM_RDAPS'],
['kwrf_rdps','WRF_RDAPS'],
['um_ldps','UM_LDAPS'],
['um_klfs','UM_KLAPS'],
['um_vdps','UM_VDAPS']
]
},

{
id:'ended_ens',
label:'종료모델',
models:[
['um_epsg','UM_EPSG'],
['um_lens','UM_LENS']
]
},

{
id:'model_analysis',
label:'모델분석',
models:[
['kim_anal','KIM_ANAL'],
['kas','KAS'],
['kim_klps', 'KIM_KLPS']
]
},

{
id:'ended_analysis',
label:'종료모델',
models:[
['um_anal','UM_ANAL'],
['ecmwf_ra','ECMWF'],
['um_klps', 'UM_KLPS']
]
},

{
id:'observation_hidden',
label:'관측',
hidden:true,
models:[
['obs_upper','OBS_UPPER']
]
},

{
id:'edit_hidden',
label:'편집',
hidden:true,
models:[
['edit_chart','EDIT_CHART']
]
}

];


const MODEL_GROUP_VISIBILITY_BY_MENU={
edit:['edit_hidden'],
analysis:['model_analysis', 'observation_hidden', 'ended_analysis'],
forecast:['global','regional','local','nowcast','ended'],
hazard:['global','regional','local','nowcast','ended'],
ensemble:['gens','lens','ended_ens']
};

function getFirstModelIdInCurrentMenu({
includeHidden=false
}={}){

for(let group of getVisibleModelGroups()){

if(group.hidden && !includeHidden){
continue;
}

if(group.models.length){
return group.models[0][0];
}

}

return null;

}


function getVisibleModelGroups(){

let ids=MODEL_GROUP_VISIBILITY_BY_MENU[currentMainMenu];

if(!ids){
return modelGroups;
}

return modelGroups.filter(group=>
ids.includes(group.id)
);

}


function isModelVisibleInCurrentMenu(modelId){

return getVisibleModelGroups().some(group=>
group.models.some(model=>model[0]===modelId)
);

}


function getFirstVisibleModelId(){

for(let group of getVisibleModelGroups()){

if(group.hidden){
continue;
}

if(group.models.length){
return group.models[0][0];
}

}

return null;

}


function ensureCurrentModelVisibleForMenu(){

if(isModelVisibleInCurrentMenu(currentModel)){
return;
}

let fallback=
getFirstModelIdInCurrentMenu({includeHidden:false}) ||
getFirstModelIdInCurrentMenu({includeHidden:true});

if(fallback){
currentModel=fallback;
}

}

const CURRENT_PRODUCT_EXISTENCE_MODE="all";

const AUTO_CHECK_LATEST_ON_SELECTION_CHANGE=false;

const NOW_LOOKBACK_HOURS=168;
const NOW_MAX_CANDIDATES=32;
const NOW_IMAGE_TIMEOUT_MS=7000;
const AUTO_CHECK_DEBOUNCE_MS=250;

let latestSearchSeq=0;
let autoCheckTimer=null;

const MAIN_MENU_META={

edit:{
label:"편집일기도",
catalog:"edit"
},

analysis:{
label:"분석장",
catalog:"analysis"
},

forecast:{
label:"예보장",
catalog:"forecast"
},

hazard:{
label:"위험기상",
catalog:"hazard"
},

ensemble:{
label:"앙상블",
catalog:"ensemble"
}

};


const EMPTY_PRODUCT_CATEGORIES=[
{id:"empty",name:"준비중"}
];

const EMPTY_PRODUCTS=[
{category:"empty",id:"empty",label:"준비중",patternByModel:{}}
];


function getSafeGlobal(name,fallback){

try{

if(typeof window!=="undefined" && Object.prototype.hasOwnProperty.call(window,name)){
return window[name];
}

}
catch(e){}

try{

return Function(`return typeof ${name} !== "undefined" ? ${name} : undefined`)() ?? fallback;

}
catch(e){

return fallback;

}

}


function getCurrentCatalogKey(){

return MAIN_MENU_META[currentMainMenu]?.catalog || 'forecast';

}

function getCurrentMainMenuLabel(){

return MAIN_MENU_META[currentMainMenu]?.label || currentMainMenu;

}


function getCurrentModelName(modelId=currentModel){

return MODELS[modelId]?.name || modelId;

}


function getCurrentProductLabel(product=getCurrentProduct()){

return product?.label || '현재 선택한 산출자료';

}


function makeLatestNotFoundMessage(){

let menuLabel=getCurrentMainMenuLabel();
let modelName=getCurrentModelName();
let productLabel=getCurrentProductLabel();

return (
`${menuLabel} / ${modelName}\n`+
`현재 선택한 산출자료(${productLabel})의 최근 사용 가능한 자료를 찾지 못했습니다.\n`+
`아직 생산되지 않았거나 해당 산출물이 최근 cycle에 없을 수 있습니다.`
);

}


function makeProductArchiveStartMessage({
modelId=currentModel,
product=getCurrentProduct(),
start
}={}){

let menuLabel=getCurrentMainMenuLabel();
let modelName=getCurrentModelName(modelId);
let productLabel=getCurrentProductLabel(product);

return (
`${menuLabel} / ${modelName}\n`+
`현재 선택한 산출자료(${productLabel})는\n`+
`${start} 이후부터 조회할 수 있습니다.`
);

}


function makeProductArchiveEndMessage({
modelId=currentModel,
product=getCurrentProduct(),
end
}={}){

let menuLabel=getCurrentMainMenuLabel();
let modelName=getCurrentModelName(modelId);
let productLabel=getCurrentProductLabel(product);

return (
`${menuLabel} / ${modelName}\n`+
`현재 선택한 산출자료(${productLabel})는\n`+
`${end}까지만 조회할 수 있습니다.`
);

}


function getCatalogConfig(){

let all=getSafeGlobal('CATALOG_CONFIG',{});
let key=getCurrentCatalogKey();

return all[key] || all.empty || {};

}


function resolveCatalogValue(value,fallback){

if(typeof value==='function'){

try{
return value() ?? fallback;
}
catch(e){
console.warn('catalog 설정을 읽지 못했습니다.',e);
return fallback;
}

}

return value ?? fallback;

}


function getCatalogValue(key,fallback){

return resolveCatalogValue(
getCatalogConfig()[key],
fallback
);

}


function getActiveCategories(){

return getCatalogValue('categories',EMPTY_PRODUCT_CATEGORIES);

}


function isCategoryHeader(category){

return category.type==='header' || category.type==='separator';

}


function getSelectableCategories(){

return getActiveCategories().filter(
c=>!isCategoryHeader(c) && c.id
);

}


function getActiveProducts(){

return getCatalogValue('products',EMPTY_PRODUCTS);

}


function getActiveProductCategoryUIConfig(){

return getCatalogValue('productCategoryUi',{});

}


function getActiveCategoryModelRestrictions(){

return getCatalogValue('categoryModelRestrictions',{});

}


function getActiveSelectionModelRestrictions(){

return getCatalogValue('selectionModelRestrictions',{});

}


function getActiveDefaultProductByCategory(){

return getCatalogValue('defaultProductByCategory',{});

}


function getActiveModelSpecificProductCategory(){

return getCatalogValue('modelSpecificProductCategory',{});

}


function getActiveCategoryRedirectByModel(){

return getCatalogValue('categoryRedirectByModel',{});

}


function getActiveDisabledProductCategoriesByModel(){

return getCatalogValue('disabledProductCategoriesByModel',{});

}



function isForecastCatalog(){

return getCurrentCatalogKey()==="forecast";

}

function inferMainMenuIdFromButton(btn,index){

if(btn.dataset?.menu){
return btn.dataset.menu;
}

let text=(btn.textContent || "").trim();

if(text.includes("편집")){
return "edit";
}

if(text.includes("분석")){
return "analysis";
}

if(text.includes("예보")){
return "forecast";
}

if(text.includes("위험")){
return "hazard";
}

if(text.includes("앙상블")){
return "ensemble";
}

return ["edit","analysis","forecast","hazard","ensemble"][index] || "forecast";

}


function bindMainMenu(){

let buttons=[...document.querySelectorAll(".menu-btn")];

buttons.forEach((btn,index)=>{

let menuId=inferMainMenuIdFromButton(btn,index);
btn.dataset.menu=menuId;

btn.onclick=()=>{

if(menuId===currentMainMenu){
return;
}

currentMainMenu=menuId;
ensureCurrentModelVisibleForMenu();

buttons.forEach(b=>{
b.classList.toggle("active",b.dataset.menu===currentMainMenu);
});

let selectableCategories=getSelectableCategories();
let firstCategory=selectableCategories[0];

if(firstCategory){
productCategory.value=firstCategory.id;
}

let firstProduct=getDefaultProductForCategory(
productCategory.value || firstCategory?.id
);

if(firstProduct){
currentProduct=firstProduct.id;
}
else{
currentProduct="";
}

currentAuxValue=null;

enforceModelRestrictionForCurrentCategory();

refreshView({
updateCategories:true,
updateProducts:true,
updateHours:true,
resetSlider:true,
updateChartAfter:false
});

setTimeout(()=>{

jumpLatestAvailableForCurrentSelection({
silent:false
});

},0);

};

});

buttons.forEach(btn=>{
btn.classList.toggle("active",btn.dataset.menu===currentMainMenu);
});

}


function getDefaultProductForCategory(categoryId){

let defaults=getActiveDefaultProductByCategory();
let preferredId=defaults[categoryId];

if(preferredId){

let preferredProduct=getActiveProducts().find(
p=>
p.category===categoryId &&
p.id===preferredId &&
p.type!=="header"
);

if(preferredProduct){
return preferredProduct;
}

}

return getActiveProducts().find(
p=>
p.category===categoryId &&
p.type!=="header"
);

}


/* 특정 드롭다운 영역/지점 선택 보조 패널 */







const AUTO_NOW_ON_STARTUP=true;


function init(){

validateCatalog();
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
auxAvailabilityLoadingKey===key
){
return;
}

if(!auxAvailabilityCache.has(key)){
await probeAuxAvailabilityForCurrentSelection();
return;
}

}

if(updateChartAfter){
updateChart();
}

}


function renderModels(){

modelGrid.innerHTML='';

let groups=getVisibleModelGroups().filter(
group=>!group.hidden
);

let modelBox=modelGrid.closest('.model-box');

if(modelBox){
modelBox.classList.toggle('hidden',groups.length===0);
}

groups.forEach(group=>{

let section=document.createElement('div');
section.className='model-section';

let title=document.createElement('div');
title.className='model-section-title';
title.textContent=group.label;

let buttons=document.createElement('div');
buttons.className='model-button-list';

group.models.forEach(m=>{

let modelId=m[0];
let label=m[1];
let modelAllowed=isModelAllowedByCurrentCategory(modelId);

let btn=document.createElement('button');
btn.type='button';
btn.className=
'model-cell'+
(modelId===currentModel ? ' active' : '')+
(!modelAllowed ? ' disabled' : '');

btn.disabled=!modelAllowed;
btn.textContent=label;

btn.onclick=()=>{

if(!modelAllowed){
return;
}

let previousForecastHour=getSelectedForecastHour();

currentModel=modelId;

applyCategoryRedirectForCurrentModel();

refreshView({
updateCategories:true,
updateProducts:true,
updateHours:true,
resetSlider:true,
preserveForecastHour:previousForecastHour,
updateChartAfter:true
});

};

buttons.appendChild(btn);

});

section.appendChild(title);
section.appendChild(buttons);
modelGrid.appendChild(section);

});

}


function pad2(value){
return String(value).padStart(2,'0');
}


function formatDateInputLocal(date){
let y=date.getFullYear();
let m=pad2(date.getMonth()+1);
let d=pad2(date.getDate());
return `${y}-${m}-${d}`;
}


function formatDateInputFromUTCParts(date){
let y=date.getUTCFullYear();
let m=pad2(date.getUTCMonth()+1);
let d=pad2(date.getUTCDate());
return `${y}-${m}-${d}`;
}


function formatUTCStampFromDate(date){
let y=date.getUTCFullYear();
let m=pad2(date.getUTCMonth()+1);
let d=pad2(date.getUTCDate());
let h=pad2(date.getUTCHours());
return `${y}${m}${d}${h}`;
}


function setToday(){
runDate.value=formatDateInputLocal(new Date());
}


function parseDateOnly(dateString){

let [y,m,d]=dateString.split('-').map(Number);

return new Date(
Date.UTC(y,m-1,d)
);

}


function getSelectedUTCDate(){

if(!runDate.value){
return new Date();
}

let [y,m,d]=runDate.value.split('-').map(Number);
let h=parseInt(runHour.value || '0',10);

if(Number.isNaN(h)){
h=0;
}

if(timeMode==='KST'){
return new Date(Date.UTC(y,m-1,d,h-9));
}

return new Date(Date.UTC(y,m-1,d,h));

}


function setControlsFromUTCDate(utcDate,mode=timeMode){

let displayDate;

if(mode==='KST'){
displayDate=new Date(utcDate.getTime()+9*60*60*1000);
}
else{
displayDate=new Date(utcDate.getTime());
}

runDate.value=formatDateInputFromUTCParts(displayDate);
runHour.value=pad2(displayDate.getUTCHours());

}


function getUTCStamp(){
return formatUTCStampFromDate(getSelectedUTCDate());
}


function getCyclesForSelection(modelId,product,date){

let productCycles=
product?.cyclesByModel?.[modelId] ||
product?.cycles ||
null;

if(productCycles){
return productCycles;
}

return getAvailableCycles(
modelId,
date
) || [];

}


function getCyclesForCurrentSelection(date=parseDateOnly(runDate.value)){

return getCyclesForSelection(
currentModel,
getCurrentProduct(),
date
);

}


function populateHours(preferredUTCDate=null){

let previousUTC=preferredUTCDate || getSelectedUTCDate();
let previousUTCStamp=formatUTCStampFromDate(previousUTC);

runHour.innerHTML='';

let cycles=getCyclesForCurrentSelection(
parseDateOnly(runDate.value)
);

let optionToSelect=null;

cycles.forEach(cycleHour=>{

let displayHour=timeMode==='KST'
?(cycleHour+9)%24
:cycleHour;

let o=document.createElement('option');
o.value=pad2(displayHour);
o.textContent=o.value+':00';
o.dataset.utcHour=pad2(cycleHour);

let testDate=new Date(previousUTC.getTime());
testDate.setUTCHours(cycleHour,0,0,0);

if(formatUTCStampFromDate(testDate)===previousUTCStamp){
optionToSelect=o.value;
}

runHour.appendChild(o);

});

if(runHour.options.length===0){
return;
}

if(optionToSelect && [...runHour.options].some(o=>o.value===optionToSelect)){
runHour.value=optionToSelect;
}
else if([...runHour.options].some(o=>o.value===runHour.value)){
/* keep current value */
}
else{
runHour.selectedIndex=0;
}

}


function getProductsInCategory(categoryId){

return getActiveProducts().filter(
p=>
p.category===categoryId &&
p.type!=="header"
);

}


function productSupportsModel(product,modelId){

if(!product || product.type==="header"){
return false;
}

return !!(
product.patternByModel &&
product.patternByModel[modelId]
);

}

function getSelectionRestrictionForProduct(product){

if(!product || !product.category || !product.id){
return null;
}

let restrictions=getActiveSelectionModelRestrictions();

return (
restrictions[`${product.category}:${product.id}`] ||
restrictions[`${product.category}:*`] ||
null
);

}




function canSelectProductByModelSwitch(product){

let restriction=getSelectionRestrictionForProduct(product);

if(!restriction || !restriction.allowModelSwitch){
return false;
}

let fallback=restriction.fallbackModel;

if(!fallback){
return false;
}

if(!isModelVisibleInCurrentMenu(fallback)){
return false;
}

return productSupportsModel(product,fallback);

}


function isProductSelectableInDropdown(product,modelId=currentModel){

return (
productSupportsModel(product,modelId) ||
canSelectProductByModelSwitch(product)
);

}


function getSupportedProductsInCategory(categoryId,modelId=currentModel){

return getProductsInCategory(categoryId).filter(
p=>productSupportsModel(p,modelId)
);

}


function categoryHasSupportedProduct(categoryId,modelId=currentModel){

return getProductsInCategory(categoryId).some(
p=>productSupportsModel(p,modelId)
);

}


function isCategoryAllowedByModelRestriction(categoryId,modelId=currentModel){

let restriction=getActiveCategoryModelRestrictions()[categoryId];

if(!restriction){
return true;
}

return restriction.allowedModels.includes(modelId);

}

function categoryHasSupportedProductForAnyVisibleModel(categoryId){

for(let group of getVisibleModelGroups()){

for(let model of group.models){

let modelId=model[0];

if(!isCategoryAllowedByModelRestriction(categoryId,modelId)){
continue;
}

if(categoryHasSupportedProduct(categoryId,modelId)){
return true;
}

}

}

return false;

}

function isProductCategoryDisabled(categoryId){

if(getCurrentCatalogKey()==="empty" || categoryId==="empty"){
return false;
}

if(
(
getActiveDisabledProductCategoriesByModel()[currentModel] || []
).includes(categoryId)
){
return true;
}

/*
1차 드롭다운은 현재 모델 기준으로 막지 않는다.
현재 대메뉴에서 보이는 모델 중 하나라도 해당 category 산출물을 지원하면 활성화한다.
*/
if(!categoryHasSupportedProductForAnyVisibleModel(categoryId)){
return true;
}

return false;

}


function getFirstEnabledProductCategory(){

return getSelectableCategories().find(
c=>!isProductCategoryDisabled(c.id)
);

}

function applyModelSwitchForCurrentProduct(){

let product=getCurrentProduct();
let restriction=getSelectionRestrictionForProduct(product);

if(!product || !restriction || !restriction.allowModelSwitch){
return false;
}

if(productSupportsModel(product,currentModel)){
return false;
}

let fallback=restriction.fallbackModel;

if(
fallback &&
isModelVisibleInCurrentMenu(fallback) &&
productSupportsModel(product,fallback)
){
currentModel=fallback;
return true;
}

return false;

}


function populateProductCategories(){

let categories=getActiveCategories();
let selectableCategories=getSelectableCategories();

let prevCategory=
productCategory.value ||
selectableCategories[0]?.id ||
'empty';

if(!selectableCategories.some(c=>c.id===prevCategory)){
prevCategory=selectableCategories[0]?.id || 'empty';
}

productCategory.innerHTML='';

categories.forEach(c=>{

let o=document.createElement('option');

if(isCategoryHeader(c)){

o.textContent=c.name || c.label || '────────';
o.disabled=true;
o.className='group-header';
productCategory.appendChild(o);
return;

}

o.value=c.id;
o.textContent=c.name;

if(isProductCategoryDisabled(c.id)){
o.disabled=true;
}

productCategory.appendChild(o);

});

if(isProductCategoryDisabled(prevCategory)){

let firstEnabled=getFirstEnabledProductCategory();

if(firstEnabled){
productCategory.value=firstEnabled.id;
}

}
else{
productCategory.value=prevCategory;
}

if(!productCategory.value && selectableCategories.length){
productCategory.value=selectableCategories[0].id;
}

}

function renderProductList(){

productSelect.innerHTML='';

let cat=getCurrentCategory();
let products=getActiveProducts();

products.forEach(p=>{

if(p.category!==cat) return;

let o=document.createElement('option');

if(p.type==='header'){
o.textContent=p.label;
o.disabled=true;
o.className='group-header';
productSelect.appendChild(o);
return;
}

o.value=p.id;
o.textContent=p.label;

let supported=isProductSelectableInDropdown(p,currentModel);

if(!supported){
o.disabled=true;
}

productSelect.appendChild(o);

});

let defaultProduct=getDefaultProductForCategory(cat);

let currentProductObject=products.find(
p=>p.category===cat && p.id===currentProduct && p.type!=='header'
);

let existsInCategory=!!currentProductObject;

let currentProductSupported=
currentProductObject &&
isProductSelectableInDropdown(currentProductObject,currentModel);

let supportedDefaultProduct=
defaultProduct &&
isProductSelectableInDropdown(defaultProduct,currentModel)
?defaultProduct
:getProductsInCategory(cat).find(
p=>isProductSelectableInDropdown(p,currentModel)
);

if(getProductCategoryUIConfig().hideProductSelect){

if(supportedDefaultProduct){
currentProduct=supportedDefaultProduct.id;
}

}
else if(!existsInCategory || !currentProductSupported){

if(supportedDefaultProduct){
currentProduct=supportedDefaultProduct.id;
}

}

productSelect.value=currentProduct;

}

function getSelectedForecastHour(){

if(!productUsesForecastHour()){
return null;
}

let index=Number(slider.value || 0);

return currentForecastList[index] ?? null;

}


function getForecastIndexByHour(hour){

if(hour===null || hour===undefined){
return -1;
}

return currentForecastList.findIndex(
h=>Number(h)===Number(hour)
);

}


function getSelectedForecastHour(){

if(!productUsesForecastHour()){
return null;
}

let index=Number(slider.value || 0);

return currentForecastList[index] ?? null;

}


function getForecastIndexByHour(hour){

if(hour===null || hour===undefined){
return -1;
}

return currentForecastList.findIndex(
h=>Number(h)===Number(hour)
);

}

function rebuildForecastAxis({
reset=true,
preserveForecastHour=null
}={}){

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

currentForecastList=[0];
slider.min=0;
slider.max=0;
slider.step=1;
slider.value=0;
slider.disabled=true;
forecastLabel.textContent='자료 없음';
forecastLoadStates=['missing'];
renderForecastTimeline();
return;

}

let productStatus=getProductArchiveStatus(
p,
currentModel,
parseDateOnly(runDate.value)
);

if(!productStatus.available){

currentForecastList=[0];
slider.min=0;
slider.max=0;
slider.step=1;
slider.value=0;
slider.disabled=true;
forecastLabel.textContent='자료 없음';
forecastLoadStates=['missing'];
renderForecastTimeline();
return;

}

if(!productUsesForecastHour()){

currentForecastList=[0];
slider.min=0;
slider.max=0;
slider.step=1;
slider.value=0;
slider.disabled=true;
forecastLabel.textContent='단일 이미지';
forecastLoadStates=['loading'];
renderForecastTimeline();
return;

}

currentForecastList=getForecastHoursForCurrentSelection();

if(!currentForecastList.length){
currentForecastList=[0];
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
slider.value=Math.max(0,Math.min(oldValue,currentForecastList.length-1));
}

updateForecastLabel();
renderForecastTimeline();

}


function updateForecastLabel(){

if(!productUsesForecastHour()){
forecastLabel.textContent='단일 이미지';
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


function getCurrentAuxRule(){

let catalogKey=getCurrentCatalogKey();
let cat=getCurrentCategory();
let p=getCurrentProduct();
let rules=(getSafeGlobal('AUX_USAGE_RULES',{}) || {})[catalogKey] || {};

let comboKey=p?.id ? `${cat}:${p.id}` : null;

return (
(comboKey && rules[comboKey]) ||
(p?.auxSelectorKey && rules[p.auxSelectorKey]) ||
(p?.id && rules[p.id]) ||
rules[cat] ||
null
);

}


function resolveAuxItems(items,rule){

return items.map(item=>{

if(item.type!=='item'){
return {...item};
}

let enabled=true;
let includeList=rule.includeByModel?.[currentModel];
let excludeList=rule.excludeByModel?.[currentModel];

if(includeList){
enabled=includeList.includes(item.value);
}

if(excludeList && excludeList.includes(item.value)){
enabled=false;
}

return {
...item,
disabled:!enabled
};

});

}


function getCurrentAuxConfig(){

let rule=getCurrentAuxRule();

if(!rule){
return null;
}

let selectors=getSafeGlobal('AUX_SELECTORS',{});
let optionSets=getSafeGlobal('AUX_OPTION_SETS',{});
let selector=selectors[rule.selector];

if(!selector){
return null;
}

let optionSet=optionSets[selector.optionSet];

if(!optionSet || !Array.isArray(optionSet.items)){
return null;
}

return {
...selector,
defaultValue:rule.defaultValue || selector.defaultValue,
items:resolveAuxItems(optionSet.items,rule)
};

}

function isAuxItemStaticallySupported(item){

if(item.type!=='item'){
return false;
}

if(item.disabled){
return false;
}

if(item.excludeModels && item.excludeModels.includes(currentModel)){
return false;
}

if(item.models){
return item.models.includes(currentModel);
}

return true;

}

function isAuxItemVisible(item){

if(!item){
return false;
}

if(item.type!=='item'){
return true;
}

/*
일반 지점은 항상 표시 후보
*/
if(!item.hidden){
return true;
}

let rule=getCurrentAuxRule();
let showHiddenValues=rule?.showHiddenValues || [];
let showHiddenByModel=rule?.showHiddenByModel?.[currentModel] || [];

/*
명시적으로 보이게 한 hidden 지점
*/
if(
showHiddenValues.includes(item.value) ||
showHiddenByModel.includes(item.value)
){
return true;
}

/*
동적 availability가 켜진 경우:
hidden 지점은 검사 결과 available일 때만 표시한다.
*/
if(rule?.dynamicAvailability){

let key=getAuxAvailabilityCacheKey();
let availableSet=auxAvailabilityCache.get(key);

return !!(
availableSet &&
availableSet.has(item.value)
);

}

/*
동적 검사가 없는 일반 상황에서는 hidden 지점은 숨김
*/
return false;

}

function getVisibleAuxItems(config){

if(!config || !Array.isArray(config.items)){
return [];
}

let raw=config.items.filter(item=>isAuxItemVisible(item));

let cleaned=[];

raw.forEach(item=>{

if(item.type==='separator'){

/*
맨 앞 separator 제거
*/
if(cleaned.length===0){
return;
}

/*
separator 연속 제거
*/
let prev=cleaned[cleaned.length-1];

if(prev.type==='separator'){
return;
}

}

cleaned.push(item);

});

/*
맨 끝 separator 제거
*/
while(
cleaned.length &&
cleaned[cleaned.length-1].type==='separator'
){
cleaned.pop();
}

return cleaned;

}


function getAuxAvailabilityCacheKey(){

return [
currentMainMenu,
currentModel,
getCurrentCategory(),
currentProduct,
getUTCStamp()
].join('|');

}


function isDynamicAuxAvailabilityEnabled(){

let rule=getCurrentAuxRule();
return !!(rule && rule.dynamicAvailability);

}


function isAuxItemSupported(item){

if(!isAuxItemStaticallySupported(item)){
return false;
}

if(!isDynamicAuxAvailabilityEnabled()){
return true;
}

let key=getAuxAvailabilityCacheKey();
let availableSet=auxAvailabilityCache.get(key);

if(!availableSet){
return false;
}

return availableSet.has(item.value);

}


function getAuxEnabledItems(config){

if(!config) return [];

return getVisibleAuxItems(config).filter(
item=>isAuxItemSupported(item)
);

}


function getCurrentAuxToken(){

let config=getCurrentAuxConfig();

if(!config) return null;

let selected=config.items.find(
item=>item.type==='item' && item.value===currentAuxValue
);

if(!selected) return null;

if(!isAuxItemSupported(selected)) return null;

return selected.value;

}


function renderAuxSidebar(){

let config=getCurrentAuxConfig();

auxSidebar.classList.remove('aux-wide','aux-narrow');

if(!config){

currentAuxValue=null;
auxSidebar.classList.add('hidden');
auxSidebarTitle.textContent='';
auxSidebarList.innerHTML='';
return;

}

if(config.widthClass==='wide'){
auxSidebar.classList.add('aux-wide');
}

if(config.widthClass==='narrow'){
auxSidebar.classList.add('aux-narrow');
}

auxSidebar.classList.remove('hidden');
auxSidebarTitle.textContent=config.title || '상세 선택';
auxSidebarList.innerHTML='';

let visibleItems=getVisibleAuxItems(config);

let enabledItems=visibleItems.filter(
item=>isAuxItemSupported(item)
);

let validValues=enabledItems.map(x=>x.value);

if(!validValues.includes(currentAuxValue)){
currentAuxValue=config.defaultValue;

if(!validValues.includes(currentAuxValue)){
currentAuxValue=validValues[0] || null;
}

}

visibleItems.forEach(item=>{

if(item.type==='separator'){
let sep=document.createElement('div');
sep.className='aux-separator';
auxSidebarList.appendChild(sep);
return;
}

let supported=isAuxItemSupported(item);
let btn=document.createElement('button');
btn.type='button';
btn.className=
'aux-item'+
(item.value===currentAuxValue ? ' active' : '')+
(!supported ? ' disabled' : '');
btn.disabled=!supported;
btn.textContent=item.label;

btn.onclick=()=>{

if(!supported){
return;
}

currentAuxValue=item.value;

refreshView({
updateCategories:false,
updateProducts:false,
updateHours:false,
resetSlider:true,
updateChartAfter:true
});

};

auxSidebarList.appendChild(btn);

});

let activeItem=auxSidebarList.querySelector('.aux-item.active');

if(activeItem){
activeItem.scrollIntoView({
block:'nearest',
inline:'nearest'
});
}

}


function moveAuxSelection(direction){

let config=getCurrentAuxConfig();

if(!config){
return;
}

let items=getAuxEnabledItems(config);

if(!items.length){
return;
}

let currentIndex=items.findIndex(
item=>item.value===currentAuxValue
);

if(currentIndex<0){
currentIndex=0;
}

let nextIndex=currentIndex+direction;
nextIndex=Math.max(0,Math.min(nextIndex,items.length-1));

if(nextIndex===currentIndex){
return;
}

currentAuxValue=items[nextIndex].value;

refreshView({
updateCategories:false,
updateProducts:false,
updateHours:false,
resetSlider:true,
updateChartAfter:true
});



}


function syncProductCategoryVisibility(){

if(getActiveModelSpecificProductCategory()[currentModel]){
productCategory.classList.add('hidden');
}
else{
productCategory.classList.remove('hidden');
}

}


function getProductCategoryUIConfig(){

return getActiveProductCategoryUIConfig()[
getCurrentCategory()
] || {};

}


function syncProductSelectVisibility(){

let config=getProductCategoryUIConfig();

if(config.hideProductSelect){
productSelect.classList.add('hidden');
}
else{
productSelect.classList.remove('hidden');
}

}


function getCurrentCategoryRestriction(){

let cat=getCurrentCategory();
let exactKey=`${cat}:${currentProduct}`;
let categoryKey=`${cat}:*`;

let selectionRestrictions=getActiveSelectionModelRestrictions();
let categoryRestrictions=getActiveCategoryModelRestrictions();

return (
selectionRestrictions[exactKey] ||
selectionRestrictions[categoryKey] ||
categoryRestrictions[cat] ||
null
);

}

function getProductByIdInCurrentCategory(productId){

return getActiveProducts().find(
p=>
p.category===getCurrentCategory() &&
p.id===productId &&
p.type!=="header"
);

}





function getCurrentSelectedProductForModelFiltering(){

let product=getProductByIdInCurrentCategory(currentProduct);

if(product){
return product;
}

return null;

}


function isModelAllowedByCurrentCategory(modelId){
/* category / selection restriction 확인 */
let restriction=getCurrentCategoryRestriction();

if(
restriction &&
!restriction.allowedModels.includes(modelId)
){
return false;
}


/* 현재 선택된 산출물이 해당 모델을 지원하는지 확인 */
let product=getCurrentSelectedProductForModelFiltering();

if(product && !productSupportsModel(product,modelId)){
return false;
}

return true;

}


function enforceModelRestrictionForCurrentCategory(){

let restriction=getCurrentCategoryRestriction();

if(
restriction &&
!restriction.allowedModels.includes(currentModel)
){

let fallback=restriction.fallbackModel;

if(fallback && isModelAllowedByCurrentCategory(fallback)){
currentModel=fallback;
return;
}

}

enforceModelAllowedForCurrentSelection();

}

function getFirstAllowedVisibleModelIdForCurrentSelection(){

for(let group of getVisibleModelGroups()){

for(let model of group.models){

let modelId=model[0];

if(isModelAllowedByCurrentCategory(modelId)){
return modelId;
}

}

}

return null;

}


function enforceModelAllowedForCurrentSelection(){

if(isModelAllowedByCurrentCategory(currentModel)){
return;
}

let fallback=getFirstAllowedVisibleModelIdForCurrentSelection();

if(fallback){
currentModel=fallback;
}

}


function getCurrentProduct(){

return getActiveProducts().find(
p=>p.category===getCurrentCategory() && p.id===currentProduct
);

}



function getProxyBaseUrl(){

let base=(window.CDS_PROXY_BASE_URL || '').trim();

if(!base || base.includes('YOUR-WORKER')){
return '';
}

return base.replace(/\/+$/,'');

}

function getModelImageCount(product,modelId=currentModel){

let count=product?.imageCountByModel?.[modelId];

if(Number.isFinite(Number(count)) && Number(count)>0){
return Number(count);
}

let pattern=product?.patternByModel?.[modelId];

if(Array.isArray(pattern)){
return pattern.length;
}

return pattern ? 1 : 0;

}

function productRequiresDetail(product,modelId=currentModel){

return !!product?.requiresDetailByModel?.[modelId];

}

function buildProxyChartUrl({
run,
fh='000',
detail='',
imageIndex=0
}={}){

let p=getCurrentProduct();
let base=getProxyBaseUrl();

if(!base || !p){
return '';
}

let params=new URLSearchParams({
menu:getCurrentCatalogKey(),
category:getCurrentCategory(),
product:p.id,
model:currentModel,
run:String(run || getUTCStamp()),
fh:String(fh || '000').padStart(3,'0'),
index:String(imageIndex || 0)
});

if(detail){
params.set('detail',detail);
}

return `${base}/chart?${params.toString()}`;

}

function getCurrentPattern(){

let p=getCurrentProduct();

if(!p || !p.patternByModel || !p.patternByModel[currentModel]){
return null;
}

return p.patternByModel[currentModel];

}


function getCurrentPatterns(){

let pattern=getCurrentPattern();

if(!pattern){
return [];
}

return Array.isArray(pattern)
?pattern
:[pattern];

}

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

let p=getCurrentProduct();

return !!p?.usesForecastHourByModel?.[currentModel];

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

if(!p || !MODELS[currentModel]){
return [];
}

let count=getModelImageCount(p,currentModel);

if(!count){
return [];
}

let run=getUTCStamp();
let fhValue=currentForecastList[index] ?? currentForecastList[0] ?? 0;
let fh=String(fhValue).padStart(3,'0');
let detailToken=getCurrentAuxToken();

if(productRequiresDetail(p,currentModel) && !detailToken){
return [];
}

let urls=[];

for(let imageIndex=0;imageIndex<count;imageIndex++){
urls.push(buildProxyChartUrl({
run,
fh,
detail:detailToken || '',
imageIndex
}));
}

return urls.filter(Boolean);

}

function buildImageUrlsForDetailValue(detailValue,index=Number(slider.value || 0)){

let p=getCurrentProduct();

if(!p || !MODELS[currentModel]){
return [];
}

let count=getModelImageCount(p,currentModel);

if(!count){
return [];
}

let run=getUTCStamp();
let fhValue=currentForecastList[index] ?? currentForecastList[0] ?? 0;
let fh=String(fhValue).padStart(3,'0');
let urls=[];

for(let imageIndex=0;imageIndex<count;imageIndex++){
urls.push(buildProxyChartUrl({
run,
fh,
detail:detailValue || '',
imageIndex
}));
}

return urls.filter(Boolean);

}

async function checkAuxItemAvailability(item){

if(!isAuxItemStaticallySupported(item)){
return false;
}

let urls=buildImageUrlsForDetailValue(item.value);

if(!urls.length){
return false;
}

return await urlsExist(urls);

}

async function probeAuxAvailabilityForCurrentSelection(){

let config=getCurrentAuxConfig();
let rule=getCurrentAuxRule();

if(!config || !rule || !rule.dynamicAvailability){
return false;
}

let key=getAuxAvailabilityCacheKey();

/* 이미 캐시가 있으면 재검사 안 함 */
if(auxAvailabilityCache.has(key)){
return false;
}

let seq=++auxAvailabilitySeq;
auxAvailabilityLoading=true;
auxAvailabilityLoadingKey=key;

setViewerLoading(true,rule.loadingMessage || '관측지점 자료 확인 중');

/*
동적 검사 전 상태를 먼저 한 번 렌더링해서
버튼들을 비활성화된 상태로 보이게 한다.
*/
renderAuxSidebar();

let items=config.items.filter(
item=>item.type==='item' && isAuxItemStaticallySupported(item)
);

let availableValues=new Set();
let cursor=0;

async function worker(){

while(cursor<items.length){

let item=items[cursor++];
let ok=await checkAuxItemAvailability(item);

if(seq!==auxAvailabilitySeq){
return;
}

if(ok){
availableValues.add(item.value);
}

}

}

let workers=Array.from(
{length:Math.min(AUX_AVAILABILITY_CONCURRENCY,items.length)},
()=>worker()
);

await Promise.all(workers);

if(seq!==auxAvailabilitySeq){
return true;
}

auxAvailabilityCache.set(key,availableValues);
auxAvailabilityLoading=false;
auxAvailabilityLoadingKey='';

/* 현재 선택 지점이 없거나 비활성화되면 첫 사용 가능 지점 자동 선택 */
if(
!currentAuxValue ||
!availableValues.has(currentAuxValue)
){
currentAuxValue=config.defaultValue;

if(!currentAuxValue || !availableValues.has(currentAuxValue)){
currentAuxValue=[...availableValues][0] || null;
}
}

renderAuxSidebar();
rebuildForecastAxis({reset:true});
setViewerLoading(false);

if(availableValues.size===0){
showViewerMessage('해당 시각에 사용 가능한 관측단열선도 지점이 없습니다.');
return true;
}

updateChart();
return true;

}


function getForecastHourAtIndex(index){
return currentForecastList[index] ?? 0;
}


function getForecastLeadLabel(index){

if(!productUsesForecastHour()){
return '단일';
}

let h=getForecastHourAtIndex(index);
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
chartImages.classList.add('hidden');
modelStatus.textContent=message;
modelStatus.classList.remove('hidden');

}


function showCharts(urls){

modelStatus.textContent='';
modelStatus.classList.add('hidden');
chartImages.innerHTML='';
chartImages.classList.remove('hidden');

if(!urls || urls.length===0){
showViewerMessage('표출할 이미지 URL이 없습니다.');
return;
}

let failedCount=0;

urls.forEach(url=>{

let img=document.createElement('img');
img.alt='chart';
img.decoding='async';

img.onerror=()=>{

failedCount++;

if(failedCount===urls.length){

showViewerMessage(
'이미지를 찾을 수 없습니다.\n자료가 아직 생산되지 않았거나 해당 예측시간 자료가 없을 수 있습니다.'
);

}

};

img.src=url;
chartImages.appendChild(img);

});

}


function renderForecastTimeline(){

if(!forecastTimeline){
return;
}

let count=currentForecastList.length || 1;
let activeIndex=Number(slider.value || 0);
activeIndex=Math.max(0,Math.min(activeIndex,count-1));

forecastTimeline.innerHTML='';
forecastTimeline.style.setProperty('--forecast-count',String(count));
forecastTimeline.classList.toggle('is-single',count<=1);

let track=document.createElement('div');
track.className='forecast-track';
track.style.gridTemplateColumns=`repeat(${count}, minmax(4px, 1fr))`;

for(let i=0;i<count;i++){
let state=forecastLoadStates[i] || 'loading';
let seg=document.createElement('button');
seg.type='button';
seg.className=`forecast-segment state-${state}`+(i===activeIndex?' active':'');
seg.dataset.index=String(i);
seg.title=`${getValidTimeLabel(i)} / ${getForecastLeadLabel(i)}`;
seg.onclick=()=>{
setForecastIndex(i);
};
track.appendChild(seg);
}

let marker=document.createElement('div');
marker.className='forecast-marker';
marker.innerHTML=`<div class="marker-time">${getValidTimeLabel(activeIndex)}</div><div class="marker-lead">${getForecastLeadLabel(activeIndex)}</div>`;
let left=count<=1 ? 50 : ((activeIndex+0.5)/count)*100;
marker.style.left=`${left}%`;

forecastTimeline.appendChild(track);
forecastTimeline.appendChild(marker);

bindForecastTimelinePointer(track);

}


function updateForecastSegmentState(index){

if(!forecastTimeline){
return;
}

let seg=forecastTimeline.querySelector(`.forecast-segment[data-index="${index}"]`);

if(!seg){
return;
}

seg.classList.remove('state-loading','state-available','state-missing');
seg.classList.add('state-'+(forecastLoadStates[index] || 'loading'));

}


function updateForecastTimelineMarker(){

if(!forecastTimeline){
return;
}

let count=currentForecastList.length || 1;
let activeIndex=Number(slider.value || 0);
activeIndex=Math.max(0,Math.min(activeIndex,count-1));

forecastTimeline.querySelectorAll('.forecast-segment').forEach((seg,i)=>{
seg.classList.toggle('active',i===activeIndex);
});

let marker=forecastTimeline.querySelector('.forecast-marker');
if(marker){
let left=count<=1 ? 50 : ((activeIndex+0.5)/count)*100;
marker.style.left=`${left}%`;
let time=marker.querySelector('.marker-time');
let lead=marker.querySelector('.marker-lead');
if(time){time.textContent=getValidTimeLabel(activeIndex);}
if(lead){lead.textContent=getForecastLeadLabel(activeIndex);}
}

}

function refreshForecastTimelineLabels(){

if(!forecastTimeline){
return;
}

forecastTimeline
.querySelectorAll('.forecast-segment')
.forEach((seg,i)=>{
seg.title=`${getValidTimeLabel(i)} / ${getForecastLeadLabel(i)}`;
});

updateForecastTimelineMarker();

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

if(slider.disabled){
return;
}

let max=(currentForecastList.length || 1)-1;
let next=Math.max(0,Math.min(Number(index)||0,max));

slider.value=String(next);
updateForecastLabel();
displayCurrentForecastImage();

}

function moveForecastSelection(delta){

let max=(currentForecastList.length || 1)-1;

if(max<=0 || slider.disabled){
return;
}

let current=Number(slider.value || 0);

setForecastIndex(
current+delta
);

}


function displayCurrentForecastImage(){

let index=Number(slider.value || 0);
let cached=forecastImageCache.get(index);

if(!selectionIsDisplayable()){
return;
}

/*
preload가 성공해 캐시가 있으면 캐시 URL 사용
*/
if(cached?.urls?.length){
showCharts(cached.urls);
return;
}

/*
아직 preload 결과가 없어도
현재 선택 위치 이미지는 즉시 표출 시도한다.
*/
let urls=buildImageUrlsForForecastIndex(index);

if(urls.length){
showCharts(urls);
return;
}

showViewerMessage('표출할 이미지 URL이 없습니다.');

}


function loadImage(url,timeoutMs=NOW_IMAGE_TIMEOUT_MS){

return new Promise(resolve=>{

let done=false;
let img=new Image();

let timer=setTimeout(()=>{
if(done){return;}
done=true;
resolve(false);
},timeoutMs);

img.onload=()=>{
if(done){return;}
done=true;
clearTimeout(timer);
resolve(true);
};

img.onerror=()=>{
if(done){return;}
done=true;
clearTimeout(timer);
resolve(false);
};

img.src=url;

});

}

async function headExists(url,timeoutMs=5000){

let controller=new AbortController();
let timer=setTimeout(()=>{
controller.abort();
},timeoutMs);

try{

let response=await fetch(url,{
method:'HEAD',
signal:controller.signal,
cache:'force-cache'
});

return response.ok;

}
catch(error){

return false;

}
finally{

clearTimeout(timer);

}

}


async function preloadForecastIndex(index,seq){

let urls=buildImageUrlsForForecastIndex(index);

if(!urls.length){
return {index,ok:false,urls:[]};
}

let results=await Promise.all(
urls.map(url=>loadImage(url))
);

if(seq!==imagePreloadSeq){
return {index,ok:false,urls,cancelled:true};
}

let ok=CURRENT_PRODUCT_EXISTENCE_MODE==='any'
?results.some(Boolean)
:results.every(Boolean);

return {index,ok,urls};

}


async function preloadAllForecastImages(){

let seq=++imagePreloadSeq;
let count=currentForecastList.length || 1;
let activeIndex=Number(slider.value || 0);

forecastImageCache=new Map();
forecastLoadStates=Array.from({length:count},()=> 'loading');

renderForecastTimeline();

setViewerLoading(true,'이미지 로딩 중');

/*
1. 현재 선택된 예측시간을 가장 먼저 로드한다.
*/
let firstResult=await preloadForecastIndex(activeIndex,seq);

if(seq!==imagePreloadSeq || firstResult.cancelled){
return;
}

forecastLoadStates[activeIndex]=firstResult.ok ? 'available' : 'missing';
forecastImageCache.set(activeIndex,{
urls:firstResult.urls,
ok:firstResult.ok
});

renderForecastTimeline();
displayCurrentForecastImage();

/*
현재 이미지를 띄웠으면 스피너는 끈다.
나머지 시간대 검사는 백그라운드로 진행한다.
*/
setViewerLoading(false);

/*
2. 현재 위치 주변 시간대를 우선 검사한다.
*/
let priority=[];

for(let offset=1;offset<=3;offset++){

let left=activeIndex-offset;
let right=activeIndex+offset;

if(left>=0){
priority.push(left);
}

if(right<count){
priority.push(right);
}

}

/*
3. 나머지는 그 뒤에 검사한다.
*/
let rest=[];

for(let i=0;i<count;i++){

if(i===activeIndex){
continue;
}

if(priority.includes(i)){
continue;
}

rest.push(i);

}

let indices=[...priority,...rest];
let cursor=0;

async function worker(){

while(cursor<indices.length){

let i=indices[cursor++];
let result=await preloadForecastIndex(i,seq);

if(seq!==imagePreloadSeq || result.cancelled){
return;
}

forecastLoadStates[i]=result.ok ? 'available' : 'missing';
forecastImageCache.set(i,{
urls:result.urls,
ok:result.ok
});

updateForecastSegmentState(i);

}

}

let workers=Array.from(
{length:Math.min(IMAGE_PRELOAD_CONCURRENCY,indices.length)},
()=>worker()
);

await Promise.all(workers);

if(seq!==imagePreloadSeq){
return;
}

renderForecastTimeline();

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

if(!p.patternByModel?.[currentModel]){
showViewerMessage(
`${MODELS[currentModel]?.name || currentModel}은(는)\n현재 선택한 산출자료를 지원하지 않습니다.`
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

if(!getProxyBaseUrl()){
showViewerMessage(
'Cloudflare Worker 주소가 설정되지 않았습니다.\nproxy-config.js의 CDS_PROXY_BASE_URL을 배포한 Worker 주소로 변경해 주세요.'
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


function updateChart(){

imagePreloadSeq++;

if(!selectionIsDisplayable()){

forecastImageCache=new Map();
forecastLoadStates=['missing'];

setViewerLoading(false);
return;

}

preloadAllForecastImages();

}


function getForecastHoursForProductAtRun(product,modelId,runUTC){

let usesForecastHour=!!product?.usesForecastHourByModel?.[modelId];

if(!usesForecastHour){
return [0];
}

let cycleHour=runUTC.getUTCHours();

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

if(!p || !p.patternByModel?.[currentModel]){
return [];
}

let count=getModelImageCount(p,currentModel);

if(!count){
return [];
}

let model=MODELS[currentModel];

if(!model){
return [];
}

let modelStatus=getEffectiveModelStatus(
currentModel,
runUTC,
p
);

if(!modelStatus.available){
return [];
}

let runDateOnly=parseDateOnly(
formatDateInputFromUTCParts(runUTC)
);

let productStatus=getProductArchiveStatus(
p,
currentModel,
runDateOnly
);

if(!productStatus.available){
return [];
}

let run=formatUTCStampFromDate(runUTC);
let forecastHours=getForecastHoursForProductAtRun(
p,
currentModel,
runUTC
);

let fhValue=forecastHours[0] ?? 0;
let fh=String(fhValue).padStart(3,'0');
let detailToken=getCurrentAuxToken();

if(productRequiresDetail(p,currentModel) && !detailToken){
return [];
}

let urls=[];

for(let imageIndex=0;imageIndex<count;imageIndex++){
urls.push(buildProxyChartUrl({
run,
fh,
detail:detailToken || '',
imageIndex
}));
}

return urls.filter(Boolean);

}

async function urlsExist(urls){

if(!urls || urls.length===0){
return false;
}

let results=await Promise.all(
urls.map(url=>headExists(url))
);

if(CURRENT_PRODUCT_EXISTENCE_MODE==="any"){
return results.some(Boolean);
}

return results.every(Boolean);

}


async function currentSelectionExistsAtRun(runUTC){

let urls=buildImageUrlsForCurrentSelectionAtRun(
runUTC
);

if(!urls || urls.length===0){

return {
exists:false,
urls:[]
};

}

let exists=await urlsExist(urls);

return {
exists,
urls
};

}

function getCyclesForSelection(modelId,currentProductObj,date){

let productCycles=
currentProductObj?.cyclesByModel?.[modelId] ||
currentProductObj?.cycles ||
null;

if(productCycles){
return productCycles;
}

return getAvailableCycles(
modelId,
date
) || [];

}


function getRecentRunCandidates(
modelId,
baseDate=new Date(),
lookbackHours=NOW_LOOKBACK_HOURS,
maxCandidates=NOW_MAX_CANDIDATES
){

let candidates=[];

let base=new Date(baseDate.getTime());
base.setUTCMinutes(0,0,0);

for(let i=0;i<=lookbackHours;i++){

let d=new Date(
base.getTime()-i*60*60*1000
);

let dateOnly=parseDateOnly(
formatDateInputFromUTCParts(d)
);

let cycles=getCyclesForSelection(
modelId,
getCurrentProduct(),
dateOnly
);

let cycleHour=d.getUTCHours();

if(!cycles.includes(cycleHour)){
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


function setRunControlsToUTC(runUTC){

setControlsFromUTCDate(
runUTC,
timeMode
);

populateHours(runUTC);

}


async function jumpLatestAvailableForCurrentSelection({
silent=false
}={}){

let searchId=++latestSearchSeq;

setViewerLoading(true,'최신 자료 검색 중');

try{

let candidates=getRecentRunCandidates(
currentModel,
new Date(),
NOW_LOOKBACK_HOURS,
NOW_MAX_CANDIDATES
);

for(let runUTC of candidates){

if(searchId!==latestSearchSeq){
return false;
}

let result=await currentSelectionExistsAtRun(
runUTC
);

if(result.exists){

setRunControlsToUTC(runUTC);

refreshView({
updateCategories:false,
updateProducts:true,
updateHours:false,
resetSlider:true,
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

updateChart();

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

setViewerLoading(false);

}

}




function switchTimeMode(nextMode){

latestSearchSeq++;
clearTimeout(autoCheckTimer);

if(timeMode===nextMode){
return;
}

let selectedUTC=getSelectedUTCDate();
let currentIndex=Number(slider.value || 0);

timeMode=nextMode;

kstBtn.classList.toggle('active',timeMode==='KST');
utcBtn.classList.toggle('active',timeMode==='UTC');

setControlsFromUTCDate(selectedUTC,timeMode);
populateHours(selectedUTC);

slider.value=String(
Math.max(
0,
Math.min(currentIndex,(currentForecastList.length || 1)-1)
)
);

updateForecastLabel();
refreshForecastTimelineLabels();

}


function handleCategoryChange(){

let previousForecastHour=getSelectedForecastHour();

if(getActiveModelSpecificProductCategory()[currentModel]){
return;
}

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
새 category + 새 product 기준으로 지원 가능한 모델로 이동
*/
enforceModelRestrictionForCurrentCategory();

populateProductCategories();

refreshView({
updateCategories:false,
updateProducts:true,
updateHours:true,
resetSlider:true,
preserveForecastHour:previousForecastHour,
updateChartAfter:true
});

}


function handleProductChange(event){

let previousForecastHour=getSelectedForecastHour();

if(!event.target.value){
return;
}

currentProduct=event.target.value;

applyModelSwitchForCurrentProduct();
enforceModelAllowedForCurrentSelection();

refreshView({
updateCategories:false,
updateProducts:true,
updateHours:true,
resetSlider:true,
preserveForecastHour:previousForecastHour,
updateChartAfter:true
});

}


function bindEvents(){

productCategory.onchange=handleCategoryChange;
productSelect.onchange=handleProductChange;

slider.addEventListener('input',()=>{

if(slider.disabled){
return;
}

updateForecastLabel();
displayCurrentForecastImage();

});

document.addEventListener('keydown',e=>{

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

runDate.onchange=()=>{
latestSearchSeq++;
clearTimeout(autoCheckTimer);
populateHours();
refreshView({
  updateCategories:false,
  updateProducts:true,
  updateHours:false,
  resetSlider:true,
  updateChartAfter:true
});
};

runHour.onchange=()=>{
latestSearchSeq++;
clearTimeout(autoCheckTimer);
refreshView({
  updateCategories:false,
  updateProducts:true,
  updateHours:false,
  resetSlider:true,
  updateChartAfter:true
});
};

kstBtn.onclick=()=>switchTimeMode('KST');
utcBtn.onclick=()=>switchTimeMode('UTC');
nowBtn.onclick=()=>{

jumpLatestAvailableForCurrentSelection({
silent:false
});

};

}


function validateCatalog(){

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
let editCategories=getSafeGlobal("EDIT_CATEGORIES",[]);

let hazardProducts=getSafeGlobal("HAZARD_PRODUCTS",[]);
let ensembleProducts=getSafeGlobal("ENSEMBLE_PRODUCTS",[]);
let analysisProducts=getSafeGlobal("ANALYSIS_PRODUCTS",[]);
let editProducts=getSafeGlobal("EDIT_PRODUCTS",[]);

[...hazardCategories,...ensembleCategories,...analysisCategories,...editCategories].forEach(c=>{
if(c && c.id){
categoryIds.add(c.id);
}
});

let allProducts=[
...(PRODUCTS || []),
...hazardProducts,
...ensembleProducts,
...analysisProducts,
...editProducts
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

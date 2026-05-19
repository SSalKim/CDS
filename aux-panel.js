/* Auxiliary selector panel helpers. Depends on app.js globals at call time. */

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

invalidateSelectionAsyncWork({latest:false});
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

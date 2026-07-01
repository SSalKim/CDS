/* Model groups, visibility, and model button rendering. Depends on app.js globals at call time. */

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
label:'분석모델',
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
['obs_upper','OBS_UPPER'],
['sat_gk2a','SAT_GK2A'],
['usst','USST']
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


const COLLAPSIBLE_MODEL_GROUP_IDS=new Set([
'ended',
'ended_ens',
'ended_analysis'
]);

const collapsedModelGroupState={};

function isCollapsibleModelGroup(group){

return COLLAPSIBLE_MODEL_GROUP_IDS.has(group.id);

}

function modelGroupHasCurrentSelection(group){

let ids=group.models.map(model=>model[0]);

if(ids.includes(currentModel)){
return true;
}

if(modelCompareMode){
return compareModels.some(modelId=>ids.includes(modelId));
}

return false;

}

function isModelGroupCollapsed(group){

if(!isCollapsibleModelGroup(group)){
return false;
}

if(modelGroupHasCurrentSelection(group)){
return false;
}

return collapsedModelGroupState[group.id]!==false;

}

function toggleModelGroupCollapsed(groupId){

collapsedModelGroupState[groupId]=!(collapsedModelGroupState[groupId]!==false);
renderModels();

}

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

function applyModelButtonVisualState(button,{selected=false,available=false,compareSelected=false}={}){
button.style.opacity='';
button.style.cursor='pointer';
button.style.pointerEvents='auto';

if(selected || compareSelected){
button.style.color='#ffffff';
button.style.background='linear-gradient(135deg,#1d4ed8 0%,#2563eb 48%,#38bdf8 100%)';
button.style.borderColor='#1d4ed8';
button.style.boxShadow='0 8px 18px rgba(37,99,235,0.26)';
button.style.fontWeight='700';
return;
}

if(available){
button.style.color='#0f172a';
button.style.background='#dbeafe';
button.style.borderColor='#93c5fd';
button.style.boxShadow='0 1px 4px rgba(59,130,246,0.18)';
button.style.fontWeight='650';
return;
}

button.style.color='#111827';
button.style.background='#ffffff';
button.style.borderColor='#d1d5db';
button.style.boxShadow='none';
button.style.fontWeight='500';
}


function getCategoryIdForModelButtonFallback(modelId,categoryId){
let nextCategory=categoryId;

if(isForecastCatalog()){
let redirects=getActiveCategoryRedirectByModel()[modelId];
if(redirects && redirects[nextCategory]){
nextCategory=redirects[nextCategory];
}
}

return nextCategory;
}


function findProductFallbackForModel(modelId){
let categories=getSelectableCategories().filter(c=>c && c.id);
let currentCategory=getBaseVisibleCategory();
let orderedCategories=[
currentCategory,
...categories.map(c=>c.id).filter(id=>id!==currentCategory)
].filter(Boolean);

for(let categoryId of orderedCategories){
let targetCategory=getCategoryIdForModelButtonFallback(modelId,categoryId);

if(!isCategoryAllowedByModelRestriction(targetCategory,modelId)){
continue;
}

let product=getProductsInCategory(targetCategory).find(p=>
productSupportsModel(p,modelId)
);

if(product){
return {categoryId:targetCategory,productId:product.id};
}
}

return null;
}


function switchSelectionToModelSupportedProduct(modelId){
let fallback=findProductFallbackForModel(modelId);

if(!fallback){
return false;
}

if(productCategory){
productCategory.value=fallback.categoryId;
}
currentProduct=fallback.productId;
return true;
}


function renderModels(){

modelGrid.innerHTML='';

let groups=getVisibleModelGroups().filter(
group=>!group.hidden
);

let utilityLaunchers=[];

if(typeof renderRadarAnalysisLauncher==='function'){
utilityLaunchers.push(renderRadarAnalysisLauncher());
}

if(typeof renderTyphoonGuidanceLauncher==='function'){
utilityLaunchers.push(renderTyphoonGuidanceLauncher());
}

let compareToggle=renderModelCompareToggle();
if(compareToggle){
modelGrid.appendChild(compareToggle);
}

groups.forEach(group=>{

let section=document.createElement('div');
section.className='model-section'+(isCollapsibleModelGroup(group)?' collapsible-model-section':'');
section.dataset.modelGroup=group.id;

let collapsed=isModelGroupCollapsed(group);

let title;

if(isCollapsibleModelGroup(group)){

title=document.createElement('button');
title.type='button';
title.className='model-section-title model-section-toggle';
title.setAttribute('aria-expanded',String(!collapsed));
title.textContent=`${group.label} ${collapsed?'▾':'▴'}`;
title.onclick=()=>toggleModelGroupCollapsed(group.id);

}
else{

title=document.createElement('div');
title.className='model-section-title';
title.textContent=group.label;

}

let buttons=document.createElement('div');
buttons.className='model-button-list'+(collapsed?' hidden':'');

if(!collapsed){

group.models.forEach(m=>{

let modelId=m[0];
let label=m[1];
let modelAllowed=getModelButtonAllowed(modelId);
let compareSelected=modelCompareMode && compareModels.includes(modelId);
let modelSelected=!modelCompareMode && modelId===currentModel;

let btn=document.createElement('button');
btn.type='button';
btn.className=
'model-cell'+
(modelSelected ? ' active' : '')+
(compareSelected ? ' compare-selected' : '')+
(modelAllowed ? ' available' : ' unsupported-clickable');

btn.disabled=false;
btn.setAttribute('aria-disabled','false');
btn.title=modelAllowed
?'현재 산출물을 지원하는 모델입니다.'
:'현재 산출물은 이 모델을 지원하지 않습니다. 클릭하면 지원 산출물로 자동 전환합니다.';
btn.textContent=label;

applyModelButtonVisualState(btn,{
selected:modelSelected,
available:modelAllowed,
compareSelected
});

btn.onclick=()=>{

if(modelCompareMode){
if(!modelAllowed){
showViewerNotice('현재 산출물은 이 모델을 지원하지 않습니다.');
return;
}
toggleCompareModel(modelId);
return;
}

let previousForecastHour=getSelectedForecastHour();
let needsProductSwitch=!modelAllowed;

invalidateSelectionAsyncWork();
currentModel=modelId;

if(needsProductSwitch){
let switched=switchSelectionToModelSupportedProduct(modelId);
if(switched && typeof showSelectionToast==='function'){
showSelectionToast('현재 산출물은 이 모델을 지원하지 않습니다. 지원하는 산출물로 자동 전환합니다.');
}
else if(!switched){
showViewerNotice('이 모델에서 지원하는 산출물을 찾지 못했습니다.');
}
}
else{
applyCategoryRedirectForCurrentModel();
}

refreshViewAfterSelectionChange({
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

}

section.appendChild(title);
section.appendChild(buttons);
modelGrid.appendChild(section);

});

utilityLaunchers.filter(Boolean).forEach(launcher=>modelGrid.appendChild(launcher));

let modelBox=modelGrid.closest('.model-box');

if(modelBox){
modelBox.classList.toggle('hidden',modelGrid.children.length===0);
}

}

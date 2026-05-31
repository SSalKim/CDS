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

function renderModels(){

modelGrid.innerHTML='';

let groups=getVisibleModelGroups().filter(
group=>!group.hidden
);

let radarLauncher=null;

if(typeof renderRadarAnalysisLauncher==='function'){
radarLauncher=renderRadarAnalysisLauncher();
}

let compareToggle=renderModelCompareToggle();
if(compareToggle){
modelGrid.appendChild(compareToggle);
}

groups.forEach(group=>{

let section=document.createElement('div');
section.className='model-section'+(isCollapsibleModelGroup(group)?' collapsible-model-section':'');

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

let btn=document.createElement('button');
btn.type='button';
btn.className=
'model-cell'+
(!modelCompareMode && modelId===currentModel ? ' active' : '')+
(compareSelected ? ' compare-selected' : '')+
(!modelAllowed ? ' disabled' : '');

btn.disabled=!modelAllowed;
btn.textContent=label;

btn.onclick=()=>{

if(!modelAllowed){
return;
}

if(modelCompareMode){
toggleCompareModel(modelId);
return;
}

let previousForecastHour=getSelectedForecastHour();

invalidateSelectionAsyncWork();
currentModel=modelId;

applyCategoryRedirectForCurrentModel();

let categoryId=getCurrentCategory();

let currentProductObject=getProductByIdInCategory(
categoryId,
currentProduct
);

if(
!currentProductObject ||
!productSupportsModel(currentProductObject,currentModel)
){

let fallbackProduct=getProductsInCategory(categoryId).find(
p=>productSupportsModel(p,currentModel)
);

if(fallbackProduct){
currentProduct=fallbackProduct.id;
}

}

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

}

section.appendChild(title);
section.appendChild(buttons);
modelGrid.appendChild(section);

});

if(radarLauncher){
modelGrid.appendChild(radarLauncher);
}

let modelBox=modelGrid.closest('.model-box');

if(modelBox){
modelBox.classList.toggle('hidden',modelGrid.children.length===0);
}

}

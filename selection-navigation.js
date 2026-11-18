/* User-initiated selection changes are committed only after confirmation. */
let selectionConfirmation=null;

function createSelectionCancelHandler({runUTC=getSelectedUTCDate()}={}){
let previous={
model:currentModel,product:currentProduct,category:getCurrentCategory(),aux:currentAuxValue,
runUTC:new Date(runUTC.getTime()),forecastHour:getSelectedTimelineHourForPreserve(),
hours:[...currentForecastList],states:[...forecastLoadStates],cache:new Map(forecastImageCache),
slider:{value:slider.value,min:slider.min,max:slider.max,step:slider.step,disabled:slider.disabled},
nodes:[...chartImages.childNodes],className:chartImages.className,style:chartImages.getAttribute('style'),
status:modelStatus.textContent,statusClass:modelStatus.className,
scrollLeft:viewerWrap?.scrollLeft || 0,scrollTop:viewerWrap?.scrollTop || 0
};
return async()=>{
invalidateSelectionAsyncWork();
currentModel=previous.model;currentProduct=previous.product;currentAuxValue=previous.aux;
productCategory.value=previous.category;
setRunControlsToUTCAllowUnsupported(previous.runUTC);
let key=getSelectionNavigationKey();
await refreshView({updateCategories:true,updateProducts:true,updateHours:false,
resetSlider:true,preserveForecastHour:previous.forecastHour,updateChartAfter:false});
if(key!==getSelectionNavigationKey()) return;
setCurrentForecastList(previous.hours);
setForecastLoadStates(previous.states);
resetForecastImageCache();
for(let [index,value] of previous.cache) setForecastImageCacheEntry(index,value);
Object.assign(slider,previous.slider);
updateForecastLabel();
renderForecastTimeline();
chartImages.replaceChildren(...previous.nodes);
chartImages.className=previous.className;
if(previous.style===null) chartImages.removeAttribute('style');
else chartImages.setAttribute('style',previous.style);
modelStatus.textContent=previous.status;modelStatus.className=previous.statusClass;
setViewerLoading(false);
if(viewerWrap){viewerWrap.scrollLeft=previous.scrollLeft;viewerWrap.scrollTop=previous.scrollTop;}
};
}

function openViewerDialog(dialog,{maxWidth=420,onClose=()=>{}}={}){
if(selectionConfirmation) selectionConfirmation(false);
stopCompareAnimation();
let previousFocus=document.activeElement;
document.body.appendChild(dialog);
let viewer=document.querySelector('.viewer-wrap');
viewer?.classList.add('selection-blurred');
let position=()=>{
let bounds=viewer?.getBoundingClientRect();
let width=document.documentElement.clientWidth;
let left=Math.max(12,bounds?.left || 0);
let right=Math.min(width-12,bounds?.right || width);
let top=Math.max(12,bounds?.top || 0);
let bottom=Math.min(innerHeight-12,bounds?.bottom || innerHeight);
dialog.style.width=Math.min(maxWidth,width-32,Math.max(240,right-left-16))+'px';
let height=dialog.getBoundingClientRect().height;
let x=Math.min(width-dialog.offsetWidth/2-12,Math.max(dialog.offsetWidth/2+12,(left+right)/2));
let y=Math.min(innerHeight-height/2-12,Math.max(height/2+12,(top+bottom)/2));
dialog.style.left=x+'px';
dialog.style.top=y+'px';
};
let done=false;
let finish=accepted=>{
if(done) return;
done=true;
selectionConfirmation=null;
viewer?.classList.remove('selection-blurred');
window.removeEventListener('resize',position);
document.removeEventListener('scroll',position,true);
dialog.close();
dialog.remove();
previousFocus?.focus?.({preventScroll:true});
onClose(accepted);
};
selectionConfirmation=finish;
dialog.addEventListener('cancel',event=>{event.preventDefault();finish(false);});
dialog.showModal();
position();
window.addEventListener('resize',position);
document.addEventListener('scroll',position,true);
return {close:finish,position};
}

function confirmSelectionChange(message,{notice=false}={}){
let dialog=document.createElement('dialog');
dialog.className='selection-confirmation';
dialog.setAttribute('aria-label',notice?'안내':'자료 전환 확인');
dialog.setAttribute('aria-describedby','selectionConfirmationMessage');
let body=document.createElement('p');
body.id='selectionConfirmationMessage';body.textContent=message;
let actions=document.createElement('div');
actions.className='selection-confirmation-actions';
let confirm=document.createElement('button');
confirm.type='button';confirm.className='selection-confirmation-accept';confirm.textContent='확인';
dialog.append(body,actions);
return new Promise(resolve=>{
let modal=openViewerDialog(dialog,{onClose:resolve});
if(!notice){
let cancel=document.createElement('button');
cancel.type='button';cancel.textContent='취소';cancel.onclick=()=>modal.close(false);
actions.append(cancel);cancel.focus();
}
actions.append(confirm);confirm.onclick=()=>modal.close(true);
if(notice) confirm.focus();
modal.position();
});
}

function getSelectionNavigationKey(){
return JSON.stringify([currentMainMenu,currentModel,currentProduct,getCurrentCategory(),
getSelectedUTCDate().getTime(),modelCompareMode,compareModels]);
}

function modelSupportsSelectionProduct(modelId,product){
let restriction=getSelectionRestrictionForProduct(product);
return isCategoryAllowedByModelRestriction(product.category,modelId) &&
(!restriction || restriction.allowedModels.includes(modelId)) && productSupportsModel(product,modelId);
}

function getSuggestedModelForProduct(product){
let supported=getVisibleModelsSupportingProduct(product).filter(modelId=>modelSupportsSelectionProduct(modelId,product));
let preferred=getSelectionRestrictionForProduct(product)?.fallbackModel;
return [preferred,'kim_gdps',...supported].find(modelId=>supported.includes(modelId)) || null;
}

function getModelButtonLabel(modelId){
return modelGroups.flatMap(group=>group.models).find(model=>model[0]===modelId)?.[1] ||
MODELS[modelId]?.timelineName || modelId;
}

function modelRunIsUnsupported(modelId,product=getCurrentProduct(),runUTC=getSelectedUTCDate()){
if(currentMainMenu!=='forecast') return false;
let date=parseDateOnly(formatDateInputFromUTCParts(runUTC));
return !cyclesIncludeValue(getCyclesForSelection(modelId,product,date),getCycleValueFromDate(runUTC));
}

function getMostRecentSupportedRun(modelId,product,runUTC){
for(let days=0;days<8;days++){
let day=new Date(runUTC.getTime());
day.setUTCHours(0,0,0,0);
day.setUTCDate(day.getUTCDate()-days);
let candidates=(getCyclesForSelection(modelId,product,day) || []).map(cycle=>
new Date(day.getTime()+Number(cycle)*3600000)).filter(date=>date<=runUTC);
candidates.sort((a,b)=>b-a);
for(let date of candidates){
if(getEffectiveModelStatus(modelId,date,product).available) return date;
}
}
return null;
}

async function requestModelSelection(modelId){
if(typeof missingRunPromptKey!=='undefined') missingRunPromptKey='';
if(modelCompareMode && compareModels.includes(modelId)){
toggleCompareModel(modelId);
return;
}
let key=getSelectionNavigationKey();
let isCurrent=()=>key===getSelectionNavigationKey();
let product=getCurrentProduct();
let fallback=null;
if(!getModelButtonAllowed(modelId)){
fallback=findProductFallbackForModel(modelId);
if(!fallback){showViewerNotice('이 모델에서 지원하는 산출물을 찾지 못했습니다.');return;}
product=getProductByIdInCategory(fallback.categoryId,fallback.productId);
if(!await confirmSelectionChange(`이 산출물에서는 지원하지 않는 모델입니다.\n지원되는 산출물(${getCurrentProductLabel(product)})로 이동할까요?`) || !isCurrent()) return;
}
let runUTC=getSelectedUTCDate();
let targetRun=null;
if(modelRunIsUnsupported(modelId,product,runUTC)){
targetRun=getMostRecentSupportedRun(modelId,product,runUTC);
if(!targetRun){showViewerNotice('이 모델에서 지원하는 자료시각을 찾지 못했습니다.');return;}
if(!await confirmSelectionChange('해당 시간대에는 생산되지 않는 모델입니다.\n가장 최근 자료의 시간대로 이동할까요?') || !isCurrent()) return;
}
if(modelCompareMode && compareModels.length>=COMPARE_MAX_MODELS){
showViewerNotice(`모델 비교는 최대 ${COMPARE_MAX_MODELS}개까지 선택할 수 있습니다.`);return;
}
let previousForecastHour=getSelectedTimelineHourForPreserve();
let cancelSelection=createSelectionCancelHandler();
invalidateSelectionAsyncWork();
currentModel=modelId;
if(fallback){productCategory.value=fallback.categoryId;currentProduct=fallback.productId;}
else applyCategoryRedirectForCurrentModel();
if(modelCompareMode){compareModels.push(modelId);normalizeCompareModels();}
if(targetRun) setRunControlsToUTCAllowUnsupported(targetRun);
refreshViewAfterSelectionChange({updateCategories:true,updateProducts:true,updateHours:!targetRun,
resetSlider:true,preserveForecastHour:previousForecastHour,updateChartAfter:true,cancelSelection});
}

async function confirmProductModelSwitch(product){
if(modelSupportsSelectionProduct(currentModel,product)) return {accepted:true,modelId:currentModel};
let modelId=getSuggestedModelForProduct(product);
if(!modelId){showViewerNotice('이 산출물을 지원하는 모델을 찾지 못했습니다.');return {accepted:false};}
let accepted=await confirmSelectionChange(`이 모델에서는 지원하지 않는 산출물입니다.\n지원되는 모델(${getModelButtonLabel(modelId)})로 이동할까요?`);
return {accepted,modelId};
}

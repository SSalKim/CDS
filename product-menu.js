/* Product category/product option helpers and rendering. Depends on app.js globals at call time. */

const ANALYSIS_OBSERVATION_MODEL_IDS=new Set(['obs_upper','usst','sat_gk2a']);
const ANALYSIS_ALWAYS_ACTIVE_CATEGORY_IDS=new Set(['skewob','skewds','ssta']);

function isAnalysisCatalogActive(){
return typeof currentMainMenu!=='undefined' && currentMainMenu==='analysis';
}

function isAnalysisObservationModel(modelId=currentModel){
return isAnalysisCatalogActive() && ANALYSIS_OBSERVATION_MODEL_IDS.has(modelId);
}

function isAnalysisAlwaysActiveCategory(categoryId){
return isAnalysisCatalogActive() && ANALYSIS_ALWAYS_ACTIVE_CATEGORY_IDS.has(categoryId);
}

function suppressAnalysisObservationUnsupportedStyling(categoryId=getCurrentCategory(),modelId=currentModel){
return isAnalysisAlwaysActiveCategory(categoryId) || isAnalysisObservationModel(modelId);
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


function getVisibleModelsSupportingProduct(product){

let supported=[];

for(let group of getVisibleModelGroups()){
for(let model of group.models){
let modelId=model[0];

if(productSupportsModel(product,modelId)){
supported.push(modelId);
}
}
}

return supported;

}


function canSelectProductByModelSwitch(product){
return getVisibleModelsSupportingProduct(product).length>0;
}


function isProductSelectableInDropdown(product){
return !!product && product.type!=="header";
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

function isProductCategoryUnsupportedForModel(categoryId,modelId=currentModel){

if(getCurrentCatalogKey()==="empty" || categoryId==="empty"){
return false;
}

if(
(
getActiveDisabledProductCategoriesByModel()[modelId] || []
).includes(categoryId)
){
return true;
}

if(!isCategoryAllowedByModelRestriction(categoryId,modelId)){
return true;
}

return !categoryHasSupportedProduct(categoryId,modelId);

}

/*
CDS 3.4에서는 산출물 선택을 우선한다.
1차/2차 드롭다운은 클릭을 막지 않고, 현재 모델 미지원 항목만 회색으로 표시한다.
*/
function isProductCategoryDisabled(){
return false;
}


function getFirstEnabledProductCategory(){
return getSelectableCategories()[0] || null;
}


function applyModelSwitchForCurrentProduct(){
return enforceModelAllowedForCurrentSelection();
}


function markOptionSupported(option,message='현재 모델에서 바로 표출 가능한 산출물입니다.'){
option.classList.add('supported-option');
option.dataset.supported='true';
option.style.color='#0f172a';
option.style.backgroundColor='#dbeafe';
option.style.fontWeight='400';
option.title=message;
}


function markOptionNeutral(option,message=''){
option.classList.remove('supported-option','unsupported-option');
delete option.dataset.supported;
delete option.dataset.unsupported;
option.style.color='#111827';
option.style.backgroundColor='';
option.style.fontWeight='400';
option.title=message;
}


function markOptionUnsupported(option,message){
option.classList.add('unsupported-option');
option.dataset.unsupported='true';
option.style.color='#111827';
option.style.backgroundColor='';
option.style.fontWeight='400';
option.title=message;
}


function isCategoryVisuallySupportedForDropdown(categoryId,modelId=currentModel){
let categoryUnsupported=isProductCategoryUnsupportedForModel(categoryId,modelId);
return !categoryUnsupported || suppressAnalysisObservationUnsupportedStyling(categoryId,modelId);
}


function isProductVisuallySupportedForDropdown(product,modelId=currentModel){
if(!product || product.type==='header'){
return false;
}

return productSupportsModel(product,modelId) || suppressAnalysisObservationUnsupportedStyling(product.category,modelId);
}

let productCategoryWidthMeasureCanvas=null;

function syncMobileProductCategoryWidth(){

let row=document.querySelector('.toolbar-product-row');

if(!row || !productCategory){
return;
}

let isMobilePortrait=typeof window.matchMedia==='function' &&
window.matchMedia('(max-width: 700px) and (orientation: portrait)').matches;

if(!isMobilePortrait){
row.style.removeProperty('--product-category-width');
return;
}

let option=productCategory.options[productCategory.selectedIndex];
let text=option?.textContent?.trim() || '';
let style=window.getComputedStyle(productCategory);

productCategoryWidthMeasureCanvas ||= document.createElement('canvas');
let context=productCategoryWidthMeasureCanvas.getContext('2d');

if(!context){
return;
}

context.font=`${style.fontWeight} ${style.fontSize} ${style.fontFamily}`;

let padding=(parseFloat(style.paddingLeft)||0)+(parseFloat(style.paddingRight)||0);
let desiredWidth=Math.ceil(context.measureText(text).width+padding+26);
let rowStyle=window.getComputedStyle(row);
let gap=parseFloat(rowStyle.columnGap)||2;
let controlsWidth=81;
let minimumCategoryWidth=72;
let minimumProductWidth=96;
let maximumCategoryWidth=Math.max(
minimumCategoryWidth,
row.clientWidth-controlsWidth-(gap*2)-minimumProductWidth
);
let categoryWidth=Math.max(
minimumCategoryWidth,
Math.min(desiredWidth,maximumCategoryWidth)
);

row.style.setProperty('--product-category-width',`${categoryWidth}px`);

}


function headerHasSupportedItems(items,headerIndex,isHeaderFn,isSupportedFn){
for(let i=headerIndex+1;i<items.length;i++){
let item=items[i];
if(isHeaderFn(item)){
break;
}
if(isSupportedFn(item)){
return true;
}
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

categories.forEach((c,index)=>{

let o=document.createElement('option');

if(isCategoryHeader(c)){

o.textContent=c.name || c.label || '────────';
o.disabled=true;
o.className='group-header';

if(headerHasSupportedItems(
categories,
index,
isCategoryHeader,
item=>isCategoryVisuallySupportedForDropdown(item.id,currentModel)
)){
markOptionSupported(o,'이 구역에 현재 선택 조건에서 표출 가능한 산출물이 있습니다.');
}
else{
markOptionNeutral(o);
}

productCategory.appendChild(o);
return;

}

o.value=c.id;
o.textContent=c.name;

let categoryUnsupported=isProductCategoryUnsupportedForModel(c.id,currentModel);

if(categoryUnsupported && !suppressAnalysisObservationUnsupportedStyling(c.id,currentModel)){
markOptionUnsupported(
o,
'현재 모델에서 이 분류의 산출물을 지원하지 않습니다. 선택하면 지원 모델로 자동 전환됩니다.'
);
}
else{
markOptionSupported(o);
}

productCategory.appendChild(o);

});

productCategory.value=prevCategory;

if(!productCategory.value && selectableCategories.length){
productCategory.value=selectableCategories[0].id;
}

productCategory.dataset.selectedCategory=productCategory.value;

syncMobileProductCategoryWidth();

}

function renderProductList(){

productSelect.innerHTML='';

let cat=getCurrentCategory();
let products=getActiveProducts();
let categoryProducts=products.filter(p=>p.category===cat);

categoryProducts.forEach((p,index)=>{

let o=document.createElement('option');

if(p.type==='header'){
o.textContent=p.label;
o.disabled=true;
o.className='group-header';

if(headerHasSupportedItems(
categoryProducts,
index,
item=>item.type==='header',
item=>isProductVisuallySupportedForDropdown(item,currentModel)
)){
markOptionSupported(o,'이 구역에 현재 선택 조건에서 표출 가능한 산출물이 있습니다.');
}
else{
markOptionNeutral(o);
}

productSelect.appendChild(o);
return;
}

o.value=p.id;
o.textContent=p.label;

let productUnsupported=!productSupportsModel(p,currentModel);

if(productUnsupported && !suppressAnalysisObservationUnsupportedStyling(p.category,currentModel)){
markOptionUnsupported(
o,
'현재 모델에서는 지원하지 않는 산출물입니다. 선택하면 지원 모델로 자동 전환됩니다.'
);
}
else{
markOptionSupported(o);
}

productSelect.appendChild(o);

});

let defaultProduct=getDefaultProductForCategory(cat);
let currentProductObject=products.find(
p=>p.category===cat && p.id===currentProduct && p.type!=='header'
);

if(getProductCategoryUIConfig().hideProductSelect || !currentProductObject){
if(defaultProduct){
currentProduct=defaultProduct.id;
}
else{
let firstProduct=getProductsInCategory(cat)[0];
currentProduct=firstProduct?.id || '';
}
}

productSelect.value=currentProduct;

}

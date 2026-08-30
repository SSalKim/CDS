/* Catalog, product, and model selection helpers. Depends on app.js globals at call time. */

const FORECAST_CATEGORY_PRODUCT_TRANSITIONS={
"hkor:asia":{
acptot:"surfce"
}
};


function resolveProductIdForCategoryTransition(fromCategory,toCategory,productId){

if(!isForecastCatalog()){
return productId;
}

return (
FORECAST_CATEGORY_PRODUCT_TRANSITIONS[`${fromCategory}:${toCategory}`]?.[productId] ||
productId
);

}

function syncProductCategoryVisibility(){
productCategory.classList.remove('hidden');
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

function getBaseVisibleCategory(){

let selectableCategories=getSelectableCategories();

return (
productCategory.value ||
selectableCategories[0]?.id ||
'empty'
);

}


function getCategoryIdForModelFiltering(modelId){

let categoryId=getBaseVisibleCategory();

if(isForecastCatalog()){
let redirects=getActiveCategoryRedirectByModel()[modelId];

if(redirects && redirects[categoryId]){
categoryId=redirects[categoryId];
}
}

return categoryId;

}


function getProductByIdInCategory(categoryId,productId){

return getActiveProducts().find(
p=>
p.category===categoryId &&
p.id===productId &&
p.type!=="header"
);

}


function getCategoryRestrictionForModelFiltering(modelId){

let categoryId=getCategoryIdForModelFiltering(modelId);
let product=getProductByIdInCategory(categoryId,currentProduct);
let productId=product?.id || currentProduct;
let exactKey=`${categoryId}:${productId}`;
let categoryKey=`${categoryId}:*`;

let selectionRestrictions=getActiveSelectionModelRestrictions();
let categoryRestrictions=getActiveCategoryModelRestrictions();

return (
selectionRestrictions[exactKey] ||
selectionRestrictions[categoryKey] ||
categoryRestrictions[categoryId] ||
null
);

}


function modelUsesSpecificProductCategory(){
return false;
}


function isModelAllowedByCurrentCategory(modelId){

let categoryId=getCategoryIdForModelFiltering(modelId);
let restriction=getCategoryRestrictionForModelFiltering(modelId);

if(
restriction &&
!restriction.allowedModels.includes(modelId)
){
return false;
}

let product=getProductByIdInCategory(
categoryId,
currentProduct
);

if(!product){
return false;
}

return productSupportsModel(product,modelId);

}


function getPreferredAllowedVisibleModelIdForCurrentSelection(){

let restriction=getCurrentCategoryRestriction();
let preferred=restriction?.fallbackModel;

if(
preferred &&
isModelVisibleInCurrentMenu(preferred) &&
isModelAllowedByCurrentCategory(preferred)
){
return preferred;
}

return getFirstAllowedVisibleModelIdForCurrentSelection();

}


function enforceModelRestrictionForCurrentCategory({notify=false}={}){
return enforceModelAllowedForCurrentSelection({notify});
}


function shouldSuppressAnalysisObservationNotice(){
if(typeof currentMainMenu==='undefined' || currentMainMenu!=='analysis'){
return false;
}

if(
typeof suppressAnalysisObservationUnsupportedStyling==='function' &&
suppressAnalysisObservationUnsupportedStyling(getBaseVisibleCategory(),currentModel)
){
return true;
}

return false;
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


function enforceModelAllowedForCurrentSelection({notify=false}={}){

if(isModelAllowedByCurrentCategory(currentModel)){
return false;
}

let fallback=getPreferredAllowedVisibleModelIdForCurrentSelection();

if(!fallback){
return false;
}

currentModel=fallback;

if(
notify &&
typeof showSelectionToast==='function' &&
!shouldSuppressAnalysisObservationNotice()
){
showSelectionToast('해당 모델에서는 지원하지 않는 자료입니다.');
}

return true;

}


function getCurrentProduct(){

return getActiveProducts().find(
p=>p.category===getCurrentCategory() && p.id===currentProduct
);

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

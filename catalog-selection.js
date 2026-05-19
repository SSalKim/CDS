/* Catalog, product, and model selection helpers. Depends on app.js globals at call time. */

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

function getBaseVisibleCategory(){

let selectableCategories=getSelectableCategories();

return (
productCategory.value ||
selectableCategories[0]?.id ||
'empty'
);

}


function getCategoryIdForModelFiltering(modelId){

/*
초단기처럼 모델 전용 category가 있는 경우:
대상 모델 기준의 전용 category를 사용한다.
예: kim_klfs / um_klfs / um_vdps → klfs_vdps
*/
if(
isForecastCatalog() &&
getActiveModelSpecificProductCategory()[modelId]
){
return getActiveModelSpecificProductCategory()[modelId];
}

/*
일반 모델로 돌아가는 경우:
현재 currentModel이 초단기더라도 getCurrentCategory()를 쓰면 klfs_vdps가 반환된다.
따라서 숨겨져 있던 실제 1차 드롭다운 값(productCategory.value)을 기준으로 복귀해야 한다.
*/
let categoryId=getBaseVisibleCategory();

/*
모델별 category redirect 적용.
예: kim_ldps에서 asia → hkor
*/
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

let product=getProductByIdInCategory(
categoryId,
currentProduct
);

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


function modelUsesSpecificProductCategory(modelId){

return !!(
isForecastCatalog() &&
getActiveModelSpecificProductCategory()[modelId]
);

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

/*
초단기/VDAPS처럼 모델 전용 category를 쓰는 모델은
현재 선택된 일반 산출물 ID에 묶이면 안 된다.
해당 전용 category 안에서 지원 산출물이 하나라도 있으면 선택 가능하게 둔다.
*/
if(modelUsesSpecificProductCategory(modelId)){
return categoryHasSupportedProduct(categoryId,modelId);
}

/*
일반 모델로 돌아가는 경우:
현재 currentProduct가 klfs_vdps 전용 product일 수 있다.
그 product가 일반 category에 없으면, 현재 product 기준으로 막지 말고
해당 category에서 지원 가능한 산출물이 하나라도 있는지만 본다.
*/
let product=getProductByIdInCategory(
categoryId,
currentProduct
);

if(!product){
return categoryHasSupportedProduct(categoryId,modelId);
}

/*
일반 상태에서는 현재 선택 산출물을 지원하는 모델만 활성화한다.
*/
if(!productSupportsModel(product,modelId)){
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

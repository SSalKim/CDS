/* Product category/product option helpers and rendering. Depends on app.js globals at call time. */

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

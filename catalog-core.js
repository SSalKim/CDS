/* Catalog metadata and active catalog accessors. Depends on app.js globals at call time. */

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

const MODEL_SPECIFIC_PRODUCT_CATEGORY={
kim_klfs:"klfs_vdps",
um_klfs:"klfs_vdps",
um_vdps:"klfs_vdps"
};

const PRODUCT_CATEGORY_UI_CONFIG={
isen:{
hideProductSelect:true
},
skew:{
hideProductSelect:true
}
};

const CATEGORY_MODEL_RESTRICTIONS={

lkor1:{
allowedModels:[
"kim_rdps",
"kim_ldps",
"um_ldps"
],
fallbackModel:"kim_ldps"
},

lkor2:{
allowedModels:[
"kim_rdps",
"kim_ldps",
"um_ldps"
],
fallbackModel:"kim_ldps"
},

nhem:{
allowedModels:[
"kim_gdps",
"um_gdps",
"ecmwf"
],
fallbackModel:"kim_gdps"
},

radm:{
allowedModels:[
"kim_gdps",
"um_gdps",
"ecmwf",
"kim_rdps",
"um_ldps"
],
fallbackModel:"kim_gdps"
},

isen:{
allowedModels:[
"kim_gdps",
"um_gdps",
"kim_rdps"
],
fallbackModel:"kim_gdps"
},

wtem1:{
allowedModels:[
"kim_gdps",
"um_gdps",
"ecmwf",
"kim_rdps",
"um_rdps",
"kim_ldps",
"um_ldps"
],
fallbackModel:"kim_gdps"
},

wtem2:{
allowedModels:[
"kim_gdps",
"um_gdps",
"ecmwf"
],
fallbackModel:"kim_gdps"
},

skew:{
allowedModels:[
"kim_gdps",
"um_gdps",
"ecmwf",
"kim_rdps",
"um_rdps",
"kwrf_rdps",
"kim_ldps",
"um_ldps"
],
fallbackModel:"kim_gdps"
},

city:{
allowedModels:[
"kim_gdps",
"um_gdps",
"ecmwf",
"kim_rdps",
"um_rdps",
"kwrf_rdps",
"kim_ldps",
"um_ldps"
],
fallbackModel:"kim_gdps"
}

};

const SELECTION_MODEL_RESTRICTIONS={

"city:long":{
allowedModels:[
"kim_gdps",
"um_gdps",
"ecmwf"
],
fallbackModel:"kim_gdps"
}

};

const CATEGORY_REDIRECT_BY_MODEL={
kim_ldps:{
asia:"hkor"
}
};

const DISABLED_PRODUCT_CATEGORIES_BY_MODEL={

};

const DEFAULT_PRODUCT_BY_CATEGORY={

asia:"gph500",
radm:"rmir"

};

/* 대메뉴별 catalog 설정 */
const CATALOG_CONFIG={

edit:{
  categories:()=>typeof EDIT_CATEGORIES!=='undefined'?EDIT_CATEGORIES:[],
  products:()=>typeof EDIT_PRODUCTS!=='undefined'?EDIT_PRODUCTS:[],
  productCategoryUi:()=>typeof EDIT_PRODUCT_CATEGORY_UI_CONFIG!=='undefined'?EDIT_PRODUCT_CATEGORY_UI_CONFIG:{},
  categoryModelRestrictions:()=>typeof EDIT_CATEGORY_MODEL_RESTRICTIONS!=='undefined'?EDIT_CATEGORY_MODEL_RESTRICTIONS:{},
  selectionModelRestrictions:()=>typeof EDIT_SELECTION_MODEL_RESTRICTIONS!=='undefined'?EDIT_SELECTION_MODEL_RESTRICTIONS:{},
  defaultProductByCategory:()=>typeof EDIT_DEFAULT_PRODUCT_BY_CATEGORY!=='undefined'?EDIT_DEFAULT_PRODUCT_BY_CATEGORY:{},
  modelSpecificProductCategory:{},
  categoryRedirectByModel:{},
  disabledProductCategoriesByModel:{}
},

analysis:{
  categories:()=>typeof ANALYSIS_CATEGORIES!=='undefined'?ANALYSIS_CATEGORIES:[],
  products:()=>typeof ANALYSIS_PRODUCTS!=='undefined'?ANALYSIS_PRODUCTS:[],
  productCategoryUi:()=>typeof ANALYSIS_PRODUCT_CATEGORY_UI_CONFIG!=='undefined'?ANALYSIS_PRODUCT_CATEGORY_UI_CONFIG:{},
  categoryModelRestrictions:()=>typeof ANALYSIS_CATEGORY_MODEL_RESTRICTIONS!=='undefined'?ANALYSIS_CATEGORY_MODEL_RESTRICTIONS:{},
  selectionModelRestrictions:()=>typeof ANALYSIS_SELECTION_MODEL_RESTRICTIONS!=='undefined'?ANALYSIS_SELECTION_MODEL_RESTRICTIONS:{},
  defaultProductByCategory:()=>typeof ANALYSIS_DEFAULT_PRODUCT_BY_CATEGORY!=='undefined'?ANALYSIS_DEFAULT_PRODUCT_BY_CATEGORY:{},
  modelSpecificProductCategory:{},
  categoryRedirectByModel:{},
  disabledProductCategoriesByModel:{}
},

forecast:{
  categories:()=>PRODUCT_CATEGORIES,
  products:()=>PRODUCTS,
  productCategoryUi:PRODUCT_CATEGORY_UI_CONFIG,
  categoryModelRestrictions:CATEGORY_MODEL_RESTRICTIONS,
  selectionModelRestrictions:SELECTION_MODEL_RESTRICTIONS,
  defaultProductByCategory:DEFAULT_PRODUCT_BY_CATEGORY,
  modelSpecificProductCategory:MODEL_SPECIFIC_PRODUCT_CATEGORY,
  categoryRedirectByModel:CATEGORY_REDIRECT_BY_MODEL,
  disabledProductCategoriesByModel:DISABLED_PRODUCT_CATEGORIES_BY_MODEL
},

hazard:{
  categories:()=>typeof HAZARD_CATEGORIES!=='undefined'?HAZARD_CATEGORIES:[],
  products:()=>typeof HAZARD_PRODUCTS!=='undefined'?HAZARD_PRODUCTS:[],
  productCategoryUi:()=>typeof HAZARD_PRODUCT_CATEGORY_UI_CONFIG!=='undefined'?HAZARD_PRODUCT_CATEGORY_UI_CONFIG:{},
  categoryModelRestrictions:()=>typeof HAZARD_CATEGORY_MODEL_RESTRICTIONS!=='undefined'?HAZARD_CATEGORY_MODEL_RESTRICTIONS:{},
  selectionModelRestrictions:()=>typeof HAZARD_SELECTION_MODEL_RESTRICTIONS!=='undefined'?HAZARD_SELECTION_MODEL_RESTRICTIONS:{},
  defaultProductByCategory:()=>typeof HAZARD_DEFAULT_PRODUCT_BY_CATEGORY!=='undefined'?HAZARD_DEFAULT_PRODUCT_BY_CATEGORY:{},
  modelSpecificProductCategory:{},
  categoryRedirectByModel:{},
  disabledProductCategoriesByModel:{}
},

ensemble:{
  categories:()=>typeof ENSEMBLE_CATEGORIES!=='undefined'?ENSEMBLE_CATEGORIES:[],
  products:()=>typeof ENSEMBLE_PRODUCTS!=='undefined'?ENSEMBLE_PRODUCTS:[],
  productCategoryUi:()=>typeof ENSEMBLE_PRODUCT_CATEGORY_UI_CONFIG!=='undefined'?ENSEMBLE_PRODUCT_CATEGORY_UI_CONFIG:{},
  categoryModelRestrictions:()=>typeof ENSEMBLE_CATEGORY_MODEL_RESTRICTIONS!=='undefined'?ENSEMBLE_CATEGORY_MODEL_RESTRICTIONS:{},
  selectionModelRestrictions:()=>typeof ENSEMBLE_SELECTION_MODEL_RESTRICTIONS!=='undefined'?ENSEMBLE_SELECTION_MODEL_RESTRICTIONS:{},
  defaultProductByCategory:()=>typeof ENSEMBLE_DEFAULT_PRODUCT_BY_CATEGORY!=='undefined'?ENSEMBLE_DEFAULT_PRODUCT_BY_CATEGORY:{},
  modelSpecificProductCategory:{},
  categoryRedirectByModel:{},
  disabledProductCategoriesByModel:{}
}

};


/* expose config for app.js safe lookup */
if(typeof window!=='undefined'){
  window.CATALOG_CONFIG=CATALOG_CONFIG;
}

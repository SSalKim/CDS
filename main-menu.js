/* Main menu binding and default product helpers. Depends on app.js globals at call time. */

function inferMainMenuIdFromButton(btn,index){

if(btn.dataset?.menu){
return btn.dataset.menu;
}

let text=(btn.textContent || "").trim();

if(text.includes("편집")){
return "edit";
}

if(text.includes("분석")){
return "analysis";
}

if(text.includes("예보")){
return "forecast";
}

if(text.includes("위험")){
return "hazard";
}

if(text.includes("앙상블")){
return "ensemble";
}

return ["edit","analysis","forecast","hazard","ensemble"][index] || "forecast";

}


function bindMainMenu(){

let buttons=[...document.querySelectorAll(".menu-btn")];

buttons.forEach((btn,index)=>{

let menuId=inferMainMenuIdFromButton(btn,index);
btn.dataset.menu=menuId;

btn.onclick=()=>{

if(menuId===currentMainMenu){
return;
}

invalidateSelectionAsyncWork();
currentMainMenu=menuId;

if(!supportsModelCompareInCurrentMenu()){
disableModelCompareMode();
}

ensureCurrentModelVisibleForMenu();

buttons.forEach(b=>{
b.classList.toggle("active",b.dataset.menu===currentMainMenu);
});

let selectableCategories=getSelectableCategories();
let firstCategory=selectableCategories[0];

if(firstCategory){
productCategory.value=firstCategory.id;
}

let firstProduct=getDefaultProductForCategory(
productCategory.value || firstCategory?.id
);

if(firstProduct){
currentProduct=firstProduct.id;
}
else{
currentProduct="";
}

currentAuxValue=null;

enforceModelRestrictionForCurrentCategory();

refreshView({
updateCategories:true,
updateProducts:true,
updateHours:true,
resetSlider:true,
updateChartAfter:false
});

setTimeout(()=>{

jumpLatestAvailableForCurrentSelection({
silent:false
});

},0);

};

});

buttons.forEach(btn=>{
btn.classList.toggle("active",btn.dataset.menu===currentMainMenu);
});

}


function getDefaultProductForCategory(categoryId){

let defaults=getActiveDefaultProductByCategory();
let preferredId=defaults[categoryId];

if(preferredId){

let preferredProduct=getActiveProducts().find(
p=>
p.category===categoryId &&
p.id===preferredId &&
p.type!=="header"
);

if(preferredProduct){
return preferredProduct;
}

}

return getActiveProducts().find(
p=>
p.category===categoryId &&
p.type!=="header"
);

}

/* Date/time, cycle-hour, and run-time control helpers. Depends on app.js globals at call time. */

let lastRunSelectionUTC=null;

function pad2(value){
return String(value).padStart(2,'0');
}


function formatDateInputLocal(date){
let y=date.getFullYear();
let m=pad2(date.getMonth()+1);
let d=pad2(date.getDate());
return `${y}-${m}-${d}`;
}


function formatDateInputFromUTCParts(date){
let y=date.getUTCFullYear();
let m=pad2(date.getUTCMonth()+1);
let d=pad2(date.getUTCDate());
return `${y}-${m}-${d}`;
}


function formatUTCStampFromDate(date){
let y=date.getUTCFullYear();
let m=pad2(date.getUTCMonth()+1);
let d=pad2(date.getUTCDate());
let h=pad2(date.getUTCHours());
return `${y}${m}${d}${h}`;
}


function setToday(){
runDate.value=formatDateInputLocal(new Date());
}



function parseDateOnly(dateString){

let [y,m,d]=dateString.split('-').map(Number);

return new Date(
Date.UTC(y,m-1,d)
);

}


function getSelectedUTCDate(){

if(!runDate.value){
return new Date();
}

let [y,m,d]=runDate.value.split('-').map(Number);
let h=parseInt(runHour.value || '0',10);

if(Number.isNaN(h)){
h=0;
}

if(timeMode==='KST'){
return new Date(Date.UTC(y,m-1,d,h-9));
}

return new Date(Date.UTC(y,m-1,d,h));

}


function rememberSelectedRunUTC(runUTC=getSelectedUTCDate()){

if(!(runUTC instanceof Date) || Number.isNaN(runUTC.getTime())){
return;
}

lastRunSelectionUTC=new Date(runUTC.getTime());

}


function getRememberedRunUTC(){

if(lastRunSelectionUTC instanceof Date && !Number.isNaN(lastRunSelectionUTC.getTime())){
return new Date(lastRunSelectionUTC.getTime());
}

return getSelectedUTCDate();

}


function getForecastHourForRunChange(previousRunUTC,nextRunUTC){

let currentLead=typeof getSelectedTimelineHourForPreserve==='function'
?getSelectedTimelineHourForPreserve()
:null;

if(!Number.isFinite(currentLead)){
return null;
}

if(typeof productUsesForecastHour==='function' && !productUsesForecastHour()){
return currentLead;
}

if(
!(previousRunUTC instanceof Date) || Number.isNaN(previousRunUTC.getTime()) ||
!(nextRunUTC instanceof Date) || Number.isNaN(nextRunUTC.getTime())
){
return currentLead;
}

let runDifferenceHours=(previousRunUTC.getTime()-nextRunUTC.getTime())/(60*60*1000);
let nextLead=currentLead+runDifferenceHours;
let roundedLead=Math.round(nextLead);

return Math.abs(nextLead-roundedLead)<1e-6 ? roundedLead : nextLead;

}


function setControlsFromUTCDate(utcDate,mode=timeMode){

let displayDate;

if(mode==='KST'){
displayDate=new Date(utcDate.getTime()+9*60*60*1000);
}
else{
displayDate=new Date(utcDate.getTime());
}

runDate.value=formatDateInputFromUTCParts(displayDate);
runHour.value=pad2(displayDate.getUTCHours());


}


function getUTCStamp(){
return formatUTCStampFromDate(getSelectedUTCDate());
}


function getCyclesForSelection(modelId,product,date){

let productCycles=
product?.cyclesByModel?.[modelId] ||
product?.cycles ||
null;

if(productCycles){
return productCycles;
}

return getAvailableCycles(
modelId,
date
) || [];

}


function getCyclesForCurrentSelection(date=parseDateOnly(runDate.value)){

return getCyclesForSelection(
currentModel,
getCurrentProduct(),
date
);

}


function populateHours(preferredUTCDate=null){

let previousUTC=preferredUTCDate || getSelectedUTCDate();
let previousUTCStamp=formatUTCStampFromDate(previousUTC);

runHour.innerHTML='';

let displayDate=parseDateOnly(runDate.value);
let cycles=getCyclesForCurrentSelection(displayDate);
let optionItems=[];

cycles.forEach(cycleHour=>{

let displayUTC;
let displayHour;

if(timeMode==='KST'){
/*
KST 기준 날짜는 로컬 날짜다.
예: KST 03시는 같은 날짜 03KST = 전날 18UTC.
*/
displayUTC=new Date(Date.UTC(
displayDate.getUTCFullYear(),
displayDate.getUTCMonth(),
displayDate.getUTCDate(),
cycleHour+9
));
displayHour=displayUTC.getUTCHours();
}
else{
displayUTC=new Date(Date.UTC(
displayDate.getUTCFullYear(),
displayDate.getUTCMonth(),
displayDate.getUTCDate(),
cycleHour
));
displayHour=cycleHour;
}

let value=pad2(displayHour);
let candidateUTC=timeMode==='KST'
?new Date(Date.UTC(
displayDate.getUTCFullYear(),
displayDate.getUTCMonth(),
displayDate.getUTCDate(),
displayHour-9
))
:new Date(Date.UTC(
displayDate.getUTCFullYear(),displayDate.getUTCMonth(),displayDate.getUTCDate(),displayHour));

optionItems.push({
value,
text:`${value}:00`,
utcHour:pad2(cycleHour),
utcStamp:formatUTCStampFromDate(candidateUTC),
sortHour:displayHour
});

});

/* KST에서는 03,09,15,21처럼 화면에 보이는 날짜 기준 오름차순으로 정렬한다. */
optionItems.sort((a,b)=>a.sortHour-b.sortHour);

let optionToSelect=null;

optionItems.forEach(item=>{
let o=document.createElement('option');
o.value=item.value;
o.textContent=item.text;
o.dataset.utcHour=item.utcHour;
o.dataset.utcStamp=item.utcStamp;

if(item.utcStamp===previousUTCStamp){
optionToSelect=o.value;
}

runHour.appendChild(o);
});

if(runHour.options.length===0){
return;
}

if(optionToSelect && [...runHour.options].some(o=>o.value===optionToSelect)){
runHour.value=optionToSelect;
}
else if([...runHour.options].some(o=>o.value===runHour.value)){
/* keep current value */
}
else{
runHour.selectedIndex=0;
}


}

function setRunControlsToUTC(runUTC){

setControlsFromUTCDate(
runUTC,
timeMode
);

populateHours(runUTC);
rememberSelectedRunUTC(runUTC);

}


function setRunControlsToUTCAllowUnsupported(runUTC){

let display=timeMode==='KST'
?new Date(runUTC.getTime()+9*60*60*1000)
:new Date(runUTC.getTime());

runDate.value=formatDateInputFromUTCParts(display);
populateHours(runUTC);

let desiredHour=pad2(display.getUTCHours());
let hasOption=[...runHour.options].some(option=>option.value===desiredHour);

if(!hasOption){
let option=document.createElement('option');
option.value=desiredHour;
option.textContent=`${desiredHour}:00`;
option.dataset.unsupported='true';
runHour.appendChild(option);
}

runHour.value=desiredHour;
rememberSelectedRunUTC(runUTC);

}

function shiftRunTimeByHours(hours){

let delta=Number(hours);

if(!Number.isFinite(delta) || delta===0){
return;
}

invalidateSelectionAsyncWork();
stopCompareAnimation();

let previousRunUTC=getSelectedUTCDate();

let nextUTC=new Date(
previousRunUTC.getTime()+delta*60*60*1000
);

let preserveForecastHour=getForecastHourForRunChange(previousRunUTC,nextUTC);

setRunControlsToUTCAllowUnsupported(nextUTC);

refreshViewAfterSelectionChange({
updateCategories:false,
updateProducts:true,
updateHours:false,
resetSlider:true,
preserveForecastHour,
updateChartAfter:true
});

}

function switchTimeMode(nextMode){

invalidateSelectionAsyncWork();

if(timeMode===nextMode){
return;
}

let selectedUTC=getSelectedUTCDate();
let currentIndex=Number(slider.value || 0);

timeMode=nextMode;

kstBtn.classList.toggle('active',timeMode==='KST');
utcBtn.classList.toggle('active',timeMode==='UTC');

setControlsFromUTCDate(selectedUTC,timeMode);
populateHours(selectedUTC);
rememberSelectedRunUTC(selectedUTC);

slider.value=String(forecastTimelineState.clampIndex(currentIndex));

updateForecastLabel();
refreshForecastTimelineLabels();

}

function handleRunDateChanged(){

let previousRunUTC=getRememberedRunUTC();
normalizeRunDateYearInput();

invalidateSelectionAsyncWork();
populateHours();
let nextRunUTC=getSelectedUTCDate();
let preserveForecastHour=getForecastHourForRunChange(previousRunUTC,nextRunUTC);
rememberSelectedRunUTC(nextRunUTC);
refreshViewAfterSelectionChange({
  updateCategories:false,
  updateProducts:true,
  updateHours:false,
  resetSlider:true,
  preserveForecastHour,
  updateChartAfter:true
});

}

function handleRunHourChanged(){

let previousRunUTC=getRememberedRunUTC();
invalidateSelectionAsyncWork();
let nextRunUTC=getSelectedUTCDate();
let preserveForecastHour=getForecastHourForRunChange(previousRunUTC,nextRunUTC);
rememberSelectedRunUTC(nextRunUTC);
refreshViewAfterSelectionChange({
  updateCategories:false,
  updateProducts:true,
  updateHours:false,
  resetSlider:true,
  preserveForecastHour,
  updateChartAfter:true
});

}

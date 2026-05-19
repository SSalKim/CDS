(function(global){

function normalizeForecastList(list){

if(!Array.isArray(list) || !list.length){
return [0];
}

return [...list];

}

function clampIndex(index,length){

let max=Math.max(0,(Number(length)||1)-1);
let value=Number(index);

if(!Number.isFinite(value)){
value=0;
}

return Math.max(0,Math.min(value,max));

}

function findForecastHourIndex(list,hour){

if(hour===null || hour===undefined){
return -1;
}

return list.findIndex(
h=>Number(h)===Number(hour)
);

}

function makeLoadStates(length,state='loading'){

return Array.from(
{length:Math.max(1,Number(length)||1)},
()=>state
);

}

function createTimelineState(){

let forecastList=[0];
let loadStates=['loading'];
let imageCache=new Map();

return {

setForecastList(list){
forecastList=normalizeForecastList(list);
return forecastList;
},

getForecastList(){
return forecastList;
},

getLength(){
return forecastList.length || 1;
},

getHour(index){
return forecastList[clampIndex(index,forecastList.length)] ?? 0;
},

indexOfHour(hour){
return findForecastHourIndex(forecastList,hour);
},

clampIndex(index){
return clampIndex(index,forecastList.length);
},

setLoadStates(states){
loadStates=Array.isArray(states) && states.length
?[...states]
:['loading'];
return loadStates;
},

setAllLoadStates(length,state='loading'){
loadStates=makeLoadStates(length,state);
return loadStates;
},

setLoadState(index,state){
loadStates[clampIndex(index,loadStates.length || forecastList.length)]=state;
return loadStates;
},

getLoadState(index){
return loadStates[clampIndex(index,loadStates.length || forecastList.length)] || 'loading';
},

resetImageCache(){
imageCache=new Map();
return imageCache;
},

setImageCacheEntry(index,value){
imageCache.set(clampIndex(index,forecastList.length),value);
},

getImageCacheEntry(index){
return imageCache.get(clampIndex(index,forecastList.length));
},

getImageCache(){
return imageCache;
}

};

}

global.CDSTimelineState={
normalizeForecastList,
clampIndex,
findForecastHourIndex,
makeLoadStates,
createTimelineState
};

})(window);

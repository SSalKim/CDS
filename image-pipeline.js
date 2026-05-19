(function(global){

function resultMeetsMode(results,mode='all'){

if(!Array.isArray(results) || !results.length){
return false;
}

return mode==='any'
?results.some(Boolean)
:results.every(Boolean);

}

function loadedImagesMeetMode(loadedImages,urls,mode='all'){

let loadedCount=Array.isArray(loadedImages)
?loadedImages.length
:Number(loadedImages)||0;
let totalCount=Array.isArray(urls)
?urls.length
:Number(urls)||0;

if(totalCount<=0){
return false;
}

return mode==='any'
?loadedCount>=1
:loadedCount===totalCount;

}

async function urlsExist(urls,{
loadImage,
existenceMode='all'
}={}){

if(!urls || urls.length===0 || typeof loadImage!=='function'){
return false;
}

let results=await Promise.all(
urls.map(url=>loadImage(url))
);

return resultMeetsMode(results,existenceMode);

}

async function preloadForecastIndex(index,{
buildUrls,
loadImage,
existenceMode='all',
isCancelled=()=>false
}={}){

let urls=typeof buildUrls==='function'
?buildUrls(index)
:[];

if(!urls.length){
return {index,ok:false,urls:[]};
}

let results=await Promise.all(
urls.map(url=>loadImage(url))
);

if(isCancelled()){
return {index,ok:false,urls,cancelled:true};
}

return {
index,
ok:resultMeetsMode(results,existenceMode),
urls
};

}

async function prepareDisplayImages(urls,{
createDisplayImage,
existenceMode='all'
}={}){

if(!urls || urls.length===0 || typeof createDisplayImage!=='function'){
return {
prepared:[],
loadedImages:[],
enough:false
};
}

let prepared=await Promise.all(
urls.map(url=>createDisplayImage(url))
);
let loadedImages=prepared.filter(Boolean);

return {
prepared,
loadedImages,
enough:loadedImagesMeetMode(
loadedImages,
urls,
existenceMode
)
};

}

async function runConcurrentRange({
count,
concurrency=4,
isCancelled=()=>false,
task
}={}){

let total=Math.max(0,Number(count)||0);

if(total===0 || typeof task!=='function'){
return;
}

let cursor=0;

async function worker(){

while(cursor<total){

if(isCancelled()){
return;
}

let index=cursor++;
let shouldContinue=await task(index);

if(shouldContinue===false){
return;
}

}

}

let workers=Array.from(
{length:Math.min(Math.max(1,Number(concurrency)||1),total)},
()=>worker()
);

await Promise.all(workers);

}

global.CDSImagePipeline={
resultMeetsMode,
loadedImagesMeetMode,
urlsExist,
preloadForecastIndex,
prepareDisplayImages,
runConcurrentRange
};

})(window);

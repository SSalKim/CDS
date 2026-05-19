(function(global){

const DEFAULT_CHART_BASE_URL='https://data.kma.go.kr/CHT';

function normalizePatternList(pattern){

if(!pattern){
return [];
}

return Array.isArray(pattern)
?pattern
:[pattern];

}

function getProductFolderForModel(product,modelId,models){

return product?.folderByModel?.[modelId] || models?.[modelId]?.folder || '';

}

function getChartUrlParts(runUTC,formatUTCStampFromDate){

let run=formatUTCStampFromDate(runUTC);

return {
run,
ym:run.slice(0,6),
day:run.slice(6,8)
};

}

function applyChartPatternTokens(pattern,{
run,
forecastHour=0,
detailToken=null
}={}){

let file=pattern.replaceAll('{run}',run);

if(file.includes('{fh}')){
file=file.replaceAll(
'{fh}',
String(Number(forecastHour || 0)).padStart(3,'0')
);
}

if(file.includes('{detail}')){
file=file.replaceAll('{detail}',detailToken || '');
}

return file;

}

function makeChartImageUrls({
product,
modelId,
runUTC,
patterns,
forecastHour=0,
detailToken=null,
requireDetailToken=true,
checkAvailability=false,
models,
formatUTCStampFromDate,
parseDateOnly,
formatDateInputFromUTCParts,
getEffectiveModelStatus,
getProductArchiveStatus,
baseUrl=DEFAULT_CHART_BASE_URL
}={}){

if(!product || !models?.[modelId] || !runUTC || !formatUTCStampFromDate){
return [];
}

let patternList=normalizePatternList(
patterns ?? product.patternByModel?.[modelId]
).filter(pattern=>typeof pattern==='string');

if(!patternList.length){
return [];
}

let folder=getProductFolderForModel(product,modelId,models);

if(!folder){
return [];
}

if(checkAvailability){

let modelStatus=getEffectiveModelStatus?.(
modelId,
runUTC,
product
);

if(!modelStatus?.available){
return [];
}

let runDateOnly=parseDateOnly(
formatDateInputFromUTCParts(runUTC)
);

let productStatus=getProductArchiveStatus?.(
product,
modelId,
runDateOnly
);

if(!productStatus?.available){
return [];
}

}

if(
requireDetailToken &&
patternList.some(pattern=>pattern.includes('{detail}')) &&
!detailToken
){
return [];
}

let {run,ym,day}=getChartUrlParts(runUTC,formatUTCStampFromDate);

return patternList.map(pattern=>{

let file=applyChartPatternTokens(pattern,{
run,
forecastHour,
detailToken
});

return `${baseUrl}/${folder}/${ym}/${day}/${file}`;

});

}

function loadImage(url,timeoutMs){

return new Promise(resolve=>{

let done=false;
let img=new Image();

let timer=setTimeout(()=>{
if(done){return;}
done=true;
resolve(false);
},timeoutMs);

img.onload=()=>{
if(done){return;}
done=true;
clearTimeout(timer);
resolve(true);
};

img.onerror=()=>{
if(done){return;}
done=true;
clearTimeout(timer);
resolve(false);
};

img.src=url;

});

}

function createImageLoader({
decodeTimeoutMs=20000,
cacheLimit=500,
trimTo=250
}={}){

let decodedImageCache=new Map();

function resetCacheIfLarge(){

if(decodedImageCache.size<=cacheLimit){
return;
}

decodedImageCache=new Map(
[...decodedImageCache.entries()].slice(-trimTo)
);

}

function getDecodedImage(url,timeoutMs=decodeTimeoutMs){

if(decodedImageCache.has(url)){
return decodedImageCache.get(url);
}

let promise=new Promise(resolve=>{
let done=false;
let img=new Image();
img.decoding='async';
img.loading='eager';

let timer=setTimeout(()=>{
if(done){return;}
done=true;
resolve({ok:false,url,img:null});
},timeoutMs);

img.onload=async()=>{
if(done){return;}

try{
if(typeof img.decode==='function'){
await img.decode();
}
}
catch(e){}

if(done){return;}
done=true;
clearTimeout(timer);
resolve({ok:true,url,img});
};

img.onerror=()=>{
if(done){return;}
done=true;
clearTimeout(timer);
resolve({ok:false,url,img:null});
};

img.src=url;
});

decodedImageCache.set(url,promise);

promise.then(result=>{
if(!result?.ok){
decodedImageCache.delete(url);
}
});

resetCacheIfLarge();
return promise;

}

async function createDecodedDisplayImage(url){

let result=await getDecodedImage(url);

if(!result.ok || !result.img){
return null;
}

let img=result.img.cloneNode(false);
img.src=url;
img.alt='chart';
img.decoding='async';
img.loading='eager';
img.classList.add('prepared-chart-image');
return img;

}

function revealPreparedImages(root){

let images=[...root.querySelectorAll('.prepared-chart-image')];

images.forEach(img=>{
img.classList.remove('image-fade-in','is-visible');
img.style.opacity='';
img.style.transition='';
});

}

return {
getDecodedImage,
createDecodedDisplayImage,
revealPreparedImages,
resetCacheIfLarge
};

}

global.CDSChartUtils={
normalizePatternList,
getProductFolderForModel,
getChartUrlParts,
applyChartPatternTokens,
makeChartImageUrls,
loadImage,
createImageLoader
};

})(window);

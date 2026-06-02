(function(global){

const DEFAULT_CHART_BASE_URL='https://dmdw.kma.go.kr/map/data/CHT';

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
runmin:run+'00',
ym:run.slice(0,6),
day:run.slice(6,8),
hour:run.slice(8,10)
};

}

function applyChartPatternTokens(pattern,{
run,
runmin=null,
ym=null,
day=null,
hour=null,
forecastHour=0,
detailToken=null
}={}){

let file=pattern.replaceAll('{run}',run);

if(file.includes('{runmin}')){
file=file.replaceAll('{runmin}',runmin || (run ? run+'00' : ''));
}

if(file.includes('{ym}')){
file=file.replaceAll('{ym}',ym || '');
}

if(file.includes('{day}')){
file=file.replaceAll('{day}',day || '');
}

if(file.includes('{hour}')){
file=file.replaceAll('{hour}',hour || '');
}

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

function isAbsoluteUrlPattern(pattern){

return /^https?:\/\//i.test(pattern);

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

let hasRelativePattern=patternList.some(pattern=>!isAbsoluteUrlPattern(pattern));
let folder=getProductFolderForModel(product,modelId,models);

if(hasRelativePattern && !folder){
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

let {run,runmin,ym,day,hour}=getChartUrlParts(runUTC,formatUTCStampFromDate);

return patternList.map(pattern=>{

let file=applyChartPatternTokens(pattern,{
run,
runmin,
ym,
day,
hour,
forecastHour,
detailToken
});

if(isAbsoluteUrlPattern(file)){
return file;
}

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

if(typeof url==='string' && url.includes('nmsc.kma.go.kr/IMG/GK2A')){
img.classList.add('nmsc-chart-image');

if(url.includes('/EA/') || url.includes('_ea020lc_')){
img.classList.add('nmsc-ea-image');
}

if(url.includes('/KO/') || url.includes('_ko020lc_')){
img.classList.add('nmsc-ko-image');
}

if(
url.includes('/L2/mT_DAI/') ||
url.includes('gk2a_ami_le2_dai_') ||
url.includes('gk2a_ami_le2_dab-')
){
img.classList.add('nmsc-mt-image');
}
}

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

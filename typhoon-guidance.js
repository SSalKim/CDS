const TYPHOON_MANIFEST_PATH='VTG_IMG/manifest.json';
const TYPHOON_REFRESH_MS=10*60*1000;

const typhoonState={
root:null,
manifest:null,
runs:[],
selectedIndex:0,
timer:null
};

function openTyphoonGuidancePage(){
window.open('typhoon.html','_blank','noopener');
}

function renderTyphoonGuidanceLauncher(){
let section=document.createElement('div');
section.className='model-section typhoon-guidance-section';

let button=document.createElement('button');
button.type='button';
button.className='typhoon-guidance-launcher';
button.title='태풍 모델예측 페이지 열기';
button.innerHTML='<span class="typhoon-launcher-icon">↗</span><span class="typhoon-launcher-text"><span>태풍</span><span>모델예측</span><small>(EXP)</small></span>';
button.onclick=openTyphoonGuidancePage;

section.appendChild(button);
return section;
}

function initTyphoonGuidancePage(){
let root=document.getElementById('typhoonGuidanceApp');
if(!root){
return;
}

typhoonState.root=root;
renderTyphoonShell();
loadTyphoonManifest();

if(!typhoonState.timer){
typhoonState.timer=window.setInterval(loadTyphoonManifest,TYPHOON_REFRESH_MS);
}

document.addEventListener('visibilitychange',()=>{
if(document.visibilityState==='visible'){
loadTyphoonManifest();
}
});
}

function renderTyphoonShell(){
let root=typhoonState.root;
if(!root){
return;
}

let page=document.createElement('main');
page.className='typhoon-page';

let header=document.createElement('header');
header.className='typhoon-header';

let titleWrap=document.createElement('div');
titleWrap.className='typhoon-title-wrap';

let title=document.createElement('div');
title.className='typhoon-title';
title.textContent='태풍 모델예측';

let subtitle=document.createElement('div');
subtitle.className='typhoon-subtitle';
subtitle.dataset.role='subtitle';
subtitle.textContent='VTG';

titleWrap.appendChild(title);
titleWrap.appendChild(subtitle);

let refresh=document.createElement('button');
refresh.type='button';
refresh.className='typhoon-refresh-button';
refresh.title='새로고침';
refresh.textContent='↻';
refresh.onclick=loadTyphoonManifest;

header.appendChild(titleWrap);
header.appendChild(refresh);

let cycleBar=document.createElement('div');
cycleBar.className='typhoon-cycle-bar';
cycleBar.dataset.role='cycleBar';

let content=document.createElement('section');
content.className='typhoon-content';

let viewer=document.createElement('div');
viewer.className='typhoon-viewer';
viewer.dataset.role='viewer';

let side=document.createElement('aside');
side.className='typhoon-side-panel';
side.dataset.role='sidePanel';

content.appendChild(viewer);
content.appendChild(side);
page.appendChild(header);
page.appendChild(cycleBar);
page.appendChild(content);

root.replaceChildren(page);
}

async function loadTyphoonManifest(){
let root=typhoonState.root;
if(!root){
return;
}

root.classList.add('typhoon-loading-state');

try{
let response=await fetch(`${TYPHOON_MANIFEST_PATH}?fresh=${Date.now()}`,{
cache:'no-store'
});
if(!response.ok){
throw new Error(`HTTP ${response.status}`);
}

let manifest=await response.json();
typhoonState.manifest=manifest;
typhoonState.runs=normalizeTyphoonRuns(manifest);

if(typhoonState.selectedIndex>=typhoonState.runs.length){
typhoonState.selectedIndex=0;
}

renderTyphoonManifest();
}
catch(error){
typhoonState.manifest=null;
typhoonState.runs=[];
renderTyphoonEmpty(`자료 없음 (${error.message})`);
}
finally{
root.classList.remove('typhoon-loading-state');
}
}

function normalizeTyphoonRuns(manifest){
let runs=Array.isArray(manifest?.runs) ? manifest.runs : [];

return runs
.map((entry,index)=>{
let metadata=entry?.result?.metadata || {};
let job=entry?.job || {};
let windowInfo=entry?.window || {};
let imagePath=normalizeTyphoonAssetPath(metadata.image_path || '');
let dataTime=metadata.data_time || job.data_time || windowInfo.data_time || '';
let generatedAt=metadata.generated_at_utc || manifest.updated_at_utc || '';
return {
index,
entry,
metadata,
job,
windowInfo,
imagePath,
dataTime,
generatedAt,
sortKey:`${dataTime}${generatedAt}`.padEnd(26,'0')
};
})
.filter(run=>run.dataTime || run.imagePath)
.sort((a,b)=>b.sortKey.localeCompare(a.sortKey));
}

function normalizeTyphoonAssetPath(value){
let path=String(value || '').replace(/\\/g,'/');
if(!path){
return '';
}

if(/^https?:\/\//i.test(path)){
return path;
}

let marker='VTG_IMG/';
let markerIndex=path.indexOf(marker);
if(markerIndex>=0){
return path.slice(markerIndex);
}

return path.replace(/^\/+/,'');
}

function cacheBustedTyphoonPath(path,version){
if(!path){
return '';
}
let separator=path.includes('?') ? '&' : '?';
return `${path}${separator}fresh=${encodeURIComponent(version || Date.now())}`;
}

function renderTyphoonManifest(){
let runs=typhoonState.runs;
let manifest=typhoonState.manifest || {};
updateTyphoonSubtitle(manifest,runs);
renderTyphoonCycleBar(runs);

if(!runs.length){
renderTyphoonEmpty('표출 가능한 자료 없음');
return;
}

renderTyphoonRun(runs[typhoonState.selectedIndex] || runs[0]);
}

function updateTyphoonSubtitle(manifest,runs){
let subtitle=typhoonState.root?.querySelector('[data-role="subtitle"]');
if(!subtitle){
return;
}

let updated=formatTyphoonTime(manifest.updated_at_utc);
let activeCount=runs.length;
subtitle.textContent=updated ? `VTG · ${updated} 업데이트 · ${activeCount}개 산출물` : `VTG · ${activeCount}개 산출물`;
}

function renderTyphoonCycleBar(runs){
let bar=typhoonState.root?.querySelector('[data-role="cycleBar"]');
if(!bar){
return;
}

bar.innerHTML='';

if(!runs.length){
return;
}

runs.forEach((run,index)=>{
let button=document.createElement('button');
button.type='button';
button.className='typhoon-cycle-button'+(index===typhoonState.selectedIndex?' active':'');
button.innerHTML=[
`<span>${escapeHtml(cycleStormLabel(run))}</span>`,
`<strong>${escapeHtml(formatCycleCompact(run.dataTime))}</strong>`,
`<small>${escapeHtml(modelCountLabel(run))}</small>`
].join('');
button.onclick=()=>{
typhoonState.selectedIndex=index;
renderTyphoonManifest();
};
bar.appendChild(button);
});
}

function renderTyphoonRun(run){
let viewer=typhoonState.root?.querySelector('[data-role="viewer"]');
let side=typhoonState.root?.querySelector('[data-role="sidePanel"]');
if(!viewer || !side){
return;
}

viewer.innerHTML='';
side.innerHTML='';

if(!run.imagePath){
renderTyphoonEmpty('이미지 없음');
return;
}

let image=document.createElement('img');
image.className='typhoon-guidance-image';
image.alt='태풍 모델예측 이미지';
image.decoding='async';
image.src=cacheBustedTyphoonPath(run.imagePath,run.generatedAt);

let error=document.createElement('div');
error.className='typhoon-status-panel hidden';
error.textContent='이미지 로드 실패';

image.onerror=()=>{
error.classList.remove('hidden');
};

viewer.appendChild(image);
viewer.appendChild(error);

renderTyphoonSidePanel(side,run);
}

function renderTyphoonSidePanel(side,run){
let metadata=run.metadata || {};
let models=Array.isArray(metadata.models) ? metadata.models : [];

let title=document.createElement('div');
title.className='typhoon-side-title';
title.textContent=cycleStormLabel(run);

let rows=document.createElement('div');
rows.className='typhoon-info-rows';

[
['자료시각',formatTyphoonTime(run.dataTime)],
['KST',formatTyphoonKst(run.dataTime)],
['강도',metadata.intensity || '-'],
['모델',modelCountLabel(run)],
['ATCF',metadata.atcf_id || run.job?.atcf_id || '-']
].forEach(([label,value])=>{
let row=document.createElement('div');
row.className='typhoon-info-row';
row.innerHTML=`<span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong>`;
rows.appendChild(row);
});

let modelTitle=document.createElement('div');
modelTitle.className='typhoon-model-title';
modelTitle.textContent='표출 모델';

let modelList=document.createElement('div');
modelList.className='typhoon-model-list';

if(models.length){
models.forEach(model=>{
let item=document.createElement('span');
item.textContent=model;
modelList.appendChild(item);
});
}
else{
let empty=document.createElement('span');
empty.textContent='-';
modelList.appendChild(empty);
}

side.appendChild(title);
side.appendChild(rows);
side.appendChild(modelTitle);
side.appendChild(modelList);
}

function renderTyphoonEmpty(message){
let viewer=typhoonState.root?.querySelector('[data-role="viewer"]');
let side=typhoonState.root?.querySelector('[data-role="sidePanel"]');
let bar=typhoonState.root?.querySelector('[data-role="cycleBar"]');
if(bar){
bar.innerHTML='';
}
if(viewer){
viewer.innerHTML=`<div class="typhoon-status-panel">${escapeHtml(message)}</div>`;
}
if(side){
side.innerHTML='';
}
updateTyphoonSubtitle(typhoonState.manifest || {},[]);
}

function cycleStormLabel(run){
let metadata=run.metadata || {};
let job=run.job || {};
let number=metadata.typ_number || job.typ_number || '';
let name=metadata.typ_name || job.typ_name || 'NAMELESS';
let year=String(metadata.storm_year || job.year || run.dataTime.slice(0,4) || '').slice(-2);
let cycloneId=number ? `${year}${String(number).padStart(2,'0')}` : '';
return `${cycloneId} ${name}`.trim();
}

function modelCountLabel(run){
let metadata=run.metadata || {};
let count=metadata.model_count;
let target=metadata.target_model_count || 33;
if(count===undefined || count===null || count===''){
return `0/${target}`;
}
return `${count}/${target}`;
}

function formatCycleCompact(value){
if(!value || value.length<10){
return '-';
}
return `${value.slice(4,6)}-${value.slice(6,8)} ${value.slice(8,10)}UTC`;
}

function formatTyphoonTime(value){
if(!value || value.length<10){
return '';
}
return `${value.slice(0,4)}-${value.slice(4,6)}-${value.slice(6,8)} ${value.slice(8,10)}UTC`;
}

function formatTyphoonKst(value){
let date=parseTyphoonUtcDate(value);
if(!date){
return '-';
}
date.setUTCHours(date.getUTCHours()+9);
return `${date.getUTCFullYear()}-${pad2(date.getUTCMonth()+1)}-${pad2(date.getUTCDate())} ${pad2(date.getUTCHours())}KST`;
}

function parseTyphoonUtcDate(value){
if(!value || value.length<10){
return null;
}
let year=Number(value.slice(0,4));
let month=Number(value.slice(4,6))-1;
let day=Number(value.slice(6,8));
let hour=Number(value.slice(8,10));
let minute=Number(value.slice(10,12) || 0);
if([year,month,day,hour,minute].some(Number.isNaN)){
return null;
}
return new Date(Date.UTC(year,month,day,hour,minute));
}

function pad2(value){
return String(value).padStart(2,'0');
}

function escapeHtml(value){
return String(value ?? '').replace(/[&<>"']/g,character=>({
'&':'&amp;',
'<':'&lt;',
'>':'&gt;',
'"':'&quot;',
"'":'&#39;'
}[character]));
}

document.addEventListener('DOMContentLoaded',initTyphoonGuidancePage);

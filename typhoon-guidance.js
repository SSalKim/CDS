const TYPHOON_MANIFEST_PATH='VTG_IMG/manifest.json';
const TYPHOON_REFRESH_MS=10*60*1000;
const TYPHOON_SLOT_HOURS=6;

const TYPHOON_MODEL_LABELS={
KMA:'KMA OFCL',
ECMWF:'ECMWF',
ECMWF_EPS:'ECMWF EPS',
KIM_3h:'KIM',
KIM_6h:'KIM',
KIM_EPS:'KIM EPS',
UM:'UM',
UM_GFDL_6h:'UM',
UM_KEPS:'UM KEPS',
UKM:'UKMO',
UKMO_EPS:'UKMO EPS',
GFS:'GFS',
GFS_EPS:'GFS GEFS',
CMC:'CMC',
CMC_EPS:'CMC GEPS',
NAVGEM:'NAVGEM',
FNMOC_EPS:'NAVGEM EPS',
JGSM:'JGSM',
TEPS:'JGSM TEPS',
CTCX:'COAMPS-TC',
COAMPS_EPS:'COAMPS-TC EPS',
AFUM:'GALWEM',
HAFS:'HAFS',
HWRF:'HWRF',
ECMWF_AIFS:'ECMWF AIFS',
ECMWF_AIFS_EPS:'ECMWF AIFS EPS',
IFEC_AI:'KMA AIFS-ECMWF',
IFKM_AI:'KMA AIFS-KIM',
AGFS:'AIGFS',
AIGEFS:'AIGEFS',
FNEC_AI:'FourCastNet-ECMWF',
FNKM_AI:'FourCastNet-KIM',
PGEC_AI:'Pangu-Weather-ECMWF',
PGKM_AI:'Pangu-Weather-KIM',
GCEC_AI:'GraphCast-ECMWF',
GCKM_AI:'GraphCast-KIM',
GENC:'GenCast',
FNV3:'FNV3'
};

const typhoonState={
root:null,
manifest:null,
entries:[],
years:[],
storms:[],
slots:[],
selectedYear:'',
selectedStormKey:'',
selectedSlotIndex:0,
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

let controls=document.createElement('div');
controls.className='typhoon-select-controls';

let yearSelect=document.createElement('select');
yearSelect.className='typhoon-year-select';
yearSelect.dataset.role='yearSelect';
yearSelect.onchange=event=>{
typhoonState.selectedYear=event.target.value;
selectDefaultStormForYear();
renderTyphoonManifest();
};

let stormSelect=document.createElement('select');
stormSelect.className='typhoon-storm-select';
stormSelect.dataset.role='stormSelect';
stormSelect.onchange=event=>{
typhoonState.selectedStormKey=event.target.value;
selectLatestSlotForStorm();
renderTyphoonManifest();
};

let refresh=document.createElement('button');
refresh.type='button';
refresh.className='typhoon-refresh-button';
refresh.title='새로고침';
refresh.textContent='↻';
refresh.onclick=loadTyphoonManifest;

controls.appendChild(yearSelect);
controls.appendChild(stormSelect);
controls.appendChild(refresh);

header.appendChild(titleWrap);
header.appendChild(controls);

let timeBar=document.createElement('div');
timeBar.className='forecast-bar typhoon-time-bar';

let shell=document.createElement('div');
shell.className='forecast-shell compare-active typhoon-time-shell';

let slider=document.createElement('input');
slider.type='range';
slider.min='0';
slider.max='0';
slider.step='1';
slider.value='0';
slider.className='native-forecast-slider typhoon-time-slider';
slider.dataset.role='timeSlider';
slider.oninput=event=>{
typhoonState.selectedSlotIndex=Number(event.target.value);
renderTyphoonSelectedRun();
renderTyphoonTimeline();
};

let timeline=document.createElement('div');
timeline.className='forecast-timeline typhoon-timeline';
timeline.dataset.role='timeline';

let timeLabel=document.createElement('div');
timeLabel.className='forecast-label-hidden';
timeLabel.dataset.role='timeLabel';

shell.appendChild(slider);
shell.appendChild(timeline);
shell.appendChild(timeLabel);
timeBar.appendChild(shell);

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
page.appendChild(timeBar);
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
let response=await fetch(`${TYPHOON_MANIFEST_PATH}?fresh=${Date.now()}`,{cache:'no-store'});
if(!response.ok){
throw new Error(`HTTP ${response.status}`);
}

let manifest=await response.json();
typhoonState.manifest=manifest;
typhoonState.entries=normalizeTyphoonEntries(manifest);
syncTyphoonSelection();
renderTyphoonManifest();
}
catch(error){
typhoonState.manifest=null;
typhoonState.entries=[];
syncTyphoonSelection();
renderTyphoonEmpty(`자료 없음 (${error.message})`);
}
finally{
root.classList.remove('typhoon-loading-state');
}
}

function normalizeTyphoonEntries(manifest){
let source=Array.isArray(manifest?.inventory) && manifest.inventory.length ? manifest.inventory : manifest?.runs;
let runs=Array.isArray(source) ? source : [];

return runs
.map((entry,index)=>{
let metadata=entry?.result?.metadata || {};
let job=entry?.job || {};
let windowInfo=entry?.window || {};
let imagePath=normalizeTyphoonAssetPath(metadata.image_path || '');
let dataTime=metadata.data_time || job.data_time || windowInfo.data_time || '';
let generatedAt=metadata.generated_at_utc || manifest.updated_at_utc || '';
let year=String(metadata.storm_year || job.year || dataTime.slice(0,4) || '');
let stage=(metadata.storm_stage || job.stage || 'TYP').toUpperCase();
let typNumber=Number(metadata.typ_number || job.typ_number || 0);
let tdNumber=metadata.linked_td_number || job.linked_td_number || job.td_number || null;
let typNameKo=metadata.typ_name_ko || job.typ_name_ko || '';
let typName=metadata.typ_name || job.typ_name || 'NAMELESS';
let stormKey=[year,stage,typNumber,typName].join('|');
return {
index,
entry,
metadata,
job,
windowInfo,
imagePath,
dataTime,
generatedAt,
year,
stage,
typNumber,
tdNumber,
typNameKo,
typName,
stormKey,
sortKey:`${year}${String(typNumber).padStart(2,'0')}${dataTime}${generatedAt}`.padEnd(34,'0')
};
})
.filter(run=>run.year && run.dataTime)
.sort((a,b)=>a.sortKey.localeCompare(b.sortKey));
}

function syncTyphoonSelection(){
typhoonState.years=[...new Set(typhoonState.entries.map(entry=>entry.year))].sort((a,b)=>b.localeCompare(a));

if(!typhoonState.years.includes(typhoonState.selectedYear)){
typhoonState.selectedYear=typhoonState.years[0] || '';
}

typhoonState.storms=buildTyphoonStormsForYear(typhoonState.selectedYear);

if(!typhoonState.storms.some(storm=>storm.key===typhoonState.selectedStormKey)){
selectDefaultStormForYear();
}

typhoonState.slots=buildTyphoonSlotsForStorm(typhoonState.selectedStormKey);

if(typhoonState.selectedSlotIndex<0 || typhoonState.selectedSlotIndex>=typhoonState.slots.length){
selectLatestSlotForStorm();
}
}

function buildTyphoonStormsForYear(year){
let byKey=new Map();
typhoonState.entries
.filter(entry=>entry.year===year)
.forEach(entry=>{
if(!byKey.has(entry.stormKey)){
byKey.set(entry.stormKey,{
key:entry.stormKey,
typNumber:entry.typNumber,
label:stormDropdownLabel(entry),
latest:entry.dataTime
});
}
let storm=byKey.get(entry.stormKey);
if(entry.dataTime>storm.latest){
storm.latest=entry.dataTime;
}
});
return [...byKey.values()].sort((a,b)=>a.typNumber-b.typNumber || a.label.localeCompare(b.label));
}

function selectDefaultStormForYear(){
let storms=buildTyphoonStormsForYear(typhoonState.selectedYear);
typhoonState.storms=storms;
typhoonState.selectedStormKey=storms.length ? storms[storms.length-1].key : '';
selectLatestSlotForStorm();
}

function selectLatestSlotForStorm(){
typhoonState.slots=buildTyphoonSlotsForStorm(typhoonState.selectedStormKey);
let latestAvailable=-1;
typhoonState.slots.forEach((slot,index)=>{
if(slot.entry){
latestAvailable=index;
}
});
typhoonState.selectedSlotIndex=Math.max(0,latestAvailable);
}

function buildTyphoonSlotsForStorm(stormKey){
let entries=typhoonState.entries
.filter(entry=>entry.stormKey===stormKey)
.sort((a,b)=>a.dataTime.localeCompare(b.dataTime));

if(!entries.length){
return [];
}

let byTime=new Map(entries.map(entry=>[entry.dataTime,entry]));
let start=parseTyphoonUtcDate(entries[0].dataTime);
let end=parseTyphoonUtcDate(entries[entries.length-1].dataTime);
if(!start || !end){
return entries.map(entry=>({dataTime:entry.dataTime,entry}));
}

let slots=[];
for(let cursor=new Date(start.getTime());cursor<=end;cursor.setUTCHours(cursor.getUTCHours()+TYPHOON_SLOT_HOURS)){
let dataTime=formatTyphoonStamp(cursor);
slots.push({dataTime,entry:byTime.get(dataTime) || null});
}
return slots;
}

function renderTyphoonManifest(){
updateTyphoonSubtitle();
renderTyphoonSelects();
renderTyphoonTimeline();

if(!typhoonState.entries.length){
renderTyphoonEmpty('표출 가능한 자료 없음');
return;
}

renderTyphoonSelectedRun();
}

function renderTyphoonSelects(){
let yearSelect=typhoonState.root?.querySelector('[data-role="yearSelect"]');
let stormSelect=typhoonState.root?.querySelector('[data-role="stormSelect"]');
if(!yearSelect || !stormSelect){
return;
}

yearSelect.innerHTML='';
typhoonState.years.forEach(year=>{
let option=document.createElement('option');
option.value=year;
option.textContent=year;
yearSelect.appendChild(option);
});
yearSelect.value=typhoonState.selectedYear;

stormSelect.innerHTML='';
typhoonState.storms.forEach(storm=>{
let option=document.createElement('option');
option.value=storm.key;
option.textContent=storm.label;
stormSelect.appendChild(option);
});
stormSelect.value=typhoonState.selectedStormKey;

yearSelect.disabled=!typhoonState.years.length;
stormSelect.disabled=!typhoonState.storms.length;
}

function updateTyphoonSubtitle(){
let subtitle=typhoonState.root?.querySelector('[data-role="subtitle"]');
if(!subtitle){
return;
}
let manifest=typhoonState.manifest || {};
let updated=formatTyphoonTime(manifest.updated_at_utc);
let count=typhoonState.entries.length;
subtitle.textContent=updated ? `VTG · ${updated} 업데이트 · ${count}개 산출물` : `VTG · ${count}개 산출물`;
}

function renderTyphoonTimeline(){
let timeline=typhoonState.root?.querySelector('[data-role="timeline"]');
let slider=typhoonState.root?.querySelector('[data-role="timeSlider"]');
let label=typhoonState.root?.querySelector('[data-role="timeLabel"]');
if(!timeline || !slider || !label){
return;
}

let slots=typhoonState.slots;
timeline.innerHTML='';
slider.min='0';
slider.max=String(Math.max(0,slots.length-1));
slider.value=String(Math.min(typhoonState.selectedSlotIndex,Math.max(0,slots.length-1)));
slider.disabled=slots.length<=1;

slots.forEach((slot,index)=>{
let segment=document.createElement('button');
segment.type='button';
segment.className='typhoon-time-segment'+(slot.entry?' available':' missing')+(index===typhoonState.selectedSlotIndex?' active':'');
segment.textContent=formatCycleCompact(slot.dataTime);
segment.title=slot.entry ? formatTyphoonTime(slot.dataTime) : `${formatTyphoonTime(slot.dataTime)} 자료 없음`;
segment.onclick=()=>{
typhoonState.selectedSlotIndex=index;
renderTyphoonSelectedRun();
renderTyphoonTimeline();
};
timeline.appendChild(segment);
});

let selected=slots[typhoonState.selectedSlotIndex];
label.textContent=selected ? formatTyphoonTime(selected.dataTime) : '';
}

function renderTyphoonSelectedRun(){
let slots=typhoonState.slots;
let selected=slots[typhoonState.selectedSlotIndex];
if(!selected){
renderTyphoonEmpty('표출 가능한 자료 없음');
return;
}

if(!selected.entry){
renderTyphoonMissingSlot(selected.dataTime);
return;
}

renderTyphoonRun(selected.entry);
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
renderTyphoonMissingSlot(run.dataTime);
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
let models=displayModelLabels(metadata);

let title=document.createElement('div');
title.className='typhoon-side-title';
title.textContent=cycleStormLabel(run);

let rows=document.createElement('div');
rows.className='typhoon-info-rows';

[
['자료시각',formatTyphoonTime(run.dataTime)],
['KST',formatTyphoonKst(run.dataTime)],
['예측기간',`${metadata.fcst_hours || '-'}h`],
['강도',metadata.intensity || '-'],
['모델',modelCountLabel(run)],
['ATCF',metadata.atcf_id || run.job?.atcf_id || '-'],
['TD',run.tdNumber ? `${run.tdNumber}호` : '-']
].forEach(([rowLabel,value])=>{
let row=document.createElement('div');
row.className='typhoon-info-row';
row.innerHTML=`<span>${escapeHtml(rowLabel)}</span><strong>${escapeHtml(value)}</strong>`;
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

function renderTyphoonMissingSlot(dataTime){
let viewer=typhoonState.root?.querySelector('[data-role="viewer"]');
let side=typhoonState.root?.querySelector('[data-role="sidePanel"]');
if(viewer){
viewer.innerHTML=`<div class="typhoon-status-panel">${escapeHtml(formatTyphoonTime(dataTime))} 자료 없음</div>`;
}
if(side){
side.innerHTML='';
}
}

function renderTyphoonEmpty(message){
let viewer=typhoonState.root?.querySelector('[data-role="viewer"]');
let side=typhoonState.root?.querySelector('[data-role="sidePanel"]');
let timeline=typhoonState.root?.querySelector('[data-role="timeline"]');
if(timeline){
timeline.innerHTML='';
}
if(viewer){
viewer.innerHTML=`<div class="typhoon-status-panel">${escapeHtml(message)}</div>`;
}
if(side){
side.innerHTML='';
}
updateTyphoonSubtitle();
renderTyphoonSelects();
}

function displayModelLabels(metadata){
let labels=Array.isArray(metadata.model_labels) ? metadata.model_labels : [];
if(labels.length){
return labels;
}
let models=Array.isArray(metadata.models) ? metadata.models : [];
let seen=new Set();
let result=[];
models.forEach(model=>{
let label=TYPHOON_MODEL_LABELS[model] || model;
if(!seen.has(label)){
seen.add(label);
result.push(label);
}
});
return result;
}

function stormDropdownLabel(entry){
if(entry.stage==='TD'){
return `TD ${entry.typNumber}호`;
}
let name=entry.typNameKo || entry.typName;
return `제${entry.typNumber}호 ${name}`.trim();
}

function cycleStormLabel(run){
let year=String(run.year || run.dataTime.slice(0,4)).slice(-2);
let cycloneId=run.typNumber ? `${year}${String(run.typNumber).padStart(2,'0')}` : '';
return `${cycloneId} ${run.typName}`.trim();
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

function formatTyphoonStamp(date){
return `${date.getUTCFullYear()}${pad2(date.getUTCMonth()+1)}${pad2(date.getUTCDate())}${pad2(date.getUTCHours())}${pad2(date.getUTCMinutes())}`;
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

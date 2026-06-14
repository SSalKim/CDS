const TYPHOON_MANIFEST_PATH='VTG_IMG/manifest.json';
const TYPHOON_STATUS_PATH='VTG_IMG/vtg_auto_status.json';
const TYPHOON_REFRESH_MS=10*60*1000;
const TYPHOON_SLOT_HOURS=6;
const TYPHOON_PAGE_CACHE_TOKEN=new URLSearchParams(window.location.search).get('fresh') || String(Date.now());
const TYPHOON_IMAGE_PRELOAD_RADIUS=4;
const TYPHOON_IMAGE_CACHE_LIMIT=80;
const TYPHOON_IMAGE_TIMEOUT_MS=20000;
const TYPHOON_FCST_OPTIONS=[
{hours:120,label:'5일예측'},
{hours:240,label:'10일예측'}
];

const TYPHOON_KO_NAME_FALLBACK={
JANGMI:'장미'
};

const TYPHOON_MODEL_LABELS={
KMA:'KMA OFCL',
ECMWF:'ECMWF',
ECMWF_EPS:'ECMWF EPS',
KIM_3h:'KIM',
KIM_6h:'KIM',
KIM_EPS:'KIM EPS',
UM:'UM',
UM_GFDL_6h:'UM',
UM_KEPS:'UM EPS',
UKM:'UKMO',
UKMO_EPS:'UKMO EPS',
GFS:'GFS',
GFS_EPS:'GFS EPS',
CMC:'CMC',
CMC_EPS:'CMC EPS',
NAVGEM:'NAVGEM',
FNMOC_EPS:'NAVGEM EPS',
JGSM:'JGSM',
TEPS:'JGSM EPS',
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
AIGEFS:'AIGFS EPS',
FNEC_AI:'FourCastNet-ECMWF',
FNKM_AI:'FourCastNet-KIM',
FNUM_AI:'FourCastNet-UM',
PGEC_AI:'Pangu-Weather-ECMWF',
PGKM_AI:'Pangu-Weather-KIM',
PGUM_AI:'Pangu-Weather-UM',
GCEC_AI:'GraphCast-ECMWF',
GCKM_AI:'GraphCast-KIM',
GCUM_AI:'GraphCast-UM',
GENC:'GenCast',
FNV3:'FNV3',
HKO_AREC: 'Aurora-ECMWF',
HKO_FXEC: 'FuXi-ECMWF',
HKO_FWEC: 'FengWu-ECMWF',
};

const TYPHOON_MODEL_INFO=[
{name:'ECMWF',description:'유럽중기예보센터(ECMWF) 전구모델(IFS)'},
{name:'ECMWF EPS',description:'유럽중기예보센터(ECMWF) 앙상블모델(EPS) 평균'},
{name:'KIM',description:'기상청 전구모델(KIM GDAPS)'},
{name:'KIM EPS',description:'기상청 앙상블모델(KIM GENS) 평균'},
{name:'UKMO',description:'영국기상청(UKMO) 전구모델(UM)'},
{name:'UKMO EPS',description:'영국기상청(UKMO) 앙상블모델(MOGREPS-G) 평균'},
{name:'GFS',description:'미해양대기청(NOAA NCEP) 전구모델(GFS)'},
{name:'GFS EPS',description:'미해양대기청(NOAA NCEP) 앙상블모델(GEFS) 평균'},
{name:'CMC',description:'캐나다기상센터(CMC) 전구모델(GEM GDPS)'},
{name:'CMC EPS',description:'캐나다기상센터(CMC) 앙상블모델(GEM GEPS) 평균'},
{name:'NAVGEM',description:'미해군수치기상해양센터(FNMOC) 전구모델(NAVGEM)'},
{name:'NAVGEM EPS',description:'미해군수치기상해양센터(FNMOC) 앙상블모델(NAVGEM EPS) 평균'},
{name:'JGSM',description:'일본기상청(JMA) 전구모델(GSM)'},
{name:'JGSM EPS',description:'일본기상청(JMA) 앙상블모델(GEPS)'},
{name:'COAMPS-TC',description:'미해군연구소(NRL) 태풍모델(COAMPS-TC) (GFS 초기장)'},
{name:'COAMPS-TC EPS',description:'미해군연구소(NRL) 앙상블모델(COAMPS-TC EPS) 평균'},
{name:'GALWEM',description:'미공군(USAF) 전구모델(UM)'},
{name:'HAFS',description:'미해양대기청(NOAA EMC) 태풍모델(HAFS-A)'},
{name:'HWRF',description:'미해양대기청(NOAA EMC) 태풍모델(HWRF)'},
{name:'ECMWF AIFS',description:'[AI] 유럽중기예보센터(ECMWF) AI 전구모델(AIFS-Single)'},
{name:'ECMWF AIFS EPS',description:'[AI] 유럽중기예보센터(ECMWF) AI 앙상블모델(AIFS-ENS)'},
{name:'KMA AIFS-ECMWF',description:'[AI] 기상청 수치예보센터 수행 AIFS (ECMWF 초기장)'},
{name:'KMA AIFS-KIM',description:'[AI] 기상청 수치예보센터 수행 AIFS (KIM 초기장)'},
{name:'AIGFS',description:'[AI] 미해양대기청(NOAA NCEP) AI 전구모델(AIGFS)'},
{name:'AIGFS EPS',description:'[AI] 미해양대기청(NOAA NCEP) AI 앙상블모델(AIGEFS) 평균'},
{name:'FourCastNet-ECMWF',description:'[AI] 기상청 수치예보센터 수행 FourCastNet (ECMWF 초기장)'},
{name:'FourCastNet-KIM',description:'[AI] 기상청 수치예보센터 수행 FourCastNet (KIM 초기장)'},
{name:'Pangu-Weather-ECMWF',description:'[AI] 기상청 수치예보센터 수행 Pangu-Weather (ECMWF 초기장)'},
{name:'Pangu-Weather-KIM',description:'[AI] 기상청 수치예보센터 수행 Pangu-Weather (KIM 초기장)'},
{name:'GraphCast-ECMWF',description:'[AI] 기상청 수치예보센터 수행 GraphCast (ECMWF 초기장)'},
{name:'GraphCast-KIM',description:'[AI] 기상청 수치예보센터 수행 GraphCast (KIM 초기장)'},
{name:'GenCast',description:'[AI] 구글 딥마인드(GDM) 앙상블모델(GenCast) 평균'},
{name:'FNV3',description:'[AI] 구글 딥마인드(GDM) 앙상블 실험모델(FNV3) 평균'},
{name:'Aurora-ECMWF',description:'[AI] 홍콩기상청(HKO) 수행 Aurora (ECMWF 초기장)'},
{name:'FuXi-ECMWF',description:'[AI] 홍콩기상청(HKO) 수행 FuXi (ECMWF 초기장)'},
{name:'FengWu-ECMWF',description:'[AI] 홍콩기상청(HKO) 수행 FengWu (ECMWF 초기장)'},
];

const TYPHOON_DEFAULT_MODEL_TARGET=TYPHOON_MODEL_INFO.length;

const TYPHOON_MODEL_INFO_GROUP_ENDS=new Set([
'ECMWF EPS',
'KIM EPS',
'UKMO EPS',
'GFS EPS',
'CMC EPS',
'NAVGEM EPS',
'JGSM EPS',
'COAMPS-TC EPS',
'GALWEM',
'HWRF',
'ECMWF AIFS EPS',
'KMA AIFS-KIM',
'AIGFS EPS',
'FourCastNet-KIM',
'Pangu-Weather-KIM',
'GraphCast-KIM',
'FNV3',
'Aurora-ECMWF',
'FuXi-ECMWF',
'FengWu-ECMWF'
]);

const TYPHOON_MODEL_INFO_COLORS={
'ECMWF':'#ED2939',
'ECMWF EPS':'#FC6C85',
'KIM':'#FA8128',
'KIM EPS':'#FFB347',
'UKMO':'#FFF200',
'UM EPS':'#B8CE9E',
'UKMO EPS':'#B8CE9E',
'GFS':'#03C04A',
'GFS EPS':'#7DDBA7',
'CMC':'#0CCBF0',
'CMC EPS':'#AAF7F4',
'NAVGEM':'#4470AD',
'NAVGEM EPS':'#99AFD7',
'JGSM':'#997950',
'JGSM EPS':'#654321',
'COAMPS-TC':'#78081C',
'COAMPS-TC EPS':'#A13B4E',
'GALWEM':'#4F746C',
'HAFS':'#9D5E5C',
'HWRF':'#9E9E9E',
'ECMWF AIFS':'#C71585',
'ECMWF AIFS EPS':'#E34FA5',
'KMA AIFS-ECMWF':'#C8A3D3',
'KMA AIFS-KIM':'#DDA520',
'AIGFS':'#E0FF78',
'AIGFS EPS':'#78FF8F',
'FourCastNet-ECMWF':'#004B1C',
'FourCastNet-KIM':'#388E3C',
'Pangu-Weather-ECMWF':'#3944BC',
'Pangu-Weather-KIM':'#727EF2',
'Pangu-Weather-UM':'#8EA2FF',
'GraphCast-ECMWF':'#4D248D',
'GraphCast-KIM':'#6C33C6',
'GraphCast-UM':'#B57AD5',
'GenCast':'#9866C7',
'FNV3':'#DA70D6',
'Aurora-ECMWF':'#1E90FF',
'FuXi-ECMWF':'#20B2AA',
'FengWu-ECMWF':'#A6C875'
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
selectedFcstHours:120,
timer:null,
keyboardBound:false,
imageCache:new Map(),
imageRequestSeq:0
};

function openTyphoonGuidancePage(){
window.open('typhoon.html','_blank','noopener');
}

function reloadTyphoonGuidancePage(){
let url=new URL(window.location.href);
url.searchParams.set('fresh',String(Date.now()));
window.location.replace(url.toString());
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

if(!typhoonState.keyboardBound){
document.addEventListener('keydown',handleTyphoonKeydown);
typhoonState.keyboardBound=true;
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

let titleWrap=document.createElement('button');
titleWrap.type='button';
titleWrap.className='typhoon-title-wrap typhoon-title-button';
titleWrap.title='페이지 새로고침';
titleWrap.onclick=reloadTyphoonGuidancePage;

let title=document.createElement('div');
title.className='typhoon-title';
title.innerHTML='<span>태풍</span><span>모델예측</span>';

titleWrap.appendChild(title);

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

let updatedAt=document.createElement('div');
updatedAt.className='typhoon-updated-time';
updatedAt.dataset.role='subtitle';
updatedAt.textContent='';

controls.appendChild(yearSelect);
controls.appendChild(stormSelect);
controls.appendChild(createTyphoonFcstSelector());

header.appendChild(titleWrap);
header.appendChild(controls);
header.appendChild(updatedAt);

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
setTyphoonSlotIndex(Number(event.target.value));
};

let timeline=document.createElement('div');
timeline.className='forecast-timeline compare-timeline single-timeline typhoon-timeline';
timeline.dataset.role='timeline';

let timeLabel=document.createElement('div');
timeLabel.className='forecast-label-hidden';
timeLabel.dataset.role='timeLabel';

shell.appendChild(slider);
shell.appendChild(timeline);
shell.appendChild(timeLabel);
timeBar.appendChild(shell);

let viewer=document.createElement('div');
viewer.className='typhoon-viewer';
viewer.dataset.role='viewer';

let content=document.createElement('div');
content.className='typhoon-content';
content.appendChild(viewer);
content.appendChild(createTyphoonModelInfoPanel());

page.appendChild(header);
page.appendChild(timeBar);
page.appendChild(content);

root.replaceChildren(page);
}

function createTyphoonModelInfoPanel(){
let panel=document.createElement('aside');
panel.className='typhoon-model-info-panel';
panel.setAttribute('aria-label','태풍 모델 설명');

let list=document.createElement('div');
list.className='typhoon-model-info-list';

TYPHOON_MODEL_INFO.forEach(item=>{
let row=document.createElement('div');
row.className='typhoon-model-info-row';
if(TYPHOON_MODEL_INFO_GROUP_ENDS.has(item.name)){
row.classList.add('is-group-end');
}
row.style.setProperty('--typhoon-model-color',TYPHOON_MODEL_INFO_COLORS[item.name] || '#1d4ed8');

let name=document.createElement('div');
name.className='typhoon-model-info-name';
name.textContent=item.name;

let description=document.createElement('div');
description.className='typhoon-model-info-description';
description.textContent=item.description;

row.appendChild(name);
row.appendChild(description);
list.appendChild(row);
});

panel.appendChild(list);
return panel;
}

function createTyphoonFcstSelector(){
let group=document.createElement('div');
group.className='typhoon-fcst-toggle';
group.setAttribute('role','radiogroup');
group.setAttribute('aria-label','예측기간');

TYPHOON_FCST_OPTIONS.forEach(option=>{
let label=document.createElement('label');
label.className='typhoon-fcst-option';

let input=document.createElement('input');
input.type='radio';
input.name='typhoonFcstHours';
input.value=String(option.hours);
input.dataset.role='fcstOption';
input.checked=typhoonState.selectedFcstHours===option.hours;
input.onchange=()=>{
let currentDataTime=getSelectedTyphoonDataTime();
typhoonState.selectedFcstHours=option.hours;
selectLatestSlotForStorm(currentDataTime);
renderTyphoonManifest();
};

let text=document.createElement('span');
text.textContent=option.label;

label.appendChild(input);
label.appendChild(text);
group.appendChild(label);
});

return group;
}

async function loadTyphoonManifest(){
let root=typhoonState.root;
if(!root){
return;
}

root.classList.add('typhoon-loading-state');

try{
let manifest=null;
let status=null;
let manifestError=null;

try{
manifest=await fetchTyphoonJson(TYPHOON_MANIFEST_PATH);
}
catch(error){
manifestError=error;
}

try{
status=await fetchTyphoonJson(TYPHOON_STATUS_PATH);
}
catch(error){
status=null;
}

if(!manifest && !status){
throw manifestError || new Error('HTTP 404');
}

typhoonState.manifest=manifest;
typhoonState.entries=normalizeTyphoonEntries(manifest || {},status);
pruneTyphoonImageCache();
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

async function fetchTyphoonJson(path){
let response=await fetch(`${path}?fresh=${Date.now()}`,{cache:'no-store'});
if(!response.ok){
throw new Error(`HTTP ${response.status}`);
}
return response.json();
}

function normalizeTyphoonEntries(manifest,status){
let source=Array.isArray(manifest?.inventory) && manifest.inventory.length ? manifest.inventory : manifest?.runs;
let runs=Array.isArray(source) ? source : [];
let statusRuns=normalizeStatusRuns(status);

let seen=new Set();
let normalized=[...runs,...statusRuns]
.map((entry,index)=>{
let metadata=entry?.result?.metadata || {};
let job=entry?.job || {};
let windowInfo=entry?.window || {};
let imagePath=normalizeTyphoonAssetPath(metadata.image_path || '');
let dataTime=metadata.data_time || job.data_time || windowInfo.data_time || '';
let generatedAt=metadata.generated_at_utc || manifest.updated_at_utc || '';
let fcstHours=Number(metadata.fcst_hours || job.fcst_hours || parseTyphoonFcstHoursFromPath(imagePath) || 120);
let year=String(metadata.storm_year || job.year || dataTime.slice(0,4) || '');
let stage=(metadata.storm_stage || job.stage || 'TYP').toUpperCase();
let typNumber=Number(metadata.typ_number || job.typ_number || 0);
let tdNumber=metadata.linked_td_number || job.linked_td_number || job.td_number || null;
let linkedTypNumber=metadata.linked_typ_number || job.linked_typ_number || null;
let typName=normalizeTyphoonName(metadata.typ_name || job.typ_name || 'NONAME');
let typNameKo=metadata.typ_name_ko || job.typ_name_ko || koreanTyphoonName(typName);
let stormKey=[year,stage,typNumber,typName].join('|');
return applyTyphoonSortKey({
index,
entry,
metadata,
job,
windowInfo,
imagePath,
dataTime,
generatedAt,
fcstHours,
year,
stage,
typNumber,
tdNumber,
linkedTypNumber,
typNameKo,
typName,
stormKey
});
})
.filter(run=>run.year && run.dataTime && run.imagePath && !run.metadata?.no_output)
.filter(run=>{
let key=`${run.year}|${run.stage}|${run.typNumber}|${run.dataTime}|${run.fcstHours}|${run.imagePath}`;
if(seen.has(key)){
return false;
}
seen.add(key);
return true;
});

return dedupeLinkedTyphoonEntries(linkTdEntriesToTyphoons(normalized))
.sort((a,b)=>a.sortKey.localeCompare(b.sortKey));
}

function applyTyphoonSortKey(run){
run.sortKey=`${run.year}${String(run.typNumber).padStart(2,'0')}${run.dataTime}${String(run.fcstHours).padStart(3,'0')}${run.generatedAt}`.padEnd(37,'0');
return run;
}

function linkTdEntriesToTyphoons(entries){
let tdLinks=new Map();
let typLinks=new Map();
entries.forEach(entry=>{
if(entry.stage==='TD' || !entry.tdNumber){
if(entry.stage!=='TD' && entry.typNumber){
typLinks.set(`${entry.year}|${Number(entry.typNumber)}`,entry);
}
return;
}
tdLinks.set(`${entry.year}|${Number(entry.tdNumber)}`,entry);
if(entry.typNumber){
typLinks.set(`${entry.year}|${Number(entry.typNumber)}`,entry);
}
});

if(!tdLinks.size && !typLinks.size){
return entries;
}

return entries.map(entry=>{
if(entry.stage!=='TD'){
return entry;
}
let linked=tdLinks.get(`${entry.year}|${entry.typNumber}`);
if(!linked && entry.linkedTypNumber){
linked=typLinks.get(`${entry.year}|${Number(entry.linkedTypNumber)}`);
}
if(!linked){
return entry;
}
return applyTyphoonSortKey({
...entry,
originalStage:'TD',
stage:linked.stage,
typNumber:linked.typNumber,
typName:linked.typName,
typNameKo:linked.typNameKo,
tdNumber:entry.typNumber,
linkedTypNumber:entry.linkedTypNumber,
stormKey:linked.stormKey
});
});
}

function dedupeLinkedTyphoonEntries(entries){
let byKey=new Map();
entries.forEach(entry=>{
let key=`${entry.year}|${entry.stormKey}|${entry.dataTime}|${entry.fcstHours}`;
let existing=byKey.get(key);
if(!existing){
byKey.set(key,entry);
return;
}
if(existing.originalStage==='TD' && entry.originalStage!=='TD'){
byKey.set(key,entry);
return;
}
if(String(entry.generatedAt || '')>String(existing.generatedAt || '')){
byKey.set(key,entry);
}
});
return [...byKey.values()];
}

function normalizeStatusRuns(status){
let cycles=status?.cycles || {};
let entries=[];
Object.keys(cycles).forEach(dataTime=>{
let storms=cycles[dataTime] || {};
Object.keys(storms).forEach(stormKey=>{
let record=storms[stormKey] || {};
let metadata=record.metadata || {};
if(!metadata.data_time){
metadata={...metadata,data_time:dataTime};
}
let typName=normalizeTyphoonName(metadata.typ_name || 'NONAME');
entries.push({
job:{
storm_key:stormKey,
stage:metadata.storm_stage || 'TYP',
year:Number(metadata.storm_year || String(dataTime).slice(0,4)),
data_time:dataTime,
td_number:null,
linked_td_number:metadata.linked_td_number || null,
linked_typ_number:metadata.linked_typ_number || null,
typ_number:metadata.typ_number || 0,
typ_name:typName,
typ_name_ko:metadata.typ_name_ko || koreanTyphoonName(typName),
typ_en:typName,
atcf_id:metadata.atcf_id || '',
fcst_hours:metadata.fcst_hours || parseTyphoonFcstHoursFromPath(metadata.image_path || '') || 120,
skip_atcf:!!metadata.skip_atcf
},
window:{data_time:dataTime},
result:{status:record.last_status || 'status',metadata}
});
});
});
return entries;
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
return [...byKey.values()].sort((a,b)=>
String(b.latest || '').localeCompare(String(a.latest || '')) ||
Number(b.typNumber || 0)-Number(a.typNumber || 0) ||
a.label.localeCompare(b.label)
);
}

function selectDefaultStormForYear(){
let storms=buildTyphoonStormsForYear(typhoonState.selectedYear);
typhoonState.storms=storms;
typhoonState.selectedStormKey=storms.length ? storms[0].key : '';
selectLatestSlotForStorm();
}

function selectLatestSlotForStorm(preferredDataTime=''){
typhoonState.slots=buildTyphoonSlotsForStorm(typhoonState.selectedStormKey);
let latestAvailable=-1;
typhoonState.slots.forEach((slot,index)=>{
if(slot.entry){
latestAvailable=index;
}
});
let preferredIndex=preferredDataTime ? typhoonState.slots.findIndex(slot=>slot.dataTime===preferredDataTime && slot.entry) : -1;
typhoonState.selectedSlotIndex=Math.max(0,preferredIndex>=0 ? preferredIndex : latestAvailable);
}

function getSelectedTyphoonSlot(){
return typhoonState.slots[typhoonState.selectedSlotIndex] || null;
}

function getSelectedTyphoonRun(){
return getSelectedTyphoonSlot()?.entry || null;
}

function getSelectedTyphoonDataTime(){
return getSelectedTyphoonSlot()?.dataTime || '';
}

function setTyphoonSlotIndex(index){
let maxIndex=Math.max(0,typhoonState.slots.length-1);
let nextIndex=Math.max(0,Math.min(Number(index)||0,maxIndex));
if(nextIndex===typhoonState.selectedSlotIndex){
return;
}
typhoonState.selectedSlotIndex=nextIndex;
renderTyphoonSelectedRun();
renderTyphoonTimeline();
}

function moveTyphoonSelection(offset){
setTyphoonSlotIndex(typhoonState.selectedSlotIndex+offset);
}

function buildTyphoonSlotsForStorm(stormKey){
let entries=typhoonState.entries
.filter(entry=>entry.stormKey===stormKey)
.filter(entry=>entry.fcstHours===typhoonState.selectedFcstHours)
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

typhoonState.root?.querySelectorAll('[data-role="fcstOption"]').forEach(input=>{
input.checked=Number(input.value)===typhoonState.selectedFcstHours;
});
}

function updateTyphoonSubtitle(run=getSelectedTyphoonRun()){
let subtitle=typhoonState.root?.querySelector('[data-role="subtitle"]');
if(!subtitle){
return;
}
let updated=formatTyphoonKst(run?.generatedAt || run?.metadata?.generated_at_utc || '');
subtitle.textContent=updated && updated!=='-' ? `최근 업데이트 ${updated}` : '';
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
timeline.style.setProperty('--forecast-count',String(slots.length || 1));
slider.min='0';
slider.max=String(Math.max(0,slots.length-1));
slider.value=String(Math.min(typhoonState.selectedSlotIndex,Math.max(0,slots.length-1)));
slider.disabled=slots.length<=1;

let list=document.createElement('div');
list.className='compare-timeline-list single-timeline-list typhoon-timeline-list';

let row=document.createElement('div');
row.className='compare-timeline-row single-timeline-row typhoon-timeline-row';

let info=document.createElement('div');
info.className='compare-row-info';
info.innerHTML='<div class="compare-row-model">VTG</div>';

let track=document.createElement('div');
track.className='compare-track single-forecast-track typhoon-track';
track.tabIndex=0;
track.setAttribute('role','slider');
track.setAttribute('aria-label','태풍 모델예측 시각 슬라이더');
track.setAttribute('aria-valuemin','0');
track.setAttribute('aria-valuemax',String(Math.max(0,slots.length-1)));
track.setAttribute('aria-valuenow',String(typhoonState.selectedSlotIndex));
track.style.gridTemplateColumns=`repeat(${Math.max(1,slots.length)}, minmax(4px, 1fr))`;

slots.forEach((slot,index)=>{
let segment=document.createElement('button');
segment.type='button';
let classes=['compare-segment','forecast-segment',slot.entry?'state-available':'state-missing'];
if(index===typhoonState.selectedSlotIndex){
classes.push('active','active-time-label','active-lead-label');
}
if(index===0){
classes.push('edge-start');
}
if(index===slots.length-1){
classes.push('edge-end');
}
segment.className=classes.join(' ');
segment.dataset.index=String(index);
segment.dataset.time=formatTyphoonDateLabel(slot.dataTime);
segment.dataset.lead=formatTyphoonHourLabel(slot.dataTime);
segment.title=slot.entry ? formatTyphoonTime(slot.dataTime) : `${formatTyphoonTime(slot.dataTime)} 자료 없음`;
segment.onclick=()=>{
setTyphoonSlotIndex(index);
};
bindTyphoonTimelineHover(segment,list);
track.appendChild(segment);
});

let selected=slots[typhoonState.selectedSlotIndex];
if(selected){
track.appendChild(createTyphoonTimelineLabel('date',typhoonState.selectedSlotIndex,slots.length,selected.dataTime));
track.appendChild(createTyphoonTimelineLabel('hour',typhoonState.selectedSlotIndex,slots.length,selected.dataTime));
}

bindTyphoonTimelinePointer(track);

row.appendChild(info);
row.appendChild(track);
list.appendChild(row);
timeline.appendChild(list);

label.textContent=selected ? formatTyphoonTime(selected.dataTime) : '';
}

function bindTyphoonTimelineHover(segment,list){
segment.onpointerenter=()=>{
segment.classList.add('hover-sync','hover-time-label','hover-lead-label');
list.classList.add('is-hovering');
};
segment.onpointerleave=()=>{
segment.classList.remove('hover-sync','hover-time-label','hover-lead-label');
list.classList.remove('is-hovering');
};
}

function bindTyphoonTimelinePointer(track){
let dragging=false;
let dragRect=null;
let dragCount=1;
let activePointerId=null;

function indexFromClientX(clientX){
let rect=dragRect || track.getBoundingClientRect();
let x=Math.max(0,Math.min(clientX-rect.left,rect.width));
let count=dragCount || typhoonState.slots.length || 1;
return Math.max(0,Math.min(count-1,Math.floor((x/Math.max(1,rect.width))*count)));
}

function applyClientX(clientX){
setTyphoonSlotIndex(indexFromClientX(clientX));
}

function beginDrag(event){
if(event.button!==undefined && event.button!==0){
return false;
}
event.preventDefault();
track.focus?.({preventScroll:true});
dragRect=track.getBoundingClientRect();
dragCount=typhoonState.slots.length || 1;
dragging=true;
applyClientX(event.clientX);
return true;
}

function endPointerDrag(){
dragging=false;
dragRect=null;
dragCount=1;
activePointerId=null;
window.removeEventListener('pointermove',handleWindowPointerMove);
window.removeEventListener('pointerup',handleWindowPointerUp);
window.removeEventListener('pointercancel',handleWindowPointerUp);
}

function handleWindowPointerMove(event){
if(!dragging || (activePointerId!==null && event.pointerId!==activePointerId)){
return;
}
event.preventDefault();
applyClientX(event.clientX);
}

function handleWindowPointerUp(event){
if(activePointerId!==null && event.pointerId!==activePointerId){
return;
}
endPointerDrag();
}

track.onpointerdown=event=>{
if(!beginDrag(event)){
return;
}
activePointerId=event.pointerId;
window.addEventListener('pointermove',handleWindowPointerMove);
window.addEventListener('pointerup',handleWindowPointerUp);
window.addEventListener('pointercancel',handleWindowPointerUp);
};

track.onmousedown=event=>{
if(window.PointerEvent || dragging || !beginDrag(event)){
return;
}

let handleMove=moveEvent=>applyClientX(moveEvent.clientX);
let handleUp=()=>{
dragging=false;
dragRect=null;
dragCount=1;
window.removeEventListener('mousemove',handleMove);
window.removeEventListener('mouseup',handleUp);
};

window.addEventListener('mousemove',handleMove);
window.addEventListener('mouseup',handleUp);
};
}

function handleTyphoonKeydown(event){
let active=document.activeElement;
let tag=active?.tagName;

if(tag==='INPUT' || tag==='SELECT' || tag==='TEXTAREA'){
return;
}

if(event.key==='ArrowLeft' || event.key==='ArrowUp'){
event.preventDefault();
moveTyphoonSelection(-1);
return;
}

if(event.key==='ArrowRight' || event.key==='ArrowDown'){
event.preventDefault();
moveTyphoonSelection(1);
}
}

function renderTyphoonSelectedRun(){
let selected=getSelectedTyphoonSlot();
if(!selected){
updateTyphoonSubtitle(null);
renderTyphoonEmpty('표출 가능한 자료 없음');
return;
}

if(!selected.entry){
updateTyphoonSubtitle(null);
renderTyphoonMissingSlot(selected.dataTime);
return;
}

renderTyphoonRun(selected.entry);
}

function getTyphoonImageUrl(run){

if(!run?.imagePath){
return '';
}

let version=run.generatedAt || run.metadata?.generated_at_utc || typhoonState.manifest?.updated_at_utc || '';
return cacheBustedTyphoonPath(run.imagePath,version);

}

function configureTyphoonImageElement(image,url){

image.className='typhoon-guidance-image';
image.alt='태풍 모델예측 이미지';
image.decoding='async';
image.loading='eager';
image.dataset.cacheUrl=url;
return image;

}

function getTyphoonActiveImageUrls(){

return new Set(
typhoonState.entries
.map(run=>getTyphoonImageUrl(run))
.filter(Boolean)
);

}

function pruneTyphoonImageCache(){

let activeUrls=getTyphoonActiveImageUrls();

for(let url of typhoonState.imageCache.keys()){
if(!activeUrls.has(url)){
typhoonState.imageCache.delete(url);
}
}

while(typhoonState.imageCache.size>TYPHOON_IMAGE_CACHE_LIMIT){
let oldest=typhoonState.imageCache.keys().next().value;
if(!oldest){
break;
}
typhoonState.imageCache.delete(oldest);
}

}

function loadTyphoonCachedImage(run){

let url=getTyphoonImageUrl(run);

if(!url){
return Promise.resolve({ok:false,url:'',image:null});
}

let cached=typhoonState.imageCache.get(url);
if(cached){
return cached.promise;
}

let promise=new Promise(resolve=>{
let done=false;
let image=configureTyphoonImageElement(new Image(),url);

let timer=setTimeout(()=>{
if(done){return;}
done=true;
resolve({ok:false,url,image:null});
},TYPHOON_IMAGE_TIMEOUT_MS);

image.onload=async()=>{
if(done){return;}

try{
if(typeof image.decode==='function'){
await image.decode();
}
}
catch(e){}

if(done){return;}
done=true;
clearTimeout(timer);
resolve({ok:true,url,image});
};

image.onerror=()=>{
if(done){return;}
done=true;
clearTimeout(timer);
resolve({ok:false,url,image:null});
};

image.src=url;
});

typhoonState.imageCache.set(url,{url,promise});

promise.then(result=>{
if(!result?.ok){
typhoonState.imageCache.delete(url);
}
});

pruneTyphoonImageCache();
return promise;

}

function preloadNearbyTyphoonImages(centerIndex=typhoonState.selectedSlotIndex){

let slots=typhoonState.slots || [];
let start=Math.max(0,Number(centerIndex)-TYPHOON_IMAGE_PRELOAD_RADIUS);
let end=Math.min(slots.length-1,Number(centerIndex)+TYPHOON_IMAGE_PRELOAD_RADIUS);

for(let i=start;i<=end;i++){
let run=slots[i]?.entry;
if(run){
loadTyphoonCachedImage(run);
}
}

}

function createTyphoonStatusPanel(message,{hidden=false}={}){

let panel=document.createElement('div');
panel.className='typhoon-status-panel'+(hidden?' hidden':'');
panel.textContent=message;
return panel;

}

async function renderTyphoonRun(run){
let viewer=typhoonState.root?.querySelector('[data-role="viewer"]');
if(!viewer){
return;
}

updateTyphoonSubtitle(run);

let requestId=++typhoonState.imageRequestSeq;

if(!run.imagePath){
renderTyphoonMissingSlot(run.dataTime);
return;
}

let url=getTyphoonImageUrl(run);
let currentImage=viewer.querySelector('.typhoon-guidance-image');

preloadNearbyTyphoonImages(typhoonState.selectedSlotIndex);

if(currentImage?.dataset.cacheUrl===url && currentImage.complete){
return;
}

if(!currentImage){
viewer.replaceChildren(createTyphoonStatusPanel('이미지 로딩 중'));
}

let result=await loadTyphoonCachedImage(run);

if(requestId!==typhoonState.imageRequestSeq){
return;
}

if(result.ok && result.image){
let error=createTyphoonStatusPanel('이미지 로드 실패',{hidden:true});
viewer.replaceChildren(result.image,error);
return;
}

viewer.replaceChildren(createTyphoonStatusPanel('이미지 로드 실패'));
return;

viewer.innerHTML='';

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
}

function renderTyphoonMissingSlot(dataTime){
typhoonState.imageRequestSeq++;
let viewer=typhoonState.root?.querySelector('[data-role="viewer"]');
if(viewer){
viewer.innerHTML=`<div class="typhoon-status-panel">${escapeHtml(formatTyphoonTime(dataTime))} 자료 없음</div>`;
}
}

function renderTyphoonEmpty(message){
typhoonState.imageRequestSeq++;
let viewer=typhoonState.root?.querySelector('[data-role="viewer"]');
let timeline=typhoonState.root?.querySelector('[data-role="timeline"]');
if(timeline){
timeline.innerHTML='';
}
if(viewer){
viewer.innerHTML=`<div class="typhoon-status-panel">${escapeHtml(message)}</div>`;
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
return `제${entry.typNumber}호 TD`;
}
let name=entry.typNameKo || koreanTyphoonName(entry.typName) || entry.typName;
return `제${entry.typNumber}호 태풍 ${name}`.trim();
}

function normalizeTyphoonName(name){
let text=String(name || '').trim();
return text;
}

function koreanTyphoonName(name){
return TYPHOON_KO_NAME_FALLBACK[String(name || '').trim().toUpperCase()] || '';
}

function cycleStormLabel(run){
let year=String(run.year || run.dataTime.slice(0,4)).slice(-2);
let cycloneId=run.typNumber ? `${year}${String(run.typNumber).padStart(2,'0')}` : '';
return `${cycloneId} ${run.typName}`.trim();
}

function modelCountLabel(run){
let metadata=run.metadata || {};
let count=metadata.model_count;
let target=metadata.target_model_count || TYPHOON_DEFAULT_MODEL_TARGET;
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

function parseTyphoonFcstHoursFromPath(value){
let match=String(value || '').match(/_(\d{2,3})h\.png(?:$|\?)/i);
return match ? Number(match[1]) : 0;
}

function cacheBustedTyphoonPath(path,version){
if(!path){
return '';
}
let separator=path.includes('?') ? '&' : '?';
let cacheKey=[version,TYPHOON_PAGE_CACHE_TOKEN].filter(Boolean).join('-') || Date.now();
return `${path}${separator}fresh=${encodeURIComponent(cacheKey)}`;
}

function formatCycleCompact(value){
if(!value || value.length<10){
return '-';
}
return `${value.slice(4,6)}-${value.slice(6,8)} ${value.slice(8,10)}UTC`;
}

function formatTyphoonDateLabel(value){
if(!value || value.length<8){
return '-';
}
return `${value.slice(4,6)}.${value.slice(6,8)}`;
}

function formatTyphoonHourLabel(value){
if(!value || value.length<10){
return '-';
}
return `${value.slice(8,10)}UTC`;
}

function getTyphoonTimelineLabelLeftPercent(index,count){
if(count<=1){
return 50;
}
return ((Number(index)+0.5)/count)*100;
}

function createTyphoonTimelineLabel(type,index,count,dataTime){
let label=document.createElement('div');
let isDate=type==='date';
label.className='compare-active-label '+(isDate?'compare-active-time':'compare-active-lead');
label.textContent=isDate ? formatTyphoonDateLabel(dataTime) : formatTyphoonHourLabel(dataTime);
if(index===0){
label.classList.add('edge-start');
}
if(index===count-1){
label.classList.add('edge-end');
}
let leftPercent=getTyphoonTimelineLabelLeftPercent(index,count)+'%';
label.style.left=leftPercent;
label.style.setProperty('--label-left',leftPercent);
return label;
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
return `${date.getUTCFullYear()}-${pad2(date.getUTCMonth()+1)}-${pad2(date.getUTCDate())} ${pad2(date.getUTCHours())}:${pad2(date.getUTCMinutes())} KST`;
}

function parseTyphoonUtcDate(value){
let raw=String(value || '').trim();
if(!raw){
return null;
}
if(!/^\d{10,14}$/.test(raw)){
let date=new Date(raw);
return Number.isNaN(date.getTime()) ? null : date;
}
let year=Number(raw.slice(0,4));
let month=Number(raw.slice(4,6))-1;
let day=Number(raw.slice(6,8));
let hour=Number(raw.slice(8,10));
let minute=Number(raw.slice(10,12) || 0);
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

(function(global){
'use strict';

// Estimated publication windows in UTC from image timestamps on KMA and R2 (2026-11-20..23):
// start = median time of the first lead, end = latest time of the last lead, both rounded up
// to 5 minutes so an estimate errs late rather than early.
// Each run is checked against real data: R2 runs through the snapshot the viewer holds (and
// their upload times through HEAD requests), KMA runs by loading the first or last lead image.
const KMA_BASE='https://data.kma.go.kr/CHT';
const SCHEDULE=[
{model:'KIM_GDAPS',status:'kim_gdps',kma:['KIMG','kim_gdps_erly_asia_gph500_ft06_pa4_s{fh}_{run}.png'],runs:[
[0,'000~288','kma','03:20','05:50'],[6,'000~084','kma','09:20','10:05'],
[12,'000~288','kma','15:20','17:50'],[18,'000~084','kma','21:20','22:00']]},
// UKUM 00/12Z: 000-144 h come from KMA, 156/168 h from R2 once KMA has released 144 h.
{model:'UKUM',id:'ukmo',status:'ukmo',kma:['GDPS','ukum_erly_asia_gph500_s{fh}_{run}.png'],runs:[
[0,'000~168','kma','09:40','09:55',{last:'public'}],[6,'000~069','self','11:35','12:10'],
[12,'000~168','kma','22:35','22:55',{last:'public'}],[18,'000~069','self','23:35','00:15']]},
{model:'ECMWF',id:'ecmwf',status:'ecmwf',kma:['ECMW','ecmw_lc40_asia_gph500_s{fh}_{run}.gif'],runs:[
[0,'000~240','kma','05:55','07:00'],[0,'252~360','self','07:40','07:45'],[6,'000~144','self','12:30','12:45'],
[12,'000~240','kma','17:55','19:00'],[12,'252~360','self','19:40','19:45'],[18,'000~144','self','00:30','00:45']]},
{model:'AIFS',id:'aifs',runs:[
[0,'000~360','self','05:30','05:35'],[6,'000~360','self','11:25','11:40'],
[12,'000~360','self','17:25','17:35'],[18,'000~360','self','23:30','23:40']]},
{model:'GFS',id:'gfs',runs:[
[0,'000~360','self','03:35','05:10'],[6,'000~360','self','09:35','11:15'],
[12,'000~360','self','15:35','17:10'],[18,'000~360','self','21:40','23:15']]},
{model:'AIGFS',id:'aigfs',runs:[
[0,'000~360','self','03:45','04:20'],[6,'000~360','self','09:45','10:50'],
[12,'000~360','self','15:45','16:25'],[18,'000~360','self','21:45','22:50']]},
{model:'CMC',id:'cmc',runs:[[0,'000~240','self','04:05','04:50'],[12,'000~240','self','15:55','17:00']]},
{model:'ICON',id:'icon',runs:[
[0,'000~180','self','02:45','03:30'],[6,'000~120','self','08:45','09:20'],
[12,'000~180','self','14:45','15:35'],[18,'000~120','self','20:45','21:20']]},
{model:'KIM_RDAPS',status:'kim_rdps',kma:['KIMR1','kim_rdps_erly_asia_gph500_s{fh}_{run}.png'],runs:[
[0,'000~120','kma','03:55','05:30'],[6,'000~072','kma','09:45','10:50'],
[12,'000~120','kma','15:55','17:25'],[18,'000~072','kma','21:45','22:45']]},
{model:'KIM_LDAPS',status:'kim_ldps',kma:['KIML','kim_ldps_erly_hkor_gph500_s{fh}_{run}.png'],runs:[
[0,'000~048','kma','04:00','04:55'],[6,'000~048','kma','09:45','10:40'],
[12,'000~048','kma','15:55','16:55'],[18,'000~048','kma','21:45','22:40']]},
{model:'KIM_KLAPS',hourly:{leads:'000~012',source:'kma',start:15,end:20}}
];
const MODELS=SCHEDULE.filter(entry=>!entry.hourly).map(entry=>entry.model);
const SOURCE_LABEL={kma:'기상청',self:'자체생산'};
const STATE_LABEL={done:'완료',live:'생산중',next:'예정',late:'지연'};
const DAY=1440;
const MINUTE=60000;
const HOUR_MS=3600000;
// Runs whose estimated end is older than this are taken as finished and not checked;
// KMA checks load a whole chart image (0.2-0.6 MB), so the window stays short.
const LATE_WINDOW=3*60;
const LONG_LATE_WINDOW=6*60;
const TAB_STORE='cds.schedule.tab';
const DONE_STORE='cds.schedule.show-done';
// The 24 h timeline starts at 02:00 UTC (11:00 KST) so each day reads 00Z, 06Z, 12Z, 18Z.
const AXIS_START_UTC=2*60;
const PRODUCT={category:'asia',id:'gph500'};

const minutes=text=>{const [h,m]=text.split(':').map(Number);return h*60+m;};
const pad=value=>String(value).padStart(2,'0');
const clock=value=>{const m=((value%DAY)+DAY)%DAY;return pad(Math.floor(m/60))+':'+pad(m%60);};
const offsetFor=mode=>mode==='UTC'?0:540;
const axisMinute=(value,offset)=>((value-AXIS_START_UTC-offset)%DAY+DAY)%DAY;
const leadRange=leads=>leads.split('~').map(Number);
const dayMinute=ms=>Math.floor((ms%86400000)/MINUTE);
const nowMs=()=>global.CDSPublicCharts?.clockNow?.()??Date.now();

function windows(){
const rows=[];
for(const entry of SCHEDULE){
if(entry.hourly){
for(let hour=0;hour<24;hour++) rows.push({model:entry.model,cycle:hour,leads:entry.hourly.leads,source:entry.hourly.source,
start:hour*60+entry.hourly.start,end:hour*60+entry.hourly.end,hourly:true});
continue;
}
for(const [cycle,leads,source,start,end,checks={}] of entry.runs){
let from=minutes(start),to=minutes(end);
if(to<from) to+=DAY;
const kind=source==='self'?'public':'kma';
rows.push({model:entry.model,id:entry.id,kma:entry.kma,status:source==='kma'?entry.status:undefined,cycle,leads,source,start:from,end:to,
firstCheck:checks.first||kind,lastCheck:checks.last||kind});
}
}
return rows;
}

// Every occurrence of every window from two days back to one day ahead, as absolute times.
function occurrences(now){
const midnight=Math.floor(now/86400000)*86400000;
const result=[];
for(const row of windows()){
if(row.hourly) continue;
const lag=((row.start-row.cycle*60)%DAY+DAY)%DAY;
for(const day of [-2,-1,0,1]){
const startMs=midnight+(day*DAY+row.start)*MINUTE;
const endMs=midnight+(day*DAY+row.end)*MINUTE;
const cycleMs=Math.round((startMs-lag*MINUTE)/HOUR_MS)*HOUR_MS;
result.push({...row,startMs,endMs,cycleMs,key:`${row.model}|${row.cycle}|${row.leads}|${cycleMs}`});
}
}
return result;
}

// ---------- Real data ----------
const probeCache=new Map();
function kmaImageLoads(url){
const cached=probeCache.get(url);
if(cached && (cached.ok || Date.now()-cached.at<120000)) return cached.promise;
const promise=new Promise(resolve=>{
const image=new Image();
const timer=setTimeout(()=>resolve(null),10000);
image.onload=()=>{clearTimeout(timer);resolve(image.naturalWidth>0);};
image.onerror=()=>{clearTimeout(timer);resolve(false);};
image.referrerPolicy='no-referrer';
image.src=url;
});
const entry={promise,at:Date.now(),ok:false};
promise.then(ok=>{entry.ok=ok===true;});
probeCache.set(url,entry);
return promise;
}

const timeCache=new Map();
function uploadTime(url){
if(!timeCache.has(url)){
const promise=fetch(url,{method:'HEAD',credentials:'omit'})
.then(response=>{
const value=response.ok?Date.parse(response.headers.get('Last-Modified')||''):NaN;
if(!Number.isFinite(value)) timeCache.delete(url);
return Number.isFinite(value)?value:null;
})
.catch(()=>{timeCache.delete(url);return null;});
timeCache.set(url,promise);
}
return timeCache.get(url);
}

function cycleText(ms){
const d=new Date(ms);
return d.getUTCFullYear()+pad(d.getUTCMonth()+1)+pad(d.getUTCDate())+pad(d.getUTCHours());
}

// KMA release times published by the producer (status/releases.json on R2). The browser cannot
// read KMA response headers, so this is where KMA runs get real times; it also spares the
// viewer from loading whole chart images to see whether a run is out.
const RELEASE_KEY='status/releases.json';
const RELEASE_STALE=20*MINUTE;
async function loadReleases(now){
const origin=global.CDSPublicCharts?.getR2Base?.();
if(!origin) return null;
try{
const response=await fetch(origin+RELEASE_KEY,{cache:'no-store',credentials:'omit'});
if(!response.ok) return null;
const status=await response.json();
const at=Date.parse(status?.generated_at);
if(status?.schema!==1 || !Number.isFinite(at) || now-at>RELEASE_STALE || typeof status.runs!=='object') return null;
return status.runs;
}catch{return null;}
}

function releaseEntry(run,ctx){
if(!ctx.releases || !run.status) return undefined;
return ctx.releases[`${run.status}/${cycleText(run.cycleMs)}`]||null;
}

// true / false, or null when it cannot be told (no fresh R2 snapshot, KMA not answering).
function leadExists(run,hour,kind,ctx){
if(kind==='public'){
const store=global.CDSPublicCharts;
if(!ctx.publicFresh || !store?.readyHours || !run.id) return Promise.resolve(null);
const hours=store.readyHours({modelId:run.id,product:PRODUCT,runUTC:new Date(run.cycleMs)});
return Promise.resolve(hours.includes(hour));
}
const entry=releaseEntry(run,ctx);
if(entry!==undefined){
if(!entry) return Promise.resolve(false);
return Promise.resolve(Boolean(hour===entry.leads?.[0]?entry.first:entry.last));
}
if(!run.kma) return Promise.resolve(null);
const text=cycleText(run.cycleMs);
const [folder,template]=run.kma;
const name=template.replace('{fh}',String(hour).padStart(3,'0')).replace('{run}',text);
return kmaImageLoads(`${KMA_BASE}/${folder}/${text.slice(0,6)}/${text.slice(6,8)}/${name}`);
}

// When a lead appeared: R2 upload time for self-produced runs, the producer's record of KMA's
// release for KMA runs (UKUM 00/12Z ends when KMA's 144 h is out, as 156/168 h wait for it).
function leadTime(run,hour,ctx){
if(run.source!=='self'){
const entry=releaseEntry(run,ctx);
const value=entry?Date.parse(hour===leadRange(run.leads)[0]?entry.first:entry.last):NaN;
return Promise.resolve(Number.isFinite(value)?value:null);
}
const store=global.CDSPublicCharts;
const origin=store?.getR2Base?.();
if(!ctx.publicFresh || !origin || !store?.resolveUrls) return Promise.resolve(null);
const url=store.resolveUrls({modelId:run.id,product:PRODUCT,runUTC:new Date(run.cycleMs),forecastHour:hour})[0];
return url&&url.startsWith(origin)?uploadTime(url):Promise.resolve(null);
}

async function resolveRun(run,now,ctx,deep){
const duration=run.endMs-run.startMs;
const estimate={...run,showStart:run.startMs,showEnd:run.endMs,realStart:false,realEnd:false};
if(run.cycleMs>now) return {...estimate,state:'next'};
// Old runs and runs far from starting are not checked.
const recent=run.endMs>=now-ctx.window*MINUTE;
if(!recent && !deep) return {...estimate,state:'done'};
if(now<run.startMs-HOUR_MS) return {...estimate,state:'next'};
const [first,last]=leadRange(run.leads);
const finished=await leadExists(run,last,run.lastCheck,ctx);
if(finished===true){
const [start,end]=await Promise.all([leadTime(run,first,ctx),leadTime(run,last,ctx)]);
return {...estimate,state:'done',showStart:start??run.startMs,showEnd:end??run.endMs,realStart:!!start,realEnd:!!end};
}
const started=await leadExists(run,first,run.firstCheck,ctx);
if(started===true){
const start=await leadTime(run,first,ctx);
const showStart=start??run.startMs;
// A late start pushes the end back; an early one does not pull it before the estimate.
const showEnd=Math.max(run.endMs,showStart+duration);
return {...estimate,state:now>showEnd&&recent?'late':now>showEnd?'done':'live',showStart,showEnd,realStart:!!start};
}
if(finished===false && started===false){
return {...estimate,state:now>run.endMs?(recent?'late':'done'):'next'};
}
// Unknown: fall back to the estimate alone, which never claims a delay.
return {...estimate,state:now<run.startMs?'next':now<run.endMs?'live':'done'};
}

async function resolveStates(now){
const store=global.CDSPublicCharts;
const ctx={publicFresh:false,releases:null,window:LATE_WINDOW};
const [loaded,releases]=await Promise.all([Promise.resolve(store?.load?.()).catch(()=>null),loadReleases(now)]);
ctx.publicFresh=loaded?.ok===true && store.getSource?.()==='r2';
ctx.releases=releases;
// With the producer's record no KMA image has to be loaded, so lateness is watched longer.
if(releases) ctx.window=LONG_LATE_WINDOW;
const runs=occurrences(now);
// Each stream's latest older run gets its real times too (it is what "최근 완료" shows) when
// they are cheap to read: R2 upload times, or KMA times from the producer's record.
const older=new Map();
for(const run of runs){
if(run.endMs>=now-ctx.window*MINUTE || run.source!=='self' && !releases) continue;
const stream=`${run.model}|${run.cycle}|${run.leads}`;
if(!older.has(stream) || older.get(stream).cycleMs<run.cycleMs) older.set(stream,run);
}
const deep=new Set([...older.values()].map(run=>run.key));
return Promise.all(runs.map(run=>resolveRun(run,now,ctx,deep.has(run.key))
.catch(()=>({...run,showStart:run.startMs,showEnd:run.endMs,state:run.endMs<now?'done':'next'}))));
}

// ---------- Board selection ----------
const ACTIVE_ORDER={late:0,live:1,next:2};
function boardRows(states,{model,cycle,showDone}){
const pool=states.filter(run=>cycle===null||run.cycle===cycle);
const latestDone=list=>list.filter(run=>run.state==='done').sort((a,b)=>b.showEnd-a.showEnd)[0];
if(model){
const mine=pool.filter(run=>run.model===model);
const streams=new Set(mine.map(run=>run.cycle+'|'+run.leads)).size;
const ahead=mine.filter(run=>run.state!=='done').sort((a,b)=>a.showStart-b.showStart).slice(0,Math.max(1,streams-1));
return [latestDone(mine),...ahead].filter(Boolean);
}
const active=[],done=[];
for(const name of MODELS){
const mine=pool.filter(run=>run.model===name);
const pick=mine.filter(run=>run.state==='late').sort((a,b)=>b.showEnd-a.showEnd)[0]
||mine.filter(run=>run.state==='live').sort((a,b)=>a.showStart-b.showStart)[0]
||mine.filter(run=>run.state==='next').sort((a,b)=>a.showStart-b.showStart)[0];
if(pick) active.push(pick);
if(showDone){const last=latestDone(mine);if(last) done.push(last);}
}
active.sort((a,b)=>ACTIVE_ORDER[a.state]-ACTIVE_ORDER[b.state]||a.showStart-b.showStart);
done.sort((a,b)=>b.showEnd-a.showEnd);
return [...active,...done];
}

// ---------- Rendering ----------
function duration(value){
value=Math.max(0,Math.round(value));
if(value<60) return value+'분';
const h=Math.floor(value/60),m=value%60;
return m?`${h}시간 ${m}분`:`${h}시간`;
}

function element(tag,className,text){
const node=document.createElement(tag);
if(className) node.className=className;
if(text!==undefined) node.textContent=text;
return node;
}

function currentMode(){
try{return typeof timeMode==='string'&&timeMode==='UTC'?'UTC':'KST';}catch{return 'KST';}
}

function remainText(run,now){
if(run.state==='done') return duration((now-run.showEnd)/MINUTE)+' 전 완료';
if(run.state==='live') return duration((run.showEnd-now)/MINUTE)+' 남음';
if(run.state==='late') return duration((now-run.showEnd)/MINUTE)+' 지연';
return run.showStart>now?duration((run.showStart-now)/MINUTE)+' 후':'시작 대기';
}

function renderBoard(container,mode,now,states,filters){
container.replaceChildren();
const table=element('table','schedule-board');
const body=element('tbody');
if(!states){
const tr=element('tr','is-loading');
tr.append(element('td','schedule-board-empty','실제 자료를 확인하고 있습니다…'));
body.append(tr);
}else{
const rows=boardRows(states,filters);
if(!rows.length){
const tr=element('tr','is-loading');
tr.append(element('td','schedule-board-empty','조건에 맞는 자료가 없습니다.'));
body.append(tr);
}
const offset=offsetFor(mode)*MINUTE;
for(const run of rows){
const tr=element('tr','is-'+run.state);
const status=element('td','schedule-board-state');
status.append(element('span','schedule-state is-'+run.state,STATE_LABEL[run.state]));
const time=element('td','schedule-board-time');
time.append(element('span',run.realStart?'':'is-est',clock(dayMinute(run.showStart+offset))),
document.createTextNode('–'),
element('span',run.realEnd?'':'is-est',clock(dayMinute(run.showEnd+offset))));
const cycle=element('td','schedule-board-cycle');
cycle.append(element('mark','schedule-mark c'+pad(run.cycle),pad(run.cycle)+'Z'));
tr.append(status,time,
element('td','schedule-board-source',SOURCE_LABEL[run.source]),
element('td','schedule-board-model',run.model),
cycle,
element('td','schedule-board-leads','+'+run.leads+'h'),
element('td','schedule-board-remain',remainText(run,now)));
body.append(tr);
}
}
table.append(body);
container.append(table);
}

function renderTimeline(container,mode,now,filters,onSelect){
container.replaceChildren();
const offset=offsetFor(mode);
const axis=element('div','schedule-axis');
axis.append(element('span'));
const ticks=element('div','schedule-axis-track');
for(let hour=0;hour<24;hour+=3){
const tick=element('span','schedule-axis-tick',pad(hour));
tick.style.left=(axisMinute(hour*60,offset)/DAY*100)+'%';
ticks.append(tick);
}
axis.append(ticks);
container.append(axis);
const all=windows();
for(const entry of SCHEDULE){
const laneDim=filters.model&&filters.model!==entry.model;
const lane=element('div','schedule-lane'+(laneDim?' is-dim':''));
lane.append(element('span','schedule-lane-name',entry.model));
const track=element('div','schedule-lane-track');
for(const row of all.filter(item=>item.model===entry.model)){
const dim=laneDim||(filters.cycle!==null&&(row.hourly||row.cycle!==filters.cycle));
const start=axisMinute(row.start+offset,offset);
const length=Math.max(row.end-row.start,row.hourly?2:5);
const parts=start+length>DAY?[[start,DAY-start],[0,start+length-DAY]]:[[start,length]];
parts.forEach(([from,width],index)=>{
const bar=element('button',`schedule-bar is-${row.source}${row.hourly?' is-hourly':' c'+pad(row.cycle)}${dim?' is-dim':''}`);
bar.type='button';
bar.style.left=(from/DAY*100)+'%';
bar.style.width=(width/DAY*100)+'%';
const text=`${row.model} ${pad(row.cycle)}Z ${row.leads}h ${SOURCE_LABEL[row.source]} ${clock(row.start+offset)}~${clock(row.end+offset)} ${mode}`;
bar.title=text;bar.setAttribute('aria-label',text);
bar.addEventListener('click',()=>onSelect(row,bar));
track.append(bar);
if(!row.hourly && index===0){
const tag=element('span',`schedule-bar-tag c${pad(row.cycle)}${dim?' is-dim':''}`,pad(row.cycle)+'Z');
tag.style.left=(from/DAY*100)+'%';
track.append(tag);
}
});
}
lane.append(track);
container.append(lane);
}
const nowLine=element('div','schedule-now');
const nowMinutes=dayMinute(now);
nowLine.style.setProperty('--now',String(axisMinute(nowMinutes+offset,offset)/DAY));
nowLine.append(element('span','schedule-now-label',clock(nowMinutes+offset)));
container.append(nowLine);
}

// Cycle tags that would overlap the previous one in the same lane are hidden.
function hideCrowdedTags(root){
for(const track of root.querySelectorAll('.schedule-lane-track')){
let right=-Infinity;
const tags=[...track.querySelectorAll('.schedule-bar-tag')]
.sort((a,b)=>a.offsetLeft-b.offsetLeft);
for(const tag of tags){
tag.hidden=false;
// A tag at the far right is pulled back inside the track.
const overflow=tag.offsetLeft+tag.offsetWidth-track.clientWidth;
if(overflow>0) tag.style.left=(track.clientWidth-tag.offsetWidth)+'px';
const left=tag.offsetLeft;
if(left<right+3){tag.hidden=true;continue;}
right=left+tag.offsetWidth;
}
}
// Axis hours hidden under the "now" label.
const label=root.querySelector('.schedule-now-label')?.getBoundingClientRect();
for(const tick of root.querySelectorAll('.schedule-axis-tick')){
tick.style.visibility='';
const box=tick.getBoundingClientRect();
if(label && box.right>label.left-2 && box.left<label.right+2) tick.style.visibility='hidden';
}
}

function renderTable(container,mode,states){
container.replaceChildren();
const offset=offsetFor(mode);
const badges=new Map();
for(const run of states||[]){
const stream=run.model+run.cycle+run.leads;
if(run.state==='late') badges.set(stream,'late');
else if(run.state==='live' && badges.get(stream)!=='late') badges.set(stream,'live');
}
const table=element('table','schedule-table');
const head=element('thead');
const headRow=element('tr');
for(const text of ['모델','자료시각','예측시간','구분',`표출 (${mode})`]) headRow.append(element('th','',text));
head.append(headRow);
const body=element('tbody');
for(const entry of SCHEDULE){
const runs=entry.hourly
?[{cycle:null,label:'매시',leads:entry.hourly.leads,source:entry.hourly.source,time:`정시+${entry.hourly.start}~${entry.hourly.end}분`}]
:entry.runs.map(([cycle,leads,source,start,end])=>({cycle,label:pad(cycle)+'Z',leads,source,
time:`${clock(minutes(start)+offset)}–${clock(minutes(end)+offset)}`}));
runs.forEach((run,index)=>{
const state=run.cycle===null?'':badges.get(entry.model+run.cycle+run.leads)||'';
const tr=element('tr',state?'is-'+state:'');
if(index===0){
const name=element('th','schedule-table-model',entry.model);
name.scope='row';name.rowSpan=runs.length;
tr.append(name);
}
const time=element('td','schedule-table-time',run.time);
const cycle=element('td','schedule-table-cycle');
cycle.append(run.cycle===null?document.createTextNode(run.label):element('mark','schedule-mark c'+pad(run.cycle),run.label));
if(state) time.append(element('span','schedule-state is-'+state,STATE_LABEL[state]));
tr.append(cycle,element('td','schedule-table-leads',run.leads),
element('td','schedule-table-source',SOURCE_LABEL[run.source]),time);
body.append(tr);
});
}
table.append(head,body);
container.append(table);
}

// Horizontal overflow hint: fades the edge and shows ▶ while more content sits to the right.
function scrollHint(wrap){
const arrow=element('button','schedule-scroll-more','▶');
arrow.type='button';arrow.setAttribute('aria-label','오른쪽 내용 더 보기');arrow.tabIndex=-1;
arrow.onclick=()=>wrap.querySelector('.schedule-scroll')?.scrollBy({left:160,behavior:'smooth'});
wrap.append(arrow);
const update=()=>{
const scroller=wrap.querySelector('.schedule-scroll');
if(!scroller) return;
wrap.classList.toggle('has-more-right',scroller.scrollWidth-scroller.clientWidth-scroller.scrollLeft>4);
};
wrap.addEventListener('scroll',update,{capture:true,passive:true});
return update;
}

function open(){
const dialog=element('dialog','schedule-dialog');
dialog.setAttribute('aria-labelledby','scheduleTitle');
let mode=currentMode();
let tab='timeline';
try{if(localStorage.getItem(TAB_STORE)==='table') tab='table';}catch{}
const filters={model:null,cycle:null,showDone:false};
try{filters.showDone=localStorage.getItem(DONE_STORE)==='1';}catch{}
let states=null;

const header=element('header','schedule-header');
const title=element('h2','schedule-title','모델 표출 시간표');
title.id='scheduleTitle';
const modes=element('div','schedule-mode');
modes.setAttribute('role','group');modes.setAttribute('aria-label','시간 기준');
const modeButtons=['KST','UTC'].map(value=>{
const button=element('button','',value);button.type='button';
button.onclick=()=>{mode=value;render();};
modes.append(button);return button;
});
const close=element('button','schedule-close','×');
close.type='button';close.setAttribute('aria-label','시간표 닫기');close.title='닫기';
close.onclick=()=>dialog.close();
header.append(title,modes,close);

// Filters: recent completions, one model, one cycle.
const filterBar=element('div','schedule-filters');
const doneLabel=element('label','schedule-check');
const doneBox=element('input');doneBox.type='checkbox';doneBox.checked=filters.showDone;
doneBox.onchange=()=>{filters.showDone=doneBox.checked;try{localStorage.setItem(DONE_STORE,doneBox.checked?'1':'0');}catch{}render();};
doneLabel.append(doneBox,document.createTextNode('최근 완료된 모델도 표시'));
const modelLabel=element('label','schedule-select');
const modelSelect=element('select');
modelSelect.setAttribute('aria-label','모델 필터');
modelSelect.append(new Option('모델 전체',''));
for(const name of MODELS) modelSelect.append(new Option(name,name));
modelSelect.onchange=()=>{filters.model=modelSelect.value||null;render();};
modelLabel.append(modelSelect);
const cycleGroup=element('div','schedule-cycles');
cycleGroup.setAttribute('role','group');cycleGroup.setAttribute('aria-label','시간대 필터');
const cycleButtons=[[null,'전체'],[0,'00Z'],[6,'06Z'],[12,'12Z'],[18,'18Z']].map(([value,text])=>{
const button=element('button',value===null?'':'c'+pad(value),text);button.type='button';
button.onclick=()=>{filters.cycle=value;render();};
cycleGroup.append(button);return {value,button};
});
filterBar.append(doneLabel,modelLabel,cycleGroup);

const boardWrap=element('div','schedule-scroll-wrap');
const board=element('div','schedule-scroll schedule-board-wrap');
boardWrap.append(board);
const updateBoardHint=scrollHint(boardWrap);

const tabs=element('div','schedule-tabs');
tabs.setAttribute('role','tablist');
const tabButtons={};
for(const [value,text] of [['timeline','24시간'],['table','표']]){
const button=element('button','',text);button.type='button';button.setAttribute('role','tab');
button.onclick=()=>{tab=value;try{localStorage.setItem(TAB_STORE,tab);}catch{}render();};
tabButtons[value]=button;tabs.append(button);
}

const timeline=element('div','schedule-timeline');
const detail=element('p','schedule-detail');
detail.setAttribute('aria-live','polite');
const timelinePanel=element('div','schedule-panel');
timelinePanel.append(timeline,detail);
const tableWrap=element('div','schedule-panel schedule-scroll-wrap');
const tablePanel=element('div','schedule-scroll schedule-table-wrap');
tableWrap.append(tablePanel);
const updateTableHint=scrollHint(tableWrap);

const legend=element('footer','schedule-legend');
const sources=element('span','schedule-legend-group');
sources.append(element('i','schedule-key is-kma'),document.createTextNode('기상청'),
element('i','schedule-key is-self'),document.createTextNode('자체생산'));
const cycles=element('span','schedule-legend-group');
for(const cycle of [0,6,12,18]) cycles.append(element('mark','schedule-mark c'+pad(cycle),pad(cycle)+'Z'));
legend.append(sources,cycles,element('span','schedule-legend-note','최근 4일 실측 기준'));

dialog.append(header,filterBar,boardWrap,tabs,timelinePanel,tableWrap,legend);

let selected=null;
const select=(row,bar)=>{
selected=row;
timeline.querySelectorAll('.schedule-bar.is-selected').forEach(node=>node.classList.remove('is-selected'));
bar?.classList.add('is-selected');
const offset=offsetFor(mode);
detail.textContent=row.hourly
?`${row.model} 매시 · +${row.leads}h · ${SOURCE_LABEL[row.source]} · 정시+${row.start%60}~${row.end%60}분`
:`${row.model} ${pad(row.cycle)}Z · +${row.leads}h · ${SOURCE_LABEL[row.source]} · 추정 ${clock(row.start+offset)} 시작 → ${clock(row.end+offset)} 완료 (${mode})`;
};

function render(){
const now=nowMs();
modeButtons.forEach(button=>button.setAttribute('aria-pressed',String(button.textContent===mode)));
for(const [value,button] of Object.entries(tabButtons)) button.setAttribute('aria-selected',String(value===tab));
cycleButtons.forEach(({value,button})=>button.setAttribute('aria-pressed',String(value===filters.cycle)));
doneBox.disabled=!!filters.model;
doneLabel.classList.toggle('is-disabled',!!filters.model);
timelinePanel.hidden=tab!=='timeline';
tableWrap.hidden=tab!=='table';
renderBoard(board,mode,now,states,filters);
renderTimeline(timeline,mode,now,filters,select);
renderTable(tablePanel,mode,states);
const first=selected||(states&&boardRows(states,filters)[0]);
if(first){
const match=[...timeline.querySelectorAll('.schedule-bar')]
.find(bar=>bar.getAttribute('aria-label').startsWith(`${first.model} ${pad(first.cycle)}Z ${first.leads}h`));
select(first,match);
}
requestAnimationFrame(()=>{hideCrowdedTags(timeline);updateBoardHint();updateTableHint();});
}

let checking=false;
async function refresh(){
if(checking) return;
checking=true;
try{states=await resolveStates(nowMs());}
finally{checking=false;}
if(dialog.open) render();
}

const resize=()=>{hideCrowdedTags(timeline);updateBoardHint();updateTableHint();};
const timer=setInterval(()=>{if(dialog.open){render();refresh();}},60000);
dialog.addEventListener('close',()=>{clearInterval(timer);global.removeEventListener('resize',resize);dialog.remove();});
dialog.addEventListener('click',event=>{if(event.target===dialog) dialog.close();});
global.addEventListener('resize',resize);
document.body.append(dialog);
render();
dialog.showModal();
refresh();
}

function button(){
const node=element('button','viewer-icon-button schedule-button');
node.type='button';node.title='모델 표출 시간표';node.setAttribute('aria-label','모델 표출 시간표');
node.setAttribute('aria-haspopup','dialog');
node.append(CDSViewerIcons('Clock'),element('span','schedule-button-text','시간표'));
node.onclick=open;
return node;
}

global.CDSModelSchedule={button,open,windows,occurrences,resolveStates,boardRows,SCHEDULE};
})(window);

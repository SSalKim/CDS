(function(global){
'use strict';

// Approximate publication windows in UTC, measured from image timestamps on KMA and R2
// (2026-11-20..23). "start" is when the first lead appears, "end" when the last lead does.
// "check" says how to tell whether a run has finished: from the R2 snapshot the viewer
// already holds (public), or by loading the last lead's KMA image (kma: folder and file).
const KMA_BASE='https://data.kma.go.kr/CHT';
const SCHEDULE=[
{model:'KIM_GDAPS',kma:['KIMG','kim_gdps_erly_asia_gph500_ft06_pa4_s{fh}_{run}.png'],runs:[
[0,'000~288','kma','03:15','05:50'],[6,'000~084','kma','09:15','10:00'],
[12,'000~288','kma','15:15','17:50'],[18,'000~084','kma','21:15','22:00']]},
{model:'UKUM',id:'ukmo',runs:[
[0,'000~168','kma','09:35','09:50','public'],[6,'000~069','self','11:30','12:05'],
[12,'000~168','kma','22:35','22:50','public'],[18,'000~069','self','23:30','00:10']]},
{model:'ECMWF',id:'ecmwf',kma:['ECMW','ecmw_lc40_asia_gph500_s{fh}_{run}.gif'],runs:[
[0,'000~240','kma','05:50','07:00'],[0,'252~360','self','07:35','07:45'],[6,'000~144','self','12:25','12:40'],
[12,'000~240','kma','17:50','19:00'],[12,'252~360','self','19:35','19:45'],[18,'000~144','self','00:25','00:40']]},
{model:'AIFS',id:'aifs',runs:[
[0,'000~360','self','05:20','05:35'],[6,'000~360','self','11:20','11:35'],
[12,'000~360','self','17:20','17:35'],[18,'000~360','self','23:25','23:35']]},
{model:'GFS',id:'gfs',runs:[
[0,'000~360','self','03:30','05:10'],[6,'000~360','self','09:30','11:10'],
[12,'000~360','self','15:30','17:10'],[18,'000~360','self','21:30','23:10']]},
{model:'AIGFS',id:'aigfs',runs:[
[0,'000~360','self','03:40','04:20'],[6,'000~360','self','09:35','10:20'],
[12,'000~360','self','15:40','16:25'],[18,'000~360','self','21:40','22:25']]},
{model:'CMC',id:'cmc',runs:[[0,'000~240','self','03:50','04:55'],[12,'000~240','self','15:50','16:55']]},
{model:'ICON',id:'icon',runs:[
[0,'000~180','self','02:35','03:30'],[6,'000~120','self','08:40','09:20'],
[12,'000~180','self','14:40','15:35'],[18,'000~120','self','20:40','21:15']]},
{model:'KIM_RDAPS',kma:['KIMR1','kim_rdps_erly_asia_gph500_s{fh}_{run}.png'],runs:[
[0,'000~120','kma','03:50','05:30'],[6,'000~072','kma','09:40','10:45'],
[12,'000~120','kma','15:50','17:25'],[18,'000~072','kma','21:40','22:45']]},
{model:'KIM_LDAPS',kma:['KIML','kim_ldps_erly_hkor_gph500_s{fh}_{run}.png'],runs:[
[0,'000~048','kma','03:50','04:55'],[6,'000~048','kma','09:40','10:35'],
[12,'000~048','kma','15:50','16:55'],[18,'000~048','kma','21:40','22:40']]},
{model:'KIM_KLAPS',hourly:{leads:'000~012',source:'kma',start:13,end:20}}
];
const SOURCE_LABEL={kma:'기상청',self:'자체생산'};
const DAY=1440;
const HOUR_MS=3600000;
// A run that has not finished this long after its usual end is no longer reported as late.
const LATE_WINDOW=6*60;
const TAB_STORE='cds.schedule.tab';

const minutes=text=>{const [h,m]=text.split(':').map(Number);return h*60+m;};
const pad=value=>String(value).padStart(2,'0');
const clock=value=>{const m=((value%DAY)+DAY)%DAY;return pad(Math.floor(m/60))+':'+pad(m%60);};
const offsetFor=mode=>mode==='UTC'?0:540;
const lastLead=leads=>Number(leads.split('~')[1]);

function windows(){
const rows=[];
for(const entry of SCHEDULE){
if(entry.hourly){
for(let hour=0;hour<24;hour++) rows.push({model:entry.model,cycle:hour,leads:entry.hourly.leads,source:entry.hourly.source,
start:hour*60+entry.hourly.start,end:hour*60+entry.hourly.end,hourly:true});
continue;
}
for(const [cycle,leads,source,start,end,check] of entry.runs){
let from=minutes(start),to=minutes(end);
if(to<from) to+=DAY;
rows.push({model:entry.model,id:entry.id,kma:entry.kma,cycle,leads,source,start:from,end:to,
check:check||(source==='self'?'public':'kma')});
}
}
return rows;
}

// Each window's latest occurrence that has started, and its next one, as absolute times.
function occurrences(nowMs){
const midnight=Math.floor(nowMs/86400000)*86400000;
const result=[];
for(const row of windows()){
if(row.hourly) continue;
const lag=((row.start-row.cycle*60)%DAY+DAY)%DAY;
for(const day of [-1,0,1]){
const startMs=midnight+(day*DAY+row.start)*60000;
const endMs=midnight+(day*DAY+row.end)*60000;
const cycleMs=Math.round((startMs-lag*60000)/HOUR_MS)*HOUR_MS;
result.push({...row,startMs,endMs,cycleMs});
}
}
return result;
}

function upcoming(nowUTC,limit=5){
const now=nowUTC.getTime();
const all=occurrences(now);
const live=all.filter(row=>row.startMs<=now&&row.endMs>now)
.map(row=>({...row,state:'live',left:Math.round((row.endMs-now)/60000)}))
.sort((a,b)=>a.left-b.left);
const next=all.filter(row=>row.startMs>now)
.map(row=>({...row,state:'next',wait:Math.round((row.startMs-now)/60000)}))
.sort((a,b)=>a.wait-b.wait);
return [...live,...next].slice(0,limit);
}

// ---------- Completion checks ----------
const probeCache=new Map();
function kmaImageLoads(url){
const cached=probeCache.get(url);
if(cached && (cached.ok || Date.now()-cached.at<120000)) return cached.promise;
const promise=new Promise(resolve=>{
const image=new Image();
const timer=setTimeout(()=>resolve(null),15000);
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

function cycleText(ms){
const d=new Date(ms);
return d.getUTCFullYear()+pad(d.getUTCMonth()+1)+pad(d.getUTCDate())+pad(d.getUTCHours());
}

// true when finished, false when not, null when it cannot be told.
async function finished(row,publicFresh){
const hour=lastLead(row.leads);
if(row.check==='public'){
const store=global.CDSPublicCharts;
// A stale or missing R2 snapshot cannot tell a late run from one it has not seen yet.
if(!publicFresh || !store?.readyHours || !row.id) return null;
const hours=store.readyHours({modelId:row.id,product:{category:'asia',id:'gph500'},runUTC:new Date(row.cycleMs)});
return hours.some(value=>value>=hour);
}
if(!row.kma) return null;
const run=cycleText(row.cycleMs);
const [folder,template]=row.kma;
const name=template.replace('{fh}',String(hour).padStart(3,'0')).replace('{run}',run);
return kmaImageLoads(`${KMA_BASE}/${folder}/${run.slice(0,6)}/${run.slice(6,8)}/${name}`);
}

async function lateRuns(nowMs){
const store=global.CDSPublicCharts;
let publicFresh=false;
try{publicFresh=(await store?.load?.())?.ok===true && store.getSource?.()==='r2';}catch{}
const overdue=occurrences(nowMs).filter(row=>row.endMs<=nowMs && nowMs-row.endMs<=LATE_WINDOW*60000);
const results=await Promise.all(overdue.map(row=>finished(row,publicFresh).catch(()=>null)));
return overdue.filter((row,index)=>results[index]===false)
.map(row=>({...row,state:'late',late:Math.round((nowMs-row.endMs)/60000)}))
.sort((a,b)=>a.late-b.late);
}

// ---------- Rendering ----------
function duration(value){
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

const STATE_LABEL={live:'생산중',next:'예정',late:'지연'};

function boardRows(now,late){
const lateKeys=new Set(late.map(row=>row.model+row.cycle+row.leads+row.cycleMs));
const list=upcoming(now,99).filter(row=>!lateKeys.has(row.model+row.cycle+row.leads+row.cycleMs));
const live=list.filter(row=>row.state==='live').slice(0,3);
const next=list.filter(row=>row.state==='next');
const shown=[...late.slice(0,3),...live];
return [...shown,...next.slice(0,Math.max(3,7-shown.length))];
}

function renderBoard(container,mode,now,late){
container.replaceChildren();
const offset=offsetFor(mode);
const table=element('table','schedule-board');
const body=element('tbody');
for(const row of boardRows(now,late)){
const tr=element('tr','is-'+row.state);
const status=element('td','schedule-board-state');
status.append(element('span','schedule-state is-'+row.state,STATE_LABEL[row.state]));
const time=element('td','schedule-board-time');
time.append(element('mark','schedule-mark c'+pad(row.cycle),`${clock(row.start+offset)}–${clock(row.end+offset)}`));
const remain=row.state==='live'?duration(row.left)+' 남음':row.state==='late'?duration(row.late)+' 지연':duration(row.wait)+' 후';
tr.append(status,time,
element('td','schedule-board-source',SOURCE_LABEL[row.source]),
element('td','schedule-board-model',row.model),
element('td','schedule-board-cycle',pad(row.cycle)+'Z'),
element('td','schedule-board-leads','+'+row.leads+'h'),
element('td','schedule-board-remain',remain));
body.append(tr);
}
table.append(body);
container.append(table);
}

function renderTimeline(container,mode,now,onSelect){
container.replaceChildren();
const offset=offsetFor(mode);
const axis=element('div','schedule-axis');
axis.append(element('span'));
const ticks=element('div','schedule-axis-track');
for(let hour=0;hour<=24;hour+=3){
const tick=element('span','schedule-axis-tick',pad(hour));
tick.style.left=(hour/24*100)+'%';
ticks.append(tick);
}
axis.append(ticks);
container.append(axis);
const all=windows();
for(const entry of SCHEDULE){
const lane=element('div','schedule-lane');
lane.append(element('span','schedule-lane-name',entry.model));
const track=element('div','schedule-lane-track');
for(const row of all.filter(item=>item.model===entry.model)){
const start=((row.start+offset)%DAY+DAY)%DAY;
const length=Math.max(row.end-row.start,row.hourly?2:5);
const parts=start+length>DAY?[[start,DAY-start],[0,start+length-DAY]]:[[start,length]];
parts.forEach(([from,width],index)=>{
const bar=element('button',`schedule-bar is-${row.source}${row.hourly?' is-hourly':' c'+pad(row.cycle)}`);
bar.type='button';
bar.style.left=(from/DAY*100)+'%';
bar.style.width=(width/DAY*100)+'%';
const text=`${row.model} ${pad(row.cycle)}Z ${row.leads}h ${SOURCE_LABEL[row.source]} ${clock(row.start+offset)}~${clock(row.end+offset)} ${mode}`;
bar.title=text;bar.setAttribute('aria-label',text);
bar.addEventListener('click',()=>onSelect(row,bar));
track.append(bar);
if(!row.hourly && index===0){
const tag=element('span','schedule-bar-tag c'+pad(row.cycle),pad(row.cycle)+'Z');
tag.style.left=(from/DAY*100)+'%';
track.append(tag);
}
});
}
lane.append(track);
container.append(lane);
}
const nowLine=element('div','schedule-now');
const nowMinutes=now.getUTCHours()*60+now.getUTCMinutes();
nowLine.style.setProperty('--now',String(((nowMinutes+offset)%DAY)/DAY));
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

function renderTable(container,mode,now,late){
container.replaceChildren();
const offset=offsetFor(mode);
const states=new Map();
for(const row of upcoming(now,99).filter(item=>item.state==='live')) states.set(row.model+row.cycle+row.leads,'live');
for(const row of late) states.set(row.model+row.cycle+row.leads,'late');
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
const state=run.cycle===null?'':states.get(entry.model+run.cycle+run.leads)||'';
const tr=element('tr',state?'is-'+state:'');
if(index===0){
const name=element('th','schedule-table-model',entry.model);
name.scope='row';name.rowSpan=runs.length;
tr.append(name);
}
const time=element('td','schedule-table-time');
time.append(run.cycle===null?document.createTextNode(run.time):element('mark','schedule-mark c'+pad(run.cycle),run.time));
if(state) time.append(element('span','schedule-state is-'+state,STATE_LABEL[state]));
tr.append(element('td','schedule-table-cycle',run.label),element('td','schedule-table-leads',run.leads),
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
let late=[];

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

dialog.append(header,boardWrap,tabs,timelinePanel,tableWrap,legend);

let selected=null;
const select=(row,bar)=>{
selected=row;
timeline.querySelectorAll('.schedule-bar.is-selected').forEach(node=>node.classList.remove('is-selected'));
bar?.classList.add('is-selected');
const offset=offsetFor(mode);
detail.textContent=row.hourly
?`${row.model} 매시 · +${row.leads}h · ${SOURCE_LABEL[row.source]} · 정시+${row.start%60}~${row.end%60}분`
:`${row.model} ${pad(row.cycle)}Z · +${row.leads}h · ${SOURCE_LABEL[row.source]} · ${clock(row.start+offset)} 시작 → ${clock(row.end+offset)} 완료 (${mode})`;
};

function render(){
const now=new Date(global.CDSPublicCharts?.clockNow?.()??Date.now());
modeButtons.forEach(button=>button.setAttribute('aria-pressed',String(button.textContent===mode)));
for(const [value,button] of Object.entries(tabButtons)) button.setAttribute('aria-selected',String(value===tab));
timelinePanel.hidden=tab!=='timeline';
tableWrap.hidden=tab!=='table';
renderBoard(board,mode,now,late);
renderTimeline(timeline,mode,now,select);
renderTable(tablePanel,mode,now,late);
const first=selected||boardRows(now,late)[0];
if(first){
const match=[...timeline.querySelectorAll('.schedule-bar')]
.find(bar=>bar.getAttribute('aria-label').startsWith(`${first.model} ${pad(first.cycle)}Z ${first.leads}h`));
select(first,match);
}
requestAnimationFrame(()=>{hideCrowdedTags(timeline);updateBoardHint();updateTableHint();});
}

let checking=false;
async function refreshLate(){
if(checking) return;
checking=true;
try{late=await lateRuns(global.CDSPublicCharts?.clockNow?.()??Date.now());}
finally{checking=false;}
if(dialog.open) render();
}

const resize=()=>{hideCrowdedTags(timeline);updateBoardHint();updateTableHint();};
const timer=setInterval(()=>{if(dialog.open){render();refreshLate();}},60000);
dialog.addEventListener('close',()=>{clearInterval(timer);global.removeEventListener('resize',resize);dialog.remove();});
dialog.addEventListener('click',event=>{if(event.target===dialog) dialog.close();});
global.addEventListener('resize',resize);
document.body.append(dialog);
render();
dialog.showModal();
refreshLate();
}

function button(){
const node=element('button','viewer-icon-button schedule-button');
node.type='button';node.title='모델 표출 시간표';node.setAttribute('aria-label','모델 표출 시간표');
node.setAttribute('aria-haspopup','dialog');
node.append(CDSViewerIcons('Clock'),element('span','schedule-button-text','시간표'));
node.onclick=open;
return node;
}

global.CDSModelSchedule={button,open,upcoming,windows,occurrences,lateRuns,SCHEDULE};
})(window);

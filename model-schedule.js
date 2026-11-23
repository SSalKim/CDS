(function(global){
'use strict';

// Approximate publication windows in UTC, measured from image timestamps on KMA and R2
// (2026-11-20..23). "start" is when the first lead appears, "end" when the last lead does.
const MEASURED='2026-11-20~23';
const SCHEDULE=[
{model:'KIM_GDAPS',runs:[
[0,'000~288','kma','03:15','05:50'],[6,'000~084','kma','09:15','10:00'],
[12,'000~288','kma','15:15','17:50'],[18,'000~084','kma','21:15','22:00']]},
{model:'UKUM',runs:[
[0,'000~168','kma','09:35','09:50'],[6,'000~069','self','11:30','12:05'],
[12,'000~168','kma','22:35','22:50'],[18,'000~069','self','23:30','00:10']]},
{model:'ECMWF',runs:[
[0,'000~240','kma','05:50','07:00'],[0,'252~360','self','07:35','07:45'],[6,'000~144','self','12:25','12:40'],
[12,'000~240','kma','17:50','19:00'],[12,'252~360','self','19:35','19:45'],[18,'000~144','self','00:25','00:40']]},
{model:'AIFS',runs:[
[0,'000~360','self','05:20','05:35'],[6,'000~360','self','11:20','11:35'],
[12,'000~360','self','17:20','17:35'],[18,'000~360','self','23:25','23:35']]},
{model:'GFS',runs:[
[0,'000~360','self','03:30','05:10'],[6,'000~360','self','09:30','11:10'],
[12,'000~360','self','15:30','17:10'],[18,'000~360','self','21:30','23:10']]},
{model:'AIGFS',runs:[
[0,'000~360','self','03:40','04:20'],[6,'000~360','self','09:35','10:20'],
[12,'000~360','self','15:40','16:25'],[18,'000~360','self','21:40','22:25']]},
{model:'CMC',runs:[[0,'000~240','self','03:50','04:55'],[12,'000~240','self','15:50','16:55']]},
{model:'ICON',runs:[
[0,'000~180','self','02:35','03:30'],[6,'000~120','self','08:40','09:20'],
[12,'000~180','self','14:40','15:35'],[18,'000~120','self','20:40','21:15']]},
{model:'KIM_RDAPS',runs:[
[0,'000~120','kma','03:50','05:30'],[6,'000~072','kma','09:40','10:45'],
[12,'000~120','kma','15:50','17:25'],[18,'000~072','kma','21:40','22:45']]},
{model:'KIM_LDAPS',runs:[
[0,'000~048','kma','03:50','04:55'],[6,'000~048','kma','09:40','10:35'],
[12,'000~048','kma','15:50','16:55'],[18,'000~048','kma','21:40','22:40']]},
{model:'KIM_KLAPS',hourly:{leads:'000~012',source:'kma',start:13,end:20}}
];
const SOURCE_LABEL={kma:'기상청',self:'자체생산'};
const DAY=1440;
const TAB_STORE='cds.schedule.tab';

const minutes=text=>{const [h,m]=text.split(':').map(Number);return h*60+m;};
const pad=value=>String(value).padStart(2,'0');
const clock=value=>{const m=((value%DAY)+DAY)%DAY;return pad(Math.floor(m/60))+':'+pad(m%60);};
const offsetFor=mode=>mode==='UTC'?0:540;

function windows(){
const rows=[];
for(const entry of SCHEDULE){
if(entry.hourly){
for(let hour=0;hour<24;hour++) rows.push({model:entry.model,cycle:hour,leads:entry.hourly.leads,source:entry.hourly.source,
start:hour*60+entry.hourly.start,end:hour*60+entry.hourly.end,hourly:true});
continue;
}
for(const [cycle,leads,source,start,end] of entry.runs){
let from=minutes(start),to=minutes(end);
if(to<from) to+=DAY;
rows.push({model:entry.model,cycle,leads,source,start:from,end:to});
}
}
return rows;
}

// Minutes until each window next starts (0 while it is running), measured from nowUTC.
function upcoming(nowUTC,limit=5){
const now=nowUTC.getUTCHours()*60+nowUTC.getUTCMinutes();
const result=[];
for(const row of windows()){
if(row.hourly) continue;
let start=row.start,end=row.end;
while(end<=now) {start+=DAY;end+=DAY;}
while(start-DAY<=now && end-DAY>now) {start-=DAY;end-=DAY;}
result.push({...row,wait:Math.max(0,start-now),live:start<=now,left:end-now});
}
return result.sort((a,b)=>a.wait-b.wait||a.left-b.left).slice(0,limit);
}

function duration(value){
if(value<60) return value+'분';
const h=Math.floor(value/60),m=value%60;
return m?`${h}시간 ${m}분`:`${h}시간`;
}

function label(row){return `${row.model} ${pad(row.cycle)}Z`;}

function element(tag,className,text){
const node=document.createElement(tag);
if(className) node.className=className;
if(text!==undefined) node.textContent=text;
return node;
}

function currentMode(){
try{return typeof timeMode==='string'&&timeMode==='UTC'?'UTC':'KST';}catch{return 'KST';}
}

function renderNext(container,mode,now){
container.replaceChildren();
const offset=offsetFor(mode);
const all=upcoming(now,99);
const live=all.filter(row=>row.live).sort((a,b)=>a.left-b.left).slice(0,3);
const next=all.filter(row=>!row.live).slice(0,6-live.length);
live.forEach((row,index)=>{row.extra=index>=2;});
next.forEach((row,index)=>{row.extra=index>=2;});
for(const row of [...live,...next]){
const item=element('li','schedule-next-item src-'+row.source+(row.live?' is-live':'')+(row.extra?' is-extra':''));
const when=element('span','schedule-next-when',row.live?`표출 중 · ${duration(row.left)} 남음`:duration(row.wait)+' 후');
const name=element('strong','schedule-next-name',label(row));
const detail=element('span','schedule-next-detail',`${row.leads}h · ${clock(row.start+offset)}~${clock(row.end+offset)}`);
const badge=element('span','schedule-source is-'+row.source,SOURCE_LABEL[row.source]);
item.append(when,name,detail,badge);
container.append(item);
}
}

function renderTimeline(container,mode,now,onSelect){
container.replaceChildren();
const offset=offsetFor(mode);
const axis=element('div','schedule-axis');
axis.append(element('span','schedule-axis-spacer'));
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
const length=Math.max(row.end-row.start,row.hourly?7:5);
const parts=start+length>DAY?[[start,DAY-start],[0,start+length-DAY]]:[[start,length]];
for(const [from,width] of parts){
const bar=element('button','schedule-bar is-'+row.source+(row.hourly?' is-hourly':''));
bar.type='button';
bar.style.left=(from/DAY*100)+'%';
bar.style.width=(width/DAY*100)+'%';
const text=`${label(row)} ${row.leads}h ${SOURCE_LABEL[row.source]} ${clock(row.start+offset)}~${clock(row.end+offset)} ${mode}`;
bar.title=text;bar.setAttribute('aria-label',text);
if(!row.hourly) bar.append(element('span','schedule-bar-label',pad(row.cycle)+'Z'));
bar.addEventListener('click',()=>onSelect(row,bar));
track.append(bar);
}
}
lane.append(track);
container.append(lane);
}
const nowLine=element('div','schedule-now');
const nowMinutes=now.getUTCHours()*60+now.getUTCMinutes();
nowLine.style.setProperty('--now',String(((nowMinutes+offset)%DAY)/DAY));
nowLine.append(element('span','schedule-now-label','현재 '+clock(nowMinutes+offset)));
container.append(nowLine);
}

function renderTable(container,mode,now){
container.replaceChildren();
const offset=offsetFor(mode);
const live=new Set(upcoming(now,99).filter(row=>row.live).map(row=>label(row)+row.leads));
const table=element('table','schedule-table');
const head=element('thead');
const headRow=element('tr');
for(const text of ['모델','자료시각','예측시간','구분',`표출 (${mode})`]) headRow.append(element('th','',text));
head.append(headRow);
const body=element('tbody');
for(const entry of SCHEDULE){
const runs=entry.hourly
?[{cycle:'매시',leads:entry.hourly.leads,source:entry.hourly.source,time:`정시+${entry.hourly.start}~${entry.hourly.end}분`}]
:entry.runs.map(([cycle,leads,source,start,end])=>({cycle:pad(cycle)+'Z',leads,source,
time:`${clock(minutes(start)+offset)}~${clock(minutes(end)+offset)}`,key:`${entry.model} ${pad(cycle)}Z${leads}`}));
runs.forEach((run,index)=>{
const tr=element('tr',live.has(run.key)?'is-live':'');
if(index===0){
const name=element('th','schedule-table-model',entry.model);
name.scope='row';name.rowSpan=runs.length;
tr.append(name);
}
const source=element('td');
source.append(element('span','schedule-source is-'+run.source,SOURCE_LABEL[run.source]));
tr.append(element('td','',run.cycle),element('td','',run.leads),source,element('td','schedule-table-time',run.time));
body.append(tr);
});
}
table.append(head,body);
container.append(table);
}

function hideCrowdedLabels(root){
for(const bar of root.querySelectorAll('.schedule-bar')){
const text=bar.querySelector('.schedule-bar-label');
if(text) text.hidden=bar.clientWidth<text.scrollWidth+4;
}
}

function open(){
const dialog=element('dialog','schedule-dialog');
dialog.setAttribute('aria-labelledby','scheduleTitle');
let mode=currentMode();
let tab='timeline';
try{if(localStorage.getItem(TAB_STORE)==='table') tab='table';}catch{}

const header=element('header','schedule-header');
const title=element('h2','schedule-title','모델별 표출 시간표');
title.id='scheduleTitle';
const modes=element('div','schedule-mode');
modes.setAttribute('role','group');modes.setAttribute('aria-label','시간 기준');
const modeButtons=['KST','UTC'].map(value=>{
const button=element('button','',value);button.type='button';
button.onclick=()=>{mode=value;render();};
modes.append(button);return button;
});
const close=element('button','schedule-close');
close.type='button';close.setAttribute('aria-label','시간표 닫기');close.title='닫기';
close.append(CDSViewerIcons('X'));
close.onclick=()=>dialog.close();
header.append(title,modes,close);

const note=element('p','schedule-note',
`최근 실측(${MEASURED}) 기준 대략적인 시각입니다. 원본 자료가 늦으면 함께 늦어집니다.`);

const nextSection=element('section','schedule-next');
nextSection.append(element('h3','schedule-section-title','지금 · 다음 표출'));
const nextList=element('ol','schedule-next-list');
nextSection.append(nextList);

const tabs=element('div','schedule-tabs');
tabs.setAttribute('role','tablist');
const tabButtons={};
for(const [value,text] of [['timeline','타임라인'],['table','표']]){
const button=element('button','',text);button.type='button';button.setAttribute('role','tab');
button.onclick=()=>{tab=value;try{localStorage.setItem(TAB_STORE,tab);}catch{}render();};
tabButtons[value]=button;tabs.append(button);
}

const timeline=element('div','schedule-timeline');
const detail=element('p','schedule-detail');
detail.setAttribute('aria-live','polite');
const timelinePanel=element('div','schedule-panel');
timelinePanel.append(timeline,detail);
const tablePanel=element('div','schedule-panel schedule-table-wrap');

const legend=element('footer','schedule-legend');
legend.append(
element('span','schedule-source is-kma','기상청'),element('span','',' KMA 원본 이미지'),
element('span','schedule-source is-self','자체생산'),element('span','',' 최근 48시간만 제공'),
element('span','schedule-legend-note','KIM_KLAPS는 매시 정시+15분경 표출')
);

dialog.append(header,note,nextSection,tabs,timelinePanel,tablePanel,legend);

let selected=null;
const select=(row,bar)=>{
selected=row;
timeline.querySelectorAll('.schedule-bar.is-selected').forEach(node=>node.classList.remove('is-selected'));
bar?.classList.add('is-selected');
const offset=offsetFor(mode);
detail.textContent=row.hourly
?`${row.model} 매시 · ${row.leads}h · ${SOURCE_LABEL[row.source]} · 정시+${row.start%60}~${row.end%60}분`
:`${label(row)} · ${row.leads}h · ${SOURCE_LABEL[row.source]} · ${clock(row.start+offset)} 시작 → ${clock(row.end+offset)} 완료 (${mode})`;
};

function render(){
const now=new Date();
modeButtons.forEach(button=>button.setAttribute('aria-pressed',String(button.textContent===mode)));
for(const [value,button] of Object.entries(tabButtons)){
button.setAttribute('aria-selected',String(value===tab));
}
timelinePanel.hidden=tab!=='timeline';
tablePanel.hidden=tab!=='table';
renderNext(nextList,mode,now);
renderTimeline(timeline,mode,now,select);
renderTable(tablePanel,mode,now);
const first=selected||upcoming(now,1)[0];
if(first){
const match=[...timeline.querySelectorAll('.schedule-bar')].find(bar=>bar.getAttribute('aria-label').startsWith(`${label(first)} ${first.leads}h`));
select(first,match);
}
requestAnimationFrame(()=>hideCrowdedLabels(timeline));
}

const resize=()=>hideCrowdedLabels(timeline);
const timer=setInterval(()=>{if(dialog.open) render();},60000);
dialog.addEventListener('close',()=>{clearInterval(timer);global.removeEventListener('resize',resize);dialog.remove();});
dialog.addEventListener('click',event=>{if(event.target===dialog) dialog.close();});
global.addEventListener('resize',resize);
document.body.append(dialog);
render();
dialog.showModal();
}

function button(){
const node=element('button','viewer-icon-button schedule-button');
node.type='button';node.title='모델별 표출 시간표';node.setAttribute('aria-label','모델별 표출 시간표');
node.setAttribute('aria-haspopup','dialog');
node.append(CDSViewerIcons('Clock'),element('span','schedule-button-text','시간표'));
node.onclick=open;
return node;
}

global.CDSModelSchedule={button,open,upcoming,windows,SCHEDULE};
})(window);

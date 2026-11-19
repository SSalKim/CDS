const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');

const source=fs.readFileSync(path.join(__dirname,'..','radar-analysis.js'),'utf8');
const calls={now:0,cacheUrls:0,paneRefresh:0};
let tick=null;
const context={
  document:{visibilityState:'visible'},
  radarState:{root:{},autoRefreshEnabled:false},
  setInterval:(callback,ms)=>{assert.equal(ms,5*60*1000);tick=callback;return 1;},
  stopRadarAutoRefresh:()=>{},updateRadarAutoRefreshButton:()=>{},
  setRadarNow:()=>{calls.now++;},
  getRefreshableRadarCacheUrls:()=>{calls.cacheUrls++;return [];},
  updateRadarTimelineActiveState:()=>{},updateRadarTimeLabel:()=>{},
  refreshRadarPaneImages:()=>{calls.paneRefresh++;},preloadRadarImages:()=>{}
};
context.globalThis=context;
vm.createContext(context);

function include(name){
  const start=source.search(new RegExp(`^function ${name}\\(`,'m'));
  assert(start>=0,name);
  let end=start;
  while((end=source.indexOf('\n}',end+1))>=0){
    const text=source.slice(start,end+2);
    try{new vm.Script(text);}catch(error){if(error instanceof SyntaxError) continue;throw error;}
    vm.runInContext(text,context);
    return;
  }
  throw new Error('Incomplete function '+name);
}
for(const name of ['refreshRadarCacheInBackground','startRadarAutoRefresh','syncRadarAfterResume']) include(name);

context.refreshRadarCacheInBackground();
assert.equal(calls.cacheUrls,1,'A visible tab refreshes the radar cache');
context.document.visibilityState='hidden';
context.refreshRadarCacheInBackground();
assert.equal(calls.cacheUrls,1,'A hidden tab skips the background cache refresh');

context.document.visibilityState='visible';
context.startRadarAutoRefresh();
context.radarState.autoRefreshEnabled=true;
tick();
assert.equal(calls.now,1,'Visible auto refresh jumps to NOW every five minutes');
context.document.visibilityState='hidden';
tick();tick();
assert.equal(calls.now,1,'Hidden tabs do not rebuild the timeline');
context.document.visibilityState='visible';
context.syncRadarAfterResume();
assert.equal(calls.now,2,'Returning catches up once on the missed auto refresh');
assert.equal(calls.cacheUrls,2,'Returning refreshes the cache');
context.syncRadarAfterResume();
assert.equal(calls.now,2,'Focus without a missed refresh does not move the timeline');

console.log('Radar: hidden tabs skip background refresh and catch up once on return passed');

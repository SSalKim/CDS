const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.join(__dirname,'..');
let now=Date.UTC(2026,10,23,0),payload={models:{ecmwf:{published:true},gfs:{published:true}},charts:[]};
const context={console,URL,URLSearchParams,Date:class extends Date{static now(){return now;}},
  setTimeout,clearTimeout,setInterval,clearInterval,location:{hostname:'localhost'},
  fetch:async()=>({ok:true,json:async()=>payload}),window:null};
context.window=context;vm.createContext(context);
for(const file of ['models.js','public-charts.js','time-controls.js']) vm.runInContext(fs.readFileSync(path.join(root,file),'utf8'),context);
const api=context.CDSPublicCharts;
const day=value=>new Date(value+'T00:00:00Z');
const cycle=value=>new Date(Date.UTC(Number(value.slice(0,4)),Number(value.slice(4,6))-1,Number(value.slice(6,8)),Number(value.slice(8,10))));
const hours=(model,date,hour)=>Array.from(context.getForecastHours(model,day(date),hour));

// Schedules switch at the 11-22 12Z cycle, not at the start of the day.
for(const model of ['gfs','aifs','aigfs']){
  assert.equal(hours(model,'2026-11-22',6).at(-1),240,model+' 06Z stays at 240 h');
  assert.equal(hours(model,'2026-11-22',12).at(-1),360,model+' 12Z runs to 360 h');
  assert.deepEqual(hours(model,'2026-11-23',0).slice(-3),[336,348,360]);
}
assert.equal(hours('ecmwf','2026-11-22',0).at(-1),240);
assert.equal(hours('ecmwf','2026-11-22',12).at(-1),360);
assert.deepEqual(hours('ecmwf','2026-11-22',12).filter(hour=>hour>=228),[228,240,252,264,276,288,300,312,324,336,348,360]);
assert.equal(hours('ecmwf','2026-11-22',18).at(-1),144,'ECMWF 06/18Z still stops at 144 h');
assert.equal(hours('ukmo','2026-11-22',0).at(-1),168,'Date-only rules are unchanged');

// KMA-only products keep KMA's own last lead.
assert.equal(context.getKmaOnlyLeadLimit('ecmwf',{category:'asia',id:'surfce'}),Infinity);
assert.equal(context.getKmaOnlyLeadLimit('ecmwf',{category:'asia',id:'thk500'}),240);
assert.equal(context.getKmaOnlyLeadLimit('ukmo',{category:'asia',id:'thk500'}),144);
assert.equal(context.getKmaOnlyLeadLimit('gfs',{category:'asia',id:'thk500'}),Infinity);

// ECMWF 00/12Z: KMA to 240 h, public charts from 252 h, only from the cutover cycle.
assert(!api.usesSource('ecmwf',cycle('2026112212'),240));
assert(api.usesSource('ecmwf',cycle('2026112212'),252));
assert(!api.usesSource('ecmwf',cycle('2026112212')),'Menus and products for 00/12Z stay on KMA');
assert(!api.usesSource('ecmwf',cycle('2026112200'),252),'Cycles before the cutover never use public charts at 00/12Z');
assert(api.usesSource('ecmwf',cycle('2026112218')));

const row=(model,run,hour,product='surfce',domain='asia')=>({model,cycle:run,hour,product,domain,
  url:`https://drive.usercontent.google.com/download?id=${model}-${run}-${hour}-${product}-${domain}`});
(async()=>{
  payload.charts=[row('ecmwf','2026112212',252),row('ecmwf','2026112212',360),row('ecmwf','2026112200',252),
    row('gfs','2026112212',360),row('gfs','2026112206',252)];
  await api.load();
  const product={category:'asia',id:'surfce'};
  const resolve=(modelId,run,forecastHour)=>Array.from(api.resolveUrls({modelId,product,runUTC:cycle(run),forecastHour}));
  assert.deepEqual(resolve('ecmwf','2026112212',252),[row('ecmwf','2026112212',252).url]);
  assert.deepEqual(resolve('ecmwf','2026112212',360),[row('ecmwf','2026112212',360).url]);
  assert.deepEqual(resolve('ecmwf','2026112200',252),[],'A pre-cutover 00Z row is ignored');
  assert.deepEqual(resolve('gfs','2026112212',360),[row('gfs','2026112212',360).url]);
  assert.deepEqual(resolve('gfs','2026112206',252),[],'Pre-cutover GFS leads stop at 240 h');
  assert.deepEqual(Array.from(api.readyHours({modelId:'ecmwf',product,runUTC:cycle('2026112212')})),[252,360]);
  console.log('360 h extension: cycle cutover, ECMWF KMA/public split, KMA-only limits and lead validation passed');
})().catch(error=>{console.error(error);process.exitCode=1;});

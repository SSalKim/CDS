const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.join(__dirname,'..');
let now=Date.UTC(2026,10,18,12),payload={models:{ukmo:{published:true}},charts:[]};
const context={console,URL,URLSearchParams,Date:class extends Date{static now(){return now;}},
  setTimeout,clearTimeout,setInterval,clearInterval,location:{hostname:'localhost'},
  fetch:async()=>({ok:true,json:async()=>payload}),window:null};
context.window=context;vm.createContext(context);
for(const file of ['models.js','public-charts.js','time-controls.js']) vm.runInContext(fs.readFileSync(path.join(root,file),'utf8'),context);
const api=context.CDSPublicCharts;
const run=hour=>new Date(Date.UTC(2026,10,18,hour));
const product={category:'asia',id:'gph200'};
const selection={modelId:'ukmo',product,runUTC:run(0),forecastHour:156};
const row=(hour=156,cycle='2026111800',id='gph300',domain='asia')=>({model:'ukmo',cycle,hour,product:id,domain,
  url:`https://drive.usercontent.google.com/download?id=ukmo-${cycle}-${hour}-${id}-${domain}`});
const date=new Date('2026-11-18T00:00:00Z');
assert.deepEqual(Array.from(context.getAvailableCycles('ukmo',date)),[0,6,12,18]);
assert.equal(context.getForecastHours('ukmo',date,0).at(-1),168);
assert.deepEqual(Array.from(context.getForecastHours('ukmo',date,6)),Array.from({length:24},(_,i)=>3*i));
assert.deepEqual(Array.from(context.getAvailableCycles('ukmo',new Date('2026-11-17T00:00:00Z'))),[0,12]);
assert.deepEqual(Array.from(context.getCyclesForSelection('ukmo',{category:'asia',id:'thk500'},date)),[0,12]);
assert.deepEqual(Array.from(context.getCyclesForSelection('ukmo',product,date)),[0,6,12,18]);
assert(!api.usesSource('ukmo',run(0),144));assert(api.usesSource('ukmo',run(0),156));assert(api.usesSource('ukmo',run(6)));

(async()=>{
  payload.charts=[row()];await api.load();assert.deepEqual(Array.from(api.resolveUrls(selection)),[]);
  payload.charts=[{...row(),kma_confirmed_at:'2026-11-18T05:00:00Z'}];await api.load();
  assert.equal(api.resolveUrls(selection).length,0,'An unspecified KMA reference cannot release the extension');
  payload.charts=[{...row(),kma_confirmed_at:'2026-11-18T05:00:00Z',kma_reference_hour:144}];await api.load();
  assert.deepEqual(Array.from(api.resolveUrls(selection)),[row().url]);
  assert.deepEqual(Array.from(api.replacementFallbacks(row().url)),[],'There is no native KMA +156h fallback');
  assert.equal(api.resolveUrls({...selection,forecastHour:168}).length,0,'An absent lead stays pending');
  payload.charts=[row(69,'2026111806')];await api.load();
  const off={...selection,runUTC:run(6),forecastHour:69};
  assert.equal(api.resolveUrls(off).length,1,'Off-cycle production never waits for nonexistent KMA originals');
  assert.equal(api.resolveUrls({...off,forecastHour:72}).length,0);
  payload.charts=[row(69,'2026111806','acptot1','hkor')];await api.load();
  assert.equal(api.resolveUrls({...off,product:{category:'hkor',id:'acptot'},variant:'compare'}).length,1);
  now=Date.UTC(2026,10,20,6,0,1);await api.load();assert.equal(api.resolveUrls(off).length,0);
  assert(!api.usesSource('ukmo',new Date('2026-11-17T06:00:00Z')));
  console.log('UKMO extensions: scopes, full timelines, KMA +144 gate, 06/18Z, layouts, expiry and no bogus fallback passed');
})().catch(error=>{console.error(error);process.exitCode=1;});

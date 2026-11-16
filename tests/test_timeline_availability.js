const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');

const root=path.join(__dirname,'..');
const context={console};
context.window=context;
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(root,'compare-mode.js'),'utf8'),context);
const run=code=>vm.runInContext(code,context);
run(`compareForecastHourMap=new Map([
  ['aifs',new Set([0,6,12])],['gfs',new Set([0,3,6,9,12])]
]);
compareImageAvailabilityMap=new Map([
  ['aifs|3','available'],['aifs|6','missing'],['gfs|3','available']
]);`);
assert.equal(run("getCompareImageAvailability('aifs',3)"),'unsupported');
assert.equal(run("getCompareImageAvailability('aifs',6)"),'missing');
assert.equal(run("getCompareImageAvailability('aifs',12)"),'loading');
assert.equal(run("getCompareImageAvailability('gfs',3)"),'available');
assert.equal(run("getCompareImageAvailability('gfs',9)"),'loading');

const classes=new Set(['compare-segment','active','state-missing']);
const segment={dataset:{index:'1',time:'11-16 12UTC',lead:'+003h'},
  classList:{remove(...names){names.forEach(name=>classes.delete(name));},add(name){classes.add(name);}},
  attributes:{},setAttribute(name,value){this.attributes[name]=value;}};
context.segment=segment;
run("setTimelineSegmentAvailability(segment,'unsupported')");
assert(classes.has('active'));
assert(classes.has('state-unsupported'));
assert(!classes.has('state-missing'));
assert(segment.title.endsWith('미지원 예측시간'));
assert.equal(segment.title,'미지원 예측시간');
assert.equal(segment.attributes['aria-label'],'11-16 12UTC / +003h / 미지원 예측시간');
run("setTimelineSegmentAvailability(segment,'missing')");
assert(!classes.has('state-unsupported'));
assert(segment.title.endsWith('이미지 없음'));
run("setTimelineSegmentAvailability(segment,'available')");
assert(classes.has('state-available'));
assert(!classes.has('state-missing'));

const app=fs.readFileSync(path.join(root,'app.js'),'utf8');
function include(name){
  const start=app.search(new RegExp(`^function ${name}\\(`,'m'));
  assert(start>=0,name);
  let end=start;
  while((end=app.indexOf('\n}',end+1))>=0){
    const source=app.slice(start,end+2);
    try{new vm.Script(source);}catch{continue;}
    vm.runInContext(source,context);
    return;
  }
  throw new Error('Incomplete function: '+name);
}
include('refreshForecastTimelineLabels');
context.forecastTimeline={querySelectorAll:()=>[segment,segment]};
context.getValidTimeLabel=index=>'time-'+index;
context.getForecastLeadLabel=index=>'lead-'+index;
context.updateCompareTimelineActiveLabels=()=>{};
run("setTimelineSegmentAvailability(segment,'unsupported');refreshForecastTimelineLabels()");
assert.equal(segment.dataset.time,'time-1','Each comparison row uses its own forecast index');
assert(segment.title.endsWith('미지원 예측시간'),'Changing time mode preserves unsupported status');
console.log('Timeline availability: unsupported schedules, missing images, state changes, tooltips and time-label refresh passed');

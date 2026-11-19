const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');

const app=fs.readFileSync(path.join(__dirname,'..','app.js'),'utf8');
const context={currentMainMenu:'forecast',slider:{value:'0'},currentForecastList:[],isRunTimeSliderMode:()=>false};
vm.createContext(context);

function include(name){
  const start=app.search(new RegExp(`^function ${name}\\(`,'m'));
  assert(start>=0,name);
  let end=start;
  while((end=app.indexOf('\n}',end+1))>=0){
    const source=app.slice(start,end+2);
    try{new vm.Script(source);}catch(error){if(error instanceof SyntaxError) continue;throw error;}
    vm.runInContext(source,context);
    return;
  }
  throw new Error('Incomplete function '+name);
}

vm.runInContext(app.match(/^const IMAGE_PRELOAD_CONCURRENCY=\d+;$/m)[0],context);
include('getImagePreloadConcurrency');
include('getForecastPreloadOrder');
const order=(...args)=>Array.from(vm.runInContext(`getForecastPreloadOrder(${args.join(',')})`,context));

assert.deepEqual(order(7,3),[3,4,2,5,1,6,0],'Frames nearest the visible one load first, forward before backward');
assert.deepEqual(order(5,0),[0,1,2,3,4],'From the first frame the order stays chronological');
assert.deepEqual(order(4,9),[3,2,1,0],'An out-of-range slider value is clamped');
context.slider.value='2';
assert.deepEqual(order(5),[2,3,1,4,0],'The slider position is the default centre');

context.currentMainMenu='analysis';
context.isRunTimeSliderMode=()=>true;
context.currentForecastList=[-12,-6,0,6];
assert.deepEqual(order(4,3),[2,1,0,3],'Analysis run-time sliders keep their own zero-first order');

const concurrency=connection=>vm.runInContext('getImagePreloadConcurrency',context)(connection);
assert.equal(concurrency(undefined),4);
assert.equal(concurrency({effectiveType:'4g',saveData:false}),4);
assert.equal(concurrency({effectiveType:'3g'}),2,'Slow connections fetch fewer frames at once');
assert.equal(concurrency({effectiveType:'4g',saveData:true}),2,'Data saver halves parallel chart downloads');

console.log('Preload priority: nearest frames first and connection-aware concurrency passed');

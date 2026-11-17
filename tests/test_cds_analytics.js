const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
function setup(){
  const events=[];
  const context={console,Map,Date,URL,location:{href:'https://ssalkim.github.io/CDS/',hostname:'ssalkim.github.io'},
    gtag:(command,event,params)=>events.push({command,event,params})};
  context.window=context;
  vm.createContext(context);
  vm.runInContext(fs.readFileSync(path.join(__dirname,'..','cds-analytics.js'),'utf8'),context);
  return {context,events,track:params=>context.CDSAnalytics.trackProductView({menu:'forecast',category:'asia',
    product_id:'gph500',product_key:'forecast|asia|gph500|gfs',product_name:'500 고도,기온,풍속',model_id:'gfs',
    run_utc:'2026-11-17T00:00:00.000Z',forecast_hour:0,view_context:'single',...params})};
}
{
  const {events,track}=setup();
  track({});track({});
  assert.equal(events.length,1,'automatic refresh of the same displayed image is ignored');
  track({forecast_hour:3});
  track({forecast_hour:240});
  track({forecast_hour:0});
  assert.equal(events.length,4,'each changed forecast lead remains in detailed history');
  track({run_utc:'2026-11-17T06:00:00.000Z'});
  assert.equal(events.length,5,'the next initialization is a different view');
}
{
  const {events,track}=setup();
  for(const model of ['gfs','aifs','aigfs','cmc']) track({model_id:model,view_context:'compare'});
  assert.equal(events.length,4,'comparison models are all recorded separately');
  for(const model of ['gfs','aifs','aigfs','cmc']) track({model_id:model,view_context:'compare'});
  assert.equal(events.length,4,'a comparison refresh does not inflate history');
  track({view_context:'single'});
  track({view_context:'compare'});
  assert.equal(events.length,6,'switching presentation modes starts a new display');
}
{
  const {context,events,track}=setup();
  context.CDSUsage={isAllowed:()=>false,record:()=>{throw Error('must not collect');}};
  track({});
  assert.equal(events.length,0,'opt-out stops both collectors');
}
console.log('CDS analytics: forecast leads, cycles, comparison models, refresh suppression and opt-out passed');

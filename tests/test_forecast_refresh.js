const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const root=path.join(__dirname,'..');
const app=fs.readFileSync(path.join(root,'app.js'),'utf8');
const context={console,Date,Promise,Map,Set,document:{visibilityState:'visible'},
  currentModel:'kim_gdps',modelCompareMode:false,compareModels:[],currentForecastList:[0,6,12],
  imagePreloadSeq:1,compareImageAvailabilitySeq:0,latestSearchInProgress:false,IMAGE_PRELOAD_CONCURRENCY:4,
  slider:{value:'1',disabled:false},selectionKey:'one',
  productUsesForecastHour:()=>true,getSelectedUTCDate:()=>new Date(Date.now()-3600000),
  isPublicChartModel:()=>false,isRunTimeFrameFuture:()=>false,
  getCompareAvailabilityContextKey:()=>context.selectionKey};
context.window=context;
vm.createContext(context);
for(const file of ['forecast-refresh.js','timeline-state.js','image-pipeline.js']){
  vm.runInContext(fs.readFileSync(path.join(root,file),'utf8'),context,{filename:file});
}
function include(name){
  const start=app.search(new RegExp(`^(?:async )?function ${name}\\(`,'m'));
  assert(start>=0,name);
  let end=start;
  while((end=app.indexOf('\n}',end+1))>=0){
    const code=app.slice(start,end+2);
    try{new vm.Script(code);}catch{continue;}
    vm.runInContext(code,context);
    return;
  }
  throw new Error('Function not found: '+name);
}
for(const name of ['canRefreshForecastAvailability','getForecastRefreshContextKey','refreshMissingForecastFrames']) include(name);
const run=code=>vm.runInContext(code,context);

async function main(){
  let now=0,visible=true,refreshCount=0,interval,intervalCount=0,cleared=0,release;
  const options=[];
  const refresher=context.CDSForecastRefresh.createRefresher({
    refresh:input=>{
      refreshCount++;
      options.push(input);
      return refreshCount===1?new Promise(resolve=>{release=resolve;}):Promise.resolve(true);
    },
    canRefresh:()=>visible,now:()=>now,
    setIntervalImpl:(callback,ms)=>{interval=callback;intervalCount++;assert.equal(ms,60000);return 7;},
    clearIntervalImpl:id=>{assert.equal(id,7);cleared++;}
  });
  refresher.start();refresher.start();
  assert.equal(intervalCount,1);
  const first=refresher.request({manual:true});
  await Promise.resolve();
  const second=refresher.request();
  release(true);
  await Promise.all([first,second]);
  assert.equal(refreshCount,1,'Overlapping checks must share one refresh');
  assert.equal(options[0].manual,true);
  now=14999;
  assert.equal(await refresher.request(),false,'Repeated clicks respect the cooldown');
  now=60000;visible=false;
  assert.equal(await interval(),false);
  assert.equal(refreshCount,1,'Hidden tabs do not poll');
  visible=true;
  assert.equal(await interval(),true);
  assert.equal(refreshCount,2);
  refresher.stop();assert.equal(cleared,1);
  let failures=0;
  const recovering=context.CDSForecastRefresh.createRefresher({
    refresh:()=>{if(!failures++) throw new Error('offline');return true;},now:()=>now,
    setIntervalImpl:()=>1,clearIntervalImpl:()=>{}
  });
  assert.equal(await recovering.request(),false);
  now+=15000;
  assert.equal(await recovering.request(),true,'A failed check must not disable future checks');

  assert.equal(run('canRefreshForecastAvailability()'),true);
  context.getSelectedUTCDate=()=>new Date(Date.now()-72*3600000);
  assert.equal(run('canRefreshForecastAvailability()'),false,'Old archives are not polled automatically');
  assert.equal(run('canRefreshForecastAvailability({manual:true})'),true);
  context.document.visibilityState='hidden';
  assert.equal(run('canRefreshForecastAvailability({manual:true})'),false);
  context.document.visibilityState='visible';
  context.getSelectedUTCDate=()=>new Date(NaN);
  assert.equal(run('canRefreshForecastAvailability({manual:true})'),false);
  context.getSelectedUTCDate=()=>new Date(Date.now()-3600000);

  const state=context.CDSTimelineState.createTimelineState();
  state.setForecastList([0,6,12]);state.setLoadStates(['available','missing','missing']);
  context.forecastTimelineState=state;
  let probes=[],displays=0;
  context.preloadForecastIndex=async(index,seq,options)=>{
    probes.push({index,seq,...options});
    return {index,ok:index===1,urls:['new-image'],baseUrls:['original-image']};
  };
  context.setForecastAvailabilityResult=(index,result)=>{
    state.setLoadState(index,result.ok?'available':'missing');
    state.setImageCacheEntry(index,result);
  };
  context.displayCurrentForecastImage=()=>{displays++;};
  assert.equal(await run('refreshMissingForecastFrames()'),true);
  assert.deepEqual(probes.map(probe=>probe.index).sort(),[1,2]);
  assert(probes.every(probe=>probe.imageRefreshToken));
  assert.equal(state.getLoadState(0),'available');
  assert.equal(state.getLoadState(1),'available');
  assert.equal(state.getLoadState(2),'missing');
  assert.equal(context.slider.value,'1','Refreshing never moves the selected lead');
  assert.equal(displays,1,'A newly available selected frame is displayed automatically');
  probes=[];
  await run('refreshMissingForecastFrames()');
  assert.deepEqual(probes.map(probe=>probe.index),[2],'Ready frames are never reprobed');
  assert.equal(displays,1,'An unchanged current image is not rendered again');

  context.preloadForecastIndex=index=>new Promise(resolve=>{release=()=>resolve({index,ok:true});});
  const stale=run('refreshMissingForecastFrames()');
  context.selectionKey='changed';release();
  assert.equal(await stale,false);
  assert.equal(state.getLoadState(2),'missing','Late replies from a prior selection are discarded');
  context.isPublicChartModel=()=>true;
  let manifestChecks=0;
  context.CDSPublicCharts={load:async()=>{manifestChecks++;context.selectionKey='new manifest';}};
  await run('refreshMissingForecastFrames({manual:true})');
  assert.equal(manifestChecks,1,'A timeline click also checks the exact public manifest');

  vm.runInContext(fs.readFileSync(path.join(root,'compare-mode.js'),'utf8'),context);
  context.getCompareAvailabilityContextKey=()=>'comparison';
  context.currentModel='ecmwf';context.modelCompareMode=true;
  context.compareModels=['ecmwf'];context.currentForecastList=[0,6,12];
  context.isPublicChartModel=()=>false;
  run('compareForecastHourMap=new Map([["ecmwf",new Set([0,6,12])]]);compareImageAvailabilityContextKey="comparison";compareImageAvailabilityMap=new Map([["ecmwf|0","available"],["ecmwf|6","missing"],["ecmwf|12","missing"]])');
  let compareProbes=[],compareRenders=0;
  context.getEffectiveCompareProductForModel=()=>({});
  context.getProductExistenceMode=()=>'all';
  context.buildCompareImageUrlsForModel=(model,hour)=>['https://example.invalid/'+hour];
  context.urlsExist=async(urls,options)=>{compareProbes.push({urls,options});return urls[0].endsWith('/6');};
  context.updateCompareSegmentAvailability=()=>{};
  context.renderCompareImages=()=>{compareRenders++;};
  context.renderCompareForecastTimeline=()=>{throw new Error('Background checks must not rebuild the timeline');};
  assert.equal(await run('probeCompareImageAvailability({retryMissing:true,imageRefreshToken:"fresh"})'),true);
  assert.deepEqual(compareProbes.map(probe=>probe.urls[0]).sort(),['https://example.invalid/12','https://example.invalid/6']);
  assert(compareProbes.every(probe=>probe.options.imageRefreshToken==='fresh'));
  assert.equal(run('compareImageAvailabilityMap.get("ecmwf|0")'),'available');
  assert.equal(run('compareImageAvailabilityMap.get("ecmwf|6")'),'available');
  assert.equal(run('compareImageAvailabilityMap.get("ecmwf|12")'),'missing');
  assert.equal(run('compareImageRefreshTokens.get("ecmwf|6")'),'fresh');
  assert.equal(compareRenders,1);
  context.urlsExist=()=>new Promise(resolve=>{release=()=>resolve(true);});
  const staleCompare=run('probeCompareImageAvailability({retryMissing:true,imageRefreshToken:"late"})');
  run('compareImageAvailabilitySeq++');release();
  await staleCompare;
  assert.equal(run('compareImageAvailabilityMap.get("ecmwf|12")'),'missing');
  console.log('Forecast refresh: cadence, visibility, throttling, single/comparison retries, selected-hour preservation and stale-reply protection passed');
}

main().catch(error=>{console.error(error);process.exitCode=1;});

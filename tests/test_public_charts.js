const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');

const root=path.join(__dirname,'..');
let mobile=false;
let payload={models:{},charts:[]};
let status=200;
let badJson=false;
let networkError=false;
let intervalCallback=null;
let intervalCalls=0;
let clearCalls=0;
const requests=[];
const context={
  console,Date,URL,URLSearchParams,
  location:{hostname:'localhost'},
  matchMedia:()=>({matches:mobile}),
  setInterval:callback=>{intervalCallback=callback;intervalCalls++;return 1;},
  clearInterval:()=>{clearCalls++;},
  fetch:async(url,options)=>{
    requests.push({url,options});
    if(networkError) throw new Error('offline');
    return {ok:status===200,status,json:async()=>{
      if(badJson) throw new Error('invalid JSON');
      return payload;
    }};
  },
  currentMainMenu:'forecast',currentModel:'kim_gdps',currentProduct:'gph500',
  productCategory:{value:'asia'},runDate:{value:'2026-11-15'},runHour:{value:'00:00'},
  timeMode:'UTC',modelCompareMode:false,compareModels:[],COMPARE_MAX_MODELS:6,
  currentForecastList:[24],slider:{value:'0'},
  chartResolvedUrlCache:new Map(),
  publicChartNoticeDismissed:false,
  sessionStorage:{values:new Map(),getItem(key){return this.values.get(key) || null;},setItem(key,value){this.values.set(key,value);}},
  getCurrentAuxToken:()=>null,
  getCurrentCategory:()=>context.productCategory.value
};
context.window=context;
vm.createContext(context);
for(const file of ['models.js','public-charts.js','products.js','catalog-config.js','catalog-core.js',
  'model-menu.js','product-menu.js','catalog-selection.js','time-controls.js',
  'forecast-domain.js','compare-mode.js','chart-utils.js']){
  vm.runInContext(fs.readFileSync(path.join(root,file),'utf8'),context,{filename:file});
}
const app=fs.readFileSync(path.join(root,'app.js'),'utf8');
function includeAppFunction(name){
  const start=app.search(new RegExp(`^(?:async )?function ${name}\\(`,'m'));
  assert(start>=0,name);
  // Let the JS parser find a complete function without evaluating adjacent globals.
  let end=start;
  while((end=app.indexOf('\n}',end+1))>=0){
    const source=app.slice(start,end+2);
    try{new vm.Script(source);}catch(error){
      if(error instanceof SyntaxError) continue;
      throw error;
    }
    vm.runInContext(source,context,{filename:'app.js:'+name});
    return;
  }
  throw new Error('Incomplete app function: '+name);
}
for(const name of ['getOrderedChartUrlCandidates','isPublicChartModel','updatePublicChartNotice','dismissPublicChartNotice','refreshPublicChartManifestView','makeChartImageUrls',
  'getCycleSupportStatus','getForecastHoursForProductAtRun','buildImageUrlsForCurrentSelectionAtRun',
  'getRecentRunCandidates','selectionIsDisplayable','shouldJumpOlderAvailableRunForMissingSelection',
  'displayCurrentForecastImage','rebuildForecastAxis','updateChart','jumpLatestAvailableForCurrentSelection',
  'jumpOlderAvailableRunForMissingSelection','getLatestSearchLookbackHours',
  'getLatestSearchMaxCandidates','getDefaultLatestSearchBaseDate','isSeaSurfaceTemperatureDailySelection']) includeAppFunction(name);
const evaluate=code=>vm.runInContext(code,context);
const snapshot=code=>JSON.parse(evaluate(`JSON.stringify(${code})`));
const api=context.CDSPublicCharts;
const date=cycle=>new Date(`${cycle.slice(0,4)}-${cycle.slice(4,6)}-${cycle.slice(6,8)}T${cycle.slice(8)}:00:00Z`);
const product=(id='gph500',category='hkor')=>({id,category});
const row=(model='aifs',cycle='2026111500',hour=24,id='gph500',domain='hkor',extra={})=>({
  model,cycle,hour,product:id,domain,
  url:`https://drive.usercontent.google.com/download?id=${model}_${cycle}_${hour}_${domain}_${id}&export=view`,
  size:12345,sha256:'a'.repeat(64),file_id:'public-file',...extra
});
const manifest=charts=>({schema_version:1,models:Object.fromEntries(
  ['aifs','gfs','aigfs','cmc','ecmwf'].map(id=>[id,{published:true}])
),charts});
const selection=(id='gph500',modelId='aifs',cycle='2026111500',hour=24,category='hkor',variant='normal')=>({
  modelId,product:product(id,category),runUTC:date(cycle),forecastHour:hour,variant
});
const urls=(...args)=>Array.from(api.resolveUrls(selection(...args)));
const visible=()=>snapshot('getVisibleModelGroups().flatMap(group=>group.models.map(model=>model[0]))');

async function main(){
  const original=row().url;
  const id=new URL(original).searchParams.get('id');
  assert.equal(api.browserImageCandidates(original)[0],`https://lh3.googleusercontent.com/d/${id}=s0`);
  assert.deepEqual(Array.from(api.browserImageCandidates('https://example.invalid/image.webp')),[]);
  assert.equal(evaluate(`getOrderedChartUrlCandidates(${JSON.stringify(original)})[0]`),`https://lh3.googleusercontent.com/d/${id}=s0`);
  assert.equal(evaluate('currentModel'),'kim_gdps','Drive candidates must also work in mixed-model comparison');
  assert.equal(evaluate("getOrderedChartUrlCandidates('https://data.kma.go.kr/CHT/KIMG/chart.png')[0]"),
    'https://data.kma.go.kr/CHT/KIMG/chart.png');
  const notice={hidden:true};
  context.document={getElementById:id=>id==='publicChartNotice'?notice:null};
  assert(fs.readFileSync(path.join(root,'index.html'),'utf8').includes('System 3.6'));
  assert(fs.readFileSync(path.join(root,'index.html'),'utf8').includes(
    '※ 시험운영 외부 예측모델(AIFS, GFS, AIGFS, CMC)은 과거 예측자료 조회를 지원하지 않으며, 최근 48시간 이내 생산자료만 제공됩니다.'));
  for(const model of ['aifs','gfs','aigfs','cmc','kim_gdps']){
    context.currentModel=model;
    context.modelCompareMode=false;
    context.updatePublicChartNotice();
    assert.equal(notice.hidden,false);
  }
  context.modelCompareMode=true;
  for(const models of [['kim_gdps','aifs'],['gfs','cmc'],['kim_gdps','ukmo'],[]]){
    context.compareModels=models;
    context.updatePublicChartNotice();
    assert.equal(notice.hidden,false);
  }
  context.dismissPublicChartNotice();
  assert.equal(notice.hidden,true);
  context.publicChartNoticeDismissed=false;
  context.updatePublicChartNotice();
  assert.equal(notice.hidden,true,'Dismissal survives model changes and reloads in this tab');
  context.sessionStorage.values.clear();
  context.updatePublicChartNotice();
  assert.equal(notice.hidden,false);
  context.modelCompareMode=false;
  context.compareModels=[];
  context.currentModel='kim_gdps';
  assert.equal(api.manifestUrl({hostname:'localhost'}),'data/public_charts_manifest.json');
  assert.equal(api.manifestUrl({hostname:'127.0.0.1'}),'data/public_charts_manifest.json');
  assert.equal(api.manifestUrl({hostname:'[::1]'}),'data/public_charts_manifest.json');
  assert.equal(api.manifestUrl({hostname:'ssalkim.github.io'}),
    'https://raw.githubusercontent.com/SSalKim/CDS-Public-Charts/main/data/public_charts_manifest.json');
  assert(!visible().some(api.isModel));
  let remoteRequest='';
  const remoteStore=api.createStore({location:{hostname:'ssalkim.github.io'},fetchImpl:async url=>{
    remoteRequest=url;
    return {ok:true,json:async()=>manifest([])};
  }});
  await remoteStore.load();
  assert.match(remoteRequest,/public_charts_manifest\.json\?t=\d+$/);
  payload=manifest([]);
  await api.load();
  assert(!visible().some(api.isModel),'A published flag alone must not reveal empty models');
  payload=manifest([row()]);
  payload.models.aifs.published=false;
  await api.load();
  assert(!api.hasPublishedCharts('aifs'));

  const rows=[...['aifs','gfs','aigfs','cmc'].map(id=>row(id)),
    ...['aifs','gfs','aigfs','cmc'].flatMap(id=>[
      row(id,'2026111500',0,'gph500'),row(id,'2026111500',0,'wnd925'),row(id,'2026111500',0,'surfce')]),
    row('aifs','2026111500',0,'gph500'),row('aifs','2026111500',0,'wnd850'),
    row('aifs','2026111500',0,'surfce'),row('aifs','2026111500',0,'acrain'),
    row('aifs','2026111500',0,'acptot1'),
    row('aifs','2026111500',24,'gph300'),row('aifs','2026111500',24,'gph200'),
    row('aifs','2026111500',24,'acptot'),row('aifs','2026111500',24,'acptot1'),
    row('aifs','2026111500',24,'acrain'),row('aifs','2026111500',24,'acrain1'),
    row('aifs','2026111500',120,'acptot'),
    row('aifs','2026111500',24,'surfce','asia'),
    row('aigfs','2026111500',0,'surfce'),row('aigfs','2026111500',24,'surfce'),
    row('aigfs','2026111500',24,'acrain'),row('aigfs','2026111500',24,'acptot1'),
    row('aifs','2026111512',24),row('aifs','2026111600',24),
    row('aifs','2026100100',24,'gph200'),row('aifs','2026100100',24,'gph300'),
    row('aifs','2026100100',24,'acptot1'),
    row('aifs','2026050100',24,'gph200'),row('aifs','2026050100',24,'surfce')];
  payload=manifest(rows);
  await api.load();
  assert.equal(requests.at(-1).options.credentials,'omit');
  assert.equal(requests.at(-1).options.cache,'no-store');
  assert.equal(requests.at(-1).url,'data/public_charts_manifest.json');
  assert.deepEqual(visible().filter(api.isModel).sort(),['aifs','aigfs','cmc','gfs']);
  assert.equal(evaluate('MODELS.aifs.name'),'ECMWF AIFS-Single (N320)');
  assert.equal(evaluate("modelGroups.find(group=>group.id==='global').models.find(model=>model[0]==='aifs')[1]"),'AIFS');
  for(const [id,label] of [['gfs','GFS'],['aigfs','AIGFS'],['cmc','CMC']]){
    assert.equal(evaluate(`modelGroups.find(group=>group.id==='global').models.find(model=>model[0]==='${id}')[1]`),label);
    assert.equal(evaluate(`getCurrentModelName('${id}')`),label);
  }
  assert.equal(evaluate("getCurrentModelName('aifs')"),'AIFS');
  assert.equal(evaluate("getCurrentModelName('ecmwf')"),'ECMWF');
  const unsupportedCycle=evaluate("getCycleSupportStatus('cmc',getCurrentProduct(),new Date('2026-11-15T18:00:00Z'))");
  assert(unsupportedCycle.message.startsWith('CMC은(는)'));
  assert(!unsupportedCycle.message.includes('GDPS'));
  assert.equal(evaluate('MODELS.cmc.name'),'CMC GDPS (GEM 0.135\u02da L84)');
  assert.equal(evaluate('MODELS.gfs.name'),'NCEP GFS (C768 L127)');
  assert.equal(evaluate('MODELS.aigfs.name'),'NCEP AIGFS (0.25\u00b0)');
  context.currentMainMenu='hazard';
  assert(!visible().some(api.isModel),'Public chart models must not leak into other catalogs');
  context.currentMainMenu='forecast';

  for(const modelId of ['aifs','gfs','aigfs','cmc']){
    assert.equal(evaluate(`PRODUCTS.filter(p=>p.category==='asia' && productSupportsModel(p,'${modelId}')).length`),8);
    assert.equal(evaluate(`PRODUCTS.filter(p=>p.category==='hkor' && productSupportsModel(p,'${modelId}')).length`),9);
    assert.deepEqual(urls('gph500',modelId),[row(modelId).url]);
    assert.deepEqual(urls('gph500',modelId,'2026111500',0),[row(modelId,'2026111500',0,'gph500').url]);
    assert.deepEqual(urls('wnd925',modelId,'2026111500',0),[row(modelId,'2026111500',0,'wnd925').url]);
    assert.deepEqual(urls('acptot',modelId,'2026111500',0),[row(modelId,'2026111500',0,'surfce').url]);
    assert.deepEqual(urls('acrain',modelId,'2026111500',0),[]);
  }
  assert.deepEqual(urls('gph500','aifs','2026111500',6),[]);
  assert.deepEqual(urls('gph500','aifs','2026111400'),[]);
  assert.deepEqual(urls('gph500','aifs','2026111512'),[row('aifs','2026111512').url]);
  assert.deepEqual(urls('gph500','gfs','2026111512'),[],'Never borrow another model/cycle URL');
  assert.deepEqual(urls('gph200'),[row('aifs','2026111500',24,'gph300').url]);
  assert.deepEqual(urls('gph200','aifs','2026100100'),[row('aifs','2026100100',24,'gph200').url]);
  assert.deepEqual(urls('gph200','aifs','2026050100'),[row('aifs','2026050100',24,'gph200').url]);
  assert.deepEqual(urls('acptot','aifs','2026100100',24,'hkor','compare'),[row('aifs','2026100100',24,'acptot1').url]);
  assert.deepEqual(urls('acptot','aifs','2026050100'),[row('aifs','2026050100',24,'surfce').url]);
  assert.deepEqual(urls('acptot'),[row('aifs','2026111500',24,'acptot').url]);
  assert.deepEqual(urls('acptot','aifs','2026111500',24,'hkor','compare'),[row('aifs','2026111500',24,'acptot1').url]);
  assert.deepEqual(urls('acptot','aifs','2026111500',0,'hkor','compare'),[row('aifs','2026111500',0,'acptot1').url]);
  assert.deepEqual(urls('acrain','aifs','2026111500',24,'hkor','compare'),[row('aifs','2026111500',24,'acrain1').url]);
  assert.deepEqual(urls('acptot','aifs','2026111500',120,'hkor','compare'),[],
    'A missing explicit comparison variant must not fall back to a different layout');
  assert.deepEqual(urls('acptot','aigfs','2026111500',24,'hkor','compare'),[row('aigfs','2026111500',24,'surfce').url]);
  assert.deepEqual(urls('acrain','aigfs','2026111500',24,'hkor','compare'),[row('aigfs','2026111500',24,'acrain').url]);
  assert.deepEqual(urls('acrain','aifs','2026111500',0),[],'No fabricated zero-hour accumulation');
  assert.deepEqual(urls('acptot','aifs','2026111500',0),[row('aifs','2026111500',0,'surfce').url]);
  assert.deepEqual(urls('acptot','aifs','2026111500',0,'hkor','compare'),[row('aifs','2026111500',0,'acptot1').url]);
  assert.deepEqual(urls('gph500','aifs','2026111500',0),[row('aifs','2026111500',0,'gph500').url]);
  assert.deepEqual(urls('wnd850','aifs','2026111500',0),[row('aifs','2026111500',0,'wnd850').url]);
  assert.deepEqual(urls('acptot','aifs','2026111500',24,'asia'),[]);
  assert.deepEqual(urls('acrain','aifs','2026111500',24,'asia'),[]);
  assert.deepEqual(urls('surfce','aifs','2026111500',24,'asia'),[row('aifs','2026111500',24,'surfce','asia').url]);
  assert.deepEqual(Array.from(api.readyHours(selection('acrain'))),[24]);
  assert.deepEqual(Array.from(api.readyHours(selection('acptot'))),[0,24,120]);
  assert.deepEqual(Array.from(api.resolveUrls({...selection(),runUTC:new Date('2026-11-15T00:30:00Z')})),[]);

  const rejected=[
    row('aifs','2026023000'),row('cmc','2026111506'),row('aifs','2026111500',3),
    row('gfs','2026111500',87),row('gfs','2026111500',24,'wnd700'),
    row('gfs','2026111500',24,'gph500','typh'),row('unknown'),
    row('gfs','2026111500','24'),row('gfs','2026111500',24,'acrain','asia'),
    ...['javascript:alert(1)','http://drive.google.com/uc?id=foo',
      'https://example.com/image.webp','https://user:password@drive.google.com/uc?id=foo',
      'https://drive.google.com/uc?id=foo&access_token=secret'].map(url=>row('gfs',undefined,undefined,undefined,undefined,{url}))
  ];
  payload=manifest(rejected);
  await api.load();
  assert(!visible().some(api.isModel),'Invalid rows cannot reveal any new model');
  payload=manifest([row(),row('aifs',undefined,undefined,undefined,undefined,{url:row().url+'&other=1'})]);
  await api.load();
  assert.deepEqual(urls(),[],'Conflicting duplicate keys must fail closed');

  payload=manifest(rows);
  await api.load();
  context.currentModel='aifs';
  context.productCategory.value='hkor';
  context.currentProduct='acptot';
  assert.equal(evaluate('productUsesForecastHour()'),true);
  assert.equal(evaluate("productUsesForecastHourForModel(getCurrentProduct(),'aifs')"),true);
  const sixHourly=evaluate("getForecastHours('aifs',new Date('2026-11-15T00:00:00Z'),0)");
  assert.deepEqual(snapshot('getForecastHoursForCurrentSelection()'),Array.from(sixHourly));
  assert.deepEqual(snapshot("getForecastHoursForCompareModel('aifs')"),Array.from(sixHourly));
  assert.equal(sixHourly.at(-1),240,'Unpublished leads remain on the slider through +240h');
  assert.deepEqual(snapshot("buildCompareImageUrlsForModel('aifs',120)"),[],
    'Unpublished comparison frames remain missing, not replaced by another layout');
  for(const model of ['aifs','gfs','aigfs','cmc']){
    const hours=Array.from(evaluate(`getPublicChartTimelineHours('${model}',getCurrentProduct(),new Date('2026-11-15T00:00:00Z'))`));
    assert.equal(hours.length,['aifs','aigfs'].includes(model)?29:43);
    assert.equal(hours.at(-1),240);
    assert(hours.includes(84)&&hours.includes(90)&&hours.includes(96)&&hours.includes(108));
    assert.equal(hours.includes(3),['gfs','cmc'].includes(model));
    assert(!hours.includes(87)&&!hours.includes(102));
    assert.deepEqual(snapshot(`getPublicChartTimelineHours('${model}',{id:'acrain',category:'hkor'},new Date('2026-11-15T00:00:00Z'))`),
      hours.filter(hour=>hour!==0),'Total precipitation has no unsupported +000h tile');
  }
  assert.deepEqual(snapshot("getPublicChartTimelineHours('cmc',getCurrentProduct(),new Date('2026-11-15T06:00:00Z'))"),[]);
  assert.deepEqual(snapshot("getPublicChartTimelineHours('aifs',{id:'wnd700',category:'hkor'},new Date('2026-11-15T00:00:00Z'))"),[]);
  assert.deepEqual(urls('acptot','aifs','2026111500',6),[],
    'A scheduled but unpublished tile must not invent an image URL');
  assert.deepEqual(snapshot("buildCompareImageUrlsForModel('aifs',24)"),[row('aifs','2026111500',24,'acptot1').url]);
  assert.deepEqual(snapshot("buildCompareImageUrlsForModel('aigfs',24)"),[row('aigfs','2026111500',24,'surfce').url]);
  mobile=true;
  assert.deepEqual(snapshot("buildCompareImageUrlsForModel('aifs',24)"),[row('aifs','2026111500',24,'acptot').url]);
  mobile=false;
  assert.deepEqual(snapshot("getForecastHoursForProductAtRun(getCurrentProduct(),'aifs',new Date('2026-11-15T00:00:00Z'))"),[0,24,120]);
  assert.deepEqual(snapshot("buildImageUrlsForCurrentSelectionAtRun(new Date('2026-11-15T00:00:00Z'))"),[row('aifs','2026111500',0,'surfce').url]);
  context.currentProduct='acrain';
  assert.deepEqual(snapshot("buildImageUrlsForCurrentSelectionAtRun(new Date('2026-11-15T00:00:00Z'))"),[row('aifs','2026111500',24,'acrain').url]);
  context.currentProduct='gph500';
  context.NOW_LOOKBACK_HOURS=24;
  context.NOW_MAX_CANDIDATES=32;
  assert.deepEqual(snapshot("getRecentRunCandidates('aifs',new Date('2026-11-15T18:00:00Z')).map(date=>formatUTCStampFromDate(date))"),
    ['2026111512','2026111500']);
  assert.equal(evaluate('getLatestSearchLookbackHours()'),48);
  const oldNowBase=context.getDefaultLatestSearchBaseDate;
  context.getDefaultLatestSearchBaseDate=()=>date('2026111600');
  assert.equal(evaluate('shouldJumpOlderAvailableRunForMissingSelection()'),true);
  context.getDefaultLatestSearchBaseDate=oldNowBase;
  let message='';
  context.showViewerMessage=value=>{message=value;};
  assert.equal(evaluate('selectionIsDisplayable()'),true,'Manifest sources need no KMA folder/pattern');
  context.runDate.value='2026-11-14';
  assert.equal(evaluate('selectionIsDisplayable()'),false);
  assert(message.includes('초기시각'));
  context.forecastTimelineState={};
  context.setCurrentForecastList=list=>{context.currentForecastList=list;};
  context.setForecastLoadStates=()=>{};
  context.renderForecastTimeline=()=>{};
  context.getForecastIndexByHour=hour=>context.currentForecastList.indexOf(hour);
  context.updateForecastLabel=()=>{};
  context.forecastLabel={};
  evaluate('rebuildForecastAxis()');
  assert.equal(context.slider.disabled,false,'An unpublished cycle keeps the complete scheduled timeline');
  assert.deepEqual(Array.from(context.currentForecastList),Array.from(sixHourly));
  evaluate('rebuildForecastAxis({reset:false,preserveForecastHour:24})');
  assert.equal(context.currentForecastList[Number(context.slider.value)],24,'Rebuilding preserves the selected lead');
  let missingStates=[];
  context.setAllForecastLoadStates=(count,state)=>{missingStates=Array(count).fill(state);};
  context.invalidateImagePreload=()=>{};
  context.invalidateForecastDisplay=()=>{};
  context.resetAnalysisResolutionState=()=>{};
  context.resetForecastImageCache=()=>{};
  context.setViewerLoading=()=>{};
  context.chartImages={classList:{remove(){}}};
  context.getSelectedTimelineHourForPreserve=()=>24;
  context.latestSearchInProgress=false;
  await evaluate('updateChart()');
  assert.deepEqual(missingStates,Array(sixHourly.length).fill('missing'),
    'A cycle with no images marks every scheduled tile gray');

  const savedFallbackHooks=Object.fromEntries(['currentSelectionExistsAtRun','setRunControlsToUTC',
    'refreshView','preloadAllForecastImages','updateCompareChart','getDefaultLatestSearchBaseDate']
    .map(name=>[name,context[name]]));
  const fallbackRows=[...['aifs','gfs','aigfs'].map(model=>row(model,'2026111518',24)),
    row('aifs','2026111512',24),row('cmc','2026111512',24),
    row('cmc','2026111600',24,'wnd925'),
    row('aifs','2026111600',24,'gph500','asia'),row('aifs','2026111606',24)];
  payload=manifest(fallbackRows);
  await api.load();
  let fallbackRefresh=null,preloads=0,compareUpdates=0;
  const probedCycles=[];
  context.latestSearchSeq=0;
  context.getDefaultLatestSearchBaseDate=()=>date('2026111600');
  context.currentSelectionExistsAtRun=async runUTC=>{
    probedCycles.push(runUTC.toISOString());
    const chartUrls=context.buildImageUrlsForCurrentSelectionAtRun(runUTC);
    return {exists:chartUrls.length>0,urls:chartUrls};
  };
  context.setRunControlsToUTC=runUTC=>{
    context.runDate.value=runUTC.toISOString().slice(0,10);
    context.runHour.value=runUTC.toISOString().slice(11,16);
  };
  context.refreshView=options=>{fallbackRefresh=options;};
  context.preloadAllForecastImages=()=>{preloads++;};
  context.updateCompareChart=()=>{compareUpdates++;};
  context.currentProduct='gph500';
  for(const model of ['aifs','gfs','aigfs','cmc']){
    context.currentModel=model;
    context.runDate.value='2026-11-16';
    context.runHour.value='00:00';
    fallbackRefresh=null;
    const before=probedCycles.length;
    await evaluate('updateChart({preserveForecastHour:24})');
    assert.equal(evaluate('getUTCStamp()'),model==='cmc'?'2026111512':'2026111518',
      'A missing public-model cycle selects the closest earlier run for this product and domain');
    assert.equal(fallbackRefresh.preserveForecastHour,24);
    assert.equal(probedCycles.length,before+1,'The nearest published cycle is probed first');
    assert.equal(context.latestSearchInProgress,false);
  }
  context.currentModel='cmc';
  context.runDate.value='2026-11-15';
  context.runHour.value='18:00';
  await evaluate('updateChart({preserveForecastHour:24})');
  assert.equal(evaluate('getUTCStamp()'),'2026111512',
    'CMC switches to 12Z even when the selected 18Z cycle is unsupported');

  context.runDate.value='2026-11-16';
  context.runHour.value='00:00';
  context.modelCompareMode=true;
  const beforeCompare=probedCycles.length;
  await evaluate('updateChart({preserveForecastHour:24})');
  assert.equal(compareUpdates,1);
  assert.equal(probedCycles.length,beforeCompare,'Comparison mode never changes the common run automatically');
  assert.equal(evaluate('getUTCStamp()'),'2026111600');
  context.modelCompareMode=false;

  payload=manifest([...fallbackRows,row('aifs','2026111600',12)]);
  await api.load();
  context.currentModel='aifs';
  const beforePartial=probedCycles.length;
  await evaluate('updateChart({preserveForecastHour:24})');
  assert.equal(evaluate('getUTCStamp()'),'2026111600');
  assert.equal(probedCycles.length,beforePartial,'Gray leads in a partly published cycle do not trigger fallback');
  assert.equal(preloads,1);
  assert.deepEqual(snapshot("getRecentRunCandidates('aifs',new Date('2026-11-17T18:00:00Z'),6).map(date=>formatUTCStampFromDate(date))"),[],
    'Automatic fallback does not exceed its lookback window');
  Object.assign(context,savedFallbackHooks);
  payload=manifest(rows);
  await api.load();
  context.runDate.value='2026-11-15';
  context.runHour.value='00:00';
  context.currentForecastList=[24];

  let shown=[];
  const loaded=[];
  context.getForecastImageCacheEntry=()=>({ok:true,urls:[row('gfs').url],baseUrls:[row('gfs').url]});
  context.forecastDisplayRequest=1;
  context.isRunTimeFrameFuture=()=>false;
  context.resolveAnalysisResolutionUrls=async urls=>urls;
  context.setForecastAvailabilityResult=()=>{};
  context.showCharts=urls=>{shown=urls;};
  context.urlsExist=async urls=>{loaded.push(...urls);return true;};
  context.addImageRefreshTokenToUrls=urls=>urls;
  await evaluate('displayCurrentForecastImage()');
  assert.deepEqual(Array.from(shown),[row().url],'A cached different-model image must never be displayed');
  assert.deepEqual(loaded,[row().url]);

  context.currentModel='ecmwf';
  context.productCategory.value='asia';
  assert.equal(evaluate("productSupportsModel(getCurrentProduct(),'ecmwf')"),true);
  assert.equal(evaluate("productSupportsModel(getCurrentProduct(),'aifs')"),true);
  assert.deepEqual(snapshot("makeChartImageUrls({modelId:'ecmwf',product:getCurrentProduct(),runUTC:new Date('2026-11-15T00:00:00Z'),forecastHour:24})"),
    ['https://data.kma.go.kr/CHT/ECMW/202611/15/ecmw_lc40_asia_gph500_s024_2026111500.gif']);
  assert.deepEqual(snapshot("getForecastHours('kim_gdps',new Date('2026-11-15T00:00:00Z'),6)"),
    Array.from({length:29},(_,i)=>i*3));
  assert.equal(evaluate("getForecastHours('aifs',new Date(),0).length"),29);
  assert.equal(evaluate("getForecastHours('gfs',new Date(),0).length"),43);
  assert.equal(evaluate("getAvailableCycles('cmc',new Date()).join(',')"),'0,12');

  const beforeHybrid={model:context.currentModel,product:context.currentProduct,
    category:context.productCategory.value,date:context.runDate.value,hour:context.runHour.value,time:context.timeMode};
  payload=manifest([...rows,row('ecmwf','2026111606',24,'gph500','asia'),
    row('ecmwf','2026111618',0,'gph500','asia'),row('ecmwf','2026111606',24,'acptot1'),
    row('ecmwf','2026111606',144,'gph500','asia'),
    row('ecmwf','2026111600',24,'gph500','asia'),row('ecmwf','2026111606',156,'gph500','asia')]);
  await api.load();
  context.currentModel='ecmwf';context.currentProduct='gph500';context.productCategory.value='asia';
  context.runDate.value='2026-11-16';context.runHour.value='06:00';context.timeMode='UTC';
  assert.equal(api.isModel('ecmwf'),false,'ECMWF must retain its existing button and legacy catalog');
  assert.equal(api.usesSource('ecmwf',date('2026111606')),true);
  assert.equal(api.usesSource('ecmwf',date('2026111600')),false);
  assert.deepEqual(snapshot("getAvailableCycles('ecmwf',new Date('2026-11-15')).map(Number)"),[0,12]);
  assert.deepEqual(snapshot("getAvailableCycles('ecmwf',new Date('2026-11-16')).map(Number)"),[0,6,12,18]);
  assert.equal(evaluate('isPublicChartModel()'),true);
  const hybridHours=snapshot('getForecastHoursForCurrentSelection()');
  assert.equal(hybridHours.length,35);assert.equal(hybridHours.at(-1),144);
  assert.deepEqual(snapshot("getForecastHoursForCompareModel('ecmwf')"),hybridHours);
  assert.deepEqual(snapshot("buildCompareImageUrlsForModel('ecmwf',24)"),[row('ecmwf','2026111606',24,'gph500','asia').url]);
  assert.deepEqual(urls('gph500','ecmwf','2026111600',24,'asia'),[],'Public manifest cannot replace 00/12Z KMA charts');
  assert.deepEqual(urls('gph500','ecmwf','2026111606',156,'asia'),[],'Off-cycle forecasts stop at +144h');
  assert.deepEqual(urls('acptot','ecmwf','2026111606',24,'hkor','compare'),[row('ecmwf','2026111606',24,'acptot1').url]);
  assert.deepEqual(snapshot("makeChartImageUrls({modelId:'ecmwf',product:getCurrentProduct(),runUTC:new Date('2026-11-16T00:00Z'),forecastHour:24})"),
    ['https://data.kma.go.kr/CHT/ECMW/202611/16/ecmw_lc40_asia_gph500_s024_2026111600.gif'],
    'Routing follows the requested run, not the currently selected 06Z widget');
  assert.deepEqual(snapshot("getForecastHoursForProductAtRun(getCurrentProduct(),'ecmwf',new Date('2026-11-16T06:00Z'))"),[24,144]);
  assert(evaluate("getRecentRunCandidates('ecmwf',new Date('2026-11-16T18:00Z'),48,20).some(date=>date.getUTCHours()===0)"),
    'Mixed-source NOW searches must still consider legacy cycles');
  const unsupportedHybridProduct={id:'thk500',category:'asia',patternByModel:{ecmwf:'legacy'}};
  assert.equal(context.productSupportsModel(unsupportedHybridProduct,'ecmwf'),false);
  context.runHour.value='00:00';
  assert.equal(context.productSupportsModel(unsupportedHybridProduct,'ecmwf'),true);
  context.currentModel=beforeHybrid.model;context.currentProduct=beforeHybrid.product;
  context.productCategory.value=beforeHybrid.category;context.runDate.value=beforeHybrid.date;
  context.runHour.value=beforeHybrid.hour;context.timeMode=beforeHybrid.time;
  payload=manifest(rows);await api.load();

  let changes=0;
  await api.startPolling(()=>{changes++;});
  await api.startPolling();
  assert.equal(intervalCalls,1);
  assert.equal(changes,0,'Unchanged snapshots must not reset the selected frame');
  context.compareModels=['aifs','ecmwf'];
  const previousCompareKey=evaluate('getCompareAvailabilityContextKey()');
  payload=manifest([...rows,row('aifs','2026111500',48)]);
  await intervalCallback();
  assert.equal(changes,1);
  assert.notEqual(evaluate('getCompareAvailabilityContextKey()'),previousCompareKey,
    'A revised manifest must invalidate comparison availability, including prior failures');
  context.compareModels=[];
  assert.deepEqual(Array.from(api.readyHours(selection())),[0,24,48]);
  const before=requests.length;
  await Promise.all([api.load(),api.load()]);
  assert.equal(requests.length,before+1,'Concurrent loads share one request');
  networkError=true;
  await api.load();
  assert(api.hasPublishedCharts('aifs'),'Transient network failure preserves the last validated exact snapshot');
  networkError=false;
  status=404;
  await api.load();
  assert(!visible().some(api.isModel),'A missing manifest must hide public models');
  status=200;
  payload=manifest(rows);
  await api.load();
  badJson=true;
  await api.load();
  assert(!visible().some(api.isModel));
  badJson=false;
  await api.load();
  payload={models:{aifs:{published:true}},charts:[]};
  await api.load();
  assert(!visible().some(api.isModel),'Retention removal must not retain old chart URLs');
  assert.deepEqual(urls(),[]);
  api.stopPolling();
  assert.equal(clearCalls,1);

  let menuRefreshes=0;
  let viewRefreshes=0;
  let invalidation=null;
  context.renderModels=()=>{menuRefreshes++;};
  context.getSelectedTimelineHourForPreserve=()=>24;
  context.invalidateSelectionAsyncWork=options=>{invalidation=options;};
  context.resetForecastImageCache=()=>{};
  context.ensureCurrentModelVisibleForMenu=()=>{};
  context.refreshView=()=>{viewRefreshes++;};
  evaluate('refreshPublicChartManifestView()');
  assert.equal(menuRefreshes,1);
  assert.equal(viewRefreshes,0,'Legacy single-model viewing must not be reset by manifest polling');
  context.currentModel='aifs';
  evaluate('refreshPublicChartManifestView()');
  assert.equal(viewRefreshes,1);
  assert.equal(invalidation.latest,false,'Manifest refresh must not cancel its own NOW lookup');

  const originalLoad=api.load;
  let finishLoad;
  api.load=()=>new Promise(resolve=>{finishLoad=resolve;});
  context.latestSearchSeq=0;
  context.getLatestSearchLookbackHours=()=>48;
  context.getLatestSearchMaxCandidates=()=>32;
  context.getDefaultLatestSearchBaseDate=()=>date('2026111600');
  context.setViewerLoading=()=>{};
  let candidateLookups=0;
  context.getRecentRunCandidates=()=>{candidateLookups++;return [];};
  const nowSearch=evaluate('jumpLatestAvailableForCurrentSelection()');
  context.latestSearchSeq++;
  context.currentModel='ecmwf';
  finishLoad({ok:true});
  assert(!await nowSearch);
  assert.equal(candidateLookups,0,'Changing selections during manifest fetch must cancel the pending search');
  api.load=originalLoad;

  assert(fs.readFileSync(path.join(root,'index.html'),'utf8').indexOf('public-charts.js')<
    fs.readFileSync(path.join(root,'index.html'),'utf8').indexOf('app.js?'));
  console.log('Public charts: manifest validation, exact URLs, seasons, +000h, comparison, polling, cache and legacy paths passed');
}

main().catch(error=>{console.error(error);process.exitCode=1;});

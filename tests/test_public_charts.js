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
  const next=app.slice(start+1).search(/\n(?:async )?function \w+\(/);
  vm.runInContext(app.slice(start,next<0?undefined:start+1+next),context,{filename:'app.js:'+name});
}
for(const name of ['isPublicChartModel','updatePublicChartNotice','refreshPublicChartManifestView','makeChartImageUrls',
  'getCycleSupportStatus','getForecastHoursForProductAtRun','buildImageUrlsForCurrentSelectionAtRun',
  'getRecentRunCandidates','selectionIsDisplayable','shouldJumpOlderAvailableRunForMissingSelection',
  'displayCurrentForecastImage','rebuildForecastAxis','jumpLatestAvailableForCurrentSelection']) includeAppFunction(name);
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
  ['aifs','gfs','aigfs','cmc'].map(id=>[id,{published:true}])
),charts});
const selection=(id='gph500',modelId='aifs',cycle='2026111500',hour=24,category='hkor',variant='normal')=>({
  modelId,product:product(id,category),runUTC:date(cycle),forecastHour:hour,variant
});
const urls=(...args)=>Array.from(api.resolveUrls(selection(...args)));
const visible=()=>snapshot('getVisibleModelGroups().flatMap(group=>group.models.map(model=>model[0]))');

async function main(){
  const notice={hidden:true};
  context.document={getElementById:id=>id==='publicChartNotice'?notice:null};
  assert(fs.readFileSync(path.join(root,'index.html'),'utf8').includes('System 3.6'));
  for(const model of ['aifs','gfs','aigfs','cmc','kim_gdps']){
    context.currentModel=model;
    context.modelCompareMode=false;
    context.updatePublicChartNotice();
    assert.equal(notice.hidden,!api.isModel(model));
  }
  context.modelCompareMode=true;
  for(const models of [['kim_gdps','aifs'],['gfs','cmc'],['kim_gdps','ukmo'],[]]){
    context.compareModels=models;
    context.updatePublicChartNotice();
    assert.equal(notice.hidden,!models.some(api.isModel));
  }
  context.modelCompareMode=false;
  context.compareModels=[];
  context.currentModel='kim_gdps';
  assert.equal(api.manifestUrl({hostname:'localhost'}),'data/public_charts_manifest.json');
  assert.equal(api.manifestUrl({hostname:'127.0.0.1'}),'data/public_charts_manifest.json');
  assert.equal(api.manifestUrl({hostname:'[::1]'}),'data/public_charts_manifest.json');
  assert.equal(api.manifestUrl({hostname:'ssalkim.github.io'}),
    'https://raw.githubusercontent.com/SSalKim/CDS/main/data/public_charts_manifest.json');
  assert(!visible().some(api.isModel));
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
  assert.deepEqual(urls('acrain','aifs','2026111500',24,'hkor','compare'),[row('aifs','2026111500',24,'acrain1').url]);
  assert.deepEqual(urls('acptot','aifs','2026111500',120,'hkor','compare'),[],
    'A missing explicit comparison variant must not fall back to a different layout');
  assert.deepEqual(urls('acptot','aigfs','2026111500',24,'hkor','compare'),[row('aigfs','2026111500',24,'surfce').url]);
  assert.deepEqual(urls('acrain','aigfs','2026111500',24,'hkor','compare'),[row('aigfs','2026111500',24,'acrain').url]);
  assert.deepEqual(urls('acrain','aifs','2026111500',0),[],'No fabricated zero-hour accumulation');
  assert.deepEqual(urls('acptot','aifs','2026111500',0),[row('aifs','2026111500',0,'surfce').url]);
  assert.deepEqual(urls('acptot','aifs','2026111500',0,'hkor','compare'),[row('aifs','2026111500',0,'surfce').url]);
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
  assert.deepEqual(snapshot('getForecastHoursForCurrentSelection()'),[0,24,120]);
  assert.deepEqual(snapshot("getForecastHoursForCompareModel('aifs')"),[0,24]);
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
  assert.equal(evaluate('shouldJumpOlderAvailableRunForMissingSelection()'),false);
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
  context.forecastLabel={};
  evaluate('rebuildForecastAxis()');
  assert.equal(context.slider.disabled,true,'An empty manifest timeline must not expose a fake +000 frame');
  context.runDate.value='2026-11-15';
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

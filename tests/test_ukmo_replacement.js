const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const root=path.join(__dirname,'..');
let now=Date.UTC(2026,10,18,4),payload={models:{ukmo:{published:true}},charts:[]};
const run=new Date(Date.UTC(2026,10,18));
const product={category:'hkor',id:'acptot',patternByModel:{ukmo:'ukum_erly_hkor_acptot_s{fh}_{run}.png'}};
const native='https://data.kma.go.kr/CHT/GDPS/202611/18/ukum_erly_hkor_acptot_s054_2026111800.png';
const row=(name='acptot',hour=54)=>({model:'ukmo',cycle:'2026111800',hour,product:name,domain:'hkor',
  url:`https://drive.usercontent.google.com/download?id=ukmo-${name}-${hour}`,kma_confirmed_at:'2026-11-18T03:00:00Z'});
const context={console,URL,URLSearchParams,Date:class extends Date{static now(){return now;}},
  location:{hostname:'localhost'},fetch:async()=>({ok:true,json:async()=>payload}),
  setTimeout,clearTimeout,setInterval,clearInterval,
  chartResolvedUrlCache:new Map(),isPublicChartModel:()=>false,
  CDSChartUtils:{getProductPatternsForDetail:()=>product.patternByModel.ukmo,makeChartImageUrls:()=>[native],getChartUrlCandidates:url=>[url]},
  MODELS:{},formatUTCStampFromDate:()=>'',parseDateOnly:()=>null,formatDateInputFromUTCParts:()=>'',
  getEffectiveModelStatus:()=>({}),getProductArchiveStatus:()=>({})};
let viewRefreshes=0;
Object.assign(context,{currentModel:'ukmo',modelCompareMode:false,compareModels:[],
  getCurrentProduct:()=>product,getSelectedUTCDate:()=>run,getSelectedTimelineHourForPreserve:()=>54,
  invalidateSelectionAsyncWork:()=>{},resetForecastImageCache:()=>{},ensureCurrentModelVisibleForMenu:()=>{},
  invalidateLatestSearch:()=>{},renderModels:()=>{},refreshView:()=>viewRefreshes++});
context.window=context;vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(root,'public-charts.js'),'utf8'),context);
const source=fs.readFileSync(path.join(root,'app.js'),'utf8');
for(const name of ['makeChartImageUrls','getOrderedChartUrlCandidates','refreshPublicChartManifestView']){
  const start=source.search(new RegExp(`^function ${name}\\(`,'m'));
  let end=start;
  while((end=source.indexOf('\n}',end+1))>=0){
    const code=source.slice(start,end+2);
    try{new vm.Script(code);}catch(error){continue;}
    vm.runInContext(code,context);break;
  }
}

(async()=>{
  const api=context.CDSPublicCharts;
  const selection={modelId:'ukmo',product,runUTC:run,forecastHour:54};
  const urls=()=>Array.from(context.makeChartImageUrls(selection));
  assert.deepEqual(urls(),[native],'No private image yet: keep original KMA product');
  payload.charts=[{...row(),kma_confirmed_at:null}];await api.load();
  assert.deepEqual(urls(),[native],'An uploaded but unconfirmed UKMO image must never be shown');
  payload.charts=[row(),row('acptot1')];await api.load();
  assert.deepEqual(urls(),[row().url]);
  assert.deepEqual(Array.from(api.resolveUrls({...selection,variant:'compare'})),[row('acptot1').url]);
  assert.deepEqual(Array.from(context.getOrderedChartUrlCandidates(row().url)).slice(-1),[native]);
  context.chartResolvedUrlCache.set(row().url,native);
  assert.notEqual(context.getOrderedChartUrlCandidates(row().url)[0],native,'A transient fallback must not permanently pin the original');
  assert.deepEqual(Array.from(api.resolveUrls({...selection,product:{category:'hkor',id:'acrain'}})),[],'Confirmation is not shared across products');
  assert.deepEqual(Array.from(api.resolveUrls({...selection,forecastHour:57})),[],'A different forecast lead cannot inherit confirmation');
  assert(!api.supportsReplacement('ukmo',{category:'asia',id:'surfce'},run));
  assert(!api.supportsReplacement('ukmo',product,new Date(Date.UTC(2026,10,18,6))));
  const expired=Date.UTC(2026,10,20,0,0,1);now=expired;
  assert.deepEqual(urls(),[native],'48h expiration falls back even before another manifest arrives');
  let refreshed=0;
  context.fetch=async()=>({ok:true,json:async()=>payload});
  now=Date.UTC(2026,10,18,4);
  const expiring=context.CDSPublicCharts.createStore({fetchImpl:async()=>{
    if(now===expired) throw new Error('Offline');
    return {ok:true,json:async()=>payload};
  }});
  await expiring.startPolling(()=>refreshed++);
  assert.equal(expiring.resolveUrls(selection).length,1);
  now=expired;await expiring.load();expiring.stopPolling();
  assert.equal(refreshed,2,'An open view is refreshed on expiry even when the manifest fetch fails');
  assert.equal(expiring.resolveUrls(selection).length,0);
  assert(api.isReplacementProduct('ukmo',product),'Expiry must still invalidate the displayed UKMO view');
  context.refreshPublicChartManifestView();
  assert.equal(viewRefreshes,1,'Expiry must redraw an already displayed UKMO chart, not just its model buttons');
  now=Date.UTC(2026,10,18,4);payload.charts=[];await api.load();
  assert.deepEqual(urls(),[native],'Retention removal restores native KMA URLs');
  assert(!api.supportsReplacement('ukmo',product,new Date(Date.UTC(2027,4,18)),Date.UTC(2027,4,18,4)));
  const css=fs.readFileSync(path.join(root,'style.css'),'utf8');
  const rule=css.match(/\.winter-product-notice\{([^}]+)\}/)[1];
  assert(rule.includes('#eef6ff') && rule.includes('#285f9e'));
  console.log('UKMO: independent KMA release gates, seasonal/region scope, original fallback, 48h expiry and blue notice passed');
})().catch(error=>{console.error(error);process.exitCode=1;});

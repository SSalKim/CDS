const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');

const context={
  console,window:{},Date,
  currentMainMenu:'ensemble',currentModel:'ukmo_epsg',currentProduct:'spgt',
  productCategory:{value:'spgt'},runDate:{value:'2026-07-30'},
  runHour:{value:'12:00'},timeMode:'UTC',
  getCurrentCategory:()=>context.productCategory.value
};
vm.createContext(context);
for(const file of [
  'models.js','ensemble.js','aux-data.js','aux-rules.js','catalog-config.js',
  'catalog-core.js','model-menu.js','product-menu.js','catalog-selection.js',
  'aux-panel.js','time-controls.js','forecast-domain.js','compare-mode.js','chart-utils.js',
  'main-menu.js'
]){
  vm.runInContext(fs.readFileSync(path.join(__dirname,'..',file),'utf8'),context);
}
const evaluate=code=>vm.runInContext(code,context);
const snapshot=code=>JSON.parse(evaluate(`JSON.stringify(${code})`));
const select=(model,category,product)=>{
  context.currentModel=model;
  context.productCategory.value=category;
  context.currentProduct=product;
};
const urls=(run,detail,lead)=>Array.from(context.window.CDSChartUtils.makeChartImageUrls({
  product:snapshot('getCurrentProduct()'),modelId:context.currentModel,
  runUTC:new Date(run),detailToken:detail,forecastHour:lead,
  models:snapshot('MODELS'),formatUTCStampFromDate:context.formatUTCStampFromDate
}));

assert.equal(evaluate("isModelVisibleInCurrentMenu('ukmo_epsg')"),true);
assert.equal(evaluate("getEffectiveModelStatus('ukmo_epsg',new Date('2026-07-29T12:00:00Z')).available"),false);
assert.deepEqual(snapshot("getAvailableCycles('ukmo_epsg',parseDateOnly('2026-07-29'))"),[]);
assert.deepEqual(snapshot("getCyclesForSelection('ukmo_epsg',getCurrentProduct(),parseDateOnly('2026-07-30'))"),[12]);
assert.deepEqual(snapshot("getAvailableCycles('ukmo_epsg',parseDateOnly('2026-07-31'))"),[0,12]);
for(const cycle of [0,12]){
  assert.deepEqual(snapshot(`getForecastHours('ukmo_epsg',parseDateOnly('2026-07-31'),${cycle})`),
    Array.from({length:41},(_,index)=>index*6));
}
assert.deepEqual(urls('2026-07-30T12:00:00Z','hg01',240),[
  'https://data.kma.go.kr/CHT/EPSG/202607/30/ukmo_epsg_stdv_spgt_hg01_s240_2026073012.png'
]);
assert(snapshot('getComparableModelsForCurrentProduct()').includes('ukmo_epsg'));
assert.equal(evaluate('getCurrentAuxConfig().defaultValue'),'hg01');

select('ukmo_epsg','snwp','snwp');
assert.deepEqual(snapshot('getForecastHoursForCurrentSelection()'),
  Array.from({length:10},(_,index)=>15+index*24));

select('kim_epsg','week','week');
assert.equal(evaluate('productUsesForecastHour()'),false);
assert.deepEqual(snapshot('getComparableModelsForCurrentProduct()').sort(),['kim_epsg','um_epsg']);
assert.deepEqual(urls('2026-09-29T00:00:00Z','no1',120),[
  'https://data.kma.go.kr/CHT/KIME/202609/29/kim_cmpr_week_epsg_2026092900.png'
]);
select('um_epsg','week','week');
assert.deepEqual(urls('2026-03-01T00:00:00Z','no1',120),[
  'https://data.kma.go.kr/CHT/EXTJ/202603/01/cmpr_week_epsg_2026030100.gif'
]);

for(const [category,productId,family,title] of [
  ['cnf1','area','area','일강수'],['cnf2','ar12','12hr','12H강수']
]){
  for(const [model,prefix,folder] of [
    ['kim_epsg','kim','KIME'],['ukmo_epsg','ukmo','EPSG']
  ]){
    select(model,category,productId);
    assert.equal(evaluate(`getDefaultProductForCategory('${category}').id`),productId);
    assert.equal(evaluate('productUsesForecastHour()'),false);
    assert.deepEqual(snapshot('getComparableModelsForCurrentProduct()').sort(),category==='cnf2'
      ?['ecmwf_eps','kim_epsg','ukmo_epsg','um_epsg']
      :['kim_epsg','ukmo_epsg','um_epsg']);
    const aux=snapshot('getCurrentAuxConfig()');
    assert.equal(aux.title,title);
    assert.equal(aux.defaultValue,'no1');
    assert.deepEqual(aux.items.map(item=>item.value),['no1','no2','no3','no4','no5','no6','no7']);
    for(const detail of aux.items.map(item=>item.value)){
      assert.deepEqual(urls('2026-09-29T00:00:00Z',detail,240),[
        `https://data.kma.go.kr/CHT/${folder}/202609/29/${prefix}_epsg_rain_conf_${family}_${detail}_2026092900.png`
      ]);
    }
  }
}

select('ukmo_epsg','srf3','srf3');
const stationItems=snapshot('getCurrentAuxConfig().items');
assert(stationItems.some(item=>item.value==='47108' && !item.disabled));
assert(stationItems.filter(item=>['47175','47251'].includes(item.value)).every(item=>item.disabled));

console.log('Ensemble catalog, archive boundary, forecast hours, URLs and comparison tests passed');

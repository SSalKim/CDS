const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');

const context={
  console, window:{},
  currentMainMenu:'ensemble', currentModel:'ecmwf_eps', currentProduct:'ar12',
  productCategory:{value:'cnf2'},
  getCurrentCategory:()=>context.productCategory.value
};
vm.createContext(context);
for(const file of [
  'models.js','ensemble.js','aux-data.js','aux-rules.js','catalog-config.js',
  'catalog-core.js','model-menu.js','product-menu.js','catalog-selection.js',
  'aux-panel.js','forecast-domain.js','compare-mode.js','chart-utils.js','main-menu.js'
]){
  vm.runInContext(fs.readFileSync(path.join(__dirname,'..',file),'utf8'),context);
}
const evaluate=code=>vm.runInContext(code,context);
const snapshot=code=>JSON.parse(evaluate(`JSON.stringify(${code})`));
const product=snapshot('getCurrentProduct()');
assert.deepEqual(Object.keys(product.patternByModel).sort(),['ecmwf_eps','kim_epsg','ukmo_epsg','um_epsg']);
assert.equal(product.category,'cnf2');
assert.equal(product.id,'ar12');
assert.equal(evaluate("getDefaultProductForCategory('cnf2').id"),'ar12');
assert.equal(evaluate("ENSEMBLE_CATEGORIES.some(category=>category.id==='pp12')"),false);
assert.equal(evaluate("ENSEMBLE_PRODUCTS.some(product=>product.category==='pp12')"),false);
assert.equal(evaluate('productUsesForecastHour()'),false);
assert.deepEqual(snapshot('getComparableModelsForCurrentProduct()').sort(),['ecmwf_eps','kim_epsg','ukmo_epsg','um_epsg']);
assert.equal(evaluate('getProductCategoryUIConfig().hideProductSelect'),undefined);

const aux=snapshot('getCurrentAuxConfig()');
assert.equal(aux.title,'12H강수');
assert.equal(aux.defaultValue,'no1');
const supported=aux.items.filter(item=>!item.disabled);
assert.deepEqual(supported.map(item=>[item.value,item.label]),[
  ['no1','0.1mm 이상'],['no2','0.5mm 이상'],['no3','5.0mm 이상'],
  ['no4','10mm 이상'],['no5','30mm 이상']
]);
assert.deepEqual(aux.items.filter(item=>item.disabled).map(item=>item.value),['no6','no7']);
for(const item of aux.items){
  context.item=item;
  assert.equal(evaluate('isAuxItemStaticallySupported(item)'),!item.disabled);
}

context.makeUrls=(modelId,run,detail,forecastHour)=>context.window.CDSChartUtils.makeChartImageUrls({
  product, modelId, runUTC:new Date(run), detailToken:detail, forecastHour,
  models:snapshot('MODELS'),
  formatUTCStampFromDate:date=>date.toISOString().replace(/[-:T]/g,'').slice(0,10)
});
for(const hour of ['00','12']){
  for(const item of supported){
    for(const lead of [0,24,120]){
      const urls=Array.from(context.makeUrls('ecmwf_eps',`2026-03-01T${hour}:00:00Z`,item.value,lead));
      assert.deepEqual(urls,[`https://data.kma.go.kr/CHT/ECMW/202603/01/ecmw_epsg_pp12_${item.value}_20260301${hour}.gif`]);
    }
  }
}
for(const detail of ['no6','no7']){
  assert.deepEqual(Array.from(context.makeUrls('ecmwf_eps','2026-03-01T00:00:00Z',detail,24)),[]);
  for(const model of ['kim_epsg','ukmo_epsg','um_epsg']){
    assert.equal(context.makeUrls(model,'2026-09-29T00:00:00Z',detail,24).length,1);
  }
}
assert.equal(product.archiveEndByModel,undefined,'Unconfirmed missing recent charts must not mark the product retired.');

context.productCategory.value='prep';
context.currentProduct='prep';
context.currentModel='kim_epsg';
assert.deepEqual(snapshot('getComparableModelsForCurrentProduct()').sort(),['kim_epsg','ukmo_epsg','um_epsg']);
assert.equal(evaluate('productUsesForecastHour()'),true);
assert.deepEqual(snapshot('getCurrentAuxConfig().items.map(item=>item.label)'),[
  '1mm 이상','5mm 이상','10mm 이상','25mm 이상'
]);
assert.deepEqual(snapshot('getCurrentProduct().patternByModel'),{
  kim_epsg:'kim_epsg_prob_rain_{detail}_s{fh}_{run}.png',
  ukmo_epsg:'ukmo_epsg_prob_rain_{detail}_s{fh}_{run}.png',
  um_epsg:'epsg_prob_prec_{detail}_s{fh}_{run}.gif'
});
console.log('ECMWF EPS half-day weekly probability catalog, thresholds, URLs and comparison tests passed');

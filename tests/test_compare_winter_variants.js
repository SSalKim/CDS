const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');

let mobile=false;
const context={window:{matchMedia:()=>({matches:mobile})}};
vm.createContext(context);
for(const file of ['time-controls.js','compare-mode.js']){
  vm.runInContext(fs.readFileSync(path.join(__dirname,'..',file),'utf8'),context);
}
const evaluate=code=>vm.runInContext(code,context);
function usesVariant(date,productId='acptot',modelId='kim_gdps',category='hkor'){
  context.product={category,id:productId};
  return evaluate(`shouldUseWinterCompareVariant(${JSON.stringify(modelId)},product,new Date(${JSON.stringify(date)}))`);
}

for(let month=1;month<=12;month++){
  const date=`2026-${String(month).padStart(2,'0')}-01T00:00:00Z`;
  for(const productId of ['acptot','acrain','tmerge']){
    assert.equal(usesVariant(date,productId),month>=10 || month<=4);
  }
}
assert.equal(usesVariant('2026-09-30T23:59:59Z'),false);
assert.equal(usesVariant('2026-10-01T00:00:00Z'),true);
assert.equal(usesVariant('2026-04-30T23:59:59Z'),true);
assert.equal(usesVariant('2026-05-01T00:00:00Z'),false);
assert.equal(evaluate('isWinterSeasonRunDate(new Date(NaN))'),false);
assert.equal(evaluate('isWinterSeasonRunDate(null)'),false);
context.compareModels=['kim_gdps','ecmwf','gfs','cmc','icon'];
context.getCurrentProduct=()=>({id:'acptot',category:'hkor'});
context.getSelectedUTCDate=()=>evaluate("new Date('2026-11-18T00:00:00Z')");
assert.equal(evaluate('getAutoCompareColumns()'),5,'Winter portrait charts default to n by 1');
mobile=true;assert.equal(evaluate('getAutoCompareColumns()'),5);mobile=false;
context.getCurrentProduct=()=>({id:'gph500',category:'asia'});
assert.equal(evaluate('getAutoCompareColumns()'),3,'Other automatic layouts are unchanged');
delete context.getCurrentProduct;delete context.getSelectedUTCDate;

for(const [productId,token] of [['acptot','acptot'],['acrain','acrain'],['tmerge','merg']]){
  const pattern=`kim_gdps_erly_hkor_${token}_s{fh}_{run}.png`;
  assert.equal(
    evaluate(`getWinterCompareVariantPattern(${JSON.stringify(pattern)},${JSON.stringify(productId)})`),
    pattern.replace(token,`${token}1`)
  );
}
assert.equal(usesVariant('2026-10-01T00:00:00Z','acptot','ukmo'),false);
assert.equal(usesVariant('2026-10-01T00:00:00Z','acptot','aigfs'),false);
assert.equal(usesVariant('2026-10-01T00:00:00Z','acrain','aigfs'),false);
assert.equal(usesVariant('2026-10-01T00:00:00Z','acptot','um_ldps'),false);
assert.equal(usesVariant('2026-10-01T00:00:00Z','acptot','kim_gdps','asia'),false);
assert.equal(usesVariant('2026-10-01T00:00:00Z','gph500'),false);
assert.equal(usesVariant('2020-10-01T00:00:00Z'),false);
assert.equal(usesVariant('2020-12-28T18:00:00Z'),false);
assert.equal(usesVariant('2020-12-29T00:00:00Z'),true);

function winterNotice(date,modelId='ukmo',productId='acptot',category='hkor'){
  context.product={category,id:productId};
  return evaluate(`getWinterPrecipitationUnsupportedNotice(${JSON.stringify(modelId)},product,new Date(${JSON.stringify(date)}))`);
}
for(let month=1;month<=12;month++){
  for(const model of ['ukmo','aigfs']){
    for(const product of ['acptot','acrain']){
      assert.equal(!!winterNotice(`2026-${String(month).padStart(2,'0')}-01T00:00:00Z`,model,product),month>=10 || month<=4);
    }
  }
}
assert.equal(winterNotice('2026-11-17T00:00:00Z'),'겨울철 산출물(강설량/적설) 미지원 모델 입니다.');
for(const model of ['kim_gdps','aifs','gfs','cmc','icon','ecmwf','um_ldps']){
  assert.equal(winterNotice('2026-11-17T00:00:00Z',model),'');
}
assert.equal(winterNotice('2026-11-17T00:00:00Z','ukmo','acptot','asia'),'');
assert.equal(winterNotice('2026-11-17T00:00:00Z','ukmo','gph500'),'');
assert.equal(winterNotice('invalid'),'');

context.compareModels=['kim_gdps','ukmo','ecmwf'];
context.getCompareProductForModel=()=>context.product;
function topAligned(date,modelId='ukmo',productId='acptot',category='hkor',loadedImages=null){
  context.product={category,id:productId};
  context.loadedImages=loadedImages;
  return evaluate(`shouldTopAlignCompareImage(${JSON.stringify(modelId)},new Date(${JSON.stringify(date)}),loadedImages)`);
}
for(const productId of ['acptot','acrain','tmerge']){
  assert.equal(topAligned('2026-10-09T00:00:00Z','ukmo',productId),true);
}
assert.equal(topAligned('2026-10-09T00:00:00Z','kim_gdps'),false);
assert.equal(topAligned('2026-10-09T00:00:00Z','ecmwf'),false);
const singlePanel=[{naturalWidth:584,naturalHeight:666}];
const winterComposite=[{naturalWidth:600,naturalHeight:2000}];
for(const productId of ['acptot','acrain']){
  assert.equal(topAligned('2026-11-18T00:00:00Z','ukmo',productId,'hkor',singlePanel),true);
  assert.equal(topAligned('2026-11-18T00:00:00Z','ukmo',productId,'hkor',winterComposite),false);
  assert.equal(topAligned('2026-11-18T00:00:00Z','ukmo',productId,'hkor',[...singlePanel,...singlePanel,...singlePanel]),false);
}
context.CDSPublicCharts={supportsReplacement:()=>true,usesSource:()=>false};
assert.equal(topAligned('2026-11-18T00:00:00Z','ukmo','acptot','hkor',singlePanel),true,'KMA fallback stays top aligned');
assert.equal(topAligned('2026-11-18T00:00:00Z','ukmo','acptot','hkor',winterComposite),false);
context.CDSPublicCharts.usesSource=()=>true;
assert.equal(topAligned('2026-11-18T06:00:00Z','ukmo','acrain','hkor',winterComposite),false);
delete context.CDSPublicCharts;
context.compareModels=['aigfs','ecmwf'];
assert.equal(topAligned('2026-10-09T00:00:00Z','aigfs'),true);
assert.equal(topAligned('2026-11-18T00:00:00Z','aigfs','acptot','hkor',singlePanel),true);
context.compareModels=['aigfs','ukmo'];
assert.equal(topAligned('2026-10-09T00:00:00Z','aigfs'),false);
context.compareModels=['kim_gdps','ukmo','ecmwf'];
assert.equal(topAligned('2026-09-30T23:59:59Z'),false);
assert.equal(topAligned('2026-05-01T00:00:00Z'),false);
assert.equal(topAligned('2020-12-28T18:00:00Z'),false);
assert.equal(topAligned('2026-10-09T00:00:00Z','ukmo','gph500'),false);
assert.equal(topAligned('2026-10-09T00:00:00Z','ukmo','acptot','asia'),false);
context.compareModels=['ukmo'];
assert.equal(topAligned('2026-10-09T00:00:00Z'),false);
context.compareModels=['ukmo','um_ldps'];
assert.equal(topAligned('2026-10-09T00:00:00Z'),false);
context.compareModels=['ukmo','ecmwf'];
mobile=true;
assert.equal(usesVariant('2026-10-01T00:00:00Z'),false);
assert.equal(topAligned('2026-10-09T00:00:00Z'),false);

console.log('Comparison winter variants and UKUM top alignment conditions passed');

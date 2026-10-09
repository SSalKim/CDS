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

for(const [productId,token] of [['acptot','acptot'],['acrain','acrain'],['tmerge','merg']]){
  const pattern=`kim_gdps_erly_hkor_${token}_s{fh}_{run}.png`;
  assert.equal(
    evaluate(`getWinterCompareVariantPattern(${JSON.stringify(pattern)},${JSON.stringify(productId)})`),
    pattern.replace(token,`${token}1`)
  );
}
assert.equal(usesVariant('2026-10-01T00:00:00Z','acptot','ukmo'),false);
assert.equal(usesVariant('2026-10-01T00:00:00Z','acptot','um_ldps'),false);
assert.equal(usesVariant('2026-10-01T00:00:00Z','acptot','kim_gdps','asia'),false);
assert.equal(usesVariant('2026-10-01T00:00:00Z','gph500'),false);
assert.equal(usesVariant('2020-10-01T00:00:00Z'),false);
assert.equal(usesVariant('2020-12-28T18:00:00Z'),false);
assert.equal(usesVariant('2020-12-29T00:00:00Z'),true);

context.compareModels=['kim_gdps','ukmo','ecmwf'];
context.getCompareProductForModel=()=>context.product;
function topAligned(date,modelId='ukmo',productId='acptot',category='hkor'){
  context.product={category,id:productId};
  return evaluate(`shouldTopAlignCompareImage(${JSON.stringify(modelId)},new Date(${JSON.stringify(date)}))`);
}
for(const productId of ['acptot','acrain','tmerge']){
  assert.equal(topAligned('2026-10-09T00:00:00Z','ukmo',productId),true);
}
assert.equal(topAligned('2026-10-09T00:00:00Z','kim_gdps'),false);
assert.equal(topAligned('2026-10-09T00:00:00Z','ecmwf'),false);
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

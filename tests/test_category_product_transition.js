const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');

const context={
  isForecastCatalog:()=>true
};
vm.createContext(context);
vm.runInContext(
  fs.readFileSync(path.join(__dirname,'..','catalog-selection.js'),'utf8'),
  context
);

function resolve(fromCategory,toCategory,productId){
  context.fromCategory=fromCategory;
  context.toCategory=toCategory;
  context.productId=productId;
  return vm.runInContext(
    'resolveProductIdForCategoryTransition(fromCategory,toCategory,productId)',
    context
  );
}

assert.equal(
  resolve('hkor','asia','acptot'),
  'surfce',
  'Korea hourly precipitation should transition to the Asia surface product.'
);
assert.equal(resolve('asia','hkor','acptot'),'acptot');
assert.equal(resolve('hkor','asia','gph500'),'gph500');

context.isForecastCatalog=()=>false;
assert.equal(resolve('hkor','asia','acptot'),'acptot');

console.log('category product transition tests passed');

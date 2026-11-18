const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const root=path.join(__dirname,'..');
const app=fs.readFileSync(path.join(root,'app.js'),'utf8');
const limit=Number(app.match(/const COMPARE_MAX_MODELS=(\d+)/)[1]);
assert.equal(limit,10);
const models=Array.from({length:11},(_,i)=>'model'+i);
let mobile=false,notice='',refreshes=0;
const context={console,COMPARE_MAX_MODELS:limit,compareModels:[],currentModel:models[0],
  window:{matchMedia:()=>({matches:mobile})},compareLayoutMode:'auto',compareManualLayout:null,
  compareFitToScreen:true,getSelectedForecastHour:()=>24,invalidateSelectionAsyncWork:()=>{},
  refreshView:()=>refreshes++,showViewerNotice:value=>notice=value};
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(root,'compare-mode.js'),'utf8'),context);
context.isModelComparableForCurrentProduct=()=>true;
context.getComparableModelsForCurrentProduct=()=>models;
for(const model of models.slice(0,10)) context.toggleCompareModel(model);
assert.equal(context.compareModels.length,10);
assert.equal(refreshes,10);
context.toggleCompareModel(models[10]);
assert.equal(context.compareModels.length,10);
assert(notice.includes('10'));
assert.equal(refreshes,10);
for(let count=7;count<=10;count++){
  const layouts=context.getCompareLayoutOptions(count);
  assert(layouts.every(layout=>layout.cols*layout.rows>=count));
  assert(layouts.some(layout=>layout.cols===5 && layout.rows===2));
}
context.compareModels=models.slice();context.normalizeCompareModels();
assert.equal(context.compareModels.length,10);
mobile=true;assert.equal(context.getActiveCompareLayout().cols,1);
context.toggleCompareModel(models[0]);assert.equal(context.compareModels.length,9);
console.log('Comparison: ten models, eleventh rejection, removal, layouts 7-10 and mobile passed');

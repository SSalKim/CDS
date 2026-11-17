const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const context={currentMainMenu:'forecast',currentModel:'kim_gdps',currentProduct:'gph500',modelCompareMode:false,
compareModels:[],productCategory:{value:'asia'},MODELS:{ukmo:{cycles:[0,12]},cmc:{cycles:[0,12]},gfs:{cycles:[0,6,12,18]}},
getCurrentCategory:()=>context.productCategory.value,getSelectedUTCDate:()=>vm.runInContext("new Date('2026-11-17T06:00:00Z')",context),
getCurrentProduct:()=>({id:'gph500',category:'asia'}),getEffectiveModelStatus:()=>({available:true}),
getAvailableCycles:id=>context.MODELS[id].cycles,getSelectionRestrictionForProduct:()=>null,
isCategoryAllowedByModelRestriction:()=>true,productSupportsModel:()=>true,
modelGroups:[{models:[['kim_gdps','KIM_GDAPS'],['ukmo','UKUM'],['cmc','CMC']]}]};
vm.createContext(context);
for(const file of ['time-controls.js','selection-navigation.js']) vm.runInContext(fs.readFileSync(file,'utf8'),context);
context.getSelectedUTCDate=()=>vm.runInContext("new Date('2026-11-17T06:00:00Z')",context);
const run=code=>vm.runInContext(code,context);
assert.equal(run("modelRunIsUnsupported('ukmo')"),true);
assert.equal(run("modelRunIsUnsupported('cmc')"),true);
assert.equal(run("modelRunIsUnsupported('gfs')"),false);
assert.equal(run("getMostRecentSupportedRun('cmc',{},new Date('2026-11-17T06:00:00Z')).toISOString()"),'2026-11-17T00:00:00.000Z');
assert.equal(run("getMostRecentSupportedRun('ukmo',{},new Date('2026-11-17T18:00:00Z')).toISOString()"),'2026-11-17T12:00:00.000Z');
assert.equal(run("getMostRecentSupportedRun('cmc',{},new Date('2026-11-17T00:00:00Z')).toISOString()"),'2026-11-17T00:00:00.000Z');
context.currentMainMenu='analysis';assert.equal(run("modelRunIsUnsupported('ukmo')"),false);context.currentMainMenu='forecast';
context.getVisibleModelsSupportingProduct=()=>['gfs','kim_gdps'];
assert.equal(run('getSuggestedModelForProduct({category:"asia"})'),'kim_gdps');
context.getSelectionRestrictionForProduct=()=>({fallbackModel:'gfs',allowedModels:['gfs']});
assert.equal(run('getSuggestedModelForProduct({category:"asia"})'),'gfs');
context.getModelButtonAllowed=()=>true;
context.confirmSelectionChange=async()=>false;
context.getSelectedTimelineHourForPreserve=()=>24;
context.invalidateSelectionAsyncWork=()=>{throw new Error('Cancelled selection must not mutate state');};
context.getCurrentProductLabel=()=>'500 고도,기온,풍속';
context.findProductFallbackForModel=()=>({categoryId:'asia',productId:'gph500'});
context.getProductByIdInCategory=()=>({id:'gph500',category:'asia'});
context.getModelButtonAllowed=()=>false;
context.showViewerNotice=()=>{};
context.toggleCompareModel=id=>{context.removed=id;};
(async()=>{
await run("requestModelSelection('ukmo')");
assert.equal(context.currentModel,'kim_gdps');
context.getModelButtonAllowed=()=>true;
await run("requestModelSelection('cmc')");
assert.equal(context.currentModel,'kim_gdps');
context.modelCompareMode=true;context.compareModels=['kim_gdps','cmc'];
await run("requestModelSelection('cmc')");assert.equal(context.removed,'cmc');
console.log('Selection navigation: cycles, fallback preferences, cancellation and compare removal passed');
})().catch(error=>{console.error(error);process.exitCode=1;});

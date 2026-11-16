const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');

const app=fs.readFileSync(path.join(__dirname,'..','app.js'),'utf8');
let message='';
const expected='ICON\n모델·산출물·자료시각 조합은 유효하지만 이미지 파일을 찾지 못했습니다.';
const context={
  console,currentModel:'icon',forecastDisplayRequest:0,modelCompareMode:false,
  slider:{value:'0'},chartImages:{querySelector:()=>null},
  modelStatus:{textContent:'',classList:{add(){}}},
  isPublicChartModel:()=>['aifs','gfs','aigfs','cmc','icon'].includes(context.currentModel),
  makeExpectedButMissingMessage:()=>expected,
  showViewerMessage:value=>{message=value;},
  getForecastImageCacheEntry:()=>null,selectionIsDisplayable:()=>true,
  isRunTimeFrameFuture:()=>false,buildImageUrlsForForecastIndex:()=>[]
};
vm.createContext(context);
for(const name of ['showCharts','displayCurrentForecastImage']){
  const start=app.search(new RegExp(`^async function ${name}\\(`,'m'));
  assert(start>=0,name);
  let end=start,found=false;
  while((end=app.indexOf('\n}',end+1))>=0){
    const source=app.slice(start,end+2);
    try{new vm.Script(source);}catch{continue;}
    vm.runInContext(source,context);
    found=true;
    break;
  }
  assert(found,name);
}

async function main(){
  for(const model of ['aifs','gfs','aigfs','cmc','icon','kim_gdps']){
    context.currentModel=model;
    const wanted=model==='kim_gdps'?'표출할 이미지 URL이 없습니다.':expected;
    message='';
    await context.showCharts([]);
    assert.equal(message,wanted,model+' empty URL display');
    message='';
    await context.displayCurrentForecastImage();
    assert.equal(message,wanted,model+' missing timeline image');
  }
  context.currentModel='icon';
  context.selectionIsDisplayable=()=>{message='지원하지 않는 조합';return false;};
  await context.displayCurrentForecastImage();
  assert.equal(message,'지원하지 않는 조합','Unsupported combinations retain their specific explanation');
  console.log('Single missing images: ICON and other public models use the contextual placeholder; legacy behavior preserved');
}
main().catch(error=>{console.error(error);process.exitCode=1;});

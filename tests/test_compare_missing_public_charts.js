const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');

const publicModels=['aifs','gfs','aigfs','cmc','icon'];
const labels={aifs:'AIFS',gfs:'GFS',aigfs:'AIGFS',cmc:'CMC',icon:'ICON',kim_gdps:'KIM_GDAPS'};
const urls=new Map();
const blocked=new Map();
function element(){
  return {children:[],style:{setProperty(){}},classList:{add(){},remove(){},toggle(){}},
    appendChild(child){this.children.push(child);},replaceChildren(...children){this.children=children;}};
}
const viewer=element();
const context={console,Date,compareModels:publicModels,currentForecastList:[132],slider:{value:'0'},
  forecastDisplayRequest:0,timeMode:'KST',compareFitToScreen:false,compareLayoutMode:'auto',
  chartImages:viewer,modelStatus:element(),document:{createElement:element},
  CDSPublicCharts:{isModel:id=>publicModels.includes(id),usesSource:id=>publicModels.includes(id)},
  normalizeCompareLayout(){},setViewerLoading(){},getActiveCompareLayout:()=>({cols:3}),
  getSelectedUTCDate:()=>new Date('2026-11-16T12:00:00Z'),
  getModelDisplayLabel:id=>labels[id],getCurrentProductLabel:()=> '500 고도,기온,풍속',
  getForecastLeadLabelForHour:hour=>`+${hour}h`,pad2:value=>String(value).padStart(2,'0'),
  formatDateInputFromUTCParts:date=>date.toISOString().slice(0,10),
  addImageRefreshTokenToUrls:value=>value,createDecodedDisplayImage:async()=>null,
  getMobileCompareImageColumns:()=>null,clearCompareImageItemHeights(){},
  revealPreparedImages(){},scheduleCompareImageItemHeightSync(){},showViewerMessage(){}};
context.window=context;
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(__dirname,'..','compare-mode.js'),'utf8'),context);
// Keep real render/message functions, replacing only their unrelated UI/catalog dependencies.
context.shouldTopAlignCompareImage=()=>false;
context.getModelDisplayLabel=id=>labels[id];
context.getForecastLeadLabelForHour=hour=>`+${hour}h`;
context.getCompareBlockedMessage=id=>blocked.get(id) || '';
context.getCompareProductForModel=()=>({id:'gph500',category:'asia'});
context.buildCompareImageUrlsForModel=id=>urls.get(id) || [];
context.trackCompareProductViewAnalytics=()=>{};
context.getMobileCompareImageColumns=()=>null;
context.clearCompareImageItemHeights=()=>{};
context.scheduleCompareImageItemHeightSync=()=>{};

async function main(){
  await context.renderCompareImages();
  assert.equal(viewer.children.length,publicModels.length);
  for(let index=0;index<publicModels.length;index++){
    const message=viewer.children[index].children[0].textContent;
    assert(message.startsWith(labels[publicModels[index]]+'\n'));
    assert(message.includes('500 고도,기온,풍속 / 2026-11-22 09:00 KST / +132h'));
    assert(message.includes('조합은 유효하지만 이미지 파일을 찾지 못했습니다.'));
    assert(message.includes('아직 생산 또는 업로드 전일 수 있습니다.'));
    assert(!message.includes('URL을 생성하지 못했습니다.'));
  }
  blocked.set('aifs','AIFS\n+003h 예측시간을 지원하지 않습니다.');
  blocked.set('cmc','CMC\n선택한 자료시각을 지원하지 않습니다.');
  await context.renderCompareImages();
  assert.equal(viewer.children[0].children[0].textContent,blocked.get('aifs'));
  assert.equal(viewer.children[3].children[0].textContent,blocked.get('cmc'));
  blocked.clear();
  context.compareModels=['aifs','kim_gdps'];
  urls.set('aifs',['https://example.invalid/not-yet-ready.webp']);
  urls.set('kim_gdps',['https://example.invalid/not-yet-ready.gif']);
  await context.renderCompareImages();
  assert(viewer.children.every(item=>item.children[0].textContent.includes('조합은 유효하지만')),
    'URL-backed image failures still use the same existing placeholder');
  urls.clear();
  await context.renderCompareImages();
  assert(viewer.children[1].children[0].textContent.includes('이미지 URL을 생성하지 못했습니다.'),
    'Legacy URL configuration errors are not reclassified');
  console.log('Comparison missing images: all five public models, details, blocked combinations and legacy behavior passed');
}
main().catch(error=>{console.error(error);process.exitCode=1;});

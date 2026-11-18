const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const {DatabaseSync}=require('node:sqlite');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(__dirname,'..');
const output=path.join(root,'outputs/viewer-usage-20261118');fs.mkdirSync(output,{recursive:true});
const types={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.png':'image/png'};
(async()=>{
const {default:worker}=await import(pathToFileURL(path.join(root,'analytics_service/src/worker.js')));
const {insert,cleanEvent}=await import(pathToFileURL(path.join(root,'analytics_service/src/data.js')));
const sqlite=new DatabaseSync(':memory:');
for(const file of fs.readdirSync(path.join(root,'analytics_service/migrations')).filter(file=>file.endsWith('.sql')).sort())sqlite.exec(fs.readFileSync(path.join(root,'analytics_service/migrations',file),'utf8'));
const db={prepare(sql){let args=[];return {bind(...values){assert(values.length<=100,'D1 parameter limit');args=values;return this;},async all(){return {results:sqlite.prepare(sql).all(...args)};},async run(){return sqlite.prepare(sql).run(...args);}};},async batch(items){return Promise.all(items.map(item=>item.all()));}};
const now=Date.now(),key='a'.repeat(64);
for(const [index,hour]of [0,3,12,120,240,84].entries())await insert(db,{...cleanEvent({event_id:crypto.randomUUID(),occurred_at:now-10000+index,outcome:'view',menu:'forecast',region:'hkor',model_id:'gfs',model_label:'GFS',product_id:'gph500',product_label:'500 고도,기온,풍속',run_utc:'2026-11-18T00:00:00Z',valid_utc:new Date(Date.parse('2026-11-18T00:00:00Z')+hour*3600000).toISOString(),forecast_hour:hour,device_class:'mobile'},now),visitor_key:key,session_key:'one',series_key:'series'}).run();
const env={DB:db,LOCAL_PREVIEW:'true',ASSETS:{async fetch(request){const file=path.join(root,'analytics_service/web',new URL(request.url).pathname==='/'?'index.html':new URL(request.url).pathname.slice(1));return new Response(fs.readFileSync(file),{headers:{'Content-Type':types[path.extname(file)]}});}}};
const browser=await chromium.launch({headless:true,channel:'msedge'});
try{
const page=await browser.newPage({viewport:{width:1440,height:960}}),errors=[];
page.on('pageerror',error=>errors.push(error.message));
await page.route('**/*',async route=>{
const url=new URL(route.request().url());
if(url.hostname==='127.0.0.1'){
const file=path.resolve(root,url.pathname==='/'?'index.html':decodeURIComponent(url.pathname.slice(1)));
if(file.startsWith(root+path.sep)&&fs.existsSync(file)&&fs.statSync(file).isFile())return route.fulfill({body:fs.readFileSync(file),contentType:types[path.extname(file)]||'application/octet-stream'});
return route.fulfill({status:404,body:'not found'});
}
if(['data.kma.go.kr','dmdw.kma.go.kr'].includes(url.hostname))return route.fulfill({body:fs.readFileSync(path.join(root,'outputs/ukmo-extrema-20261118/after-gph500-hkor.png')),contentType:'image/png'});
return route.abort();
});
await page.goto('http://127.0.0.1:8992/',{waitUntil:'domcontentloaded'});
await page.waitForFunction(()=>typeof showViewerNotice==='function'&&typeof CDSChartCapture==='object');
const fitBorders=await page.locator('.viewer-fit-control').evaluate(control=>[control,...control.querySelectorAll('.compare-fit-toggle,.viewer-fit-direction')].map(el=>getComputedStyle(el).borderLeftWidth));
assert.deepEqual(fitBorders,['1px','0px','0px'],'Fit toggle and arrow share one outer button border');
await page.evaluate(()=>{if(selectionConfirmation)selectionConfirmation(false);showViewerNotice('모델 비교는 최대 10개까지 선택할 수 있습니다.');});
await page.locator('dialog[open]').waitFor();assert.match(await page.locator('dialog p').textContent(),/최대 10개/);
assert.equal(await page.locator('dialog button').count(),1);
assert.equal(await page.locator('.sidebar').evaluate(el=>getComputedStyle(el).filter),'none');
await page.screenshot({path:path.join(output,'comparison-limit-desktop.png')});
await page.getByRole('button',{name:'확인',exact:true}).click();
await page.evaluate(()=>{invalidateSelectionAsyncWork();void confirmSelectionChange('선택된 시각의 해당 모델 예측자료가 아직 존재하지 않습니다.\n가장 최근 자료시각으로 이동할까요?');});
await page.locator('dialog[open]').waitFor();await page.setViewportSize({width:390,height:844});
assert(await page.locator('dialog').evaluate(el=>el.getBoundingClientRect().right<=innerWidth));
await page.screenshot({path:path.join(output,'missing-confirmation-mobile.png')});
await page.getByRole('button',{name:'취소',exact:true}).click();
await page.setViewportSize({width:1440,height:960});
// Natural-size, mixed-source panels; the page's fit layout is deliberately smaller.
await page.evaluate(async()=>{
invalidateSelectionAsyncWork();chartImages.innerHTML='';chartImages.className='chart-images compare-images fit-screen';chartImages.style.setProperty('--compare-columns','2');
for(const [width,height,color]of [[600,2000,'#ef4444'],[640,730,'#10b981'],[910,660,'#3b82f6']]){
const c=document.createElement('canvas');c.width=width;c.height=height;const ctx=c.getContext('2d');ctx.fillStyle=color;ctx.fillRect(0,0,width,height);
const item=document.createElement('div');item.className='compare-image-item';const img=new Image();img.src=c.toDataURL();await img.decode();item.append(img);chartImages.append(item);
}
modelStatus.classList.add('hidden');renderTimelineTopControls();
});
await page.getByRole('button',{name:'일기도 캡처',exact:true}).click();
await page.locator('.capture-preview img').waitFor();
const dimensions=await page.locator('.capture-preview img').evaluate(img=>[img.naturalWidth,img.naturalHeight]);
assert.deepEqual(dimensions,[1553,2663]);
const pixels=await page.locator('.capture-preview img').evaluate(img=>{const c=document.createElement('canvas');c.width=img.naturalWidth;c.height=img.naturalHeight;const x=c.getContext('2d');x.drawImage(img,0,0);return [[200,20],[920,650],[20,2010]].map(([a,b])=>[...x.getImageData(a,b,1,1).data]);});
assert.deepEqual(pixels,[[239,68,68,255],[16,185,129,255],[59,130,246,255]]);
await page.screenshot({path:path.join(output,'capture-desktop.png')});
const download=page.waitForEvent('download');await page.getByRole('button',{name:'PNG 다운로드',exact:true}).click();await (await download).saveAs(path.join(output,'capture-original.png'));
await page.evaluate(()=>{navigator.clipboard.write=async items=>{window.copiedType=items[0].types[0];};});
await page.getByRole('button',{name:'이미지 복사',exact:true}).click();await page.waitForFunction(()=>window.copiedType==='image/png');
await page.setViewportSize({width:390,height:844});await page.screenshot({path:path.join(output,'capture-mobile.png')});
await page.getByRole('button',{name:'닫기',exact:true}).click();
assert.equal(await page.locator('dialog[open]').count(),0);assert(!await page.locator('.viewer-wrap').evaluate(el=>el.classList.contains('selection-blurred')));
// Fit by height: one row may overflow horizontally; fit by width: tall charts scroll vertically.
await page.setViewportSize({width:1440,height:960});
await page.evaluate(()=>{modelCompareMode=true;compareModels=['kim_gdps','ecmwf','gfs','cmc','icon'];currentProduct='acptot';productCategory.value='hkor';compareFitToScreen=true;renderTimelineTopControls();});
assert.equal(await page.evaluate(()=>getActiveCompareLayout().cols),5);
await page.getByRole('button',{name:'맞춤 방향',exact:true}).click();
// Suppress remote rerender in this synthetic-pixel fixture, preserving current panels.
await page.evaluate(()=>{renderCompareImages=()=>{};});
await page.getByRole('radio',{name:'상하',exact:true}).check();
await page.waitForFunction(()=>document.getElementById('chartImages').classList.contains('fit-height'));
let bounds=await page.evaluate(()=>{const viewer=document.querySelector('.viewer-wrap'),img=chartImages.querySelector('img').getBoundingClientRect();return {imageHeight:img.height,viewHeight:viewer.clientHeight,overflowY:viewer.scrollHeight>viewer.clientHeight+2};});
assert(bounds.imageHeight<=bounds.viewHeight&&bounds.imageHeight>bounds.viewHeight-60);assert.equal(bounds.overflowY,false);
await page.screenshot({path:path.join(output,'height-fit-desktop.png')});
await page.getByRole('radio',{name:'좌우',exact:true}).check();await page.waitForFunction(()=>!chartImages.classList.contains('fit-height'));
await page.getByRole('button',{name:'맞춤 방향',exact:true}).click();
await page.setViewportSize({width:390,height:844});await page.getByRole('button',{name:'맞춤 방향',exact:true}).click();
await page.getByRole('radio',{name:'상하',exact:true}).check();await page.waitForFunction(()=>chartImages.classList.contains('fit-height'));
assert(await page.evaluate(()=>document.querySelector('.viewer-wrap').scrollWidth>document.querySelector('.viewer-wrap').clientWidth));
await page.screenshot({path:path.join(output,'height-fit-mobile.png')});

const admin=await browser.newPage({viewport:{width:1440,height:960}});admin.on('pageerror',error=>errors.push(error.message));
await admin.route('**/*',async route=>{
if(new URL(route.request().url()).hostname!=='127.0.0.1')return route.abort();
const response=await worker.fetch(new Request(route.request().url(),{method:route.request().method(),headers:route.request().headers(),...(route.request().method()==='GET'?{}:{body:route.request().postData()})}),env);
return route.fulfill({status:response.status,headers:Object.fromEntries(response.headers),body:Buffer.from(await response.arrayBuffer())});
});
await admin.goto('http://127.0.0.1:8791/admin/',{waitUntil:'networkidle'});
await admin.getByRole('button',{name:'사용자별 이력',exact:true}).click();await admin.locator('#userRows .alias-edit').first().click();
await admin.getByRole('textbox',{name:'사용자 별칭',exact:true}).fill('예보 사용자 A');
await admin.getByRole('button',{name:'별칭 저장',exact:true}).click();await admin.getByRole('button',{name:'예보 사용자 A',exact:true}).waitFor();
assert.match(await admin.locator('#userRows').textContent(),/모바일/);
await admin.screenshot({path:path.join(output,'analytics-nickname-desktop.png')});
await admin.getByRole('button',{name:'예보 사용자 A',exact:true}).click();await admin.locator('.lead-count').waitFor();
assert.equal(await admin.locator('#historyRows tr').count(),1);assert.equal(await admin.locator('.lead-count').textContent(),'[6]');
await admin.locator('.lead-count').hover();assert.equal(await admin.locator('.lead-tooltip').textContent(),'+000\n+003\n+012\n+120\n+240\n+084');
await admin.screenshot({path:path.join(output,'analytics-grouped-history.png')});
await admin.setViewportSize({width:390,height:844});await admin.getByRole('button',{name:'사용자별 이력',exact:true}).click();
await admin.screenshot({path:path.join(output,'analytics-mobile.png')});
assert.equal(await admin.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
await admin.reload();await admin.getByRole('button',{name:'사용자별 이력',exact:true}).click();await admin.getByRole('button',{name:'예보 사용자 A',exact:true}).waitFor();
assert.deepEqual(errors,[]);console.log('Desktop/mobile popups, natural-pixel capture/download/copy, persisted nickname, grouped ordered history and device labels passed');
}finally{await browser.close();sqlite.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});

const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const dir=path.resolve('outputs/analytics-review-20261117');
fs.mkdirSync(dir,{recursive:true});

(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
 const page=await browser.newPage({viewport:{width:1440,height:950}});
 const errors=[];page.on('pageerror',error=>errors.push(error.message));
 await page.route('**/*',route=>route.request().url().startsWith('http://127.0.0.1:8980/')?route.continue():route.abort());
 await page.goto('http://127.0.0.1:8980/',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>typeof requestModelSelection==='function'&&document.querySelectorAll('.model-cell').length>3);
 await page.evaluate(()=>{
  invalidateSelectionAsyncWork();currentMainMenu='forecast';currentModel='kim_gdps';currentProduct='gph500';productCategory.value='asia';timeMode='UTC';
  setRunControlsToUTCAllowUnsupported(new Date('2026-11-17T06:00:00Z'));
  refreshView({updateProducts:true,updateHours:false,updateChartAfter:false});
 });
 const uk=page.getByRole('button',{name:'UKUM',exact:true});
 assert.equal(await uk.evaluate(el=>getComputedStyle(el).backgroundColor),'rgb(229, 231, 235)');
 assert.equal(await uk.isEnabled(),true);
 await uk.click();await page.locator('dialog[open]').waitFor();
 assert.match(await page.locator('dialog p').textContent(),/해당 시간대에는 생산되지 않는 모델/);
 assert.equal(await page.locator('dialog').evaluate(el=>getComputedStyle(el,'::backdrop').backgroundColor),'rgba(0, 0, 0, 0)');
 assert.equal(await page.locator('.viewer-wrap').evaluate(el=>el.classList.contains('selection-blurred')),true);
 assert.match(await page.locator('#chartImages').evaluate(el=>getComputedStyle(el).filter),/blur/);
 assert.equal(await page.locator('.sidebar').evaluate(el=>getComputedStyle(el).filter),'none');
 await page.screenshot({path:path.join(dir,'selection-confirmation-desktop.png')});
 await page.getByRole('button',{name:'취소',exact:true}).click();
 assert.deepEqual(await page.evaluate(()=>[currentModel,getSelectedUTCDate().getUTCHours()]),['kim_gdps',6]);
 await uk.click();await page.getByRole('button',{name:'확인',exact:true}).click();
 await page.waitForFunction(()=>currentModel==='ukmo'&&getSelectedUTCDate().getUTCHours()===0);
 await page.evaluate(()=>{
  invalidateSelectionAsyncWork();currentModel='gfs';currentProduct='gph500';productCategory.value='asia';
  refreshView({updateProducts:true,updateHours:false,updateChartAfter:false});
 });
 const unsupported=await page.evaluate(()=>getProductsInCategory('asia').find(p=>!modelSupportsSelectionProduct('gfs',p)&&modelSupportsSelectionProduct('kim_gdps',p))?.id);
 assert(unsupported,'Need a real unsupported product to test');
 await page.locator('#productSelect').selectOption(unsupported);
 await page.locator('dialog[open]').waitFor();assert.match(await page.locator('dialog p').textContent(),/KIM_GDAPS/);
 await page.keyboard.press('Escape');assert.equal(await page.evaluate(()=>currentProduct),'gph500');
 await page.locator('#productSelect').selectOption(unsupported);await page.getByRole('button',{name:'확인',exact:true}).click();
 await page.waitForFunction(id=>currentModel==='kim_gdps'&&currentProduct===id,unsupported);
 await page.evaluate(()=>{void requestModelSelection('gfs');});
 await page.locator('dialog[open]').waitFor();assert.match(await page.locator('dialog p').textContent(),/지원되는 산출물/);
 await page.setViewportSize({width:390,height:844});
 await page.screenshot({path:path.join(dir,'selection-confirmation-mobile.png')});
 assert(await page.locator('dialog').evaluate(el=>el.getBoundingClientRect().right<=innerWidth));
 const centered=await page.locator('dialog').evaluate(el=>{
 const rect=el.getBoundingClientRect(),viewer=document.querySelector('.viewer-wrap').getBoundingClientRect();
 const left=Math.max(12,viewer.left),right=Math.min(document.documentElement.clientWidth-12,viewer.right);
 const top=Math.max(12,viewer.top),bottom=Math.min(innerHeight-12,viewer.bottom);
 const x=Math.min(document.documentElement.clientWidth-rect.width/2-12,Math.max(rect.width/2+12,(left+right)/2));
 const y=Math.min(innerHeight-rect.height/2-12,Math.max(rect.height/2+12,(top+bottom)/2));
 return Math.abs(rect.left+rect.width/2-x)<3&&Math.abs(rect.top+rect.height/2-y)<3;
 });
 assert(centered,'Dialog must be centered in the visible chart viewer');
 await page.getByRole('button',{name:'취소',exact:true}).click();
 await page.evaluate(()=>{
  invalidateSelectionAsyncWork();currentModel='ukmo';currentProduct='acptot';productCategory.value='hkor';
  setRunControlsToUTCAllowUnsupported(new Date('2026-11-17T00:00:00Z'));
  createSingleImageDisplayShell({imageCount:1});
 });
 assert.equal(await page.locator('.winter-product-notice').textContent(),'겨울철 산출물(강설량/적설) 미지원 모델 입니다.');
 await page.screenshot({path:path.join(dir,'winter-notice-mobile.png')});
 assert.deepEqual(errors,[]);

 const stamp=Date.now();
 const payload={version:1,client_id:'999999.123456789',session_id:'100001',events:[0,3,6].map(hour=>({
 event_id:crypto.randomUUID(),occurred_at:stamp+hour,outcome:'view',menu:'forecast',region:'hkor',
 model_id:'gfs',model_label:'GFS',product_id:'gph500',product_label:'500 고도,기온,풍속',
 run_utc:'2026-11-17T00:00:00Z',valid_utc:`2026-11-17T${String(hour).padStart(2,'0')}:00:00Z`,
 forecast_hour:hour,view_context:'single',load_ms:500,device_class:'desktop'}))};
 const received=await fetch('http://127.0.0.1:8791/collect',{method:'POST',headers:{Origin:'http://127.0.0.1:8980','Content-Type':'application/json'},body:JSON.stringify(payload)});
 assert.equal(received.status,202);
 const stats=await browser.newPage({viewport:{width:1440,height:950}});
 const adminErrors=[];stats.on('pageerror',error=>adminErrors.push(error.message));
 await stats.goto('http://127.0.0.1:8791/admin/',{waitUntil:'networkidle'});
 await stats.waitForFunction(()=>document.getElementById('status').textContent.startsWith('갱신'));
 assert.equal(await stats.locator('#error').isVisible(),false);
 assert(Number((await stats.locator('#views').textContent()).replaceAll(',',''))>=3);
 await stats.screenshot({path:path.join(dir,'analytics-desktop.png')});
 await stats.getByRole('button',{name:'브라우저별 이력',exact:true}).click();
 await stats.locator('#userRows button').first().waitFor();
 await stats.locator('#userRows button').first().click();
 await stats.locator('#historyRows td').first().waitFor();
 assert((await stats.locator('#historyRows').textContent()).includes('+006h'));
 await stats.setViewportSize({width:390,height:844});
 await stats.getByRole('button',{name:'요약·산출물 TOP',exact:true}).click();
 await stats.waitForTimeout(250);
 await stats.screenshot({path:path.join(dir,'analytics-mobile.png'),fullPage:true});
 assert.equal(await stats.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
 assert.deepEqual(adminErrors,[]);
 console.log('Desktop/mobile dialogs, cancellation, model/product fallback, winter notice and real local D1 dashboard passed');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});

const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root=path.resolve(__dirname,'..');
const output=path.join(root,'outputs/selection-cancel-20261119');
const image=path.join(root,'outputs/ukmo-extrema-20261118/after-gph500-hkor.png');
const types={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json',
  '.png':'image/png','.woff2':'font/woff2'};

(async()=>{
  fs.mkdirSync(output,{recursive:true});
  const browser=await chromium.launch({headless:true,channel:'msedge'});
  try{
    const page=await browser.newPage({viewport:{width:1440,height:950}});
    const errors=[];
    page.on('pageerror',error=>errors.push(error.message));
    await page.route('**/*',route=>{
      const url=new URL(route.request().url());
      if(url.origin!=='http://127.0.0.1:8993') return route.abort();
      if(url.pathname==='/fixture.png'&&!fs.existsSync(image)) return route.fulfill({
        contentType:'image/svg+xml',body:'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="730"><rect width="640" height="730" fill="#dbeafe"/><text x="30" y="60" font-size="24">Previous chart</text></svg>'});
      const file=url.pathname==='/fixture.png'?image:path.resolve(root,'.'+decodeURIComponent(url.pathname==='/'?'/index.html':url.pathname));
      if(!file.startsWith(root+path.sep)||!fs.existsSync(file)||!fs.statSync(file).isFile()) return route.fulfill({status:404,body:'not found'});
      return route.fulfill({body:fs.readFileSync(file),contentType:types[path.extname(file)] || 'application/octet-stream'});
    });
    await page.goto('http://127.0.0.1:8993/',{waitUntil:'domcontentloaded'});
    await page.waitForFunction(()=>typeof requestModelSelection==='function'&&document.querySelectorAll('.model-cell').length>3);
    await page.evaluate(()=>{
      CDSPublicCharts.stopPolling();forecastAvailabilityRefresh.stop();
      window.testLatestRun=new Date();testLatestRun.setUTCHours(Math.floor(testLatestRun.getUTCHours()/6)*6,0,0,0);
      CDSPublicCharts.readyHours=({modelId,runUTC})=>modelId==='gfs'&&runUTC.getTime()===testLatestRun.getTime()?[]:[0,3,6];
    });
    async function seed(model='kim_gdps',offset=0){
      return page.evaluate(async({model,offset})=>{
        invalidateSelectionAsyncWork();
        currentMainMenu='forecast';currentModel=model;currentProduct='gph500';currentAuxValue=null;
        modelCompareMode=false;compareModels=[];productCategory.value='asia';timeMode='UTC';
        const run=new Date(testLatestRun.getTime()+offset*3600000);
        setRunControlsToUTCAllowUnsupported(run);
        await refreshView({updateCategories:true,updateProducts:true,updateHours:false,updateChartAfter:false});
        setCurrentForecastList([0,3,6]);setForecastLoadStates(['available','available','available']);resetForecastImageCache();
        setForecastImageCacheEntry(1,{ok:true,urls:['/fixture.png'],baseUrls:['/fixture.png']});
        slider.min='0';slider.max='2';slider.step='1';slider.value='1';slider.disabled=false;
        updateForecastLabel();renderForecastTimeline();
        const img=new Image();img.src='/fixture.png';await img.decode();
        createSingleImageDisplayShell({imageCount:1}).stack.append(img);
        modelStatus.textContent='';modelStatus.className='hidden';setViewerLoading(false);
        window.originalPanel=chartImages.firstElementChild;
        return {model,run:run.toISOString(),hour:3,category:'asia',product:'gph500'};
      },{model,offset});
    }
    async function unchanged(expected){
      await page.waitForFunction(()=>!document.querySelector('dialog[open]')&&chartImages.firstElementChild===originalPanel);
      const state=await page.evaluate(()=>({model:currentModel,run:getSelectedUTCDate().toISOString(),
        hour:getSelectedTimelineHourForPreserve(),category:getCurrentCategory(),product:currentProduct}));
      assert.deepEqual(state,expected);
      assert.equal(await page.evaluate(()=>forecastLoadStates.every(value=>value==='available')),true);
      assert.equal(await page.evaluate(()=>getForecastImageCacheEntry(1)?.urls?.[0]),'/fixture.png');
      assert.equal(await page.locator('.viewer-wrap').evaluate(el=>el.classList.contains('selection-blurred')),false);
    }
    let before=await seed();
    await page.getByRole('button',{name:'GFS',exact:true}).click();
    await page.locator('dialog[open]').waitFor();
    assert.match(await page.locator('dialog p').textContent(),/가장 최근 자료시각/);
    await page.getByRole('button',{name:'취소',exact:true}).click();
    await unchanged(before);
    await page.screenshot({path:path.join(output,'model-cancel-desktop.png')});

    before=await seed('gfs',-6);
    await page.locator('[data-shift-hours="6"]').click();
    await page.locator('dialog[open]').waitFor();
    await page.keyboard.press('Escape');
    await unchanged(before);

    before=await seed('gfs',-6);
    await page.locator('#runHour').selectOption(await page.evaluate(()=>formatRunTimeValue(testLatestRun)));
    await page.locator('dialog[open]').waitFor();
    await page.getByRole('button',{name:'취소',exact:true}).click();
    await unchanged(before);

    before=await seed('gfs',-24);
    await page.locator('#runDate').fill(await page.evaluate(()=>formatDateInputFromUTCParts(testLatestRun)));
    await page.locator('#runDate').dispatchEvent('change');
    await page.locator('dialog[open]').waitFor();
    await page.getByRole('button',{name:'취소',exact:true}).click();
    await unchanged(before);

    before=await seed('gfs',-6);
    const unsupported=await page.evaluate(()=>getProductsInCategory('asia').find(product=>
      !modelSupportsSelectionProduct('gfs',product)&&modelSupportsSelectionProduct('kim_gdps',product))?.id);
    assert(unsupported);
    await page.locator('#productSelect').selectOption(unsupported);
    await page.locator('dialog[open]').waitFor();
    await page.getByRole('button',{name:'취소',exact:true}).click();
    await unchanged(before);

    before=await seed();
    await page.setViewportSize({width:390,height:844});
    await page.getByRole('button',{name:'GFS',exact:true}).click();
    await page.locator('dialog[open]').waitFor();
    await page.getByRole('button',{name:'취소',exact:true}).click();
    await unchanged(before);
    await page.screenshot({path:path.join(output,'model-cancel-mobile.png')});

    await page.evaluate(()=>{
      window.latestMoves=0;
      jumpLatestAvailableForCurrentSelection=async()=>{latestMoves++;setRunControlsToUTCAllowUnsupported(new Date(testLatestRun.getTime()-6*3600000));};
    });
    await page.getByRole('button',{name:'GFS',exact:true}).click();
    await page.locator('dialog[open]').waitFor();
    await page.getByRole('button',{name:'확인',exact:true}).click();
    await page.waitForFunction(()=>latestMoves===1&&currentModel==='gfs'&&getSelectedUTCDate().getTime()===testLatestRun.getTime()-6*3600000);
    assert.deepEqual(errors,[]);
    console.log('Selection cancellation: model, shifted run, hour, date, product, Escape, desktop/mobile and acceptance passed');
  }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});

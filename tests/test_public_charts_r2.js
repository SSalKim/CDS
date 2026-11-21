const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');

const source=fs.readFileSync(path.join(__dirname,'..','public-charts.js'),'utf8');
const BASE='https://charts.example.test/';
const REV_A='a'.repeat(16),REV_B='b'.repeat(16),REV_C='c'.repeat(16);

function load(now){
  const context={console,URL,URLSearchParams,location:{hostname:'ssalkim.github.io'},
    Date:class extends Date{static now(){return now.value;}},
    setInterval:()=>1,clearInterval:()=>{}};
  vm.runInNewContext(source,context);
  return context.CDSPublicCharts;
}

function fragment(model,cycle,charts,leads=[0,3,6,24,240,252]){
  return {schema:2,model,cycle,images:'drive',leads,charts};
}

function server(){
  const objects=new Map();
  const requests=[];
  let gitStatus=200;
  let gitManifest={models:{},charts:[]};
  return {
    objects,requests,
    set git(value){gitManifest=value;},
    set gitStatus(value){gitStatus=value;},
    put(key,value){objects.set(key,value);},
    index(runs,generated_at='2026-11-19T06:00:00Z',models={gfs:{published:true},ukmo:{published:true}}){
      objects.set('manifest/index.json',{schema:2,images:'drive',generated_at,models,runs});
    },
    fetch:async(url,options={})=>{
      requests.push({url,options});
      if(url.startsWith('https://raw.githubusercontent.com/')){
        return {ok:gitStatus===200,status:gitStatus,json:async()=>gitManifest};
      }
      const key=url.startsWith(BASE)?url.slice(BASE.length):null;
      const value=objects.get(key);
      if(value instanceof Error) throw value;
      if(typeof value==='number') return {ok:false,status:value,json:async()=>({})};
      if(value===undefined) return {ok:false,status:404,json:async()=>({})};
      return {ok:true,status:200,json:async()=>JSON.parse(JSON.stringify(value))};
    }
  };
}

const date=cycle=>new Date(`${cycle.slice(0,4)}-${cycle.slice(4,6)}-${cycle.slice(6,8)}T${cycle.slice(8)}:00:00Z`);
const selection=(modelId,cycle,hour,id='gph500',category='hkor')=>({modelId,product:{id,category},runUTC:date(cycle),forecastHour:hour});
const drive=id=>`https://drive.usercontent.google.com/download?id=${id}&export=view&authuser=0`;

async function main(){
  const now={value:Date.parse('2026-11-19T06:01:00Z')};
  const api=load(now);

  // Base resolution: off by default, explicit https origins only.
  assert.equal(api.getR2Base(),'https://cds4.uzo1o1.party/','Production reads the R2 custom domain');
  const local={hostname:'localhost'};
  assert.equal(api.createStore({location:local}).getR2Base(),'','Local development keeps the bundled manifest');
  assert.equal(api.createStore({location:local,r2Base:'http://localhost:8123'}).getR2Base(),'http://localhost:8123/');
  assert.equal(api.createStore({r2Base:'http://charts.example.test/'}).getR2Base(),'','Plain HTTP is refused off localhost');
  assert.equal(api.createStore({r2Base:'https://charts.example.test/?x=1'}).getR2Base(),'');
  assert.equal(api.createStore({r2Base:'https://charts.example.test'}).getR2Base(),BASE);

  const r2=server();
  r2.put(`manifest/runs/gfs/2026111900.${REV_A}.json`,fragment('gfs','2026111900',[[24,'hkor','gph500','FileA'],[252,'hkor','gph500','FileX']]));
  r2.put(`manifest/runs/gfs/2026111906.${REV_B}.json`,fragment('gfs','2026111906',[[24,'hkor','gph500','FileB']]));
  r2.index({'gfs/2026111900':{rev:REV_A,count:2},'gfs/2026111906':{rev:REV_B,count:1}});
  const store=api.createStore({fetchImpl:r2.fetch,r2Base:BASE});

  let result=await store.load();
  assert.deepEqual({...result},{ok:true,changed:true,source:'r2'});
  assert.equal(store.getSource(),'r2');
  assert.deepEqual([...store.resolveUrls(selection('gfs','2026111900',24))],[drive('FileA')]);
  assert.deepEqual([...store.resolveUrls(selection('gfs','2026111900',252))],[drive('FileX')],
    'Producer leads, not local rules, decide which forecast hours exist');
  assert.deepEqual([...store.resolveUrls(selection('gfs','2026111900',3))],[],'A listed lead without a chart stays empty');
  const index=r2.requests.find(request=>request.url.endsWith('manifest/index.json'));
  assert.equal(index.url,BASE+'manifest/index.json','No cache-busting query on the index');
  assert.equal(index.options.cache,'no-cache','The index is revalidated, so an unchanged poll is a 304');
  assert(!r2.requests.some(request=>request.url.includes('raw.githubusercontent')),'Git is not touched while R2 works');

  // Unchanged index: one small request, no fragments, no change notification.
  r2.requests.length=0;
  result=await store.load();
  assert.equal(result.changed,false);
  assert.deepEqual(r2.requests.map(request=>request.url),[BASE+'manifest/index.json']);

  // One run changes: only its fragment is downloaded.
  r2.put(`manifest/runs/gfs/2026111906.${REV_C}.json`,fragment('gfs','2026111906',[[24,'hkor','gph500','FileB'],[24,'asia','gph500','FileC']]));
  r2.index({'gfs/2026111900':{rev:REV_A,count:2},'gfs/2026111906':{rev:REV_C,count:2}});
  r2.requests.length=0;
  result=await store.load();
  assert.equal(result.changed,true);
  assert.deepEqual(r2.requests.map(request=>request.url),
    [BASE+'manifest/index.json',`${BASE}manifest/runs/gfs/2026111906.${REV_C}.json`]);
  assert.deepEqual([...store.resolveUrls(selection('gfs','2026111906',24,'gph500','asia'))],[drive('FileC')]);

  // A run leaving the index disappears from the viewer.
  r2.index({'gfs/2026111906':{rev:REV_C,count:2}});
  await store.load();
  assert.deepEqual([...store.resolveUrls(selection('gfs','2026111900',24))],[]);
  assert.deepEqual([...store.readyCycles('gfs')],['2026111906']);

  // Any R2 inconsistency falls back to Git for that poll, and R2 is retried next poll.
  r2.git={models:{gfs:{published:true}},charts:[{model:'gfs',cycle:'2026111906',hour:24,domain:'hkor',product:'gph500',url:drive('FileB')}]};
  r2.put(`manifest/runs/gfs/2026111912.${REV_A}.json`,fragment('gfs','2026111912',[[24,'hkor','gph500','FileD']]));
  r2.index({'gfs/2026111906':{rev:REV_C,count:2},'gfs/2026111912':{rev:REV_A,count:5}});
  result=await store.load();
  assert.equal(result.source,'git','A fragment whose count disagrees with the index is rejected');
  assert.equal(store.getSource(),'git');
  assert.deepEqual([...store.resolveUrls(selection('gfs','2026111906',24))],[drive('FileB')]);
  r2.index({'gfs/2026111906':{rev:REV_C,count:2},'gfs/2026111912':{rev:REV_A,count:1}});
  result=await store.load();
  assert.equal(result.source,'r2');
  assert.deepEqual([...store.resolveUrls(selection('gfs','2026111912',24))],[drive('FileD')]);
  for(const failure of [503,new Error('offline'),{schema:1,runs:{}}]){
    r2.objects.set('manifest/index.json',failure);
    result=await store.load();
    assert.equal(result.source,'git',`Index failure ${failure} falls back to Git`);
    assert.equal(result.ok,true);
  }
  r2.gitStatus=503;
  result=await store.load();
  assert.equal(result.ok,false,'When both sources fail the last snapshot is kept');
  assert.deepEqual([...store.resolveUrls(selection('gfs','2026111906',24))],[drive('FileB')]);

  // Switching sources with identical content must not notify listeners.
  const same=server();
  same.git={models:{gfs:{published:true}},charts:[{model:'gfs',cycle:'2026111906',hour:24,domain:'hkor',product:'gph500',
    url:drive('FileB'),size:9,sha256:'f'.repeat(64)}]};
  same.put(`manifest/runs/gfs/2026111906.${REV_B}.json`,fragment('gfs','2026111906',[[24,'hkor','gph500','FileB']]));
  same.index({'gfs/2026111906':{rev:REV_B,count:1}});
  const switching=api.createStore({fetchImpl:same.fetch,r2Base:BASE});
  assert.equal((await switching.load()).changed,true);
  same.objects.set('manifest/index.json',503);
  const fallback=await switching.load();
  assert.equal(fallback.source,'git');
  assert.equal(fallback.changed,false,'Git and R2 snapshots of the same charts are identical');

  // generated_at corrects a device clock that is days off; a correct clock is left alone.
  const ukmo=server();
  ukmo.put(`manifest/runs/ukmo/2026111906.${REV_A}.json`,fragment('ukmo','2026111906',[[24,'hkor','gph500','FileU']],[0,3,24,69]));
  ukmo.index({'ukmo/2026111906':{rev:REV_A,count:1}},'2026111912'.replace(/(\d{4})(\d\d)(\d\d)(\d\d)/,'$1-$2-$3T$4:00:00Z'));
  const skewed={value:Date.parse('2026-11-15T00:00:00Z')};
  const skewedApi=load(skewed);
  const behind=skewedApi.createStore({fetchImpl:ukmo.fetch,r2Base:BASE});
  await behind.load();
  assert.deepEqual([...behind.resolveUrls(selection('ukmo','2026111906',24))],[drive('FileU')],
    'A device clock four days behind still shows current UKMO charts');
  assert(Math.abs(skewedApi.clockNow()-Date.parse('2026-11-19T12:00:00Z'))<1000);
  const correct={value:Date.parse('2026-11-19T12:03:00Z')};
  const correctApi=load(correct);
  await correctApi.createStore({fetchImpl:ukmo.fetch,r2Base:BASE}).load();
  assert.equal(correctApi.clockNow(),correct.value,'A clock within the index freshness window is trusted');
  const quiet={value:Date.parse('2026-11-19T12:50:00Z')};
  const quietApi=load(quiet);
  await quietApi.createStore({fetchImpl:ukmo.fetch,r2Base:BASE}).load();
  assert.equal(quietApi.clockNow(),quiet.value,'An index left untouched between runs must not pull a correct clock back');
  const ahead={value:Date.parse('2026-11-19T16:00:00Z')};
  const aheadApi=load(ahead);
  await aheadApi.createStore({fetchImpl:ukmo.fetch,r2Base:BASE}).load();
  assert(Math.abs(aheadApi.clockNow()-Date.parse('2026-11-19T12:00:00Z'))<1000,'A clock hours ahead is corrected');

  // UKMO confirmation fields survive the compact fragment encoding.
  const gated=server();
  gated.put(`manifest/runs/ukmo/2026111900.${REV_A}.json`,fragment('ukmo','2026111900',[
    [24,'hkor','acptot','FileK',{kma_confirmed_at:'2026-11-19T06:00:00Z',kma_reference_hour:24,other:'ignored'}],
    [48,'hkor','acptot','FileL']],[0,24,48]));
  gated.index({'ukmo/2026111900':{rev:REV_A,count:2}});
  const gatedStore=api.createStore({fetchImpl:gated.fetch,r2Base:BASE});
  await gatedStore.load();
  assert.deepEqual([...gatedStore.readyHours({modelId:'ukmo',product:{id:'acptot',category:'hkor'},runUTC:date('2026111900')})],[24],
    'Unconfirmed UKMO KMA-gated charts stay hidden');

  // Images copied to R2 load from the custom domain, with the Drive file as the fallback.
  const sha='0123456789abcdef';
  const own=`gfs_hkor_acptot_s024_2026111900_${sha}.webp`;
  const images=server();
  images.put(`manifest/runs/gfs/2026111900.${REV_A}.json`,fragment('gfs','2026111900',[
    [24,'hkor','acptot','FileR',{r2:own}],
    [24,'hkor','surfce','FileR',{r2:own}],
    [24,'hkor','gph500','FileS'],
    [24,'asia','gph500','FileT',{r2:`icon_asia_gph500_s024_2026111900_${sha}.webp`}],
    [24,'asia','surfce','FileV',{r2:'../../secret.webp'}]]));
  images.index({'gfs/2026111900':{rev:REV_A,count:5}});
  const imageStore=api.createStore({fetchImpl:images.fetch,r2Base:BASE});
  await imageStore.load();
  const r2Url=`${BASE}charts/gfs/2026111900/${own}`;
  assert.deepEqual([...imageStore.resolveUrls(selection('gfs','2026111900',24,'acptot','hkor'))],[r2Url]);
  assert.deepEqual([...imageStore.resolveUrls(selection('gfs','2026111900',24,'surfce','hkor'))],[r2Url],
    'An alias row loads the R2 object it reuses');
  assert.deepEqual([...imageStore.resolveUrls(selection('gfs','2026111900',24,'gph500','hkor'))],[drive('FileS')],
    'Rows without an R2 copy keep their Drive URL');
  assert.deepEqual([...imageStore.resolveUrls(selection('gfs','2026111900',24,'gph500','asia'))],[drive('FileT')],
    'An R2 name from another model is ignored');
  assert.deepEqual([...imageStore.resolveUrls(selection('gfs','2026111900',24,'surfce','asia'))],[drive('FileV')],
    'A malformed R2 name never becomes a URL');
  assert(imageStore.replacementFallbacks(r2Url).includes(drive('FileR')),'A failed R2 load falls back to Drive');
  assert.deepEqual([...imageStore.replacementFallbacks(drive('FileS'))],[],'Drive-only rows have no extra fallback');
  const noBase=api.createStore({fetchImpl:images.fetch,r2Base:BASE});
  images.git={models:{gfs:{published:true}},charts:[{model:'gfs',cycle:'2026111900',hour:24,domain:'hkor',
    product:'acptot',url:drive('FileR'),r2:own}]};
  images.put('manifest/index.json',503);
  await noBase.load();
  assert.equal(noBase.getSource(),'git');
  assert.deepEqual([...noBase.resolveUrls(selection('gfs','2026111900',24,'acptot','hkor'))],[drive('FileR')],
    'The Git fallback, used when R2 is unreachable, loads images from Drive');

  // Images stored in R2 alone ("r2_" ids) load from R2 and never fall back to a Drive URL.
  const onlyName=`gfs_hkor_gph500_s024_2026111900_${sha}.webp`;
  const only=server();
  only.put(`manifest/runs/gfs/2026111900.${REV_A}.json`,fragment('gfs','2026111900',[
    [24,'hkor','gph500',`r2_${onlyName.slice(0,-5)}`,{r2:onlyName}],
    [24,'asia','gph500','r2_missing_name']]));
  only.index({'gfs/2026111900':{rev:REV_A,count:2}});
  const onlyStore=api.createStore({fetchImpl:only.fetch,r2Base:BASE});
  await onlyStore.load();
  const onlyUrl=`${BASE}charts/gfs/2026111900/${onlyName}`;
  assert.deepEqual([...onlyStore.resolveUrls(selection('gfs','2026111900',24,'gph500','hkor'))],[onlyUrl]);
  assert.deepEqual([...onlyStore.replacementFallbacks(onlyUrl)],[],'An R2-only image has no Drive fallback');
  assert.deepEqual([...onlyStore.resolveUrls(selection('gfs','2026111900',24,'gph500','asia'))],[],
    'An R2-only id without its object name is dropped');
  const gitOnly=api.createStore({fetchImpl:only.fetch,r2Base:BASE});
  only.git={models:{gfs:{published:true}},charts:[{model:'gfs',cycle:'2026111900',hour:24,domain:'hkor',product:'gph500',url:onlyUrl}]};
  only.put('manifest/index.json',503);
  await gitOnly.load();
  assert.deepEqual([...gitOnly.resolveUrls(selection('gfs','2026111900',24,'gph500','hkor'))],[onlyUrl],
    'The Git fallback keeps R2-only rows, whose URL is the R2 address');

  console.log('Public charts R2: index polling, revision fragments, Git fallback, producer leads, R2 images and clock calibration passed');
}

main().catch(error=>{console.error(error);process.exitCode=1;});

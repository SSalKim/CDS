const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const {webcrypto}=require('node:crypto');
function environment({allowed=true,tag=true,hidden=false}={}){
 const calls=[];
 const context={URL,console,crypto:webcrypto,navigator:{},location:{href:'https://ssalkim.github.io/CDS/'},
   localStorage:{getItem:()=>allowed?'0':'1',setItem(){}},document:{visibilityState:hidden?'hidden':'visible',addEventListener(){}},
   setTimeout:()=>1,clearTimeout(){},innerWidth:1200,matchMedia:()=>({matches:false}),
   addEventListener(){},CDS_USAGE_CONFIG:{enabled:true,endpoint:'https://statistics.example/collect',measurementId:'G-TEST'},
   fetch:async(url,options)=>{calls.push({url,body:JSON.parse(options.body),credentials:options.credentials});return {status:202};},
   gtag:(action,id,field,cb)=>cb(tag?(field==='client_id'?'123456.987654':'12345'):null)};
 context.window=context;vm.createContext(context);vm.runInContext(fs.readFileSync('cds-usage.js','utf8'),context);
 return {context,calls};
}
const params={menu:'forecast',category:'asia',model_id:'gfs',model_name:'GFS',product_id:'gph500',product_name:'500 고도',
 run_utc:'2026-11-17T00:00:00.000Z',valid_utc:'2026-11-18T00:00:00.000Z',forecast_hour:24,email:'not-sent@example.com',image_url:'not sent'};
(async()=>{
 const active=environment();active.context.CDSUsage.record('cds_product_view',params);await active.context.CDSUsage.flush();
 assert.equal(active.calls.length,1);assert.equal(active.calls[0].body.events[0].forecast_hour,24);
 assert.equal(active.calls[0].body.events[0].email,undefined);assert.equal(active.calls[0].body.events[0].image_url,undefined);
 assert.equal(active.calls[0].credentials,'omit');
 for(const options of [{allowed:false},{tag:false},{hidden:true}]){const state=environment(options);state.context.CDSUsage.record('cds_product_view',params);await state.context.CDSUsage.flush();assert.equal(state.calls.length,0);}
 const gpc=environment();gpc.context.navigator.globalPrivacyControl=true;gpc.context.CDSUsage.record('cds_product_view',params);await gpc.context.CDSUsage.flush();assert.equal(gpc.calls.length,0);
 const disabled=environment();disabled.context.CDS_USAGE_CONFIG.enabled=false;disabled.context.CDSUsage.record('cds_product_view',params);await disabled.context.CDSUsage.flush();assert.equal(disabled.calls.length,0);
 const opt=environment();opt.context.CDSUsage.record('cds_product_view',params);opt.context.CDSUsage.setEnabled(false);await opt.context.CDSUsage.flush();assert.equal(opt.calls.length,0);
 console.log('Usage collector: metadata allowlist, batching, opt-out, GPC, hidden pages and blocked GA passed');
})().catch(error=>{console.error(error);process.exitCode=1;});

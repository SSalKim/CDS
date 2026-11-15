(function(global){
'use strict';

function createRefresher({refresh,canRefresh=()=>true,intervalMs=60000,minIntervalMs=15000,
now=()=>Date.now(),setIntervalImpl=(...args)=>global.setInterval(...args),
clearIntervalImpl=id=>global.clearInterval(id)}={}){
let pending=null;
let lastAttempt=-Infinity;
let timer=null;

async function request(options={}){
if(pending) return pending;
if(!canRefresh(options) || now()-lastAttempt<minIntervalMs) return false;
lastAttempt=now();
pending=Promise.resolve().then(()=>refresh(options)).catch(()=>false);
try{ return await pending; }
finally{ pending=null; }
}

function start(){
if(timer===null) timer=setIntervalImpl(()=>request(),intervalMs);
}

function stop(){
if(timer!==null) clearIntervalImpl(timer);
timer=null;
}

return {request,start,stop};
}

global.CDSForecastRefresh={createRefresher};
})(typeof window!=='undefined'?window:globalThis);

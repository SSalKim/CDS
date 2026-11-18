import {fingerprint} from './auth.js';

export function allowedChartUrl(value){
  try{
    const url=new URL(value);
    if(url.protocol!=='https:' || url.port || url.username || url.password) return null;
    if((url.hostname==='data.kma.go.kr' && url.pathname.startsWith('/CHT/')) ||
       (url.hostname==='dmdw.kma.go.kr' && url.pathname.startsWith('/map/data/CHT/'))){
      if(!/\.(png|gif|jpe?g|webp)$/i.test(url.pathname)) return null;
    }else if(url.hostname==='lh3.googleusercontent.com'){
      if(!/^\/d\/[\w-]{10,200}(?:=s0)?$/.test(url.pathname)) return null;
    }else if(['drive.google.com','drive.usercontent.google.com'].includes(url.hostname)){
      if(!['/uc','/download'].includes(url.pathname) || !/^[\w-]{10,200}$/.test(url.searchParams.get('id')||'')) return null;
      return new URL('https://lh3.googleusercontent.com/d/'+url.searchParams.get('id')+'=s0');
    }else return null;
    return url;
  }catch{return null;}
}

export async function chartImage(request,env){
  const origin=request.headers.get('Origin');
  if(!(env.ALLOWED_ORIGINS||'').split(',').map(value=>value.trim()).includes(origin)) return new Response('Origin not allowed',{status:403});
  const headers={'Access-Control-Allow-Origin':origin,'Vary':'Origin','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'};
  const fail=status=>new Response('Chart image unavailable',{status,headers});
  if(request.method!=='GET') return fail(405);
  let url=allowedChartUrl(new URL(request.url).searchParams.get('url'));
  if(!url)return fail(400);
  if(!env.COLLECT_LIMITER || String(env.HMAC_SECRET||'').length<32) return fail(503);
  const key=await fingerprint(env.HMAC_SECRET,'chart-export:'+request.headers.get('CF-Connecting-IP'));
  if(!(await env.COLLECT_LIMITER.limit({key})).success) return fail(429);
  try{
    for(let redirects=0;redirects<4;redirects++){
      const response=await fetch(url,{redirect:'manual',signal:AbortSignal.timeout(15000),headers:{Accept:'image/png,image/webp,image/gif,image/jpeg'}});
      if([301,302,303,307,308].includes(response.status)){
        url=allowedChartUrl(new URL(response.headers.get('Location')||'',url).href);
        await response.body?.cancel();if(!url)return fail(502);continue;
      }
      const type=response.headers.get('Content-Type')?.split(';')[0];
      if(!response.ok || !['image/png','image/gif','image/webp','image/jpeg'].includes(type)) {await response.body?.cancel();return fail(502);}
      const reader=response.body.getReader(),chunks=[];let length=0;
      while(true){const {done,value}=await reader.read();if(done)break;length+=value.byteLength;
        if(length>20000000){await reader.cancel();return fail(413);}chunks.push(value);}
      return new Response(new Blob(chunks,{type}),{headers:{...headers,'Content-Type':type}});
    }
  }catch{return fail(502);}
  return fail(502);
}

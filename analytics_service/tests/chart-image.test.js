import {test} from 'node:test';
import assert from 'node:assert/strict';
import {allowedChartUrl,chartImage} from '../src/chart-image.js';
test('chart export restricts upstream hosts, paths, credentials and private addresses',()=>{
 for(const url of ['http://data.kma.go.kr/CHT/x.png','https://127.0.0.1/x.png','https://data.kma.go.kr.evil/CHT/x.png',
 'https://data.kma.go.kr/other/x.png','https://data.kma.go.kr/CHT/x.html','https://u:p@data.kma.go.kr/CHT/x.png',
 'https://data.kma.go.kr:4430/CHT/x.png','https://lh3.googleusercontent.com/other/x'])assert.equal(allowedChartUrl(url),null,url);
 assert(allowedChartUrl('https://data.kma.go.kr/CHT/GDPS/x.png'));
 assert.equal(allowedChartUrl('https://drive.google.com/uc?id=abcdefghijk').href,'https://lh3.googleusercontent.com/d/abcdefghijk=s0');
});
test('export enforces origin, image type, redirects and request limits',async()=>{
 const url='https://export.example/chart-image?url='+encodeURIComponent('https://data.kma.go.kr/CHT/GDPS/x.png');
 const request=()=>new Request(url,{headers:{Origin:'https://site.example'}});
 const env={ALLOWED_ORIGINS:'https://site.example',HMAC_SECRET:'test-key-long-enough-for-export-requests',COLLECT_LIMITER:{limit:async()=>({success:true})}};
 assert.equal((await chartImage(new Request(url),env)).status,403);
 const original=globalThis.fetch;
 try{
 globalThis.fetch=async()=>new Response('pixels',{headers:{'Content-Type':'image/png'}});
 const response=await chartImage(request(),env);assert.equal(response.status,200);assert.equal(response.headers.get('Access-Control-Allow-Origin'),'https://site.example');
 globalThis.fetch=async()=>new Response('html',{headers:{'Content-Type':'text/html'}});
 assert.equal((await chartImage(request(),env)).status,502);
 globalThis.fetch=async()=>new Response(null,{status:302,headers:{Location:'https://127.0.0.1/private.png'}});
 assert.equal((await chartImage(request(),env)).status,502);
 assert.equal((await chartImage(request(),{...env,COLLECT_LIMITER:{limit:async()=>({success:false})}})).status,429);
 }finally{globalThis.fetch=original;}
});

import {createRemoteJWKSet,jwtVerify} from 'jose';

const keysets=new Map();

export async function administrator(request,env){
  const url=new URL(request.url);
  if(env.LOCAL_PREVIEW==='true' && ['127.0.0.1','localhost'].includes(url.hostname)){
    return {email:'local-preview'};
  }
  if(!env.ADMIN_EMAIL || !env.ACCESS_AUD || !/^[a-z0-9-]+\.cloudflareaccess\.com$/.test(env.ACCESS_TEAM_DOMAIN || '')) return null;
  const token=request.headers.get('Cf-Access-Jwt-Assertion');
  if(!token || token.length>16000) return null;
  const issuer=`https://${env.ACCESS_TEAM_DOMAIN}`;
  try{
    if(!keysets.has(issuer)) keysets.set(issuer,createRemoteJWKSet(new URL(`${issuer}/cdn-cgi/access/certs`)));
    const {payload}=await jwtVerify(token,keysets.get(issuer),{
      issuer,audience:env.ACCESS_AUD,algorithms:['RS256'],clockTolerance:10
    });
    if(typeof payload.email!=='string' || payload.email.toLowerCase()!==env.ADMIN_EMAIL.toLowerCase()) return null;
    return {email:payload.email};
  }
  catch{return null;}
}

export async function fingerprint(secret,value){
  const key=await crypto.subtle.importKey('raw',new TextEncoder().encode(secret),
    {name:'HMAC',hash:'SHA-256'},false,['sign']);
  const bytes=await crypto.subtle.sign('HMAC',key,new TextEncoder().encode(value));
  return Array.from(new Uint8Array(bytes),byte=>byte.toString(16).padStart(2,'0')).join('');
}

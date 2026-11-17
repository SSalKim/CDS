export const CONNECTION_RETENTION_DAYS=30;
const encoder=new TextEncoder();
const additionalData=encoder.encode('cds-usage-connection-v1');
let cachedSecret,cachedKey;

export function connectionRetention(env){
  return Math.min(CONNECTION_RETENTION_DAYS,Math.max(1,Number(env.CONNECTION_RETENTION_DAYS)||CONNECTION_RETENTION_DAYS));
}

export function networkAddress(value){
  if(typeof value!=='string' || value.length>45) return '';
  if(/^\d{1,3}(\.\d{1,3}){3}$/.test(value)){
    const parts=value.split('.');
    return parts.every(part=>Number(part)<=255 && String(Number(part))===part) ? value : '';
  }
  if(!value.includes(':') || !/^[a-f0-9:.]+$/i.test(value)) return '';
  try{return new URL('http://['+value+']/').hostname.slice(1,-1);}
  catch{return '';}
}

function fromBase64(value){return Uint8Array.from(atob(value),character=>character.charCodeAt(0));}
function toBase64(value){return btoa(String.fromCharCode(...value));}
async function encryptionKey(env){
  const secret=env.CONNECTION_DATA_KEY;
  if(secret===cachedSecret && cachedKey) return cachedKey;
  if(typeof secret!=='string' || !/^[a-z0-9+/]{43}=$/i.test(secret)) throw new Error('Connection key unavailable');
  const bytes=fromBase64(secret);
  if(bytes.length!==32) throw new Error('Connection key unavailable');
  const key=await crypto.subtle.importKey('raw',bytes,{name:'AES-GCM'},false,['encrypt','decrypt']);
  cachedSecret=secret;cachedKey=key;
  return key;
}

export async function captureConnection(request,env){
  if(env.COLLECT_CONNECTION_INFO!=='true') return null;
  let ip=networkAddress(request.headers.get('CF-Connecting-IP'));
  // Pseudo IPv4 replaces the header with a Class E address; preserve the original IPv6.
  if(ip && !ip.includes(':') && Number(ip.split('.')[0])>=240){
    ip=networkAddress(request.headers.get('CF-Connecting-IPv6'));
  }
  // Cloudflare substitutes a shared address for cross-zone Worker subrequests.
  if(ip==='2a06:98c0:3600::103') return null;
  const city=typeof request.cf?.city==='string' ? request.cf.city.trim().replace(/[\u0000-\u001f\u007f]/g,'').slice(0,100) : '';
  const country=/^[a-z]{2}$/i.test(request.cf?.country || '') ? request.cf.country.toUpperCase() : '';
  if(!ip && !city && !country) return null;
  const key=await encryptionKey(env);
  const nonce=crypto.getRandomValues(new Uint8Array(12));
  const clear=encoder.encode(JSON.stringify({ip_address:ip,city,country}));
  const ciphertext=new Uint8Array(await crypto.subtle.encrypt({name:'AES-GCM',iv:nonce,additionalData},key,clear));
  const envelope=new Uint8Array(nonce.length+ciphertext.length);
  envelope.set(nonce);envelope.set(ciphertext,nonce.length);
  return 'v1.'+toBase64(envelope);
}

async function decodeConnection(value,env){
  if(typeof value!=='string' || !value.startsWith('v1.') || value.length>1200) return {};
  try{
    const envelope=fromBase64(value.slice(3));
    const key=await encryptionKey(env);
    const clear=await crypto.subtle.decrypt({name:'AES-GCM',iv:envelope.slice(0,12),additionalData},key,envelope.slice(12));
    const data=JSON.parse(new TextDecoder().decode(clear));
    return {ip_address:networkAddress(data.ip_address),city:typeof data.city==='string'?data.city.slice(0,100):'',
      country:typeof data.country==='string'?data.country.slice(0,2):''};
  }catch{return {};}
}

export async function revealConnections(rows,env,now=Date.now()){
  const output=[];
  const cutoff=now-connectionRetention(env)*86400000;
  for(const row of rows){
    const {connection_ciphertext,...publicRow}=row;
    const info=Number.isFinite(Number(row.received_at)) && Number(row.received_at)>=cutoff
      ?await decodeConnection(connection_ciphertext,env):{};
    output.push({...publicRow,ip_address:info.ip_address || '',city:info.city || '',country:info.country || ''});
  }
  return output;
}

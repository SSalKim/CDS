import {test} from 'node:test';
import assert from 'node:assert/strict';
import {networkAddress,captureConnection,revealConnections} from '../src/connection.js';
const env={COLLECT_CONNECTION_INFO:'true',CONNECTION_DATA_KEY:btoa('12345678901234567890123456789012')};

test('IP parsing accepts canonical IPv4/IPv6 and rejects lists, ports, markup and invalid addresses',()=>{
 assert.equal(networkAddress('198.51.100.23'),'198.51.100.23');
 assert.equal(networkAddress('2001:0db8:0000::1'),'2001:db8::1');
 for(const value of ['999.1.1.1','01.2.3.4','1.2.3.4:80','1.2.3.4, 5.6.7.8','<script>','garbage:ip',null]) assert.equal(networkAddress(value),'');
});
test('connection envelopes use randomized authenticated encryption; tampering and wrong keys reveal nothing',async()=>{
 const request=new Request('https://test',{headers:{'CF-Connecting-IP':'198.51.100.23'}});
 Object.defineProperty(request,'cf',{value:{city:'서울',country:'KR',latitude:'not stored'}});
 const first=await captureConnection(request,env),second=await captureConnection(request,env);
 assert.notEqual(first,second);assert(!first.includes('서울'));
 const decode=async(value,settings=env)=>(await revealConnections([{received_at:Date.now(),connection_ciphertext:value}],settings))[0];
 const info=await decode(first);assert.equal(info.ip_address,'198.51.100.23');assert.equal(info.city,'서울');assert.equal(info.latitude,undefined);
 assert.equal((await decode(first.slice(0,-4)+'AAAA')).ip_address,'');
 assert.equal((await decode(first,{...env,CONNECTION_DATA_KEY:btoa('abcdefghijklmnopqrstuvwx12345678')})).ip_address,'');
 assert.equal(await captureConnection(request,{...env,COLLECT_CONNECTION_INFO:'false'}),null);
 assert.equal(await captureConnection(new Request('https://test'),env),null);
});
test('pseudo IPv4 uses preserved IPv6 and shared Worker address is not presented as a visitor',async()=>{
 const value=await captureConnection(new Request('https://test',{headers:{'CF-Connecting-IP':'250.1.2.3','CF-Connecting-IPv6':'2001:db8::9'}}),env);
 const row=(await revealConnections([{received_at:Date.now(),connection_ciphertext:value}],env))[0];assert.equal(row.ip_address,'2001:db8::9');
 assert.equal(await captureConnection(new Request('https://test',{headers:{'CF-Connecting-IP':'2a06:98c0:3600::103'}}),env),null);
});

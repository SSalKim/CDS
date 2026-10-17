const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const context={URLSearchParams,console,clearTimeout,setTimeout,document:{addEventListener(){}},window:{location:{search:''}}};
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(__dirname,'..','typhoon-guidance.js'),'utf8'),context);
vm.runInContext(`
const link={year:2026,td_number:58,typ_number:30,typ_name:'CHAMPI',state:'provisional',atcf_id:'wp292026',effective_time_utc:'202610150600'};
const td={year:'2026',stage:'TD',typNumber:58,typName:'NONAME',stormKey:'2026|TD|58|NONAME',dataTime:'202610150000',fcstHours:240,generatedAt:'202610171000',manifestPath:'old/manifest.json'};
const typ={year:'2026',stage:'TYP',typNumber:30,typName:'CHAMPI',stormKey:'2026|TYP|30|CHAMPI',dataTime:'202610150600',fcstHours:240,generatedAt:'202610170000',manifestPath:'named/manifest.json'};
typhoonState.tdTypLinks=new Map([['2026|58',link]]);
`,context);
const evaluate=code=>JSON.parse(vm.runInContext(`JSON.stringify(${code})`,context));
let grouped=evaluate('linkTdEntriesToTyphoons([td,typ])');
assert.equal(grouped[0].stormKey,grouped[1].stormKey);
assert.equal(grouped[0].originalStage,'TD');
assert.equal(grouped[0].dataTime,'202610150000');
assert.equal(grouped[0].manifestPath,'old/manifest.json');
const deduped=evaluate("dedupeLinkedTyphoonEntries(linkTdEntriesToTyphoons([typ,{...td,dataTime:typ.dataTime}]))");
assert.equal(deduped.length,1);
assert.equal(deduped[0].manifestPath,'named/manifest.json','Later-generated TD must not displace the real TYP image.');
assert.deepEqual(deduped[0].manifestPaths,['named/manifest.json','old/manifest.json']);
vm.runInContext(`typhoonState.yearIndexes.set('2026',{systems:[
{year:2026,stage:'TD',typ_number:58,typ_name:'NONAME',latest_data_time:'202610170000',manifest_path:'old/manifest.json'},
{year:2026,stage:'TYP',typ_number:30,typ_name:'CHAMPI',latest_data_time:'202610170000',manifest_path:'named/manifest.json'}
]})`,context);
assert.deepEqual(evaluate("manifestPathsForStormKey('2026','2026|TYP|30|CHAMPI')").sort(),['named/manifest.json','old/manifest.json']);
assert.equal(evaluate("tdActivityRecord({TD:58,TYP:0,TM_ST:'202610111800',TM_ED:'210012310000'},'2026',new Map())").endTime,'202610150600');
assert.equal(evaluate("tdActivityRecord({TD:59,TYP:30,TM_ST:'202610170000',TM_ED:'210012310000'},'2026',new Map([['30',{startTime:'202610150600'}]]))").endTime,'210012310000');
vm.runInContext('typhoonState.tdTypLinks=new Map()',context);
grouped=evaluate('linkTdEntriesToTyphoons([td,{...typ,tdNumber:58,tdTypLink:link}])');
assert.equal(grouped[0].stage,'TD','Missing/conflicting temporary links must not merge history.');
assert.equal(grouped[1].tdNumber,null);

(async()=>{
  vm.runInContext('fetchTyphoonJson=async()=>({version:1,links:[link]})',context);
  await vm.runInContext('loadTyphoonIdentityLinks()',context);
  assert.equal(vm.runInContext('typhoonState.tdTypLinks.size',context),1);
  vm.runInContext("tdActivityRecord({TD:58,TYP:29,TM_ST:'202610111800'},'2026',new Map())",context);
  assert.equal(vm.runInContext('typhoonState.tdTypLinks.size',context),0);
  vm.runInContext("fetchTyphoonJson=async()=>({version:1,links:[{...link,state:'conflict'}]})",context);
  await vm.runInContext('loadTyphoonIdentityLinks()',context);
  assert.equal(vm.runInContext('typhoonState.tdTypLinks.size',context),0);
  vm.runInContext('fetchTyphoonJson=async()=>{throw new Error("offline")}',context);
  await vm.runInContext('loadTyphoonIdentityLinks()',context);
  assert.equal(vm.runInContext('typhoonState.tdTypLinks.size',context),0);
  console.log('Typhoon identity links: grouping, activity, collision, and rollback tests passed.');
})().catch(error=>{console.error(error);process.exitCode=1;});

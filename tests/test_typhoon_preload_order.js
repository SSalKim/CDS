const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');

const context={
  URLSearchParams,
  console,
  clearTimeout,
  document:{addEventListener(){}},
  setTimeout,
  window:{location:{search:''}}
};
vm.createContext(context);
vm.runInContext(
  fs.readFileSync(path.join(__dirname,'..','typhoon-guidance.js'),'utf8'),
  context
);

context.runs=[
  {dataTime:'202608200000'},
  {dataTime:'202608201200'},
  {dataTime:'202608200600'},
  {dataTime:'202608201800'}
];

const ordered=JSON.parse(vm.runInContext(
  'JSON.stringify(sortTyphoonRunsNewestFirst(runs).map(run=>run.dataTime))',
  context
));

assert.deepEqual(ordered,[
  '202608201800',
  '202608201200',
  '202608200600',
  '202608200000'
]);

(async()=>{
  vm.runInContext(`
    typhoonState.entries=[
      {stormKey:'storm',fcstHours:120,dataTime:'202608200000',imagePath:'oldest.png'},
      {stormKey:'storm',fcstHours:120,dataTime:'202608200600',imagePath:'selected.png'},
      {stormKey:'storm',fcstHours:120,dataTime:'202608201200',imagePath:'newer.png'},
      {stormKey:'storm',fcstHours:120,dataTime:'202608201800',imagePath:'newest.png'}
    ];
    preloadOrder=[];
    getSelectedTyphoonRun=()=>typhoonState.entries[1];
    ensureTyphoonDriveArchiveImagesForRun=async()=>{};
    ensureTyphoonDriveArchiveImagesForPath=async()=>{};
    typhoonDriveArchivePathForRun=()=>'';
    loadTyphoonCachedImage=async run=>{
      preloadOrder.push(run.dataTime);
      return {ok:true};
    };
    pruneTyphoonImageCache=()=>{};
  `,context);

  await vm.runInContext(
    "preloadTyphoonStormImages('storm',120)",
    context
  );

  const preloadOrder=JSON.parse(vm.runInContext(
    'JSON.stringify(preloadOrder)',
    context
  ));

  assert.deepEqual(preloadOrder,[
    '202608200600',
    '202608201800',
    '202608201200',
    '202608200000'
  ]);

  console.log('typhoon preload order tests passed');
})().catch(error=>{
  console.error(error);
  process.exitCode=1;
});

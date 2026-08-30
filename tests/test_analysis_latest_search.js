const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');

const context={Date};
vm.createContext(context);
vm.runInContext(
  fs.readFileSync(path.join(__dirname,'..','time-controls.js'),'utf8'),
  context
);

function isOlder(runUTC,referenceUTC){
  context.runUTC=runUTC;
  context.referenceUTC=referenceUTC;
  return vm.runInContext(
    'isOlderThanAnalysisAutoLatestSearchWindow(runUTC,referenceUTC)',
    context
  );
}

const referenceUTC=new Date('2026-08-29T12:00:00Z');

assert.equal(
  isOlder(new Date('2026-08-24T11:59:59Z'),referenceUTC),
  true,
  '5일보다 오래된 시각은 자동 최신자료 검색을 생략해야 한다.'
);
assert.equal(
  isOlder(new Date('2026-08-24T12:00:00Z'),referenceUTC),
  false,
  '정확히 5일 전은 자동 최신자료 검색 범위에 포함한다.'
);
assert.equal(
  isOlder(new Date('2026-08-28T12:00:00Z'),referenceUTC),
  false,
  '최근 입력은 기존 자동 최신자료 검색을 유지해야 한다.'
);
assert.equal(
  isOlder(new Date('2026-08-30T12:00:00Z'),referenceUTC),
  false,
  '미래 입력은 과거 시각으로 오인하면 안 된다.'
);

console.log('analysis latest-search cutoff tests passed');

const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');

const context={
  URLSearchParams, console, clearTimeout, setTimeout,
  document:{addEventListener(){}}, window:{location:{search:''}}
};
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(__dirname,'..','typhoon-guidance.js'),'utf8'),context);
const catalog=JSON.parse(vm.runInContext(`JSON.stringify({
  labels:TYPHOON_MODEL_LABELS, colors:TYPHOON_MODEL_INFO_COLORS,
  rows:TYPHOON_MODEL_INFO, details:TYPHOON_MODEL_DETAIL_ROWS,
  groups:[...TYPHOON_MODEL_INFO_GROUP_ENDS], count:TYPHOON_DEFAULT_MODEL_TARGET
})`,context));
const backend=fs.readFileSync(path.join(__dirname,'..','VTG.py'),'utf8');
for(const id of ['WNC','WNV3']){
  const match=backend.match(new RegExp('\\{"name": "'+id+'", "color": "[^"]+"[^\\n]+'));
  const model=JSON.parse(match[0].trim().replace(/,$/,''));
  const brief=catalog.rows.find(row=>row.modelId===id);
  const detail=catalog.details.find(row=>row.model_id===id);
  assert.equal(catalog.labels[id],model.label);
  assert.equal(brief.name,model.label);
  assert.equal(detail['표출명칭'],model.label);
  assert.equal(catalog.colors[id],model.color);
  assert.equal(catalog.colors[brief.name],model.color);
}
assert.equal(catalog.labels.FNV3,catalog.labels.WNC);
assert.equal(catalog.rows.find(row=>row.modelId==='GENC').description,'[AI] 구글 딥마인드 WeatherNext1 앙상블모델(GenCast) 평균');
assert.equal(catalog.details.find(row=>row['표출명칭']==='GenCast')['참고사항'],'Google DeepMind AI모델 WeatherNext1 기반 앙상블모델(GenCast)');
assert.equal(catalog.details.find(row=>row.model_id==='WNC')['모델명'],'WeatherNext2 (WeatherNext Cyclones)');
assert.equal(catalog.details.find(row=>row.model_id==='WNV3')['모델명'],'WeatherNext3 (WeatherNext Cyclones)');
assert.equal(catalog.rows.find(row=>row.modelId==='WNC').description,'[AI] 구글 딥마인드 WeatherNext2 태풍예측모델(FNV3) 앙상블 평균');
assert.equal(catalog.rows.find(row=>row.modelId==='WNV3').description,'[AI] 구글 딥마인드 WeatherNext3 태풍예측모델(WNV3) 앙상블 평균');
assert.equal(catalog.details.find(row=>row.model_id==='WNC')['참고사항'],'Google DeepMind AI모델 WeatherNext2 기반 태풍예측모델(FNV3)');
assert.equal(catalog.details.find(row=>row.model_id==='WNV3')['참고사항'],'Google DeepMind 차세대 AI모델 WeatherNext3 기반 태풍예측모델(WNV3) (시험운영)');
assert.equal(catalog.colors.FNV3,catalog.colors.WNC);
const index=catalog.rows.findIndex(row=>row.modelId==='GENC');
assert.deepEqual(catalog.rows.slice(index,index+3).map(row=>row.modelId),['GENC','WNC','WNV3']);
assert(catalog.groups.includes('WNV3'));
assert.equal(catalog.count,40);
console.log('Weather Lab catalog, colors, labels and group separator tests passed');

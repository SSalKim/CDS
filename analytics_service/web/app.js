const $=id=>document.getElementById(id);
const form=$('filters');
let tab='overview',visitor='',cursor=null,busy=false;
let recentUsers=[];
const number=value=>Number(value||0).toLocaleString('ko-KR');
const region=value=>({asia:'아시아',hkor:'한반도'}[value]||value);
const date=(value,zone='Asia/Seoul',seconds=false)=>new Intl.DateTimeFormat('sv-SE',{
  timeZone:zone,year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',...(seconds?{second:'2-digit'}:{})
}).format(new Date(value));
const today=()=>new Date(Date.now()+9*3600000).toISOString().slice(0,10);
function params(){const p=new URLSearchParams(new FormData(form));for(const [key,value] of [...p]) if(!value)p.delete(key);return p;}
async function api(route,p=params()){
  const response=await fetch('/admin/api/'+route+'?'+p,{credentials:'same-origin',cache:'no-store'});
  if(response.status===403) throw new Error('관리자 인증이 필요합니다. 이 페이지를 새로 열어 로그인해 주세요.');
  if(!response.ok) throw new Error(response.status===400?'조회기간과 필터를 확인해 주세요.':'통계를 불러오지 못했습니다. 잠시 후 다시 조회해 주세요.');
  return response.json();
}
function cell(row,value,cls){const td=document.createElement('td');td.textContent=value??'';if(cls)td.className=cls;row.append(td);return td;}
function empty(tbody,columns){const tr=document.createElement('tr');const td=cell(tr,'조회된 기록이 없습니다.','empty');td.colSpan=columns;tbody.replaceChildren(tr);}
function setTab(value){tab=value;document.querySelectorAll('.view').forEach(el=>el.hidden=el.id!==tab);document.querySelectorAll('[data-tab]').forEach(el=>el.setAttribute('aria-selected',String(el.dataset.tab===tab)));}
function userButton(row,key){const td=cell(row,'');const button=document.createElement('button');button.type='button';button.textContent=key.slice(0,10);button.title='이 브라우저의 조회 이력';button.onclick=()=>{visitor=key;setTab('history');void refresh();};td.append(button);}
function showStats(data){
  const o=data.overview;
  $('views').textContent=number(o.views);$('usersCount').textContent=number(o.users);$('series').textContent=number(o.series_views);$('missing').textContent=number(o.missing);$('load').textContent=o.average_load_ms===null?'-':(o.average_load_ms/1000).toFixed(1)+'초';
  const top=$('topRows');top.replaceChildren();
  data.top.forEach((item,index)=>{const tr=document.createElement('tr');[index+1,item.model_label||item.model_id,item.product_label||item.product_id,region(item.region),number(item.series_views),number(item.users),number(item.cycles)].forEach(value=>cell(tr,value));top.append(tr);});
  if(!data.top.length)empty(top,7);
  const bars=$('dailyBars');bars.replaceChildren();const max=Math.max(1,...data.daily.map(x=>x.views));
  for(const item of data.daily){const wrap=document.createElement('div');wrap.className='bar-item';wrap.title=`${item.day}: ${number(item.views)}회 / ${number(item.users)} 브라우저`;
    const value=document.createElement('span');value.textContent=number(item.views);const bar=document.createElement('div');bar.className='bar';bar.style.height=(item.views/max*76)+'px';const label=document.createElement('span');label.textContent=item.day.slice(5);wrap.append(value,bar,label);bars.append(wrap);}
  if(!data.daily.length){const span=document.createElement('p');span.className='note';span.textContent='조회된 기록이 없습니다.';bars.append(span);}
  // Preserve the selected filter while adding newly observed models.
  const select=form.elements.model_id;
  for(const item of data.distribution){if([...select.options].some(x=>x.value===item.model_id))continue;const opt=document.createElement('option');opt.value=item.model_id;opt.textContent=item.model_label||item.model_id;select.append(opt);}
}
function locationLabel(item){return item.city || item.country ? [item.city||'도시 미확인',item.country].filter(Boolean).join(' · ') : '기록 없음';}
function renderUsers(){
  const term=$('userSearch').value.trim().toLowerCase();
  const rows=recentUsers.filter(item=>[item.visitor_key,item.ip_address,item.city,item.country].some(value=>String(value||'').toLowerCase().includes(term)));
  const body=$('userRows');body.replaceChildren();
  for(const item of rows){const tr=document.createElement('tr');userButton(tr,item.visitor_key);
    cell(tr,item.ip_address||'기록 없음','ip-address');cell(tr,locationLabel(item));
    [number(item.views),number(item.series_views),number(item.sessions),date(item.first_seen,'Asia/Seoul',true),date(item.last_seen,'Asia/Seoul',true)].forEach(value=>cell(tr,value));body.append(tr);}
  if(!rows.length)empty(body,8);
}
function showUsers(data){recentUsers=data.rows;renderUsers();}
function showHistory(data,append){
  const body=$('historyRows');if(!append)body.replaceChildren();
  for(const item of data.rows){const tr=document.createElement('tr');cell(tr,date(item.occurred_at,'Asia/Seoul',true));userButton(tr,item.visitor_key);
    cell(tr,item.ip_address||'기록 없음','ip-address');cell(tr,locationLabel(item));cell(tr,item.model_label||item.model_id);
    const product=cell(tr,item.product_label||item.product_id);const sub=document.createElement('span');sub.className='secondary';
    sub.textContent=region(item.region)+(item.view_context==='compare'?' · 비교':' · 단일');product.append(sub);
    cell(tr,date(item.run_utc,'UTC'));cell(tr,item.forecast_hour===null?'-':`+${String(item.forecast_hour).padStart(3,'0')}h`);
    cell(tr,date(item.valid_utc));cell(tr,item.outcome==='view'?'조회':'미표출');body.append(tr);}
  if(!body.children.length)empty(body,10);cursor=data.next;$('more').hidden=!cursor;
}
async function refresh(append=false){
  if(busy)return;busy=true;$('error').hidden=true;$('status').textContent='불러오는 중';
  for(const button of form.querySelectorAll('button'))button.disabled=true;
  try{
    const p=params();if(visitor&&tab==='history')p.set('visitor_key',visitor);if(append&&cursor)p.set('cursor',cursor);
    if(tab==='overview')showStats(await api('stats',p));
    if(tab==='users')showUsers(await api('users',p));
    if(tab==='history')showHistory(await api('history',p),append);
    const exp=params();if(visitor&&tab==='history')exp.set('visitor_key',visitor);$('export').href='/admin/api/export.csv?'+exp;
    $('historyTitle').textContent=visitor?'사용자 '+visitor.slice(0,10)+' 조회 이력':'전체 조회 이력';$('clearUser').hidden=!visitor;
    $('status').textContent='갱신 '+date(Date.now())+' KST';
  }catch(error){$('error').textContent=error.message;$('error').hidden=false;$('status').textContent='조회 실패';}
  finally{busy=false;for(const button of form.querySelectorAll('button'))button.disabled=false;}
}
function preset(days){const end=today(),start=new Date(Date.parse(end+'T00:00:00Z')-(days-1)*86400000).toISOString().slice(0,10);form.elements.start.value=start;form.elements.end.value=end;document.querySelectorAll('[data-days]').forEach(button=>button.classList.toggle('selected',Number(button.dataset.days)===days));}
form.onsubmit=event=>{event.preventDefault();void refresh();};
form.onchange=event=>{if(event.target.type==='date')document.querySelectorAll('[data-days]').forEach(button=>button.classList.remove('selected'));void refresh();};
document.querySelectorAll('[data-days]').forEach(button=>button.onclick=()=>{preset(Number(button.dataset.days));void refresh();});
document.querySelectorAll('[data-tab]').forEach(button=>button.onclick=()=>{setTab(button.dataset.tab);void refresh();});
$('more').onclick=()=>void refresh(true);$('clearUser').onclick=()=>{visitor='';void refresh();};
$('userSearch').oninput=renderUsers;
setInterval(()=>{if($('auto').checked&&document.visibilityState==='visible')void refresh();},30000);
preset(1);form.elements.start.max=today();form.elements.end.max=today();
api('whoami').then(owner=>{$('owner').textContent=owner.email;const min=new Date(Date.parse(today()+'T00:00:00Z')-(owner.retention_days-1)*86400000).toISOString().slice(0,10);form.elements.start.min=min;form.elements.end.min=min;return refresh();}).catch(error=>{$('error').textContent=error.message;$('error').hidden=false;$('status').textContent='인증 필요';});

const $=id=>document.getElementById(id);
const form=$('filters');
let tab='overview',visitor='',cursor=null,busy=false;
let recentUsers=[];
const nicknames=new Map();
const device=value=>({desktop:'PC',mobile:'모바일',tablet:'태블릿'}[value]||'기록 없음');
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
function userButton(row,key,nickname='',editable=false){
  nicknames.set(key,nickname||'');
  const td=cell(row,'');td.className='user-identity';
  const button=document.createElement('button');button.type='button';button.textContent=nickname||key.slice(0,10);button.title='이 브라우저의 조회 이력';
  button.onclick=()=>{visitor=key;setTab('history');void refresh();};td.append(button);
  if(nickname){const id=document.createElement('span');id.className='secondary';id.textContent=key.slice(0,10);td.append(id);}
  if(editable){const edit=document.createElement('button');edit.type='button';edit.className='alias-edit';edit.title='별칭 편집';edit.setAttribute('aria-label','별칭 편집');edit.append(CDSAdminIcon('Pencil'));edit.onclick=()=>editNickname(td,key,nickname);td.append(edit);}
}
function editNickname(td,key,nickname){
  const editor=document.createElement('form');editor.className='alias-editor';
  const input=document.createElement('input');input.value=nickname||'';input.maxLength=40;input.setAttribute('aria-label','사용자 별칭');
  const save=document.createElement('button');save.title='저장';save.setAttribute('aria-label','별칭 저장');save.append(CDSAdminIcon('Check'));
  const cancel=document.createElement('button');cancel.type='button';cancel.title='취소';cancel.setAttribute('aria-label','별칭 편집 취소');cancel.append(CDSAdminIcon('X'));
  const restore=()=>renderUsers();cancel.onclick=restore;input.onkeydown=event=>{if(event.key==='Escape')restore();};
  editor.append(input,save,cancel);td.replaceChildren(editor);input.focus();
  editor.onsubmit=async event=>{
    event.preventDefault();save.disabled=true;
    try{
      const response=await fetch('/admin/api/nickname',{method:'PUT',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({visitor_key:key,nickname:input.value})});
      if(!response.ok)throw new Error('별칭을 저장하지 못했습니다. 다시 시도해 주세요.');
      const value=await response.json();for(const item of recentUsers)if(item.visitor_key===key)item.nickname=value.nickname;
      nicknames.set(key,value.nickname);renderUsers();
    }catch(error){$('error').textContent=error.message;$('error').hidden=false;save.disabled=false;}
  };
}
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
  const rows=recentUsers.filter(item=>[item.nickname,item.visitor_key,item.ip_address,item.city,item.country].some(value=>String(value||'').toLowerCase().includes(term)));
  const body=$('userRows');body.replaceChildren();
  for(const item of rows){const tr=document.createElement('tr');userButton(tr,item.visitor_key,item.nickname,true);
    cell(tr,item.ip_address||'기록 없음','ip-address');cell(tr,locationLabel(item));
    cell(tr,device(item.device_class));
    [number(item.views),number(item.series_views),number(item.sessions),date(item.first_seen,'Asia/Seoul',true),date(item.last_seen,'Asia/Seoul',true)].forEach(value=>cell(tr,value));body.append(tr);}
  if(!rows.length)empty(body,9);
}
function showUsers(data){recentUsers=data.rows;renderUsers();}
const lead=value=>value===null?'-':`+${String(value).padStart(3,'0')}`;
let leadTooltip=null;
function hideLeads(){leadTooltip?.remove();leadTooltip=null;}
function forecastCell(tr,item){
  const list=item.forecasts||[{hour:item.forecast_hour,valid_utc:item.valid_utc}];
  const td=cell(tr,lead(list[0]?.hour));
  if(list.length>1){
    const button=document.createElement('button');button.type='button';button.className='lead-count';button.textContent=`[${list.length}]`;
    const lines=list.map(entry=>lead(entry.hour)).join('\n');button.setAttribute('aria-label',`조회 ${list.length}장, 예측시간 목록`);
    const show=()=>{
      hideLeads();leadTooltip=document.createElement('div');leadTooltip.className='lead-tooltip';leadTooltip.id='leadTooltip';leadTooltip.setAttribute('role','tooltip');leadTooltip.textContent=lines;
      document.body.append(leadTooltip);button.setAttribute('aria-describedby','leadTooltip');
      const rect=button.getBoundingClientRect(),height=leadTooltip.getBoundingClientRect().height;
      leadTooltip.style.left=Math.max(8,Math.min(innerWidth-140,rect.left))+'px';
      leadTooltip.style.top=Math.max(8,rect.bottom+height+8<innerHeight?rect.bottom+5:rect.top-height-5)+'px';
    };
    button.onmouseenter=show;button.onfocus=show;button.onmouseleave=hideLeads;button.onblur=hideLeads;
    button.onclick=show;td.append(button);
  }
}
function showHistory(data,append){
  hideLeads();
  const body=$('historyRows');if(!append)body.replaceChildren();
  for(const item of data.rows){const tr=document.createElement('tr');const stamp=cell(tr,date(item.occurred_at,'Asia/Seoul',true));
    if(item.view_count>1)stamp.title=date(item.first_seen,'Asia/Seoul',true)+' ~ '+date(item.occurred_at,'Asia/Seoul',true);
    userButton(tr,item.visitor_key,item.nickname);
    cell(tr,item.ip_address||'기록 없음','ip-address');cell(tr,locationLabel(item));cell(tr,item.model_label||item.model_id);
    const product=cell(tr,item.product_label||item.product_id);const sub=document.createElement('span');sub.className='secondary';
    sub.textContent=region(item.region)+(item.view_context==='compare'?' · 비교':' · 단일');product.append(sub);
    cell(tr,date(item.run_utc,'UTC'));forecastCell(tr,item);
    cell(tr,date(item.forecasts?.[0]?.valid_utc||item.valid_utc));cell(tr,device(item.device_class));cell(tr,item.outcome==='view'?'조회':'미표출');body.append(tr);}
  if(!body.children.length)empty(body,11);cursor=data.next;$('more').hidden=!cursor;
}
async function refresh(append=false){
  if(busy)return;busy=true;$('error').hidden=true;$('status').textContent='불러오는 중';
  for(const button of form.querySelectorAll('button'))button.disabled=true;
  try{
    const p=params();if(visitor&&tab==='history')p.set('visitor_key',visitor);if(append&&cursor)p.set('cursor',cursor);
    if(tab==='history')p.set('group','series');
    if(tab==='overview')showStats(await api('stats',p));
    if(tab==='users')showUsers(await api('users',p));
    if(tab==='history')showHistory(await api('history',p),append);
    const exp=params();if(visitor&&tab==='history')exp.set('visitor_key',visitor);$('export').href='/admin/api/export.csv?'+exp;
    $('historyTitle').textContent=visitor?'사용자 '+(nicknames.get(visitor)||visitor.slice(0,10))+' 조회 이력':'전체 조회 이력';$('clearUser').hidden=!visitor;
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
setInterval(()=>{if($('auto').checked&&document.visibilityState==='visible'&&!document.querySelector('.alias-editor'))void refresh();},30000);
window.addEventListener('scroll',hideLeads,true);window.addEventListener('resize',hideLeads);
preset(1);form.elements.start.max=today();form.elements.end.max=today();
api('whoami').then(owner=>{$('owner').textContent=owner.email;const min=new Date(Date.parse(today()+'T00:00:00Z')-(owner.retention_days-1)*86400000).toISOString().slice(0,10);form.elements.start.min=min;form.elements.end.min=min;return refresh();}).catch(error=>{$('error').textContent=error.message;$('error').hidden=false;$('status').textContent='인증 필요';});

export const RETENTION_DAYS=90;
const DAY=86400000;
const text=(value,max)=>typeof value==='string' ? value.trim().replace(/[\u0000-\u001f\u007f]/g,'').slice(0,max) : '';

function iso(value){
  if(typeof value!=='string' || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$/.test(value)) throw new Error('Invalid UTC timestamp');
  const date=new Date(value);
  if(Number.isNaN(date.getTime()) || date.toISOString().slice(0,19)!==value.slice(0,19)) throw new Error('Invalid UTC timestamp');
  return date.toISOString();
}

export function cleanEvent(value,now=Date.now()){
  if(!value || typeof value!=='object' || Array.isArray(value)) throw new Error('Invalid event');
  if(!/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(value.event_id || '')) throw new Error('Invalid event id');
  if(!['view','missing'].includes(value.outcome)) throw new Error('Invalid outcome');
  const occurred=Number(value.occurred_at);
  if(!Number.isSafeInteger(occurred) || occurred<now-DAY || occurred>now+300000) throw new Error('Invalid event time');
  const event={event_id:value.event_id,occurred_at:occurred,received_at:now,outcome:value.outcome};
  for(const [name,max] of Object.entries({menu:30,region:40,product_id:60,product_label:100,model_id:50,
    model_label:80,detail_token:60,image_source:60})) event[name]=text(value[name],max);
  for(const name of ['menu','region','product_id','model_id']){
    if(!/^[a-z0-9_-]+$/i.test(event[name])) throw new Error('Invalid chart field');
  }
  event.run_utc=iso(value.run_utc);
  event.valid_utc=iso(value.valid_utc);
  event.forecast_hour=value.forecast_hour===null ? null : Number(value.forecast_hour);
  if(event.forecast_hour!==null && (!Number.isFinite(event.forecast_hour) || event.forecast_hour<0 || event.forecast_hour>1000)) throw new Error('Invalid lead');
  event.view_context=value.view_context==='compare' ? 'compare' : 'single';
  event.device_class=['mobile','tablet'].includes(value.device_class) ? value.device_class : 'desktop';
  const count=value=>Number.isFinite(Number(value)) ? Math.min(20,Math.max(0,Math.trunc(Number(value)))) : 0;
  event.loaded_count=count(value.loaded_count);
  event.expected_count=count(value.expected_count);
  event.load_ms=typeof value.load_ms==='number' && Number.isFinite(value.load_ms)
    ?Math.min(120000,Math.max(0,Math.round(value.load_ms))):null;
  return event;
}

export function filters(url,now=Date.now(),retention=RETENTION_DAYS){
  const today=new Date(now+9*3600000).toISOString().slice(0,10);
  const start=url.searchParams.get('start') || today;
  const end=url.searchParams.get('end') || today;
  function day(value){
    if(!/^\d{4}-\d{2}-\d{2}$/.test(value)) throw new Error('Invalid date');
    const stamp=Date.parse(value+'T00:00:00+09:00');
    if(!Number.isFinite(stamp) || new Date(stamp+9*3600000).toISOString().slice(0,10)!==value) throw new Error('Invalid date');
    return stamp;
  }
  const from=day(start),to=day(end)+DAY;
  if(from>=to || to-from>retention*DAY || from<day(today)-(retention-1)*DAY || end>today) throw new Error('Date outside retained range');
  const clauses=['occurred_at >= ?','occurred_at < ?'];
  const args=[from,to];
  for(const key of ['model_id','region','menu','product_id','visitor_key']){
    const value=url.searchParams.get(key);
    if(!value) continue;
    if(key==='visitor_key' ? !/^[0-9a-f]{64}$/.test(value) : !/^[a-z0-9_-]{1,60}$/i.test(value)) throw new Error('Invalid filter');
    clauses.push(`${key} = ?`);
    args.push(value);
  }
  return {where:clauses.join(' AND '),args,start,end};
}

const columns=['event_id','occurred_at','received_at','visitor_key','session_key','series_key','outcome','menu',
  'region','product_id','product_label','model_id','model_label','run_utc','forecast_hour','valid_utc','detail_token',
  'view_context','image_source','loaded_count','expected_count','load_ms','device_class'];

export function insert(db,event){
  return db.prepare(`INSERT INTO events (${columns.join(',')}) VALUES (${columns.map(()=>'?').join(',')})
    ON CONFLICT(event_id) DO NOTHING`).bind(...columns.map(key=>event[key] ?? null));
}

export async function statistics(db,scope){
  const cte=`WITH filtered AS (SELECT * FROM events WHERE ${scope.where})`;
  const query=sql=>db.prepare(`${cte} ${sql}`).bind(...scope.args);
  const results=await db.batch([
    query(`SELECT COUNT(CASE WHEN outcome='view' THEN 1 END) AS views,
      COUNT(DISTINCT CASE WHEN outcome='view' THEN visitor_key END) AS users,
      COUNT(DISTINCT CASE WHEN outcome='view' THEN session_key END) AS sessions,
      COUNT(CASE WHEN outcome='missing' THEN 1 END) AS missing,
      AVG(CASE WHEN outcome='view' THEN load_ms END) AS average_load_ms,
      (SELECT COUNT(*) FROM (SELECT visitor_key,series_key FROM filtered WHERE outcome='view'
       GROUP BY visitor_key,series_key)) AS series_views FROM filtered`),
    query(`SELECT model_id,MAX(model_label) AS model_label,product_id,MAX(product_label) AS product_label,region,
      COUNT(*) AS series_views,COUNT(DISTINCT visitor_key) AS users,COUNT(DISTINCT run_utc) AS cycles FROM
      (SELECT visitor_key,series_key,model_id,model_label,product_id,product_label,region,run_utc
       FROM filtered WHERE outcome='view' GROUP BY visitor_key,series_key)
      GROUP BY model_id,product_id,region ORDER BY series_views DESC,model_id,product_id LIMIT 50`),
    query(`SELECT strftime('%Y-%m-%d',occurred_at/1000,'unixepoch','+9 hours') AS day,
      COUNT(CASE WHEN outcome='view' THEN 1 END) AS views,
      COUNT(DISTINCT CASE WHEN outcome='view' THEN visitor_key END) AS users,
      COUNT(CASE WHEN outcome='missing' THEN 1 END) AS missing FROM filtered GROUP BY day ORDER BY day`),
    query(`SELECT model_id,MAX(model_label) AS model_label,region,view_context,COUNT(*) AS views
      FROM filtered WHERE outcome='view' GROUP BY model_id,region,view_context ORDER BY views DESC LIMIT 100`)
  ]);
  return {overview:results[0].results[0],top:results[1].results,daily:results[2].results,
    distribution:results[3].results,range:{start:scope.start,end:scope.end}};
}

export async function users(db,scope){
  const result=await db.prepare(`SELECT visitor_key,COUNT(*) AS events,
    COUNT(CASE WHEN outcome='view' THEN 1 END) AS views,COUNT(DISTINCT session_key) AS sessions,
    COUNT(DISTINCT CASE WHEN outcome='view' THEN series_key END) AS series_views,
    MIN(occurred_at) AS first_seen,MAX(occurred_at) AS last_seen FROM events WHERE ${scope.where}
    GROUP BY visitor_key ORDER BY last_seen DESC,visitor_key LIMIT 100`).bind(...scope.args).all();
  return result.results;
}

export async function history(db,scope,cursor,limit=100){
  const args=[...scope.args];
  let clause=scope.where;
  if(cursor){
    const match=/^(\d{13}):([0-9a-f-]{36})$/.exec(cursor);
    if(!match) throw new Error('Invalid cursor');
    clause+=' AND (occurred_at < ? OR (occurred_at = ? AND event_id < ?))';
    args.push(Number(match[1]),Number(match[1]),match[2]);
  }
  const result=await db.prepare(`SELECT event_id,occurred_at,visitor_key,outcome,menu,region,product_id,product_label,
    model_id,model_label,run_utc,forecast_hour,valid_utc,detail_token,view_context,image_source,load_ms,device_class
    FROM events WHERE ${clause} ORDER BY occurred_at DESC,event_id DESC LIMIT ?`).bind(...args,limit+1).all();
  const rows=result.results.slice(0,limit);
  const last=rows.at(-1);
  return {rows,next:result.results.length>limit && last ? `${last.occurred_at}:${last.event_id}` : null};
}

export function csv(rows){
  const names=['occurred_at','visitor_key','outcome','menu','region','model_id','product_id','product_label',
    'run_utc','forecast_hour','valid_utc','view_context','load_ms'];
  const cell=value=>{
    let str=String(value ?? '');
    if(/^[\s]*[=+@-]/.test(str)) str="'"+str;
    return '"'+str.replaceAll('"','""')+'"';
  };
  return '\ufeff'+[names.map(cell).join(','),...rows.map(row=>names.map(name=>cell(row[name])).join(','))].join('\r\n');
}

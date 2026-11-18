(function(global){
'use strict';
function iconButton(icon,label){
const button=document.createElement('button');
button.type='button';button.className='viewer-icon-button';button.title=label;button.setAttribute('aria-label',label);
button.append(CDSViewerIcons(icon));return button;
}
function rowsFor(items){
const rows=[];
for(const item of items){
let row=rows.at(-1);
if(!row || item.left<=row.at(-1).left+1){row=[];rows.push(row);}
row.push(item);
}
return rows;
}
function packRows(rows,gap=3){
let y=0;const placements=[];
const widths=Array.from({length:Math.max(0,...rows.map(row=>row.length))},(_,index)=>Math.max(...rows.map(row=>row[index]?.width||0)));
for(const row of rows){
let x=0;const height=Math.max(...row.map(item=>item.height));
for(const [index,item] of row.entries()){placements.push({...item,x:x+Math.round((widths[index]-item.width)/2),y:y+(item.align==='top'?0:Math.round((height-item.height)/2))});x+=widths[index]+gap;}
y+=height+gap;
}
return {width:widths.reduce((total,width)=>total+width+gap,0)-(widths.length?gap:0),height:Math.max(0,y-gap),placements};
}
function snapshot(root){
let cells=[...root.children].filter(el=>el.matches('.compare-image-item,.single-image-item'));
if(!cells.length) cells=[root];
return cells.map(cell=>({left:cell.getBoundingClientRect().left,align:cell.matches('.compare-top-aligned,.has-winter-product-notice')?'top':'center',
images:[...cell.querySelectorAll('img')].filter(img=>img.complete && img.naturalWidth && img.getBoundingClientRect().width>0)
.map(img=>({url:img.currentSrc||img.src,left:img.getBoundingClientRect().left,align:getComputedStyle(img.parentElement).alignItems==='flex-start'?'top':'center'})),
message:cell.querySelector('.compare-placeholder')?.textContent || ''}));
}
async function bitmap(url,signal){
const proxy=new URL('/chart-image',global.CDS_USAGE_CONFIG?.endpoint || 'https://cds-usage-analytics.kwj1407.workers.dev');
proxy.searchParams.set('url',url);
for(const candidate of [url,proxy.href]){
try{
const response=await fetch(candidate,{mode:'cors',credentials:'omit',signal:AbortSignal.any([signal,AbortSignal.timeout(20000)])});
if(!response.ok) continue;
const blob=await response.blob();
return await createImageBitmap(blob);
}catch(error){if(signal.aborted)throw error;}
}
throw new Error('원본 이미지를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.');
}
async function compose(cells,signal){
const resources=[];
try{
const prepared=[];
for(const cell of cells){
const images=[];
for(const image of cell.images){
const source=await bitmap(image.url,signal);resources.push(source);
images.push({...image,width:source.width,height:source.height,source});
}
const block=images.length?packRows(rowsFor(images)):null;
prepared.push({...cell,block});
}
const exemplar=prepared.find(cell=>cell.block)?.block;
if(!exemplar)throw new Error('캡처할 일기도 이미지가 없습니다.');
const layout=packRows(rowsFor(prepared.map(cell=>({...cell,width:cell.block?.width||exemplar.width,height:cell.block?.height||exemplar.height}))));
if(layout.width>32760 || layout.height>32760 || layout.width*layout.height>100000000)
throw new Error('원본 이미지의 합성 크기가 너무 큽니다. 비교 모델 수를 줄여 주세요.');
const canvas=document.createElement('canvas');canvas.width=layout.width;canvas.height=layout.height;
const ctx=canvas.getContext('2d');ctx.fillStyle='white';ctx.fillRect(0,0,canvas.width,canvas.height);
for(const cell of layout.placements){
if(cell.block){for(const image of cell.block.placements)ctx.drawImage(image.source,cell.x+image.x,cell.y+image.y);}
else{
ctx.fillStyle='#f1f5f9';ctx.fillRect(cell.x,cell.y,cell.width,cell.height);
ctx.fillStyle='#64748b';ctx.font='14px sans-serif';ctx.textAlign='center';
(cell.message||'이미지 없음').split('\n').slice(0,6).forEach((line,index)=>ctx.fillText(line,cell.x+cell.width/2,cell.y+cell.height/2+index*22,cell.width-32));
}
}
const blob=await new Promise((resolve,reject)=>canvas.toBlob(value=>value?resolve(value):reject(new Error('이미지 저장에 실패했습니다.')),'image/png'));
canvas.width=canvas.height=0;
return blob;
}finally{resources.forEach(resource=>resource.close());}
}
async function captureCharts(){
const root=document.getElementById('chartImages');
const cells=snapshot(root);stopCompareAnimation();
const dialog=document.createElement('dialog');dialog.className='selection-confirmation chart-capture-dialog';dialog.setAttribute('aria-label','일기도 캡처');
const status=document.createElement('p');status.className='capture-status';status.setAttribute('role','status');status.textContent='캡처 이미지를 준비하고 있습니다.';
const preview=document.createElement('div');preview.className='capture-preview';
const actions=document.createElement('div');actions.className='selection-confirmation-actions';
const copy=iconButton('Copy','이미지 복사'),download=iconButton('Download','PNG 다운로드'),close=iconButton('X','닫기');
copy.disabled=download.disabled=true;actions.append(copy,download,close);dialog.append(status,preview,actions);
const controller=new AbortController();let objectUrl='',blob=null,closed=false;
const modal=openViewerDialog(dialog,{maxWidth:960,onClose:()=>{closed=true;controller.abort();if(objectUrl)URL.revokeObjectURL(objectUrl);}});
close.onclick=()=>modal.close(false);
copy.onclick=async()=>{
try{await navigator.clipboard.write([new ClipboardItem({'image/png':blob})]);status.textContent='이미지를 복사했습니다.';}
catch{status.textContent='복사 권한이 없거나 지원되지 않는 브라우저입니다. 다운로드를 이용해 주세요.';}
};
download.onclick=()=>{
const a=document.createElement('a');a.href=objectUrl;
a.download='CDS-'+new Date().toISOString().replace(/[:.]/g,'-')+'.png';a.click();
};
try{
blob=await compose(cells,controller.signal);if(closed)return;
objectUrl=URL.createObjectURL(blob);const image=new Image();image.alt='합성된 일기도';image.src=objectUrl;
await image.decode();if(closed)return;
preview.append(image);status.textContent=`${image.naturalWidth} × ${image.naturalHeight} px`;
download.disabled=false;copy.disabled=!navigator.clipboard?.write || !global.ClipboardItem;modal.position();
}catch(error){if(!closed){status.textContent=error.message;modal.position();}}
}
global.CDSChartCapture={packRows,rowsFor,compose,capture: captureCharts,button:()=>{
const button=iconButton('Camera','일기도 캡처');button.onclick=()=>void captureCharts();return button;
}};
})(window);

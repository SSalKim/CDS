(function(global){
'use strict';
let axis='width',closeMenu=null,frame=0;
try{if(localStorage.getItem('cds.viewer.fit-axis')==='height')axis='height';}catch{}
function sync(){
const root=document.getElementById('chartImages'),viewer=root?.closest('.viewer-wrap');
if(!viewer)return;
const heightFit=root.classList.contains('fit-screen')&&axis==='height';
root.classList.toggle('fit-height',heightFit);
if(!heightFit)return;
const cells=[...root.children].filter(cell=>cell.matches('.compare-image-item,.single-image-item'));
const columns=root.classList.contains('compare-images')?getActiveCompareLayout().cols:1;
const rows=Math.max(1,Math.ceil(cells.length/columns));
const height=Math.max(80,Math.floor((viewer.clientHeight-24-3*(rows-1))/rows));
root.style.setProperty('--fit-columns',String(columns));
for(const cell of cells){
const notice=cell.querySelector('.winter-product-notice');
const imageHeight=Math.max(40,height-8-(notice?notice.getBoundingClientRect().height+24:0));
cell.style.setProperty('--fit-cell-height',height+'px');
for(const img of cell.querySelectorAll('img')){
img.style.setProperty('--fit-image-height',imageHeight+'px');
img.style.setProperty('--fit-image-width',(imageHeight*(img.naturalWidth||1)/(img.naturalHeight||1))+'px');
}
}
}
function schedule(){cancelAnimationFrame(frame);frame=requestAnimationFrame(sync);}
function control(label,{onChange}){
closeMenu?.();
const wrap=document.createElement('div');wrap.className='viewer-fit-control';wrap.append(label);
const arrow=document.createElement('button');arrow.type='button';arrow.className='viewer-fit-direction';arrow.title='맞춤 방향';arrow.setAttribute('aria-label','맞춤 방향');arrow.setAttribute('aria-expanded','false');arrow.append(CDSViewerIcons('ChevronDown'));
const menu=document.createElement('div');menu.className='fit-direction-menu';menu.hidden=true;menu.setAttribute('role','group');menu.setAttribute('aria-label','맞춤 방향');
for(const [value,text]of [['height','상하'],['width','좌우']]){
const option=document.createElement('label'),radio=document.createElement('input');
radio.type='radio';radio.name='viewer-fit-direction';radio.value=value;radio.checked=axis===value;
radio.onchange=()=>{axis=value;try{localStorage.setItem('cds.viewer.fit-axis',axis);}catch{}onChange(true);schedule();};
option.append(radio,document.createTextNode(text));menu.append(option);
}
const close=()=>{menu.hidden=true;arrow.setAttribute('aria-expanded','false');document.removeEventListener('pointerdown',outside);document.removeEventListener('keydown',escape);if(closeMenu===close)closeMenu=null;};
const outside=event=>{if(!wrap.contains(event.target))close();};
const escape=event=>{if(event.key==='Escape'){event.preventDefault();close();arrow.focus();}};
arrow.onclick=()=>{if(!menu.hidden){close();return;}closeMenu?.();closeMenu=close;menu.hidden=false;arrow.setAttribute('aria-expanded','true');document.addEventListener('pointerdown',outside);document.addEventListener('keydown',escape);};
wrap.append(arrow,menu);return wrap;
}
const viewer=document.querySelector('.viewer-wrap'),root=document.getElementById('chartImages');
if(viewer&&root){
new ResizeObserver(schedule).observe(viewer);
new MutationObserver(schedule).observe(root,{childList:true,subtree:true});
root.addEventListener('load',schedule,true);
}
global.CDSViewerFit={control,sync,schedule,get axis(){return axis;}};
})(window);

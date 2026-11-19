(function(global){
'use strict';
// A round loupe over the chart images. In comparison mode every chart shows a loupe at the
// same relative position, so the same place can be compared across models at a glance.
const SIZE=190,MIN_ZOOM=1.5,MAX_ZOOM=6,STORE='cds.viewer.magnifier-zoom';
let active=false,zoom=2.5,lenses=new Map(),last=null,buttons=new Set();
try{const saved=Number(localStorage.getItem(STORE));if(saved>=MIN_ZOOM&&saved<=MAX_ZOOM)zoom=saved;}catch{}

function root(){return document.getElementById('chartImages');}
function images(){
const container=root();
if(!container)return [];
return [...container.querySelectorAll('img')].filter(img=>img.complete&&img.naturalWidth&&img.getBoundingClientRect().width>8&&getComputedStyle(img).visibility!=='hidden');
}
function lensFor(img){
let lens=lenses.get(img);
if(!lens){
lens=document.createElement('div');lens.className='chart-magnifier-lens';lens.setAttribute('aria-hidden','true');
document.body.appendChild(lens);lenses.set(img,lens);
}
return lens;
}
function hide(){for(const lens of lenses.values())lens.hidden=true;}
function clear(){for(const lens of lenses.values())lens.remove();lenses=new Map();}

// fx, fy: position inside the image as fractions of its displayed size.
function place(img,fx,fy,touch){
const rect=img.getBoundingClientRect(),lens=lensFor(img);
const x=rect.left+fx*rect.width,y=rect.top+fy*rect.height;
const offsetY=touch?SIZE*.75:0;  // keep the loupe above a finger
lens.style.width=lens.style.height=SIZE+'px';
lens.style.left=(x-SIZE/2)+'px';lens.style.top=(y-SIZE/2-offsetY)+'px';
lens.style.backgroundImage=`url("${(img.currentSrc||img.src).replace(/"/g,'%22')}")`;
lens.style.backgroundSize=`${rect.width*zoom}px ${rect.height*zoom}px`;
lens.style.backgroundPosition=`${SIZE/2-fx*rect.width*zoom}px ${SIZE/2-fy*rect.height*zoom}px`;
lens.hidden=false;
}

function update(event){
if(!active)return;
const target=event.target instanceof Element?event.target.closest('img'):null;
const container=root();
if(!target||!container||!container.contains(target)){hide();last=null;return;}
const rect=target.getBoundingClientRect();
const fx=(event.clientX-rect.left)/rect.width,fy=(event.clientY-rect.top)/rect.height;
if(fx<0||fx>1||fy<0||fy>1){hide();last=null;return;}
last={target,fx,fy,touch:event.pointerType==='touch'};
render();
}
function render(){
if(!last)return;
const all=images();
const compare=root()?.classList.contains('compare-images');
const shown=new Set(compare?all:[last.target]);
for(const [img,lens] of lenses){if(!shown.has(img)||!img.isConnected){lens.remove();lenses.delete(img);}}
for(const img of shown)place(img,last.fx,last.fy,last.touch&&img===last.target);
}
function wheel(event){
if(!active||!last||!(event.target instanceof Element)||!root()?.contains(event.target))return;
event.preventDefault();
zoom=Math.min(MAX_ZOOM,Math.max(MIN_ZOOM,zoom*(event.deltaY<0?1.15:1/1.15)));
try{localStorage.setItem(STORE,String(zoom));}catch{}
render();
}
function setActive(value){
active=!!value;
document.documentElement.classList.toggle('magnifier-active',active);
for(const button of buttons){
if(!button.isConnected){buttons.delete(button);continue;}
button.setAttribute('aria-pressed',String(active));button.classList.toggle('active',active);
}
if(!active){clear();last=null;}
}
function iconButton(){
const button=document.createElement('button');
button.type='button';button.className='viewer-icon-button chart-magnifier-button';
button.title='돋보기 (휠로 배율 조절, Esc로 끄기)';button.setAttribute('aria-label','돋보기');
button.setAttribute('aria-pressed',String(active));button.classList.toggle('active',active);
button.append(CDSViewerIcons('ZoomIn'));
button.onclick=()=>setActive(!active);
buttons.add(button);
return button;
}

document.addEventListener('pointermove',update,{passive:true});
document.addEventListener('pointerdown',event=>{if(active&&event.pointerType==='touch')update(event);},{passive:true});
document.addEventListener('pointerleave',hide,{passive:true});
document.addEventListener('wheel',wheel,{passive:false});
document.addEventListener('keydown',event=>{if(active&&event.key==='Escape')setActive(false);});
global.addEventListener('scroll',()=>{if(active)render();},{passive:true,capture:true});
global.addEventListener('resize',()=>{if(active)render();},{passive:true});

global.CDSChartMagnifier={button:iconButton,setActive,get active(){return active;},get zoom(){return zoom;},
_place:place,_render:render};
})(window);

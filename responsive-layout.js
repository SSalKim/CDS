(function(global){
'use strict';

// Shows a ▼ button at the bottom of a scroll container while more content sits below it.
// The desktop sidebar and the mobile model dock scroll in different elements, so both get one;
// CSS shows only the hint whose container is actually scrolling at the current size.
function attach(container,className){
if(!container) return;
const hint=document.createElement('button');
hint.type='button';
hint.className='scroll-hint '+className;
hint.setAttribute('aria-label','아래 항목 더 보기');
hint.title='아래 항목 더 보기 (드래그 또는 휠)';
const arrow=document.createElement('span');
arrow.className='scroll-hint-arrow';
arrow.setAttribute('aria-hidden','true');
arrow.textContent='▼';
hint.append(arrow);
let frame=0;
const update=()=>{
cancelAnimationFrame(frame);
frame=requestAnimationFrame(()=>{
const scrollable=/(auto|scroll)/.test(getComputedStyle(container).overflowY);
const below=container.scrollHeight-container.clientHeight-container.scrollTop;
container.classList.toggle('has-more-below',scrollable&&below>6);
});
};
hint.addEventListener('click',()=>{
container.scrollBy({top:Math.max(80,container.clientHeight*.6),behavior:'smooth'});
});
container.append(hint);
container.addEventListener('scroll',update,{passive:true});
new ResizeObserver(update).observe(container);
new MutationObserver(update).observe(container,{childList:true,subtree:true,attributes:true,attributeFilter:['class','hidden']});
global.addEventListener('resize',update,{passive:true});
update();
}

// Desktop toolbar: keep everything on one line while the product row still fits beside the
// time row (selects may shrink to their minimum); otherwise put the product row on its own line.
const MOBILE=global.matchMedia?.('(max-width: 700px) and (orientation: portrait)');
const SELECT_MINIMUM=120+150+8;
function fitToolbar(){
const left=document.querySelector('.app-shell .toolbar-left');
const time=left?.querySelector('.toolbar-time-row');
const controls=document.getElementById('timelineTopControls');
if(!left || !time || !controls) return;
let frame=0;
const update=()=>{
cancelAnimationFrame(frame);
frame=requestAnimationFrame(()=>{
if(MOBILE?.matches){left.classList.remove('is-stacked','is-tight');return;}
const style=getComputedStyle(left);
const gap=parseFloat(style.columnGap)||10;
const timeWidth=[...time.children].reduce((sum,child)=>sum+child.getBoundingClientRect().width,0)+
Math.max(0,time.children.length-1)*(parseFloat(getComputedStyle(time).columnGap)||8);
const tools=controls.firstElementChild||controls;
const toolGap=parseFloat(getComputedStyle(tools).columnGap)||8;
const toolsWidth=[...tools.children].reduce((sum,child)=>sum+child.getBoundingClientRect().width,0)+
Math.max(0,tools.children.length-1)*toolGap;
const productWidth=SELECT_MINIMUM+8+toolsWidth;
left.classList.toggle('is-stacked',timeWidth+gap+productWidth>left.clientWidth+1);
// Too narrow even for its own line: selects fill one line and the tools spread over the next.
left.classList.toggle('is-tight',productWidth>left.clientWidth+1);
});
};
new ResizeObserver(update).observe(left);
new MutationObserver(update).observe(controls,{childList:true,subtree:true});
MOBILE?.addEventListener?.('change',update);
update();
}

function init(){
attach(document.querySelector('.app-shell > .sidebar'),'scroll-hint-sidebar');
attach(document.querySelector('.app-shell .model-box'),'scroll-hint-dock');
fitToolbar();
}

if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init,{once:true});
else init();
})(window);

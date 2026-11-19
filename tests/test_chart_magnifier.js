const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');

const listeners={};
class Element{
  constructor(tag){this.tag=tag;this.style={};this.hidden=false;this.attributes={};this.children=[];this.isConnected=true;
    const classes=new Set();this.classList={add:c=>classes.add(c),remove:c=>classes.delete(c),contains:c=>classes.has(c),
      toggle:(c,on)=>{(on===undefined?!classes.has(c):on)?classes.add(c):classes.delete(c);}};}
  setAttribute(k,v){this.attributes[k]=String(v);}
  append(...items){this.children.push(...items);}
  appendChild(item){this.children.push(item);return item;}
  remove(){this.isConnected=false;}
  closest(selector){return selector==='img'&&this.tag==='img'?this:null;}
}
function image(left,top,width,height,src){
  const img=new Element('img');img.complete=true;img.naturalWidth=width*2;img.currentSrc=src;
  img.getBoundingClientRect=()=>({left,top,width,height});return img;
}
const imgs=[image(0,0,400,300,'https://a.example/1.webp'),image(420,0,400,300,'https://a.example/2.webp')];
const root=new Element('div');root.querySelectorAll=()=>imgs;root.contains=node=>imgs.includes(node);
const body=new Element('body');
const store=new Map();
const context={
  console,Element,
  document:{getElementById:id=>id==='chartImages'?root:null,createElement:tag=>new Element(tag),body,
    documentElement:new Element('html'),addEventListener:(type,fn)=>{listeners[type]=fn;}},
  localStorage:{getItem:k=>store.get(k)??null,setItem:(k,v)=>store.set(k,v)},
  getComputedStyle:()=>({visibility:'visible'}),
  CDSViewerIcons:name=>({icon:name}),
  addEventListener:()=>{}
};
context.window=context;context.globalThis=context;
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(__dirname,'..','chart-magnifier.js'),'utf8'),context);
const magnifier=context.CDSChartMagnifier;
const lenses=()=>body.children.filter(lens=>lens.isConnected&&!lens.hidden);

const button=magnifier.button();
assert.equal(button.attributes['aria-pressed'],'false');
assert.equal(button.children[0].icon,'ZoomIn');
listeners.pointermove({target:imgs[0],clientX:100,clientY:150,pointerType:'mouse'});
assert.equal(lenses().length,0,'Inactive magnifier draws nothing');

button.onclick();
assert.equal(button.attributes['aria-pressed'],'true');
listeners.pointermove({target:imgs[0],clientX:100,clientY:150,pointerType:'mouse'});
assert.equal(lenses().length,1,'Single view shows one loupe');
const lens=lenses()[0];
assert.equal(lens.style.left,(100-95)+'px');
assert.equal(lens.style.top,(150-95)+'px');
assert.equal(lens.style.backgroundSize,'1000px 750px','2.5x zoom of the displayed size');
assert.equal(lens.style.backgroundPosition,`${95-0.25*1000}px ${95-0.5*750}px`,'Loupe centre shows the pointed spot');
assert.match(lens.style.backgroundImage,/1\.webp/);

root.classList.add('compare-images');
listeners.pointermove({target:imgs[0],clientX:100,clientY:150,pointerType:'mouse'});
const shown=lenses();
assert.equal(shown.length,2,'Comparison shows a loupe on every chart');
const second=shown.find(item=>/2\.webp/.test(item.style.backgroundImage));
assert.equal(second.style.left,(420+100-95)+'px','Same relative position on the other chart');
assert.equal(second.style.backgroundPosition,lens.style.backgroundPosition);

let prevented=false;
for(let i=0;i<30;i++) listeners.wheel({target:imgs[0],deltaY:-1,preventDefault:()=>{prevented=true;}});
assert(prevented);
assert.equal(magnifier.zoom,6,'Zoom is capped');
assert.equal(store.get('cds.viewer.magnifier-zoom'),'6');
for(let i=0;i<30;i++) listeners.wheel({target:imgs[0],deltaY:1,preventDefault:()=>{}});
assert.equal(magnifier.zoom,1.5,'Zoom has a floor');

listeners.pointermove({target:new Element('div'),clientX:0,clientY:0,pointerType:'mouse'});
assert.equal(lenses().length,0,'Leaving the charts hides the loupes');

listeners.pointermove({target:imgs[0],clientX:100,clientY:150,pointerType:'touch'});
const touched=lenses().find(item=>/1\.webp/.test(item.style.backgroundImage));
assert(parseFloat(touched.style.top)<150-95,'On touch the loupe sits above the finger');

listeners.keydown({key:'Escape'});
assert.equal(magnifier.active,false);
assert.equal(button.attributes['aria-pressed'],'false');
assert.equal(lenses().length,0,'Escape removes every loupe');
console.log('Chart magnifier: loupe placement, comparison sync, zoom limits, touch offset and Escape passed');

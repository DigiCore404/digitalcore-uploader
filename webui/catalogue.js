const parse = (html) => new DOMParser().parseFromString(html,'text/html');
function plainDescription(value){
 let text=String(value||'').slice(0,100000);
 for(let pass=0;pass<2;pass++){
  const doc=parse(text);doc.querySelectorAll('script,style,iframe,noscript,template,svg').forEach(node=>node.remove());
  doc.querySelectorAll('br').forEach(node=>node.replaceWith(doc.createTextNode('\n')));
  doc.querySelectorAll('p,div,section,article,h1,h2,h3,h4,h5,h6,blockquote,ul,ol,li,tr,pre').forEach(node=>{node.prepend(doc.createTextNode('\n\n'));node.append(doc.createTextNode('\n\n'));});
  text=doc.body.textContent;
  if(!/<\/?[a-z][^>]*>/i.test(text))break;
 }
 return text.replace(/\u00a0/g,' ').replace(/[ \t\r\f\v]+/g,' ').split('\n').map(line=>line.trim()).join('\n').replace(/\n{3,}/g,'\n\n').trim().slice(0,30000);
}

'use strict';
const CatalogMetadata={plainDescription,plainDescription,
 sites:[], search:async()=>{throw new Error('Choose TMDB Movies or TV.');},
 sourceLabel:row=>row.site||'TMDB',
 sameRelease:(a,b)=>a.id===b.id&&a.kind===b.kind,
 combine(rows){
  const first=rows[0]||{metadata:{},images:[]};
  const result={...first,metadata:{...first.metadata},images:[...(first.images||[])],choices:{},fieldSources:{},imageSources:{}};
  for(const [key,value] of Object.entries({...result.metadata,title:result.title,description:result.description})){
   result.choices[key]=value?[String(value)]:[];result.fieldSources[key]=[first.site||'Metadata'];
  }
  for(const url of result.images)result.imageSources[url]=[first.site||'Metadata'];
  return result;
 }
};
if(typeof module!=='undefined')module.exports=CatalogMetadata;

(()=>{
const q=(s,r=document)=>r.querySelector(s),qa=(s,r=document)=>[...r.querySelectorAll(s)];
const menu=q('[data-menu]'),nav=q('[data-nav]');
if(menu&&nav)menu.addEventListener('click',()=>nav.classList.toggle('open'));
qa('a[href^="https://maps.apple.com"]').forEach(a=>a.remove());
qa('[data-checklist] .check-item span').forEach(s=>{if(s.textContent.includes('Google／Apple Maps'))s.textContent=s.textContent.replace('Google／Apple Maps','Google Maps')});
qa('[data-share]').forEach(b=>b.addEventListener('click',async()=>{const d={title:document.title,text:'2026 TOYOTA 英國8天6夜旅遊書',url:location.href};try{if(navigator.share)await navigator.share(d);else{await navigator.clipboard.writeText(location.href);b.textContent='已複製';setTimeout(()=>b.textContent='分享',1500)}}catch(e){}}));
qa('[data-copy]').forEach(b=>b.addEventListener('click',async()=>{const el=q(b.dataset.copy);if(!el)return;try{await navigator.clipboard.writeText(el.innerText);b.textContent='已複製';setTimeout(()=>b.textContent='複製英文過敏說明',1600)}catch(e){}}));

const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const dayMatch=location.pathname.match(/day-(\d+)\.html$/),dayNumber=dayMatch?Number(dayMatch[1]):0;

function simplifyDayPage(){
 if(dayNumber<2||dayNumber>7)return;
 document.body.classList.add('shopping-focus');
 const content=q('.content-section');if(!content)return;
 const routeButton=[...content.children].find(el=>el.matches?.('a.primary-btn')&&/Google Maps|地圖路線/.test(el.textContent||''));
 if(routeButton)routeButton.remove();
 const mapCard=q('.map-card',content);if(mapCard)mapCard.remove();
}
simplifyDayPage();

async function initAttractions(){
 if(dayNumber<2||dayNumber>7||q('.attraction-guide'))return;
 if(!q('link[data-attraction-css]')){const link=document.createElement('link');link.rel='stylesheet';link.href='assets/attractions.css?v=clean-heading-20260731-1';link.dataset.attractionCss='';document.head.appendChild(link)}
 const content=q('.content-section');if(!content)return;
 try{
  const file=dayNumber<=4?'assets/attractions-2-4.json':'assets/attractions-5-7.json';
  const res=await fetch(file+'?v=clean-heading-20260731-1',{cache:'no-store'});if(!res.ok)throw new Error('attraction data');
  const data=await res.json(),items=data[String(dayNumber)];if(!items?.length)return;
  const cards=items.map((x,i)=>`<article class="attraction-card"><figure class="attraction-media"><img src="${x.photo}" alt="${esc(x.name)}景點照片" loading="${i===0?'eager':'lazy'}" fetchpriority="${i===0?'high':'auto'}" decoding="async" referrerpolicy="no-referrer"><figcaption><a target="_blank" rel="noopener" href="${x.source}">照片：${esc(x.author)}</a>・<a target="_blank" rel="license noopener" href="${x.licenseUrl}">${esc(x.license)}</a></figcaption></figure><div class="attraction-body"><div class="attraction-head"><span class="spot-no">${String(i+1).padStart(2,'0')}</span><h3>${esc(x.name)}</h3></div><p class="spot-summary"><b>景點簡介：</b>${esc(x.subtitle)}</p><div class="tip-columns"><section class="tip-box nearby"><h4>周遭還能逛</h4><ul>${x.nearby.map(v=>`<li>${esc(v)}</li>`).join('')}</ul></section><section class="tip-box buy"><h4>推薦買什麼</h4><ul>${x.souvenirs.map(v=>`<li>${esc(v)}</li>`).join('')}</ul></section></div><p class="spot-tip"><b>時間有限：</b>${esc(x.tip)}</p></div></article>`).join('');
  const section=document.createElement('section');
  section.className='attraction-guide';section.id='attraction-guide';
  section.innerHTML=`<div class="section-heading attraction-heading"><div><span class="eyebrow">景點簡介・附近逛街・紀念品</span></div></div><div class="attraction-grid">${cards}</div><p class="attraction-note">店家營業時間、庫存與團體自由時間可能異動，實際以領隊集合時間及現場公告為準。</p>`;
  content.append(section);
  qa('.attraction-media img',section).forEach(img=>img.addEventListener('error',()=>{const media=img.closest('.attraction-media');if(media)media.classList.add('image-failed');img.remove()}));
 }catch(e){console.warn('景點介紹與周邊購物資訊暫時無法載入',e)}
}
initAttractions();

function initMaps(){qa('.js-map').forEach(el=>{const raw=q('.map-data',el);if(!raw)return;let cfg;try{cfg=JSON.parse(raw.textContent)}catch(e){el.innerHTML='<div class="map-loading">地圖資料無法讀取</div>';return}if(!window.L){el.innerHTML='<div class="map-loading">互動地圖未載入，請使用下方 Google Maps 定位</div>';return}el.innerHTML='';const map=L.map(el,{scrollWheelZoom:false,worldCopyJump:true});L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap contributors'}).addTo(map);const bounds=[];cfg.points.forEach(p=>{const icon=L.divIcon({className:'leaflet-div-icon',html:`<div class="map-pin">${p.num||''}</div>`,iconSize:[31,31],iconAnchor:[15,15]});const m=L.marker([p.lat,p.lon],{icon}).addTo(map);m.bindPopup(`<b>${p.name}</b><small>${p.sub||''}</small><a target="_blank" rel="noopener" href="${p.google}">開啟 Google Maps</a>`);bounds.push([p.lat,p.lon])});(cfg.lines||[]).forEach(line=>{const opts={color:line.color||'#b31b34',weight:line.width||4,opacity:.82};if(line.dash)opts.dashArray=line.dash;L.polyline(line.coords,opts).addTo(map);line.coords.forEach(c=>bounds.push(c))});if(bounds.length)map.fitBounds(bounds,{padding:[28,28],maxZoom:cfg.world?3:13});setTimeout(()=>map.invalidateSize(),120)});}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initMaps);else initMaps();

const list=q('[data-checklist]');if(list){const key='uk-trip-checks-v3',boxes=qa('[data-check]',list),bar=q('#progressBar'),txt=q('#progressText');let state={};try{state=JSON.parse(localStorage.getItem(key)||'{}')}catch(e){};boxes.forEach(b=>{b.checked=!!state[b.dataset.check];b.addEventListener('change',save)});function save(){state={};boxes.forEach(b=>state[b.dataset.check]=b.checked);localStorage.setItem(key,JSON.stringify(state));render()}function render(){const n=boxes.filter(b=>b.checked).length;txt.textContent=`${n} / ${boxes.length}`;bar.style.width=`${n/boxes.length*100}%`}q('[data-check-all]')?.addEventListener('click',()=>{boxes.forEach(b=>b.checked=true);save()});q('[data-reset-checks]')?.addEventListener('click',()=>{boxes.forEach(b=>b.checked=false);save()});render()}
})();

(()=>{
const q=(s,r=document)=>r.querySelector(s),qa=(s,r=document)=>[...r.querySelectorAll(s)];
const menu=q('[data-menu]'),nav=q('[data-nav]');
if(menu&&nav)menu.addEventListener('click',()=>nav.classList.toggle('open'));
qa('[data-share]').forEach(b=>b.addEventListener('click',async()=>{const d={title:document.title,text:'2026 TOYOTA 英國8天6夜旅遊書',url:location.href};try{if(navigator.share)await navigator.share(d);else{await navigator.clipboard.writeText(location.href);b.textContent='已複製';setTimeout(()=>b.textContent='分享',1500)}}catch(e){}}));
qa('[data-copy]').forEach(b=>b.addEventListener('click',async()=>{const el=q(b.dataset.copy);if(!el)return;try{await navigator.clipboard.writeText(el.innerText);b.textContent='已複製';setTimeout(()=>b.textContent='複製英文過敏說明',1600)}catch(e){}}));

const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const pathDay=location.pathname.match(/day-(\d+)\.html$/);
const pageParam=new URLSearchParams(location.search).get('page')||'';
const paramDay=pageParam.match(/^day-(\d+)$/);
const dayNumber=pathDay?Number(pathDay[1]):paramDay?Number(paramDay[1]):0;

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
 if(!q('link[data-attraction-css]')){const link=document.createElement('link');link.rel='stylesheet';link.href='assets/attractions.css?v=restore-20260801-1';link.dataset.attractionCss='';document.head.appendChild(link)}
 const content=q('.content-section');if(!content)return;
 try{
  const file=dayNumber<=4?'assets/attractions-2-4.json':'assets/attractions-5-7.json';
  const res=await fetch(file+'?v=restore-20260801-1',{cache:'no-store'});if(!res.ok)throw new Error('attraction data');
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

function initMaps(){qa('.js-map').forEach(el=>{const raw=q('.map-data',el);if(!raw)return;let cfg;try{cfg=JSON.parse(raw.textContent)}catch(e){el.innerHTML='<div class="map-loading">地圖資料無法讀取</div>';return}if(!window.L){el.innerHTML='<div class="map-loading">互動地圖未載入，請使用下方 Google／Apple 定位</div>';return}el.innerHTML='';const map=L.map(el,{scrollWheelZoom:false,worldCopyJump:true});L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:19,attribution:'© OpenStreetMap contributors'}).addTo(map);const bounds=[];cfg.points.forEach(p=>{const icon=L.divIcon({className:'leaflet-div-icon',html:`<div class="map-pin">${p.num||''}</div>`,iconSize:[31,31],iconAnchor:[15,15]});const m=L.marker([p.lat,p.lon],{icon}).addTo(map);m.bindPopup(`<b>${p.name}</b><small>${p.sub||''}</small><a target="_blank" rel="noopener" href="${p.google}">Google</a><a target="_blank" rel="noopener" href="${p.apple}">Apple</a>`);bounds.push([p.lat,p.lon])});(cfg.lines||[]).forEach(line=>{const opts={color:line.color||'#b31b34',weight:line.width||4,opacity:.82};if(line.dash)opts.dashArray=line.dash;L.polyline(line.coords,opts).addTo(map);line.coords.forEach(c=>bounds.push(c))});if(bounds.length)map.fitBounds(bounds,{padding:[28,28],maxZoom:cfg.world?3:13});setTimeout(()=>map.invalidateSize(),120)});}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initMaps);else initMaps();

const list=q('[data-checklist]');if(list){const key='uk-trip-checks-v3',boxes=qa('[data-check]',list),bar=q('#progressBar'),txt=q('#progressText');let state={};try{state=JSON.parse(localStorage.getItem(key)||'{}')}catch(e){};boxes.forEach(b=>{b.checked=!!state[b.dataset.check];b.addEventListener('change',save)});function save(){state={};boxes.forEach(b=>state[b.dataset.check]=b.checked);localStorage.setItem(key,JSON.stringify(state));render()}function render(){const n=boxes.filter(b=>b.checked).length;txt.textContent=`${n} / ${boxes.length}`;bar.style.width=`${n/boxes.length*100}%`}q('[data-check-all]')?.addEventListener('click',()=>{boxes.forEach(b=>b.checked=true);save()});q('[data-reset-checks]')?.addEventListener('click',()=>{boxes.forEach(b=>b.checked=false);save()});render()}
})();

;(()=>{
if(document.getElementById('nearbyExploreButton'))return;
const E=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const labels={shop:'好逛的店',food:'吃喝／飲料',gift:'紀念品'};
const typeName=t=>({restaurant:'餐廳',cafe:'咖啡店',fast_food:'速食',pub:'酒吧',bar:'酒吧',gift:'禮品店',souvenir:'紀念品店',department_store:'百貨',mall:'購物中心',supermarket:'超市',clothes:'服飾',shoes:'鞋店',books:'書店',jewelry:'珠寶',beauty:'美妝',chemist:'藥妝',convenience:'便利商店',bakery:'烘焙店',beverages:'飲料店',coffee:'咖啡專賣店',tea:'茶飲店',confectionery:'糖果點心店',deli:'熟食店',ice_cream:'冰品店',pastry:'甜點店',food:'食品店',food_court:'美食街',juice_bar:'果汁飲料店',biergarten:'啤酒花園'}[t]||'商店');
const distance=(a,b,c,d)=>{const R=6371000,p=Math.PI/180,x=(c-a)*p,y=(d-b)*p*Math.cos((a+c)*p/2);return Math.round(Math.sqrt(x*x+y*y)*R)};
let radius=800,category='shop',position=null,places=[],lastQuery=null,busy=false;
const button=document.createElement('button');button.id='nearbyExploreButton';button.className='nearby-fab';button.type='button';button.textContent='📍 附近探索';button.setAttribute('aria-controls','nearbyExplorePanel');button.setAttribute('aria-expanded','false');
const panel=document.createElement('aside');panel.id='nearbyExplorePanel';panel.className='nearby-panel';panel.setAttribute('aria-hidden','true');panel.innerHTML='<div class="nearby-head"><div><small>點擊更新位置</small><h2>📍 附近探索</h2></div><button class="nearby-close" type="button" aria-label="關閉">×</button></div><div class="nearby-body"><p class="nearby-street" id="nearbyStreet">按「更新我的位置」查看目前街道附近。</p><div class="nearby-actions"><button id="nearbyLocate" type="button">更新我的位置</button></div><fieldset class="nearby-radii"><legend>搜尋距離</legend><button type="button" data-radius="300">300m</button><button type="button" data-radius="800" class="active">800m</button><button type="button" data-radius="1500">1.5km</button></fieldset><div class="nearby-tabs" role="tablist"><button type="button" data-category="shop" class="active">好逛的店</button><button type="button" data-category="food">吃喝／飲料</button><button type="button" data-category="gift">紀念品</button></div><div id="nearbyStatus" class="nearby-status">定位資料只用於本次搜尋，網站不會儲存。</div><div id="nearbyResults" class="nearby-results"></div><p class="nearby-privacy">GPS 由瀏覽器取得；附近店家查詢會將座標送至 OpenStreetMap 公共服務。</p></div>';
document.body.append(button,panel);
const $=s=>panel.querySelector(s),$$=s=>[...panel.querySelectorAll(s)],status=$('#nearbyStatus'),results=$('#nearbyResults'),street=$('#nearbyStreet');
const open=()=>{panel.classList.add('open');panel.setAttribute('aria-hidden','false');button.setAttribute('aria-expanded','true')};
const close=()=>{panel.classList.remove('open');panel.setAttribute('aria-hidden','true');button.setAttribute('aria-expanded','false')};
button.addEventListener('click',open);$('.nearby-close').addEventListener('click',close);
const coordsOf=e=>e.type==='node'?[e.lat,e.lon]:[e.center?.lat,e.center?.lon];
const classify=t=>{if(t.shop==='gift'||t.shop==='souvenir'||t.shop==='arts'||t.shop==='craft')return'gift';if((t.amenity&&['restaurant','cafe','fast_food','pub','bar','food_court','ice_cream','juice_bar','biergarten'].includes(t.amenity))||['bakery','beverages','coffee','tea','confectionery','deli','ice_cream','pastry','food'].includes(t.shop))return'food';return'shop'};
const addr=t=>[t['addr:housenumber'],t['addr:street'],t['addr:suburb'],t['addr:city']].filter(Boolean).join(' ')||t['contact:address']||'地址請開啟地圖查看';
function render(){
 const list=places.filter(x=>x.category===category).slice(0,40);
 if(!list.length){results.innerHTML='<div class="nearby-empty">這個距離內暫時找不到符合分類的店家，可切換距離或分類。</div>';return}
 results.innerHTML=list.map(x=>{const search=[x.name,x.address!=='地址請開啟地圖查看'?x.address:''].filter(Boolean).join(' '),q=encodeURIComponent(search),g='https://www.google.com/maps/search/?api=1&query='+q,a='https://maps.apple.com/?q='+q;return '<article class="nearby-card"><div class="nearby-card-head"><div><h3>'+E(x.name)+'</h3><span>'+E(x.type)+'</span></div><b>'+ (x.distance<1000?x.distance+'m':(x.distance/1000).toFixed(1)+'km') +'</b></div><p>'+E(x.address)+'</p><div><a target="_blank" rel="noopener" href="'+g+'">Google Maps</a><a target="_blank" rel="noopener" href="'+a+'">Apple Maps</a></div></article>'}).join('');
}
async function reverse(lat,lon){
 try{const r=await fetch('https://nominatim.openstreetmap.org/reverse?format=jsonv2&zoom=18&addressdetails=1&lat='+lat+'&lon='+lon,{headers:{'Accept-Language':'zh-TW,zh,en'}});if(!r.ok)throw 0;const d=await r.json(),a=d.address||{},name=a.road||a.pedestrian||a.footway||a.neighbourhood||a.suburb||d.display_name;street.textContent=name?'目前在 '+name+' 附近':'已取得目前位置';}catch(e){street.textContent='已取得目前位置（街道名稱暫時無法載入）'}
}
async function query(lat,lon){
 if(busy)return;busy=true;status.textContent='正在搜尋 '+radius+'m 內的店家…';results.innerHTML='<div class="nearby-loading">搜尋附近地點中…</div>';
 const q='[out:json][timeout:25];(nwr(around:'+radius+','+lat+','+lon+')[shop];nwr(around:'+radius+','+lat+','+lon+')[amenity~"^(restaurant|cafe|fast_food|pub|bar|food_court|ice_cream|juice_bar|biergarten)$"];);out center tags;';
 try{const r=await fetch('https://overpass-api.de/api/interpreter',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'},body:'data='+encodeURIComponent(q)});if(!r.ok)throw new Error();const d=await r.json(),seen=new Set();places=(d.elements||[]).map(e=>{const c=coordsOf(e),t=e.tags||{},name=t.name||t.brand;if(!c||!name)return null;const key=name+'|'+c[0].toFixed(5)+'|'+c[1].toFixed(5);if(seen.has(key))return null;seen.add(key);const raw=t.shop||t.amenity;return{name,lat:c[0],lon:c[1],category:classify(t),type:typeName(raw),address:addr(t),distance:distance(lat,lon,c[0],c[1])}}).filter(Boolean).sort((a,b)=>a.distance-b.distance);lastQuery={lat,lon};status.textContent='找到 '+places.length+' 個附近地點（'+radius+'m）';render()}catch(e){status.textContent='公共地圖服務目前忙碌，請稍後再試。';results.innerHTML='<div class="nearby-empty">無法載入附近店家；你的定位仍未被本站儲存。</div>'}finally{busy=false}
}
function found(p){
 position={lat:p.coords.latitude,lon:p.coords.longitude};status.textContent='已定位，正在更新附近資訊…';reverse(position.lat,position.lon);query(position.lat,position.lon);
}
function locate(){if(!navigator.geolocation){status.textContent='此瀏覽器不支援定位。';return}status.textContent='正在等待位置授權…';navigator.geolocation.getCurrentPosition(p=>found(p),e=>{status.textContent=e.code===1?'未允許定位；請在瀏覽器網站設定中開啟位置權限。':'暫時無法取得位置，請到戶外或稍後重試。'},{enableHighAccuracy:true,timeout:15000,maximumAge:0})}
$('#nearbyLocate').addEventListener('click',locate);
$$('[data-radius]').forEach(b=>b.addEventListener('click',()=>{$$('[data-radius]').forEach(x=>x.classList.remove('active'));b.classList.add('active');radius=Number(b.dataset.radius);if(position)query(position.lat,position.lon)}));
$$('[data-category]').forEach(b=>b.addEventListener('click',()=>{$$('[data-category]').forEach(x=>x.classList.remove('active'));b.classList.add('active');category=b.dataset.category;render()}));
})();
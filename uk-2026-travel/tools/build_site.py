#!/usr/bin/env python3
"""Build the static field guide. Runtime never fetches the source JSON files."""
import json
from pathlib import Path
from html import escape as esc
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
I = json.loads((ROOT / 'assets/itinerary.json').read_text())
G = json.loads((ROOT / 'assets/guide.json').read_text())
VER = I['version']
EST = '推估，非旅行社正式時間'

def e(v): return esc(str(v), quote=True)
def maps(q, label='Google Maps'):
    url='https://www.google.com/maps/search/?'+urlencode({'api':1,'query':q})
    return f'<a class="map-link" href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(label)} <span aria-hidden="true">↗</span></a>'
def sources(keys):
    return '<div class="sources"><span>官方查核 2026/09/05</span>'+''.join(f'<a href="{e(G["sources"][k]["url"])}" target="_blank" rel="noopener noreferrer">{e(G["sources"][k]["title"])} ↗</a>' for k in dict.fromkeys(keys))+'</div>' if keys else ''
def ul(items,cls=''):
    return '<ul'+(f' class="{cls}"' if cls else '')+'>'+''.join('<li>'+e(x)+'</li>' for x in items)+'</ul>'
def write(name,title,body,active='',day=0):
    nav=[('index.html','首頁','home'),('guide.html','攻略','guide'),('hotels.html','飯店','hotels'),('allergy.html','飲食卡','allergy'),('checklist.html','清單','checklist')]
    html=f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><meta name="theme-color" content="#132b42"><meta name="description" content="IAN 英國 8天6夜實戰攻略：每日正式行程、每段車程、自由時間試算與官方查核的景點提醒。"><title>{e(title)}｜IAN 英國實戰攻略</title><link rel="stylesheet" href="assets/styles.css?v={VER}"><script src="assets/app.js?v={VER}" defer></script></head>
<body data-day="{day}" data-trip-start="{I['days'][0]['date']}" data-trip-end="{I['days'][-1]['date']}" data-trip-days="{len(I['days'])}" data-first-free="{min(d['n'] for d in I['days'] if d['free'])}" data-last-free="{max(d['n'] for d in I['days'] if d['free'])}"><a class="skip" href="#main">跳到內容</a><header class="site-header"><a class="brand" href="index.html"><span class="brand-icon" aria-hidden="true">I</span><span>IAN <small>UK FIELD GUIDE</small></span></a><a class="header-date" href="index.html#days">08—15 SEP 2026</a></header>
<main id="main">{body}</main><footer><p>固定行程依 9/04 正式手冊；實際集合、票券與調整以領隊通知為準。</p><p>攻略查核 2026/09/05 · 路程與自由時間皆為保守推估。</p><a href="guide.html#uncertain">查看待確認事項</a><span class="build-version">{VER}</span></footer><nav class="bottom-nav" aria-label="主要導覽">{''.join(f'<a href="{url}"'+(' aria-current="page"' if key==active else '')+f'>{label}</a>' for url,label,key in nav)}</nav></body></html>'''
    (ROOT/name).write_text(html.replace('><', '>\n<')+'\n')
def page_intro(kicker,title,desc):
    return f'<div class="page-intro"><p class="eyebrow">{e(kicker)}</p><h1>{e(title)}</h1><p class="lead">{e(desc)}</p></div>'
def image_block():
    return '<figure class="place-photo"><img src="assets/images/great-court.webp" width="956" height="720" loading="lazy" decoding="async" alt="大英博物館 Great Court，玻璃屋頂環繞圓形閱覽室"><figcaption>Great Court · D6 留五分鐘抬頭看。照片：Andy Li，CC0，<a href="https://commons.wikimedia.org/wiki/File:Great_Court,_British_Museum_2024-12-20.jpg" target="_blank" rel="noopener noreferrer">來源</a></figcaption></figure>'
def day_tiles():
    return '<div class="day-grid">'+''.join(f'<a class="day-tile" href="day-{d["n"]}.html"><span class="day-number">D{d["n"]}</span><span><small>09/{int(d["date"][-2:]):02d}・週{d["weekday"]}</small><strong>{e(d["title"])}</strong><span>{e(d["route"])}</span></span><b aria-hidden="true">→</b></a>' for d in I['days'])+'</div>'
def option_html(id, hotel=None):
    o=I['options'][id]
    runtime={k:v for k,v in o.items() if k in ['out','visit','back','steps','departBy','departures','checkin','caution','rest']}
    minimum=o['out']+o['visit']+o['back']+o.get('checkin',0)
    transport=o.get('transport','步行')
    places=o['places'] or ([hotel['name']+' '+hotel['address']] if hotel else [])
    return f'''<article class="option-card" data-option="{e(json.dumps(runtime,ensure_ascii=False))}"><div class="option-heading"><h3>{e(o['name'])}</h3><span class="verdict pending">待計算</span></div><p class="minimum">最低需要 <strong>{minimum} 分</strong> <span>＋另留集合緩衝</span></p><p>{e(o['content'])}</p><p class="time-breakdown">{e(transport)}去程 {o['out']} 分 ＋ 活動 {o['visit']} 分 ＋ 回程 {o['back']} 分{f' ＋ 提早報到 {o["checkin"]} 分' if o.get('checkin') else ''}；另加設定的 <span class="buffer-label">—</span> 分緩衝。</p><p class="option-reason">請輸入時間後重新計算。</p>{'<p class="micro-note">'+e(o['caution'])+'</p>' if o.get('caution') else ''}<div class="map-row">{''.join(maps(q,'Google Maps'+('・'+str(i+1) if len(places)>1 else '')) for i,q in enumerate(places))}</div></article>'''
def free_section(d):
    if not d['free']: return ''
    modes=[I['freeModes'][k] for k in d['free']]
    tabs=''.join(f'<button type="button" role="tab" id="tab-{idx}" aria-selected="{str(idx==0).lower()}" aria-controls="free-panel" tabindex="{0 if idx==0 else -1}" data-mode="{idx}" data-kind="{["day","night","airport"][idx]}">{e(m["label"])}</button>' for idx,m in enumerate(modes))
    infos=''
    options=''
    for idx,m in enumerate(modes):
        info_data={k:m[k] for k in ['start','end','buffer','disabled']}
        time_label = ('今晚搭機返台' if '夜間' in m['label'] else '未安排自由活動') if m['disabled'] else m['start']+' — '+m['end']
        infos+=f'<div class="free-info" data-mode-info="{idx}" data-window="{e(json.dumps(info_data))}"'+(' hidden' if idx else '')+f'><p class="estimate-label">{EST}</p><p class="window-time">{e(time_label)}</p><p><strong>地點</strong>｜{e(m["place"])}</p><p><strong>推估依據</strong>｜{e(m["basis"])}</p>{sources(m["sources"])}</div>'
        options+=f'<div class="options-list" data-mode-options="{idx}"'+(' hidden' if idx else '')+'>'+''.join(option_html(k, next((h for h in I['hotels'] if h['id']==d['hotel']),None)) for k in m['options'])+'</div>'
    return f'''<section class="free-section" id="free-time" data-date="{d['date']}"><div class="section-heading"><p class="eyebrow">LIVE TIME CHECK</p><h2>今天還有多少自由時間？</h2><p>集合時間一公布，改下面的時間就能重算。</p></div><div class="tabs" role="tablist" aria-label="自由時間時段">{tabs}</div><div role="tabpanel" id="free-panel" aria-labelledby="tab-0">{infos}<noscript><p class="warning">計算器需要 JavaScript；所有行程與攻略仍可閱讀。</p></noscript><form class="time-form"><p class="clock-note">試算模式：所有欄位使用英國當地時間。</p><div class="time-fields"><div><label for="now-time">現在時間</label><input id="now-time" name="now" type="time" required value="{modes[0]['start']}"><label class="sr-only" for="now-day">現在日期</label><select id="now-day" name="nowDay"><option value="0">當日</option><option value="1">翌日（過午夜）</option></select></div><div><label for="end-time">集合／回飯店時間</label><input id="end-time" name="end" type="time" required value="{modes[0]['end']}"><label class="sr-only" for="end-day">結束日期</label><select id="end-day" name="endDay"><option value="0">當日</option><option value="1">翌日（過午夜）</option></select></div></div><label for="buffer">額外預留集合緩衝（分鐘）</label><input id="buffer" name="buffer" type="number" inputmode="numeric" min="0" max="120" step="1" required value="{modes[0]['buffer']}"><p class="field-hint">各選項已包含走／搭車回程；這裡再留找車、集合與交通誤差。跨午夜請將結束日期選「翌日」，不自動多算一天。</p><div class="form-buttons"><button class="button primary" type="submit">重新計算</button><button class="button secondary" type="button" id="use-now">帶入英國現在時間</button></div></form><div class="time-result" role="status" aria-live="polite"><span class="result-label">剩餘可用時間</span><strong class="result-number">—</strong><span class="result-detail">請重新計算</span></div><p class="result-legend">✓ 可以／值得去　△ 很趕／需確認　✕ 不建議／來不及</p><p class="field-hint">時間足夠不代表店家或票券有空位；車程是估值，出發前比對即時路況。離團前須先確認領隊允許。</p>{options}</div></section>'''
def guide_html(g):
    body='<div class="guide-content">'
    body+='<section><h3>1｜3 個必看</h3>'+ul(g['must'],'must-see')+'</section>'
    body+='<section><h3>2｜你去這一天的情報</h3>'+ul(g['info'])+'</section>'
    body+='<section><h3>3｜時間有限怎麼逛</h3><dl class="quick-routes">'+''.join(f'<div><dt>{e(t)}</dt><dd>{e(x)}</dd></div>' for t,x in g['routes'])+'</dl><p class="micro-note">此區為攻略建議，並非旅行社公布的停留時間。</p></section>'
    body+='<section><h3>4｜拍照</h3>'+ul(g['photo'])+'</section>'
    body+='<section><h3>5｜真正值得買</h3>'+''.join(f'<div class="buy-item"><strong>{e(p)}</strong><span>{e(s)}</span><p>{e(w)}</p></div>' for p,s,w in g['buy'])+'</section>'
    body+='<section><h3>6｜踩雷提醒</h3>'+ul(g['risks'])+'</section>'
    body+=maps(g['map'],'Google Maps'+('・河岸參考，非登船點' if g['id']=='thames' else ''))+sources(g['sources'])+'</div>'
    return f'<details class="guide-card" id="{g["id"]}"><summary><span class="guide-title">{e(g["title"])}</span><span class="guide-tag">{e(g["tag"])}</span><span class="expand-text">展開 6 區攻略 <span aria-hidden="true">＋</span></span></summary>{body}</details>'
def hotel_card(h):
    return f'<article class="hotel-card"><p class="eyebrow">{e(h["nights"])}</p><h2>{e(h["name"])}</h2><p>{e(h["address"])}</p><p>{e(h["note"])}</p><div class="map-row">{maps(h["name"]+" "+h["address"])}<a class="button secondary" href="hotel-{h["id"]}.html">飯店實戰資訊 →</a></div></article>'

home=page_intro('IAN’S UK JOURNEY','英國 8天6夜','09/08–09/15 · 2026 · 英國當地時間')
home+='<p class="hero-note">把集合前的每一分鐘，留給真正想看的地方。</p><div class="quick-actions"><a class="quick-action" data-today="schedule" href="day-1.html"><span>01</span><strong>今天行程</strong><small>固定行程・每段車程 →</small></a><a class="quick-action" data-today="free" href="day-2.html?mode=day#free-time"><span>02</span><strong>自由時間</strong><small>輸入集合時間，立即重算 →</small></a><a class="quick-action" data-today="night" href="day-2.html?mode=night#free-time"><span>03</span><strong>晚餐後去哪</strong><small>算上去程、回程與關門時間 →</small></a><a class="quick-action" href="checklist.html"><span>04</span><strong>出發清單</strong><small>隨身必帶・飲食卡 →</small></a></div><p class="today-note">按鈕依英國日期選擇行程；旅行前先顯示 D1 與 D2 試算。</p>'
home+='<section class="attention"><p class="eyebrow">出門前先知道</p><h2>三個不能照舊攻略走的地方</h2>'+''.join(f'<a href="day-{g["day"]}.html#{g["id"]}">D{g["day"]}｜{e(g["tag"])} <span>→</span></a>' for id in G['highlights'] for g in G['guides'] if g['id']==id)+'</section>'
home+='<section id="days"><div class="section-heading"><p class="eyebrow">EIGHT DAYS, READY TO GO</p><h2>選一天，直接出發</h2></div>'+day_tiles()+'</section>'+image_block()
write('index.html','英國 8天6夜',home,'home')
for d in I['days']:
    n=d['n']
    body=page_intro(f'D{n} · 09/{int(d["date"][-2:]):02d} 週{d["weekday"]}',d['title'],d['route'])
    body+='<div class="day-nav" aria-label="選擇日期">'+''.join(f'<a href="day-{j}.html"'+(' aria-current="page"' if j==n else '')+f'>D{j}</a>' for j in range(1,9))+'</div>'
    body+='<div class="day-alert">'+ul(d['alerts'])+'</div><nav class="jump-links" aria-label="本日章節"><a href="#schedule">正式行程</a><a href="#coach">每段車程</a>'+('<a href="#free-time">自由時間</a>' if d['free'] else '')+('<a href="#field-guide">景點攻略</a>' if any(g['day']==n for g in G['guides']) else '')+'</nav>'
    body+='<section id="schedule"><div class="section-heading"><p class="eyebrow">OFFICIAL BASELINE · 9/04 手冊</p><h2>今天旅行社固定去哪裡</h2></div><ol class="timeline">'
    for s in d['stops']:
        body+='<li><strong>'+e(s['name'])+'</strong>'+('<p>'+e(s['note'])+'</p>' if s['note'] else '')+(f'<a href="#{s["guide"]}">看實戰攻略 →</a>' if s['guide'] else '')+'</li>'
    body+='</ol></section><section id="coach"><div class="section-heading"><p class="eyebrow">EACH TRANSFER</p><h2>每一次上車的 A → B</h2><p>保守預估，非旅行社正式行車時間；不含集合、休息站與臨時塞車。</p></div>'
    for l in d['legs']:
        body+=f'<article class="coach-leg'+(' walking' if l['walk'] else '')+f'"><span class="transport-label">{"步行" if l["walk"] else "遊覽車"}</span><h3>{e(l["a"])} <span aria-hidden="true">→</span> {e(l["b"])}</h3><strong>{e(l["time"])}</strong>'+('<p>'+e(l['note'])+'</p>' if l['note'] else '')+'</article>'
    if not d['legs']: body+='<p class="empty-note">今天沒有安排遊覽車接駁。</p>'
    body+='</section>'+free_section(d)
    guides=[g for g in G['guides'] if g['day']==n]
    if guides: body+='<section id="field-guide"><div class="section-heading"><p class="eyebrow">BEYOND THE HANDBOOK</p><h2>手冊沒有的實戰攻略</h2><p>點開景點，查看必看、日期情報、短線、拍照、買什麼與踩雷提醒。</p></div>'+''.join(guide_html(g) for g in guides)+'</section>'
    if n==6: body+=image_block()
    if d['hotel']: body+='<section class="tonight"><p class="eyebrow">TONIGHT</p>'+hotel_card(next(h for h in I['hotels'] if h['id']==d['hotel']))+'</section>'
    body+='<div class="page-turn">'+(f'<a class="button secondary" href="day-{n-1}.html">← D{n-1}</a>' if n>1 else '<a class="button secondary" href="index.html">← 首頁</a>')+(f'<a class="button primary" href="day-{n+1}.html">D{n+1} →</a>' if n<8 else '<a class="button primary" href="checklist.html">返家檢查 →</a>')+'</div>'
    write(f'day-{n}.html',f'D{n} {d["title"]}',body,day=n)
body=page_intro('SIX NIGHTS · THREE HOTELS','飯店與晚餐後','先確定出發點，再決定今晚值不值得出門。')+''.join(hotel_card(h) for h in I['hotels'])
write('hotels.html','飯店',body,'hotels')
for h in I['hotels']:
    body=page_intro(h['nights'],h['name'],h['address'])+f'<div class="contact-card">{maps(h["name"]+" "+h["address"])}<a class="button secondary" href="tel:{h["phone"].replace(" ","")}">致電飯店 {e(h["phone"])}</a></div><div class="day-alert"><p>{e(h["note"])}</p></div><section><h2>今晚怎麼安排</h2><p>{e(h["evening"])}</p>'
    ns=[d['n'] for d in I['days'] if d['hotel']==h['id']]
    body+='<div class="map-row">'+''.join(f'<a class="button primary" href="day-{n}.html?mode=night#free-time">D{n} 晚餐後試算 →</a>' for n in ns if n>1)+'</div></section><section><h2>出門前用這四步</h2>'+ul(I['hotelTips'])+'</section>'
    if h['id']=='coventry': body+=sources(['tesco','tenpin'])
    if h['id']=='park-royal': body+=sources(['tfl','nightbus'])
    body+='<p class="micro-note">飯店名稱、地址與電話來源：20260908英國(0904).pdf。</p><a class="button secondary" href="hotels.html">← 所有飯店</a>'
    write('hotel-'+h['id']+'.html',h['name'],body,'hotels')
body=page_intro('QUICK REFERENCE','把時間用在值得的地方','攻略依 2026/09/05 官方資料整理；短線與購物取捨為網站建議。')
for d in I['days']:
    gs=[g for g in G['guides'] if g['day']==d['n']]
    if gs:
        body+=f'<section><h2>D{d["n"]} · 09/{int(d["date"][-2:]):02d}</h2><div class="guide-index">'+''.join(f'<a href="day-{g["day"]}.html#{g["id"]}"><strong>{e(g["title"])}</strong><span>{e(g["tag"])} →</span></a>' for g in gs)+'</div></section>'
body+='<section id="uncertain" class="attention"><h2>還需要領隊／現場確認</h2>'+ul(G['uncertain'])+'</section><section><h2>自由時間預估總覽</h2><p class="estimate-label">'+EST+'</p><div class="window-overview">'
for d in I['days']:
    for key in d['free']:
        m=I['freeModes'][key]
        if not m['disabled']:
            kind='airport' if key=='airport' else 'night' if '夜間' in m['label'] else 'day'
            body+=f'<a href="day-{d["n"]}.html?mode={kind}#free-time"><strong>D{d["n"]}・{e(m["label"])}</strong><span>{m["start"]}–{m["end"]}</span><small>{e(m["place"])}</small></a>'
body+='</div></section><section><h2>資訊怎麼分辨</h2>'+ul(G['method'])+'</section>'
write('guide.html','實戰攻略索引',body,'guide')
body=page_intro('SHOW THIS TO STAFF','飲食與過敏溝通卡','保留既有需求：不吃牛肉、牛奶過敏。點一下可複製英文給餐廳。')
card=I['dietCard']
body+='<article class="allergy-card"><h2 lang="en">MILK ALLERGY<br>NO BEEF</h2><p id="allergy-text" lang="en">'+e(card)+'</p><button class="button primary" type="button" id="copy-allergy">複製英文餐卡</button><p id="copy-result" role="status"></p></article><section><h2>這趟在哪裡先出示</h2>'+ul(I['dietTips'])+'</section><p class="micro-note">你可以直接放大這張卡給工作人員看，沒有網路仍能使用已載入頁面。</p>'
write('allergy.html','飲食與過敏卡',body,'allergy')
body=page_intro('BEFORE YOU GO','出發清單','勾選只記在這台裝置；換手機、清除瀏覽資料或無痕模式不會同步。')
body+='<p class="check-progress" role="status"><strong id="check-count">0</strong> / '+str(len(I['checklist']))+' 已完成</p><div class="check-list">'+''.join(f'<label><input type="checkbox" data-check="{e(k)}"><span>{e(t)}</span></label>' for k,t in I['checklist'])+'</div><p id="storage-note" class="field-hint"></p><a class="button primary" href="allergy.html">開啟英文飲食卡 →</a><section><h2>出發當天</h2>'+ul(I['departureTips'])+'</section>'
write('checklist.html','出發清單',body,'checklist')
write('404.html','找不到這一頁',page_intro('404','這一頁已整理到新位置','請從首頁或攻略索引選擇日期。')+'<a class="button primary" href="index.html">回到首頁 →</a>')
print(f'Built {len([p for p in ROOT.glob("*.html") if not p.name.startswith(".")])} HTML pages from itinerary.json and guide.json')

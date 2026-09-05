#!/usr/bin/env python3
"""Build readable static pages from shared travel data; app.js owns interactions."""
import json
from pathlib import Path
from html import escape as esc
from urllib.parse import urlencode
ROOT = Path(__file__).resolve().parents[1]
I = json.loads((ROOT / 'assets/itinerary.json').read_text())
G = json.loads((ROOT / 'assets/guide.json').read_text())
VER = I['version']
EST = '推估，非旅行社正式時間'
PUBLIC = 'https://monoian.github.io/shanhe-wuming-world-bible/uk-2026-travel/'

def e(v): return esc(str(v), quote=True)
def maps(q, label='Google Maps'):
    url='https://www.google.com/maps/search/?'+urlencode({'api':1,'query':q})
    return f'<a class="map-link" href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(label)} <span aria-hidden="true">↗</span></a>'
def sources(keys):
    if not keys: return ''
    return '<details class="sources"><summary>官方資料與開放資訊 <span>查核 09/05</span></summary><div>'+''.join(f'<a href="{e(G["sources"][k]["url"])}" target="_blank" rel="noopener noreferrer">{e(G["sources"][k]["title"])} ↗</a>' for k in dict.fromkeys(keys))+'</div></details>'
def ul(items,cls=''):
    return '<ul'+(f' class="{cls}"' if cls else '')+'>'+''.join('<li>'+e(x)+'</li>' for x in items)+'</ul>'
def hotel_for(d): return next((h for h in I['hotels'] if h['id']==d['hotel']),None)
def day_select(n=1,home=False):
    return '<div class="date-picker"><label for="travel-day">'+('想看哪一天？' if home else '切換日期')+'</label><select id="travel-day" '+('data-home-day' if home else 'data-day-select')+'>'+''.join(f'<option value="{d["n"]}"'+(' selected' if d['n']==n else '')+f'>09/{int(d["date"][-2:]):02d}（{d["weekday"]}）D{d["n"]}・{e(d["title"])}</option>' for d in I['days'])+'</select></div>'
def write(name,title,body,active='',day=0):
    nav=[('index.html','⌂','首頁','home',''),(f'day-{day or 1}.html','▤','行程','day',' data-today="schedule"' if not day else ''),('hotels.html','⌑','飯店','hotels',''),('guide.html','⋯','更多','guide','')]
    html=f'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><meta name="theme-color" content="#153a38"><meta name="description" content="英國 8天6夜團員隨行指南：每天去哪、集合前能去哪、飯店導航、景點必看與出發清單。"><title>{e(title)}｜英國團員隨行指南</title><link rel="stylesheet" href="assets/styles.css?v={VER}"><script src="assets/app.js?v={VER}" defer></script></head>
<body data-day="{day}" data-trip-start="{I['days'][0]['date']}" data-trip-end="{I['days'][-1]['date']}" data-trip-days="{len(I['days'])}" data-first-free="2" data-last-free="7"><a class="skip" href="#main">跳到內容</a><header class="site-header"><a class="brand" href="index.html"><span class="brand-icon" aria-hidden="true">UK</span><span>英國隨行指南<small>團員共用・2026</small></span></a><a class="header-date" href="index.html#days">8 天行程 <span aria-hidden="true">↗</span></a></header><main id="main">{body}</main><footer><p>集合時間與行程調整，以領隊通知為準。</p><p>行程依 9/04 手冊・攻略查核 09/05・IAN 整理</p><a href="guide.html#uncertain">查看待確認事項</a></footer><nav class="bottom-nav" aria-label="主要導覽">{''.join(f'<a href="{url}"'+extra+(' aria-current="page"' if key==active else '')+f'><span aria-hidden="true">{icon}</span>{label}</a>' for url,icon,label,key,extra in nav)}</nav>{guide_dialog() if any(g['day']==day for g in G['guides']) else ''}</body></html>'''
    (ROOT/name).write_text(html.replace('><','>\n<')+'\n')
def page_intro(kicker,title,desc):
    return f'<div class="page-intro"><p class="eyebrow">{e(kicker)}</p><h1 tabindex="-1">{e(title)}</h1><p class="lead">{e(desc)}</p></div>'
def image_block(day_only=False):
    return '<figure class="place-photo"'+(' data-day-only' if day_only else '')+'><img src="assets/images/great-court.webp" width="956" height="720" loading="lazy" decoding="async" alt="大英博物館 Great Court，玻璃屋頂環繞圓形閱覽室"><figcaption>大英博物館・D6 留五分鐘抬頭看<br>照片：Andy Li，CC0，<a href="https://commons.wikimedia.org/wiki/File:Great_Court,_British_Museum_2024-12-20.jpg" target="_blank" rel="noopener noreferrer">來源</a></figcaption></figure>'
def day_tiles():
    return '<div class="day-grid">'+''.join(f'<a class="day-tile" href="day-{d["n"]}.html"><span class="day-number"><b>D{d["n"]}</b><small>09/{int(d["date"][-2:]):02d}</small></span><span><strong>{e(d["title"])}</strong><small>週{d["weekday"]}・{e(d["route"])}</small></span><b aria-hidden="true">›</b></a>' for d in I['days'])+'</div>'
def option_html(id,hotel=None):
    o=I['options'][id]
    runtime={k:v for k,v in o.items() if k in ['out','visit','back','steps','departBy','departures','checkin','caution','rest']}
    minimum=o['out']+o['visit']+o['back']+o.get('checkin',0)
    places=o['places'] or ([hotel['name']+' '+hotel['address']] if hotel else [])
    return f'''<article class="option-card" data-option="{e(json.dumps(runtime,ensure_ascii=False))}"><span class="verdict pending">待計算</span><h3>{e(o['name'])}</h3><p class="minimum">往返至少 <strong>{minimum} 分鐘</strong><span>另留集合緩衝</span></p><p>{e(o['content'])}</p><p class="option-reason">請輸入時間後重新計算。</p><details class="option-detail"><summary>查看時間分配與提醒</summary><p class="time-breakdown">{e(o.get('transport','步行'))}去程 {o['out']} 分 ＋ 活動 {o['visit']} 分 ＋ 回程 {o['back']} 分{f' ＋ 提早報到 {o["checkin"]} 分' if o.get('checkin') else ''}；另加設定的 <span class="buffer-label">—</span> 分集合緩衝。</p>{'<p class="micro-note">'+e(o['caution'])+'</p>' if o.get('caution') else ''}</details><div class="map-row">{''.join(maps(q,'Google Maps'+('・第 '+str(i+1)+' 站' if len(places)>1 else '')) for i,q in enumerate(places))}</div></article>'''
def free_section(d):
    if not d['free']: return ''
    modes=[I['freeModes'][k] for k in d['free']]
    tabs=''.join(f'<button type="button" role="tab" id="tab-{idx}" aria-selected="{str(idx==0).lower()}" aria-controls="free-panel" tabindex="{0 if idx==0 else -1}" data-mode="{idx}" data-kind="{["day","night","airport"][idx]}">{e(m["label"])}</button>' for idx,m in enumerate(modes))
    infos='';options=''
    for idx,m in enumerate(modes):
        data={k:m[k] for k in ['start','end','buffer','disabled']}
        time_label=('今晚搭機返台' if '夜間' in m['label'] else '未安排自由活動') if m['disabled'] else m['start']+'–'+m['end']
        infos+=f'<div class="free-info" data-mode-info="{idx}" data-window="{e(json.dumps(data))}"'+(' hidden' if idx else '')+f'><p class="estimate-label">{EST}</p><p class="window-time">{e(time_label)}</p><p>{e(m["place"])}</p><details class="estimate-basis"><summary>這個時段怎麼估的？</summary><p>{e(m["basis"])}</p>{sources(m["sources"])}</details></div>'
        options+=f'<div class="options-list" data-mode-options="{idx}"'+(' hidden' if idx else '')+'>'+''.join(option_html(k,hotel_for(d)) for k in m['options'])+'</div>'
    return f'''<section class="free-section" id="free-time" data-date="{d['date']}"><div class="section-heading"><p class="eyebrow">集合前，先算一下</p><h2 data-free-title>今天還有多少自由時間？</h2><p data-free-intro>填入領隊集合時間，看現在還能去哪。</p></div><div class="tabs" role="tablist" aria-label="自由時間時段">{tabs}</div><div role="tabpanel" id="free-panel" aria-labelledby="tab-0">{infos}<noscript><p class="warning">計算器需要 JavaScript；所有行程與攻略仍可閱讀。</p></noscript><form class="time-form"><p class="clock-note">時間都用英國當地時間。</p><div class="time-fields"><div><label for="now-time">現在時間</label><input id="now-time" name="now" type="time" required value="{modes[0]['start']}"><label class="sr-only" for="now-day">現在日期</label><select id="now-day" name="nowDay"><option value="0">當日</option><option value="1">翌日（過午夜）</option></select></div><div><label for="end-time">集合／回飯店時間</label><input id="end-time" name="end" type="time" required value="{modes[0]['end']}"><label class="sr-only" for="end-day">結束日期</label><select id="end-day" name="endDay"><option value="0">當日</option><option value="1">翌日（過午夜）</option></select></div></div><div class="buffer-field"><label for="buffer">再預留幾分鐘集合？<small>回程已算在各方案內</small></label><input id="buffer" name="buffer" type="number" inputmode="numeric" min="0" max="120" step="1" required value="{modes[0]['buffer']}"></div><details class="form-help"><summary>跨午夜、回程怎麼算？</summary><p>各方案已包含走／搭車回程。額外緩衝留給找車、集合與交通誤差；如果過了午夜才回飯店，把結束日期改成「翌日」。</p></details><div class="form-buttons"><button class="button primary" type="submit">重新計算 →</button><button class="button secondary" type="button" id="use-now">帶入英國現在時間</button></div></form><div class="time-result" role="status" aria-live="polite"><span class="result-label">剩餘可用時間</span><strong class="result-number">—</strong><span class="result-detail">請重新計算</span></div><div class="option-toolbar"><p class="option-summary" role="status"></p><button type="button" class="text-button" id="toggle-unavailable" aria-expanded="false" hidden>顯示不建議方案</button></div><p class="no-options" hidden>目前沒有適合出發的方案。先留在集合點附近，或確認集合時間後重算。</p><p class="field-hint result-legend">✓ 可以　△ 很趕／需確認　✕ 不建議<br>離團前先告知領隊；出發前再看路況、排隊與餘票。</p>{options}</div></section>'''
def guide_html(g):
    body='<div class="guide-content"><section><h3>1｜3 個必看</h3>'+ul(g['must'],'must-see')+'</section>'
    body+='<section><h3>2｜你去這一天的情報</h3>'+ul(g['info'])+'</section><section><h3>3｜時間有限怎麼逛</h3><dl class="quick-routes">'+''.join(f'<div><dt>{e(t)}</dt><dd>{e(x)}</dd></div>' for t,x in g['routes'])+'</dl><p class="micro-note">逛法為攻略建議，實際停留以領隊通知為準。</p></section>'
    body+='<section><h3>4｜拍照</h3>'+ul(g['photo'])+'</section><section><h3>5｜真正值得買</h3>'+''.join(f'<div class="buy-item"><strong>{e(p)}</strong><span>{e(s)}</span><p>{e(w)}</p></div>' for p,s,w in g['buy'])+'</section><section><h3>6｜踩雷提醒</h3>'+ul(g['risks'])+'</section>'
    body+=maps(g['map'],'Google Maps'+('・河岸參考，非登船點' if g['id']=='thames' else ''))+sources(g['sources'])+'</div>'
    return f'<details class="guide-card" id="{g["id"]}"><summary><span class="guide-title">{e(g["title"])}</span><span class="guide-tag">{e(g["tag"])}</span><span class="expand-text">必看・逛法・拍照・購物 <b aria-hidden="true">＋</b></span></summary>{body}</details>'
def guide_dialog():
    return '<dialog class="guide-dialog" id="guide-dialog" aria-labelledby="guide-dialog-title"><div class="dialog-header"><div><p class="eyebrow">景點攻略</p><h2 id="guide-dialog-title"></h2></div><button class="button secondary dialog-close" type="button" data-close-guide autofocus>✕ 關閉<small>回原位置</small></button></div><div class="dialog-body"></div><div class="dialog-footer"><button class="button primary" type="button" data-close-guide>看完了，回到原本位置</button></div></dialog>'
def hotel_card(h):
    return f'<article class="hotel-card"><p class="eyebrow">{e(h["nights"])}</p><h2>{e(h["name"])}</h2><p class="hotel-address">{e(h["address"])}</p><p>{e(h["note"])}</p><div class="map-row">{maps(h["name"]+" "+h["address"],"導航回飯店")}<a class="button secondary" href="hotel-{h["id"]}.html">地址、電話與晚上安排 →</a></div></article>'

home=page_intro('2026・一起去英國','英國 8天6夜','09/08–09/15・行程時間皆為英國當地時間')+day_select(home=True)
home+='<div class="quick-actions"><a class="quick-action" data-today="schedule" href="day-1.html"><span aria-hidden="true">▤</span><strong>今天行程</strong><small>看去哪、坐多久 →</small></a><a class="quick-action" data-today="free" href="day-2.html?mode=day#free-time"><span aria-hidden="true">◷</span><strong>自由時間</strong><small>集合前還能去哪 →</small></a><a class="quick-action" data-today="night" href="day-2.html?mode=night#free-time"><span aria-hidden="true">☾</span><strong>晚餐後去哪</strong><small>算上往返再決定 →</small></a><a class="quick-action" href="checklist.html"><span aria-hidden="true">✓</span><strong>出發清單</strong><small>一項項勾，不漏帶 →</small></a></div><p class="today-note">出發前先看 D1；自由時間先試算 D2。也可在上方選日期。</p>'
for d in I['days']:
    h=hotel_for(d)
    home+=f'<article class="selected-day" data-day-preview="{d["n"]}"'+(' hidden' if d['n']!=1 else '')+f'><p class="eyebrow">D{d["n"]}・09/{int(d["date"][-2:]):02d} 週{d["weekday"]}</p><h2>{e(d["title"])}</h2><p>{e(d["route"])}</p><a class="button primary" href="day-{d["n"]}.html">查看當天行程 →</a>'+(f'<a class="selected-hotel" href="hotel-{h["id"]}.html">今晚住哪？<strong>{e(h["name"])}</strong>地址與導航 →</a>' if h else '<p class="micro-note">'+('今晚搭機返台，前往機場前請確認護照與行李。' if d['n']==7 else '18:05 抵達桃園，祝平安到家。')+'</p>')+'</article>'
home+='<section class="attention"><h2>這幾天要特別留意</h2>'+''.join(f'<a href="day-{g["day"]}.html#{g["id"]}"><span>D{g["day"]}｜{e(g["tag"])}</span><b aria-hidden="true">›</b></a>' for id in G['highlights'] for g in G['guides'] if g['id']==id)+'</section><section id="days"><div class="section-heading"><p class="eyebrow">09/08 出發・09/15 回家</p><h2>8 天行程，一次看</h2></div>'+day_tiles()+'</section>'
home+='<section class="share-card"><h2>傳給同行團員</h2><p>收藏這個網址，途中查行程更方便。</p><button class="button secondary" type="button" data-copy="site-link">複製網站連結</button><a id="site-link" class="share-url" href="'+PUBLIC+'">'+PUBLIC+'</a><p class="copy-result" role="status"></p></section>'+image_block()
write('index.html','英國 8天6夜',home,'home')
for d in I['days']:
    n=d['n'];guides=[g for g in G['guides'] if g['day']==n]
    body=day_select(n)+page_intro(f'D{n}・09/{int(d["date"][-2:]):02d}（{d["weekday"]}）',d['title'],d['route'])
    body+='<nav class="jump-links" aria-label="本日章節"><a href="#schedule">今天行程</a>'+(f'<a href="?mode={"airport" if n==7 else "day"}#free-time" data-free-link="{"airport" if n==7 else "day"}">自由時間</a><a href="?mode=night#free-time" data-free-link="night">晚餐後去哪</a>' if d['free'] else '<a href="#coach">搭車時間</a>')+('<a href="#field-guide">景點怎麼逛</a>' if guides else '<a href="checklist.html">出發清單</a>')+'</nav>'
    body+='<details class="day-alert"><summary>今天先記住 <span>'+str(len(d['alerts']))+' 件事</span></summary>'+ul(d['alerts'])+'</details>'
    body+='<section id="schedule"><div class="section-heading"><p class="eyebrow">依旅行社 9/04 正式手冊</p><h2>今天行程</h2><p>集合與停留時間，請看領隊當天通知。</p></div><ol class="timeline">'
    for s in d['stops']:
        body+='<li><strong>'+e(s['name'])+'</strong>'+('<p>'+e(s['note'])+'</p>' if s['note'] else '')+(f'<a href="#{s["guide"]}" aria-label="{e(s["name"])}：查看景點攻略">查看景點攻略</a>' if s['guide'] else '')+'</li>'
    body+='</ol></section><details class="section-fold" id="coach"><summary><span><strong>這一段要坐多久？</strong><small>每次上車的地點與預估車程</small></span><b aria-hidden="true">＋</b></summary><div class="fold-content"><p class="field-hint">保守預估，非正式行車時間；不含集合、休息站與臨時塞車。</p>'
    for l in d['legs']:
        body+=f'<article class="coach-leg'+(' walking' if l['walk'] else '')+f'"><span class="transport-label">{"步行" if l["walk"] else "遊覽車"}</span><h3>{e(l["a"])} <span aria-hidden="true">→</span> {e(l["b"])}</h3><strong>{e(l["time"])}</strong>'+('<p>'+e(l['note'])+'</p>' if l['note'] else '')+'</article>'
    if not d['legs']:body+='<p class="empty-note">今天沒有安排遊覽車接駁。</p>'
    body+='</div></details>'+free_section(d)
    if guides:body+='<section id="field-guide" data-day-only><div class="section-heading"><p class="eyebrow">必看、拍照與值得買的東西</p><h2>景點怎麼逛最順？</h2><p>點選景點，依你剩下的時間選一條逛法。</p></div>'+''.join(guide_html(g) for g in guides)+'</section>'
    if n==6:body+=image_block(day_only=True)
    if d['hotel']:body+='<section class="tonight"><div class="section-heading"><h2>今晚住這裡</h2></div>'+hotel_card(hotel_for(d))+'</section>'
    body+='<div class="page-turn">'+(f'<a class="button secondary" href="day-{n-1}.html">← 前一天 D{n-1}</a>' if n>1 else '<a class="button secondary" href="index.html">← 首頁</a>')+(f'<a class="button primary" href="day-{n+1}.html">下一天 D{n+1} →</a>' if n<8 else '<a class="button primary" href="checklist.html">返家檢查 →</a>')+'</div>'
    write(f'day-{n}.html',f'D{n} {d["title"]}',body,'day',n)
body=page_intro('6 晚・3 間飯店','找飯店，一鍵導航','先對照今晚飯店名稱，再開啟地圖。')+''.join(hotel_card(h) for h in I['hotels'])
write('hotels.html','飯店與導航',body,'hotels')
for h in I['hotels']:
    body=page_intro(h['nights'],h['name'],h['address'])+f'<div class="contact-card">{maps(h["name"]+" "+h["address"],"導航回飯店")}<a class="button secondary" href="tel:{h["phone"].replace(" ","")}">致電飯店 {e(h["phone"])}</a></div><div class="notice"><p>{e(h["note"])}</p></div><section><h2>今晚怎麼安排</h2><p>{e(h["evening"])}</p>'
    ns=[d['n'] for d in I['days'] if d['hotel']==h['id']]
    body+='<div class="map-row">'+''.join(f'<a class="button primary" href="day-{n}.html?mode=night#free-time">D{n} 晚餐後還能去哪 →</a>' for n in ns if n>1)+'</div></section><section><h2>出門前，做這四件事</h2>'+ul(I['hotelTips'])+'</section>'
    if h['id']=='coventry':body+=sources(['tesco','tenpin'])
    if h['id']=='park-royal':body+=sources(['tfl','nightbus'])
    body+='<p class="micro-note">飯店資料依 9/04 旅行社手冊。</p><a class="button secondary" href="hotels.html">← 所有飯店</a>'
    write('hotel-'+h['id']+'.html',h['name'],body,'hotels')
body=page_intro('隨時用得到','攻略與隨身工具','想看哪個景點、找清單或英文溝通卡，都在這裡。')+'<div class="tool-grid"><a href="checklist.html"><strong>✓ 出發清單</strong><small>逐項勾選，存在自己的手機</small></a><a href="allergy.html"><strong>文／A 英文溝通卡</strong><small>點餐、問路與特定飲食需求</small></a><a href="#windows"><strong>◷ 自由時間總覽</strong><small>每天白天與晚上的推估</small></a><a href="#uncertain"><strong>! 行前提醒</strong><small>領隊與現場仍需確認的事</small></a></div>'
for d in I['days']:
    gs=[g for g in G['guides'] if g['day']==d['n']]
    if gs:body+=f'<section><h2>D{d["n"]}・09/{int(d["date"][-2:]):02d} 景點攻略</h2><div class="guide-index">'+''.join(f'<a href="day-{g["day"]}.html#{g["id"]}"><strong>{e(g["title"])}</strong><span>{e(g["tag"])} →</span></a>' for g in gs)+'</div></section>'
body+='<section id="windows"><h2>每天自由時間總覽</h2><p class="estimate-label">'+EST+'</p><div class="window-overview">'
for d in I['days']:
    for key in d['free']:
        m=I['freeModes'][key]
        if not m['disabled']:
            kind='airport' if key=='airport' else 'night' if '夜間' in m['label'] else 'day'
            body+=f'<a href="day-{d["n"]}.html?mode={kind}#free-time"><strong>D{d["n"]}・{e(m["label"])}</strong><span>{m["start"]}–{m["end"]}</span><small>{e(m["place"])}</small></a>'
body+='</div></section><section id="uncertain" class="attention"><h2>還需要領隊／現場確認</h2>'+ul(G['uncertain'])+'</section><details class="section-fold"><summary>行程、推估與攻略怎麼分辨？</summary><div class="fold-content">'+ul(G['method'])+'</div></details>'
write('guide.html','攻略與工具',body,'guide')
body=page_intro('把英文直接給店員看','英文溝通與飲食卡','選符合你需要的句子；特殊飲食請先告知領隊。')
for idx,p in enumerate(I['phrases']):
    body+=f'<article class="phrase-card"><h2>{e(p["title"])}</h2><p id="phrase-{idx}" lang="en">{e(p["en"])}</p><p class="micro-note">{e(p["zh"])}</p><button class="button secondary" type="button" data-copy="phrase-{idx}">複製英文</button><p class="copy-result" role="status"></p></article>'
body+='<details class="section-fold personal-card"><summary><span><strong>特定需求：牛奶過敏＋不吃牛肉</strong><small>僅符合這兩項需求者使用</small></span><b aria-hidden="true">＋</b></summary><div class="fold-content"><p class="notice">這是特定飲食需求的餐卡，請確認內容完全符合自己，再出示給餐廳。</p><article class="allergy-card"><h2 lang="en">MILK ALLERGY<br>NO BEEF</h2><p id="allergy-text" lang="en">'+e(I['dietCard'])+'</p><button class="button primary" type="button" data-copy="allergy-text">複製這張英文餐卡</button><p class="copy-result" role="status"></p></article><h2>使用這張卡時要留意</h2>'+ul(I['dietTips'])+'</div></details><p class="micro-note">其他飲食需求請直接告知領隊與餐廳。已載入的英文卡可以直接出示，不需複製也能使用。</p>'
write('allergy.html','英文溝通與飲食卡',body,'guide')
body=page_intro('出發前，一項項確認','我的出發清單','每位團員各自勾選，只記在目前這台手機。')+'<div class="check-progress" role="status"><span>準備進度</span><strong><span id="check-count">0</span> / '+str(len(I['checklist']))+'</strong><progress id="check-progress" max="'+str(len(I['checklist']))+'" value="0" aria-label="清單完成進度"></progress></div>'
for group in I['checklistGroups']:
    body+='<section class="check-group"><h2>'+e(group['title'])+'</h2><div class="check-list">'+''.join(f'<label><input type="checkbox" data-check="{e(k)}"><span>{e(t)}</span></label>' for k,t in I['checklist'] if k in group['ids'])+'</div></section>'
body+='<p id="storage-note" class="field-hint">換手機或清除瀏覽資料，勾選不會同步。</p><a class="button secondary" href="allergy.html">英文溝通與飲食卡 →</a><section class="attention"><h2>出發當天再看一次</h2>'+ul(I['departureTips'])+'</section>'
write('checklist.html','我的出發清單',body,'guide')
write('404.html','找不到這一頁',page_intro('找不到頁面','回到行程，繼續逛','這一頁可能已換位置，請從首頁重新選日期。')+'<a class="button primary" href="index.html">回到首頁 →</a>')
print(f'Built {len([p for p in ROOT.glob("*.html") if not p.name.startswith(".")])} member-facing static pages')

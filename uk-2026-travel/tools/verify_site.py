#!/usr/bin/env python3
"""Structural acceptance gates, internal anchors, and every Maps URL."""
import json, re, gzip
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, parse_qs, unquote
R=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self,path):
        super().__init__();self.ids=[];self.links=[];self.scripts=[];self.forms=0;self.guides=0;self.coach=0;self.walk=0;self.iframes=0
        self.text=path.read_text();self.feed(self.text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs);c=a.get('class','').split()
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a':self.links.append(a.get('href',''))
        if tag=='script':self.scripts.append(a.get('src',''))
        if tag=='form':self.forms+=1
        if tag=='iframe':self.iframes+=1
        if 'guide-card' in c:self.guides+=1
        if 'coach-leg' in c:
            if 'walking' in c:self.walk+=1
            else:self.coach+=1
        if tag in ('script','img','link'):
            url=a.get('src',a.get('href',''))
            if url and not urlsplit(url).scheme:assert (R/unquote(urlsplit(url).path)).exists(),url
pages={p.name:Page(p) for p in R.glob('*.html') if not p.name.startswith('.')}
assert len(pages)==17,len(pages)
map_links=set();internal=0
for name,p in pages.items():
    assert len(p.ids)==len(set(p.ids)),(name,'duplicate IDs')
    assert p.scripts==['assets/app.js?v=rebuild-20260905-1'],(name,p.scripts)
    assert p.iframes==0,(name,'unexpected iframe')
    for old in ['time-tool','time-windows','clean-view','site-clean-heading','Overpass','leaflet','British Motor Museum','Regent Street']:
        assert old not in p.text,(name,old)
    for link in p.links:
        u=urlsplit(link)
        if not u.scheme:
            target=u.path or name
            assert target in pages,(name,target)
            if u.fragment:assert unquote(u.fragment) in pages[target].ids,(name,link)
            internal+=1
        elif u.netloc=='www.google.com':
            q=parse_qs(u.query)
            assert u.scheme=='https' and u.path=='/maps/search/' and q.get('api')==['1'] and q.get('query',[''])[0].strip(),link
            map_links.add(link)
for n,expected in enumerate([1,3,5,3,5,4,4,0],1):
    p=pages[f'day-{n}.html'];assert p.coach==expected,(n,p.coach)
    assert p.ids.count('free-time')==(1 if 2<=n<=7 else 0)
    assert p.forms==(1 if 2<=n<=7 else 0)
    if 2<=n<=7:assert '推估，非旅行社正式時間' in p.text
assert pages['day-7.html'].walk==1
assert 'JRC Global Buffet Wembley' in pages['day-6.html'].text
assert 'Street Burger Charing Cross Road' in pages['day-7.html'].text
I=json.loads((R/'assets/itinerary.json').read_text());G=json.loads((R/'assets/guide.json').read_text())
for g in G['guides']:
    assert len(g['must'])==3 and all(g[k] for k in ['info','routes','photo','buy','risks','sources'])
    assert g['id'] in pages[f'day-{g["day"]}.html'].ids
    assert all(x in G['sources'] for x in g['sources'])
assert sum(p.guides for p in pages.values())==len(G['guides'])
assert not re.search(r'\bfetch\s*\(|document\.write|createElement\([\'"]script', (R/'assets/app.js').read_text())
for name in ['index.html','assets/app.js','assets/styles.css']:
    b=(R/name).read_bytes();print(f'{name}: {len(b):,} bytes; gzip {len(gzip.compress(b)):,}')
print(f'PASS {len(pages)} pages; {internal} internal links/anchors; {len(map_links)} unique valid Maps URLs; {len(G["guides"])} six-section guides; all coach legs; one calculator per D2–D7')

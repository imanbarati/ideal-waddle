#!/usr/bin/env python3
"""Polite resumable crawler for public x.ai/bot/marketplace pages.
Standard library only; honors robots.txt and never authenticates or bypasses blocks.
Review site terms before redistributing archived content.
"""
import argparse, hashlib, json, re, time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse, urldefrag, urlunparse
from urllib.request import Request, urlopen
import urllib.robotparser

ROOT = 'https://x.ai/bot/marketplace'
HOST = 'x.ai'
UA = 'ideal-waddle-public-archive/0.1 (polite research crawler)'
BASE = Path(__file__).resolve().parents[1]
DATA, PAGES, TEXTS = BASE/'data', BASE/'data/pages', BASE/'data/text'
MANIFEST, CATALOG = DATA/'manifest.jsonl', DATA/'catalog.json'

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.links=[]; self.parts=[]; self.skip=0; self.title_on=False; self.title=''
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag in ('script','style','noscript','svg'): self.skip += 1
        if tag == 'a' and a.get('href'): self.links.append(a['href'])
        if tag == 'title': self.title_on=True
        if tag in ('p','div','li','h1','h2','h3','h4','br','section','article'): self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script','style','noscript','svg') and self.skip: self.skip -= 1
        if tag == 'title': self.title_on=False
        if tag in ('p','div','li','h1','h2','h3','h4','section','article'): self.parts.append('\n')
    def handle_data(self, data):
        if self.title_on: self.title += data
        if not self.skip:
            s=re.sub(r'\s+',' ',data).strip()
            if s: self.parts.append(s+' ')
    def text(self): return re.sub(r'\n\s*\n+','\n\n',''.join(self.parts)).strip()

def norm(url):
    url,_=urldefrag(url); p=urlparse(url)
    if p.scheme not in ('http','https') or p.hostname != HOST: return None
    path=p.path or '/'
    if path != '/' and path.endswith('/'): path=path[:-1]
    return urlunparse(('https',HOST,path,'',p.query,''))

def fetch(url):
    req=Request(url,headers={'User-Agent':UA,'Accept':'text/html,application/xml,text/plain,*/*'})
    with urlopen(req,timeout=25) as r: return r.status,r.geturl(),r.headers.get('Content-Type',''),r.read()

def in_scope(url, details=False):
    p=urlparse(url)
    return p.hostname==HOST and (p.path=='/bot/marketplace' or p.path.startswith('/bot/marketplace/') or (details and '/bot/marketplace/bots/' in p.path))

def slug(url): return re.sub(r'[^a-zA-Z0-9._-]+','_',urlparse(url).path.strip('/') or 'marketplace')[:90]+'-'+hashlib.sha256(url.encode()).hexdigest()[:10]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--delay',type=float,default=2); ap.add_argument('--max-pages',type=int,default=500); ap.add_argument('--include-detail-pages',action='store_true'); args=ap.parse_args()
    if args.delay < 1: raise SystemExit('Use --delay of at least 1 second.')
    for d in (DATA,PAGES,TEXTS): d.mkdir(parents=True,exist_ok=True)
    try:
        status,_,_,raw=fetch('https://x.ai/robots.txt')
        if status>=400: raise RuntimeError('robots.txt returned HTTP '+str(status))
        robots=urllib.robotparser.RobotFileParser(); robots.set_url('https://x.ai/robots.txt'); robots.parse(raw.decode('utf-8','replace').splitlines())
    except Exception as e: raise SystemExit('Cannot verify robots.txt; refusing to crawl: '+str(e))
    rows=[]; done=set()
    if MANIFEST.exists():
        for line in MANIFEST.read_text(encoding='utf-8').splitlines():
            try:
                x=json.loads(line); rows.append(x)
                if x.get('status')==200: done.add(x.get('url'))
            except Exception: pass
    try: catalog=json.loads(CATALOG.read_text(encoding='utf-8')) if CATALOG.exists() else []
    except Exception: catalog=[]
    catalog_urls={x.get('url') for x in catalog}; seen=set(done); queue=[ROOT]; attempted=0
    with MANIFEST.open('a',encoding='utf-8') as mf:
        while queue and attempted<args.max_pages:
            url=norm(queue.pop(0))
            if not url or url in seen or not in_scope(url,args.include_detail_pages): continue
            seen.add(url); row={'url':url,'fetched_at':datetime.now(timezone.utc).isoformat()}
            if not robots.can_fetch(UA,url) or not robots.can_fetch('*',url):
                row.update(status='robots_disallowed',error='Blocked by robots.txt')
            else:
                try:
                    status,final,ctype,raw=fetch(url); row.update(status=status,final_url=final,content_type=ctype,sha256=hashlib.sha256(raw).hexdigest())
                    if status==200 and ('html' in ctype.lower() or raw.lstrip().startswith(b'<')):
                        p=Parser(); p.feed(raw.decode('utf-8','replace')); key=slug(url)
                        hp=PAGES/(key+'.html'); tp=TEXTS/(key+'.txt'); hp.write_bytes(raw); tp.write_text(p.text(),encoding='utf-8')
                        row.update(html_path=str(hp.relative_to(BASE)),text_path=str(tp.relative_to(BASE)),title=p.title.strip())
                        if url not in catalog_urls:
                            catalog.append({'url':url,'title':p.title.strip(),'text_path':row['text_path'],'sha256':row['sha256'],'fetched_at':row['fetched_at']}); catalog_urls.add(url)
                        for href in p.links:
                            nxt=norm(urljoin(final,href))
                            if nxt and nxt not in seen and in_scope(nxt,args.include_detail_pages): queue.append(nxt)
                    elif status!=200: row['error']='HTTP '+str(status)
                except (HTTPError,URLError,TimeoutError,OSError,RuntimeError) as e: row.update(status='error',error=str(e))
            mf.write(json.dumps(row,ensure_ascii=False)+'\n'); mf.flush(); rows.append(row); attempted+=1
            CATALOG.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            print(f'[{attempted}/{args.max_pages}] {row.get("status")} {url}')
            time.sleep(args.delay)
    print(f'Finished: attempted {attempted}; catalog entries {len(catalog)}')

if __name__=='__main__': main()

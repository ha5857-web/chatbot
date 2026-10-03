#!/usr/bin/env python3
"""네이버 블로그 최신 글을 posts.json 으로 저장합니다. (홈페이지가 이 파일을 읽어 '블로그' 구역에 보여줍니다)

사용법:   python update-posts.py            → ha5857 블로그의 최신 글 12개
          python update-posts.py 블로그아이디
          python update-posts.py --file 저장한rss.xml     (인터넷 없이 시험할 때)
"""
import json, re, sys, html, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

def clean(s):
    s = html.unescape(re.sub(r'<[^>]+>', ' ', s or ''))
    return re.sub(r'\s+', ' ', s).strip()

def parse(xml_bytes, limit=12):
    root = ET.fromstring(xml_bytes)
    out = []
    for it in root.iter('item'):
        title = clean(it.findtext('title'))
        link = (it.findtext('link') or '').strip()
        desc = it.findtext('description') or ''
        if not title or not link: continue
        m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', html.unescape(desc))
        try: date = parsedate_to_datetime(it.findtext('pubDate')).strftime('%Y-%m-%d')
        except Exception: date = ''
        text = clean(desc)
        out.append({'title': title, 'url': link.split('?')[0] if 'blog.naver.com' in link else link,
                    'date': date, 'thumb': m.group(1) if m else '', 'summary': text[:90] + ('…' if len(text) > 90 else '')})
        if len(out) >= limit: break
    return out

def main(argv):
    if '--file' in argv:
        data = open(argv[argv.index('--file') + 1], 'rb').read()
    else:
        bid = next((a for a in argv if not a.startswith('-')), 'ha5857')
        req = urllib.request.Request('https://rss.blog.naver.com/%s.xml' % bid, headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req, timeout=20).read()
    posts = parse(data)
    with open('posts.json', 'w', encoding='utf-8') as f: json.dump(posts, f, ensure_ascii=False, indent=1)
    print('posts.json 저장:', len(posts), '개')

if __name__ == '__main__': main(sys.argv[1:])

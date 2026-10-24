import re, sys, urllib.parse, unicodedata, json
D = sys.argv[1]  # data dir
html_path = sys.argv[2]
out_raw = sys.argv[3]

def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r'\b(various artists?|va|v/a)\b', '', s)
    return re.sub(r'[^a-z0-9]+', '', s)

recs = []      # dicts: s,g,artist,title,label,format,price,status,url
def add(r):
    r = {k: (v or '').replace('|', '/').strip() for k, v in r.items()}
    recs.append(r)

# 1. existing page data (Juno, Redeye p1 sample, Hard Wax)
page = open(html_path, encoding='utf8').read()
raw = re.search(r'const RAW=`(.*?)`;', page, re.S).group(1)
BASE = {'J': 'https://www.juno.co.uk/products/', 'R': 'https://www.redeyerecords.co.uk/vinyl/', 'H': 'https://hardwax.com/'}
for line in raw.strip().split('\n'):
    s, g, a, t, l, f, p, st, path = line.split('|')
    add(dict(s=s, g=g, artist=a, title=t, label=l, format=f, price=p, status=st, url=BASE[s] + path))

# 2. today's test digest
GMAP = {'Techno': 'T', 'Minimal/Tech House': 'M', 'Deep House': 'D', 'House (Redeye house-disco)': 'H', 'Electro': 'E'}
CUR = {'EUR': '€', 'GBP': '£', 'USD': '$', 'AUD': 'A$', 'CAD': 'C$', 'JPY': '¥', 'CHF': 'CHF ', 'SEK': 'SEK ', 'NZD': 'NZ$', 'DKK': 'DKK ', 'PLN': 'PLN '}
def unwrap(u):
    q = urllib.parse.urlparse(u)
    if 'google.com' in q.netloc:
        return urllib.parse.parse_qs(q.query)['q'][0]
    return u
genre = src = None
for line in open(f'{D}/test_email.md', encoding='utf8'):
    line = line.rstrip('\n')
    m = re.match(r'### (.+?) \(\d+\)$', line)
    if m:
        genre = GMAP.get(m.group(1)); continue
    if line.startswith('Redeye'): src = 'R'; continue
    if line.startswith('Hard Wax'): src = 'H'; continue
    if line.startswith('Clone'): src = 'C'; continue
    if line.startswith('Bandcamp'): src = 'B'; continue
    if line.startswith('### Source'): genre = None; continue
    m = re.match(r'\[(.+?)\]\((\S+?)\)(.*)$', line)
    if not (m and genre and src) or src == 'C':
        continue
    name, url, rest = m.group(1), unwrap(m.group(2)), m.group(3)
    artist, _, title = name.partition(' — ')
    parts = [x.strip() for x in rest.split(' · ') if x.strip()]
    status = ''
    if parts and re.match(r'(In stock|Out of stock|Preorder|Released)', parts[-1], re.I):
        status = parts.pop()
        status = re.sub(r'^Preorder:\s*', 'Preorder · ', status)
        if status.lower() == 'out of stock': status = 'Out of stock'
    price = ''
    for i in range(len(parts) - 1, -1, -1):
        p = parts[i]
        mm = re.match(r'^([\d.,]+)\s*([A-Z]{3})$', p)
        if mm:
            price = CUR.get(mm.group(2), mm.group(2) + ' ') + mm.group(1); parts.pop(i); break
        if re.match(r'^[£€$]', p):
            price = p; parts.pop(i); break
    fmt = parts.pop() if parts else 'Vinyl'
    label = ' '.join(parts)
    if src == 'H':  # Hard Wax label + catno → "Label · catno" like the page
        mm = re.match(r'^(.*?)\s+(\S*\d\S*)$', label)
        if mm: label = f'{mm.group(1)} · {mm.group(2)}'
        if not price.startswith('€'): price = '€' + price
    if src == 'R' and status == 'In stock': pass
    add(dict(s=src, g=genre, artist=artist, title=title, label=label, format=fmt, price=price, status=status, url=url))

# 3. Redeye pages fetched now (techno-electro p2-p4 new batch)
DROP = re.compile(r'edits? \d|tooflie|acardipane|riddim', re.I)
ELECTRO = {'the 89th passenger', 'versalife', 'intellitronic'}
for fn in ['redeye_te_p2.txt', 'redeye_te_p3.txt', 'redeye_te_p4.txt']:
    for line in open(f'{D}/{fn}', encoding='utf8'):
        if line.startswith('---'): break
        f = [x.strip() for x in line.split(' | ')]
        if len(f) < 8: continue
        a, t, l, cat, fm, p, st, u = f[:8]
        if DROP.search(a + ' ' + t + ' ' + l): continue
        st = {'Available': 'In stock', 'Out of Stock': 'Out of stock'}.get(st, st)
        st = re.sub(r'Preorder, Exp\. ', 'Preorder · ', st)
        add(dict(s='R', g='E' if a.lower() in ELECTRO else 'T', artist=a, title=t, label=l, format=fm, price=p, status=st, url=u))

# 4. Clone homepage, read through Chrome just now
CLONE = [
 ('E','The 89th Passenger','Hidden Soul EP','Analogical Force','12"','€15.99','84883'),
 ('T','Marivs','Scalene EP','Fachwerk','EP','€13.99','83816'),
 ('T','VRIL','KRUX','Delsin','2LP','€33.99','84778'),
 ('D','Jan Kincl','Lights Out','Cycle Records','12"','€13.99','84656'),
 ('T','Claudio PRC','Self Surrender Deconstructed','Delsin','12"','€14.99','84930'),
 ('T','BufoBufo','Irisation','Dream Ticket','12"','€14.99','84445'),
 ('T','Altinbas','Beyond the Veil','Clone','12" + download','€19.99','84963'),
 ('T','Various Artists','Electronic Civilisation','Under The Radar','12"','€14.99','83744'),
 ('T','Marco Shuttle','MSP03','Marco Shuttle Productions','12"','€15.49','84224'),
 ('T','SBWT','Marauders','Elektorni','12"','€15.49','84484'),
 ('T','k.o.p. 32','Symmetry','Beyond The Bridge','12"','€13.99','84446'),
 ('T','Beste Hira','MP10','Magic Power','12"','€15.99','84375'),
 ('T','Ignacio','Virton','Music Man','12"','€17.49','84263'),
 ('T','Regis','Power Is Neutral (Mark Broom Edits)','Blueprint','12"','€17.49','84393'),
]
for g, a, t, l, fm, p, i in CLONE:
    add(dict(s='C', g=g, artist=a, title=t, label=l, format=fm, price=p, status='', url=f'https://clone.nl/item{i}.html'))

# dedupe: same store + same URL, or same store + same artist/title
seen, out = set(), []
for r in recs:
    k1 = (r['s'], r['url'].rstrip('/').lower())
    k2 = (r['s'], norm(r['artist']), norm(r['title']))
    if k1 in seen or k2 in seen: continue
    seen.update([k1, k2]); out.append(r)

assert all(r['url'].startswith('http') for r in out)
lines = ['|'.join([r['s'], r['g'], r['artist'], r['title'], r['label'], r['format'], r['price'], r['status'], r['url']]) for r in out]
open(out_raw, 'w', encoding='utf8').write('\n'.join(lines))
from collections import Counter
print(len(out), Counter(r['s'] for r in out), Counter(r['g'] for r in out))
print('no price:', [(r['s'], r['artist'], r['title']) for r in out if not r['price']][:10])

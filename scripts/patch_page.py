import re, sys
src, raw_path, dst = sys.argv[1:4]
h = open(src, encoding='utf8').read()
raw = open(raw_path, encoding='utf8').read().replace('`', "'").replace('\\', '/').replace('${', '$ {')

def sub(old, new, count=1):
    global h
    assert old in h, old[:60]
    h = h.replace(old, new, count)

# colours for the new House genre
sub('--g-techno:#2b3fd1; --g-minimal:#0f8a7a; --g-deep:#b8620c; --g-electro:#8a2fb8;',
    '--g-techno:#2b3fd1; --g-minimal:#0f8a7a; --g-deep:#b8620c; --g-house:#b3266b; --g-electro:#8a2fb8;')
h = h.replace('--g-techno:#6f80ff; --g-minimal:#35c2ad; --g-deep:#e8913a; --g-electro:#bf6ef0;',
              '--g-techno:#6f80ff; --g-minimal:#35c2ad; --g-deep:#e8913a; --g-house:#f0679f; --g-electro:#bf6ef0;')
assert h.count('--g-house:') == 3

# masthead
sub('New this week · <b>w/c 5 Oct 2026</b> · Techno · Minimal/Tech House · Deep House · Electro',
    'New this week · <b>w/c 5 Oct 2026</b> · Techno · Minimal/Tech House · Deep House · House · Electro')
sub('<span class="sample">Sample built from this week\'s Juno, Redeye and Hard Wax listings</span>',
    '<span class="sample">Preview built Wed 7 Oct from all six stores · from Monday this page refreshes each week</span>')
sub('Every new record in your four genres.', 'Every new record in your genres, plus Redeye\'s house section.')

# footer
old_status = re.search(r'<section class="status".*?</section>', h, re.S).group(0)
new_status = '''<section class="status" aria-label="Source status">
    <div><strong class="ok">Juno · 98</strong><span>From your Juno email of Sun 4 Oct, including 6 preorders. Prices in GBP.</span></div>
    <div><strong class="ok">Redeye · 180</strong><span>Techno/Electro pages 1–4 (this week's batch) and House pages 1–5. Hard techno, edits and a dancehall 12" left out. Prices in GBP ex-VAT.</span></div>
    <div><strong class="ok">Bandcamp · 148</strong><span>Read through Chrome on your computer: new vinyl tagged techno, minimal, tech house, deep house and electro, released or up for preorder since 28 Sep. Prices as each seller lists them.</span></div>
    <div><strong class="ok">Hard Wax · 17</strong><span>This Week page, sorted into your genres from each description. Prices in EUR.</span></div>
    <div><strong class="ok">Clone · 14</strong><span>New arrivals on Clone's homepage that fit your genres, with links and EUR prices. Older restocks and merch left out.</span></div>
    <div><strong>Fingerprints</strong><span>Nothing in your genres this week.</span></div>
  </section>'''
h = h.replace(old_status, new_status)

# data + config
h = re.sub(r'const BASE=\{.*?\};\n', '', h, count=1)
sub('const STORE={J:"Juno",R:"Redeye",H:"Hard Wax"};',
    'const STORE={J:"Juno",R:"Redeye",B:"Bandcamp",H:"Hard Wax",C:"Clone"};')
sub('const GENRE={T:"Techno",M:"Minimal/Tech House",D:"Deep House",E:"Electro"};',
    'const GENRE={T:"Techno",M:"Minimal/Tech House",D:"Deep House",H:"House",E:"Electro"};')
sub('const GVAR={T:"--g-techno",M:"--g-minimal",D:"--g-deep",E:"--g-electro"};',
    'const GVAR={T:"--g-techno",M:"--g-minimal",D:"--g-deep",H:"--g-house",E:"--g-electro"};')
h = re.sub(r'const RAW=`.*?`;', lambda m: 'const RAW=`' + raw + '`;', h, count=1, flags=re.S)

sub('''  const [s,g,artist,title,label,format,price,status,path]=line.split("|");
  const cur=price[0], amt=parseFloat(price.slice(1));
  return {id:s+i+"-"+norm(artist+title).slice(0,40),s,g,artist,title,label,format,price,cur,amt,status,url:BASE[s]+path,key:norm(artist)+"|"+norm(title)};''',
    '''  let [s,g,artist,title,label,format,price,status,url]=line.split("|");
  const cur=(price.match(/^[^\\d]+/)||[""])[0], amt=parseFloat(price.slice(cur.length));
  if(/^\\d+(\\.\\d)?$/.test(price.slice(cur.length))) price=cur+amt.toFixed(price.includes(".")?2:0);
  return {id:s+"-"+norm(artist+title).slice(0,40),s,g,artist,title,label,format,price,cur,amt,status,url,key:norm(artist)+"|"+norm(title)};''')

# empty labels (some Bandcamp sellers)
sub('const lbl=r.label.split("·")[0].trim();', 'const lbl=r.label.split("·")[0].trim()||r.artist;')
sub('<div class="small">${esc(r.label.split("·")[0].trim())} · ${esc(r.format)}</div>',
    '<div class="small">${esc([r.label.split("·")[0].trim(),r.format].filter(Boolean).join(" · "))}</div>')

# genre sort order and price sort across currencies
sub('const gOrder="TMDE";', 'const gOrder="TMDHE";')
sub('else if(state.sort==="price") list.sort((a,b)=>a.cur===b.cur?a.amt-b.amt:(a.cur==="£"?-1:1));',
    'else if(state.sort==="price"){const co=["£","€","$"],ci=c=>co.includes(c)?co.indexOf(c):9;list.sort((a,b)=>a.cur===b.cur?a.amt-b.amt:ci(a.cur)-ci(b.cur))}')

# tally: every store
sub('''t.innerHTML=`<div><span>Records</span><strong>${recs.length}</strong></div><div><span>Juno</span><strong>${by("J")}</strong></div><div><span>Redeye</span><strong>${by("R")}</strong></div><div><span>Hard Wax</span><strong>${by("H")}</strong></div>`;''',
    '''t.innerHTML=`<div><span>Records</span><strong>${recs.length}</strong></div>`+Object.entries(STORE).map(([k,v])=>`<div><span>${v}</span><strong>${by(k)}</strong></div>`).join("");''')

# picks
old_picks = re.search(r'const PICKS=\[.*?\n\];', h, re.S).group(0)
new_picks = '''const PICKS=[
 ["Rhythim Is Rhythim","WJLB Tracks","Derrick May's Rhythim Is Rhythim project, pressed as a one-sided etched LP. At Juno and Redeye."],
 ["Robert Hood","Red Passion II","A new M-Plant 12\\" from Robert Hood, up for preorder at Redeye."],
 ["VRIL","KRUX","Delsin 2LP from VRIL, with Rene Wise guesting. In at Clone and Redeye."],
 ["Cv313","Altering Illusions [1/3] (remastered)","Echospace Detroit dub techno, remastered across two transparent red 12\\"s. In stock at Redeye."],
 ["Alex Barbu","Paths Lead Inward [Bosco060]","Minimal from Bosconi, preorder on Bandcamp."],
 ["Dream 2 Science","My Love Turns To Liquid","Deep house on Rush Hour, fresh in at Hard Wax this week."],
 ["Asa Tate","Feel So Good EP","From Redeye's house section; also on Bandcamp."],
 ["Optic Nerve aka Keith Tucker","Augmentations EP","Detroit electro from Keith Tucker on clear vinyl."]
];'''
h = h.replace(old_picks, new_picks)
open(dst, 'w', encoding='utf8').write(h)
print('ok', len(h))

#!/usr/bin/env python3
"""Write one week's records into index.html and archive them under data/.

Usage:
    python3 scripts/update_page.py week.json

week.json:
{
  "digest": {
    "week": "w/c 19 Oct 2026",
    "built": "Updated Mon 26 Oct with this week's digest email · refreshes every Monday",
    "status": [["Juno", 80, true, "One short sentence."], ...],     # Juno, Redeye, Hard Wax, Clone, Bandcamp, Fingerprints
    "playlists": [["Techno", "T", "https://open.spotify.com/playlist/..."], ...]   # [] if none
  },
  "records": [["J","T","Artist","Title","Label","Format","£13.99","In stock","https://..."], ...],
  "picks": [["Artist", "Title", "One short factual sentence."], ...]
}

Only the text between the WEEKLY DATA START and END marker lines in index.html
is replaced; everything else in the page stays byte-for-byte the same.
The script checks the result and exits non-zero (leaving index.html untouched)
if anything is wrong.
"""
import json, re, shutil, subprocess, sys, tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "index.html"
DATA = ROOT / "data"
START = "// ===== WEEKLY DATA START"
END = "// ===== WEEKLY DATA END ====="
STORES = set("JRHCB")
GENRES = set("TMDHE")
PL_GENRES = set("TDHE")


def die(msg):
    sys.exit(f"update_page: {msg}")


def clean(v):
    """Make a value safe inside the pipe-separated RAW template literal."""
    s = "" if v is None else str(v)
    s = re.sub(r"\s+", " ", s).strip()
    return (s.replace("|", "/").replace("`", "'").replace("\\", "/")
             .replace("${", "$ {"))


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def main(path):
    week = json.loads(Path(path).read_text(encoding="utf-8"))
    digest, records, picks = week["digest"], week["records"], week.get("picks", [])

    # --- digest
    for k in ("week", "built", "status", "playlists"):
        if k not in digest:
            die(f'digest is missing "{k}"')
    m = re.search(r"(\d{1,2} [A-Z][a-z]{2} \d{4})", digest["week"])
    if not m:
        die(f'digest.week should look like "w/c 19 Oct 2026", got {digest["week"]!r}')
    monday = datetime.strptime(m.group(1), "%d %b %Y").date()
    for s in digest["status"]:
        if not (len(s) == 4 and isinstance(s[1], int) and isinstance(s[2], bool)):
            die(f"bad status entry {s!r}: expected [store, count, ok, note]")
    for p in digest["playlists"]:
        if not (len(p) == 3 and p[1] in PL_GENRES and str(p[2]).startswith("https://open.spotify.com/")):
            die(f"bad playlist entry {p!r}: expected [name, T|D|H|E, open.spotify.com URL]")

    # --- records
    lines, keys = [], set()
    for i, r in enumerate(records, 1):
        if len(r) != 9:
            die(f"record {i} has {len(r)} fields, expected 9: {r!r}")
        r = [clean(x) for x in r]
        if r[0] not in STORES:
            die(f"record {i}: store must be one of J R H C B, got {r[0]!r}")
        if r[1] not in GENRES:
            die(f"record {i}: genre must be one of T M D H E, got {r[1]!r}")
        if not r[2] or not r[3]:
            die(f"record {i}: artist and title are required")
        if not r[8].startswith("http"):
            die(f"record {i}: URL must be a real product link, got {r[8]!r}")
        if "google.com/url" in r[8]:
            die(f"record {i}: URL is a Google redirect; use the store's own link")
        lines.append("|".join(r))
        keys.add((norm(r[2]), norm(r[3])))
    if not lines:
        die("no records")

    # --- picks: keep only ones that match a record exactly
    kept = []
    for p in picks:
        if len(p) == 3 and (norm(p[0]), norm(p[1])) in keys:
            kept.append([str(p[0]), str(p[1]), str(p[2])])
        else:
            print(f"update_page: dropped pick with no matching record: {p!r}", file=sys.stderr)

    block = "\n".join([
        "const DIGEST=" + json.dumps(digest, ensure_ascii=False) + ";",
        "const RAW=`" + "\n".join(lines) + "`;",
        "const PICKS=" + json.dumps(kept, ensure_ascii=False) + ";",
    ])

    # --- splice into the page
    page = PAGE.read_text(encoding="utf-8")
    if page.count(START) != 1 or page.count(END) != 1:
        die("index.html must contain each WEEKLY DATA marker exactly once")
    a = page.index("\n", page.index(START)) + 1
    b = page.index(END)
    new = page[:a] + block + "\n" + page[b:]

    # --- check the script still parses
    script = re.search(r"<script>(.*?)</script>", new, re.S)
    if not script:
        die("no <script> block found")
    if shutil.which("node"):
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
            f.write(script.group(1))
        res = subprocess.run(["node", "--check", f.name], capture_output=True, text=True)
        Path(f.name).unlink()
        if res.returncode:
            die("page script no longer parses:\n" + res.stderr)

    PAGE.write_text(new, encoding="utf-8")
    DATA.mkdir(exist_ok=True)
    out = DATA / f"records-{monday.isoformat()}.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"update_page: {len(lines)} records, {len(kept)} picks, "
          f"{len(digest['playlists'])} playlists for {digest['week']}; archived to {out.relative_to(ROOT)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        die("usage: python3 scripts/update_page.py week.json")
    main(sys.argv[1])

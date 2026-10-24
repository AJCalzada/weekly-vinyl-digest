# Weekly Vinyl Digest

A record-shop page of each week's new vinyl in Techno, Minimal/Tech House, Deep House, House and Electro, from six stores: Juno, Redeye, Bandcamp, Hard Wax, Clone and Fingerprints. It also links that week's Spotify preview playlists.

Live page: https://ajcalzada.github.io/weekly-vinyl-digest/

A scheduled Claude task runs every Monday morning. It collects the week's releases, builds the Spotify playlists, emails the digest, and updates this repo with a new commit, so the page refreshes each week and the history shows every week's records.

## Files

- `index.html` — the page. It has genre and store filters, search, sorting, and a Want list saved in your browser.
- `data/records-YYYY-MM-DD.txt` — each week's records, named by the Monday the week starts. One record per line: `store|genre|artist|title|label|format|price|status|url`.
- `scripts/update_page.py` — writes one week's records, picks, source notes and playlists into `index.html` and saves the week's file under `data/`. It only replaces the block between the `WEEKLY DATA` markers in the page, and refuses to write if the result doesn't check out.

Store codes: J Juno, R Redeye, B Bandcamp, H Hard Wax, C Clone. Genre codes: T Techno, M Minimal/Tech House, D Deep House, H House, E Electro.

Prices are as each store lists them (GBP, EUR or the Bandcamp seller's currency); Redeye prices are ex-VAT.

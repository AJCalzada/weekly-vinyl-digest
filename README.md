# Weekly Vinyl Digest

A record-shop page listing each week's new vinyl in Techno, Minimal/Tech House, Deep House, House and Electro, pulled from six stores: Juno, Redeye, Bandcamp, Hard Wax, Clone and Fingerprints.

- `index.html` — the page (week of 5 Oct 2026, 457 records). Open it in a browser; it has genre and store filters, search, sorting, and a Want list saved in your browser.
- `data/records-2026-10-05.txt` — the merged record list behind the page, one record per line: `store|genre|artist|title|label|format|price|status|url`.
- `scripts/build_raw.py` — merges the store listings into that record list and removes duplicates.
- `scripts/patch_page.py` — writes the record list, picks and source notes into the page.

Store codes: J Juno, R Redeye, B Bandcamp, H Hard Wax, C Clone. Genre codes: T Techno, M Minimal/Tech House, D Deep House, H House, E Electro.

Prices are as each store lists them (GBP, EUR or the Bandcamp seller's currency); Redeye prices are ex-VAT.

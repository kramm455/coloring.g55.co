# generate_sitemap.py
# Put this file in the same folder as pages.json
# Run: py generate_sitemap.py
# Output: sitemap.xml (in the same folder)

import json
import datetime
from urllib.parse import quote

def norm_base(base: str) -> str:
  base = (base or "").strip()
  if not base:
    raise ValueError("Missing site.baseUrl in pages.json (example: https://coloring.g55.co)")
  return base[:-1] if base.endswith("/") else base

def main():
  with open("pages.json", "r", encoding="utf-8") as f:
    data = json.load(f)

  base = norm_base(data.get("site", {}).get("baseUrl", ""))
  today = datetime.date.today().isoformat()

  urls = []

  # Home
  urls.append(f"""  <url>
    <loc>{base}/</loc>
    <lastmod>{today}</lastmod>
  </url>""")

  # Categories using index.html?c=...
  for c in data.get("categories", []):
    cid = c.get("id")
    if not cid:
      continue
    loc = f"{base}/?c={quote(str(cid), safe='')}"
    urls.append(f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{today}</lastmod>
  </url>""")

  # Pages using page.html?id=...
  for p in data.get("pages", []):
    pid = p.get("id")
    if not pid:
      continue
    loc = f"{base}/page.html?id={quote(str(pid), safe='')}"
    urls.append(f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{today}</lastmod>
  </url>""")

  xml = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "\n".join(urls) +
    "\n</urlset>\n"
  )

  with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write(xml)

  print(f"Generated sitemap.xml with {len(urls)} URLs")

if __name__ == "__main__":
  main()

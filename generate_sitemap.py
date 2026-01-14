import json
import datetime
from pathlib import Path
from urllib.parse import quote
import html

ROOT = Path(__file__).resolve().parent

def norm_base(base: str) -> str:
  base = (base or "").strip()
  if not base:
    raise ValueError("Missing site.baseUrl in pages.json (example: https://coloring.g55.co)")
  return base[:-1] if base.endswith("/") else base

def read_json(path: Path):
  with path.open("r", encoding="utf-8") as f:
    return json.load(f)

def q(value: str) -> str:
  return quote(str(value), safe="")

def xml_escape(s: str) -> str:
  # converts & to &amp; etc
  return html.escape(s, quote=True)

def main():
  index = read_json(ROOT / "pages.json")
  base = norm_base(index.get("site", {}).get("baseUrl", ""))
  today = datetime.date.today().isoformat()

  urls = []
  seen = set()

  def add_url(loc: str):
    if loc in seen:
      return
    seen.add(loc)
    urls.append(loc)

  add_url(f"{base}/")

  for c in index.get("categories", []):
    cid = c.get("id")
    if not cid:
      continue

    add_url(f"{base}/?c={q(cid)}")

    cat_path = ROOT / "categories" / f"{cid}.json"
    if not cat_path.exists():
      continue

    cat_data = read_json(cat_path)
    pages = cat_data.get("pages", [])
    if not isinstance(pages, list):
      continue

    for p in pages:
      pid = p.get("id")
      if not pid:
        continue
      add_url(f"{base}/page.html?id={q(pid)}&c={q(cid)}")

  lines = []
  lines.append('<?xml version="1.0" encoding="UTF-8"?>')
  lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

  for loc in urls:
    lines.append("  <url>")
    lines.append(f"    <loc>{xml_escape(loc)}</loc>")
    lines.append(f"    <lastmod>{today}</lastmod>")
    lines.append("  </url>")

  lines.append("</urlset>")
  xml = "\n".join(lines) + "\n"

  (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")
  print(f"Generated sitemap.xml with {len(urls)} URLs")

if __name__ == "__main__":
  main()

# generate_sitemaps.py  (Python 2.7)
# Creates:
#   - sitemap_index.xml
#   - sitemaps/sitemap_categories.xml
#   - sitemaps/sitemap_pages_001.xml, sitemap_pages_002.xml, ...
#
# Reads:
#   - pages.json (root) for site.baseUrl and categories list
#   - categories/<category_id>.json for pages
#
# Notes:
# - Escapes XML correctly (& becomes &amp;)
# - Splits page URLs into multiple sitemap files (default 40,000 per file)

import os
import json
import datetime
import codecs
from urllib import quote
from xml.sax.saxutils import escape as xml_escape

PAGES_PER_SITEMAP = 40000

def read_json(path):
  f = codecs.open(path, "r", "utf-8")
  try:
    return json.load(f)
  finally:
    f.close()

def write_text(path, text):
  f = codecs.open(path, "w", "utf-8")
  try:
    f.write(text)
  finally:
    f.close()

def norm_base(base):
  base = (base or "").strip()
  if not base:
    raise Exception("Missing site.baseUrl in pages.json (example: https://coloring.g55.co)")
  if base.endswith("/"):
    base = base[:-1]
  return base

def q(val):
  return quote(str(val), safe="")

def add_url(urls, seen, loc):
  if loc in seen:
    return
  seen.add(loc)
  urls.append(loc)

def build_urlset_xml(urls, lastmod):
  lines = []
  lines.append(u'<?xml version="1.0" encoding="UTF-8"?>')
  lines.append(u'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
  for loc in urls:
    safe_loc = xml_escape(loc)
    lines.append(u"  <url>")
    lines.append(u"    <loc>%s</loc>" % safe_loc)
    lines.append(u"    <lastmod>%s</lastmod>" % lastmod)
    lines.append(u"  </url>")
  lines.append(u"</urlset>")
  return u"\n".join(lines) + u"\n"

def build_sitemapindex_xml(sitemaps, lastmod):
  # sitemaps: list of absolute URLs to sitemap files
  lines = []
  lines.append(u'<?xml version="1.0" encoding="UTF-8"?>')
  lines.append(u'<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
  for loc in sitemaps:
    safe_loc = xml_escape(loc)
    lines.append(u"  <sitemap>")
    lines.append(u"    <loc>%s</loc>" % safe_loc)
    lines.append(u"    <lastmod>%s</lastmod>" % lastmod)
    lines.append(u"  </sitemap>")
  lines.append(u"</sitemapindex>")
  return u"\n".join(lines) + u"\n"

def chunk_list(lst, n):
  for i in range(0, len(lst), n):
    yield lst[i:i+n]

def main():
  root = os.path.dirname(os.path.abspath(__file__))

  index_path = os.path.join(root, "pages.json")
  if not os.path.exists(index_path):
    raise Exception("pages.json not found in root")

  index = read_json(index_path)
  base = norm_base(index.get("site", {}).get("baseUrl", ""))

  today = datetime.date.today().isoformat()

  # collect URLs
  seen = set()

  category_urls = []
  add_url(category_urls, seen, base + "/")  # include home in category sitemap
  categories = index.get("categories", [])
  if not isinstance(categories, list):
    categories = []

  pages_urls = []
  # don't share "seen" between categories and pages in case you want both types duplicated
  seen_pages = set()

  for c in categories:
    cid = c.get("id")
    if not cid:
      continue

    # category listing URL
    add_url(category_urls, seen, base + "/?c=" + q(cid))

    # load pages from category file
    cat_path = os.path.join(root, "categories", str(cid) + ".json")
    if not os.path.exists(cat_path):
      continue

    cat_data = read_json(cat_path)
    pages = cat_data.get("pages", [])
    if not isinstance(pages, list):
      continue

    for p in pages:
      pid = p.get("id")
      if not pid:
        continue
      loc = base + "/page.html?id=" + q(pid) + "&c=" + q(cid)
      add_url(pages_urls, seen_pages, loc)

  # output folder
  out_dir = os.path.join(root, "sitemaps")
  if not os.path.isdir(out_dir):
    os.makedirs(out_dir)

  sitemap_urls_for_index = []

  # 1) categories sitemap
  categories_filename = "sitemap_categories.xml"
  categories_path = os.path.join(out_dir, categories_filename)
  categories_xml = build_urlset_xml(category_urls, today)
  write_text(categories_path, categories_xml)
  sitemap_urls_for_index.append(base + "/sitemaps/" + categories_filename)

  # 2) pages sitemaps (chunked)
  page_files_count = 0
  for idx, chunk in enumerate(chunk_list(pages_urls, PAGES_PER_SITEMAP), start=1):
    page_files_count += 1
    fname = "sitemap_pages_%03d.xml" % idx
    fpath = os.path.join(out_dir, fname)
    xml = build_urlset_xml(chunk, today)
    write_text(fpath, xml)
    sitemap_urls_for_index.append(base + "/sitemaps/" + fname)

  # 3) sitemap index
  index_xml = build_sitemapindex_xml(sitemap_urls_for_index, today)
  index_out_path = os.path.join(root, "sitemap_index.xml")
  write_text(index_out_path, index_xml)

  print("Generated sitemap_index.xml")
  print("Generated %d category sitemap file" % 1)
  print("Generated %d page sitemap files" % page_files_count)
  print("Total page URLs: %d" % len(pages_urls))
  print("Submit this in Search Console: %s/sitemap_index.xml" % base)

if __name__ == "__main__":
  main()

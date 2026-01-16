<?php
// sitemap.php
// Dynamic sitemap index for your PHP site using JSON data.
// Outputs: XML sitemap index that points to:
//   - sitemap_categories.php
//   - sitemap_pages.php?n=1,2,3...
//
// Put in root with pages.json and categories/*.json
// URL:
//   sitemap.php

header('Content-Type: application/xml; charset=utf-8');

function read_json($path) {
  if (!file_exists($path)) return null;
  $raw = file_get_contents($path);
  if ($raw === false) return null;
  $data = json_decode($raw, true);
  return is_array($data) ? $data : null;
}

function norm_base($base) {
  $base = trim((string)$base);
  if ($base === '') return '';
  return rtrim($base, '/');
}

function xml_e($s) {
  return htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8');
}

function q($s) {
  return rawurlencode((string)$s);
}

function load_category_pages($cid) {
  $cid = preg_replace('/[^a-z0-9_-]/i', '', (string)$cid);
  $path = __DIR__ . DIRECTORY_SEPARATOR . 'categories' . DIRECTORY_SEPARATOR . $cid . '.json';
  $data = read_json($path);
  $pages = ($data && isset($data['pages']) && is_array($data['pages'])) ? $data['pages'] : [];
  return $pages;
}

$index = read_json(__DIR__ . DIRECTORY_SEPARATOR . 'pages.json');
$site = $index && isset($index['site']) ? $index['site'] : [];
$categories = $index && isset($index['categories']) && is_array($index['categories']) ? $index['categories'] : [];

$base = norm_base(isset($site['baseUrl']) ? $site['baseUrl'] : '');
if ($base === '') {
  // Fallback if baseUrl not set: build from request (works in most cases)
  $scheme = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') ? 'https' : 'http';
  $host = isset($_SERVER['HTTP_HOST']) ? $_SERVER['HTTP_HOST'] : 'localhost';
  $base = $scheme . '://' . $host;
}

$today = date('Y-m-d');

$allPageCount = 0;
foreach ($categories as $c) {
  $cid = isset($c['id']) ? $c['id'] : '';
  if ($cid === '') continue;
  $pages = load_category_pages($cid);
  $allPageCount += count($pages);
}

$perSitemap = 40000;
$pageSitemaps = (int)ceil(max(1, $allPageCount) / $perSitemap);
if ($allPageCount === 0) $pageSitemaps = 1;

echo '<?xml version="1.0" encoding="UTF-8"?>' . "\n";
echo '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' . "\n";

echo "  <sitemap>\n";
echo "    <loc>" . xml_e($base . "/sitemap_categories.php") . "</loc>\n";
echo "    <lastmod>" . xml_e($today) . "</lastmod>\n";
echo "  </sitemap>\n";

for ($i = 1; $i <= $pageSitemaps; $i++) {
  echo "  <sitemap>\n";
  echo "    <loc>" . xml_e($base . "/sitemap_pages.php?n=" . $i) . "</loc>\n";
  echo "    <lastmod>" . xml_e($today) . "</lastmod>\n";
  echo "  </sitemap>\n";
}

echo "</sitemapindex>\n";

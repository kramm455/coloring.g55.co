<?php
// app/index_pre.php
require_once __DIR__ . DIRECTORY_SEPARATOR . 'common.php';

$index = load_site_index();
$site = $index['site'] ?? [];
$categories = get_categories_sorted($index);

$cid = isset($_GET['c']) ? $_GET['c'] : '';
$cid = clean_slug($cid);
$isCategory = ($cid !== '');

$title = '';
$metaDesc = $site['description'] ?? '';
$canonical = 'https://coloring.g55.co/';

$h1 = '';
$desc = '';
$gridItems = []; // each: id,title,image,category

if (!$isCategory) {
  $totalCount = 0;

  foreach ($categories as $c) {
    $catId = $c['id'] ?? '';
    if (!$catId) continue;

    list($_, $pages) = load_category_pages($catId);
    $totalCount += count($pages);

    $newest = newest_page($pages);
    if ($newest && isset($newest['id'], $newest['title'], $newest['image'])) {
      $gridItems[] = [
        'id' => $newest['id'],
        'title' => $newest['title'],
        'image' => $newest['image'],
        'category' => $catId
      ];
    }
  }

  $h1Base = $site['h1'] ?? '';
  $h1 = ($totalCount > 0 ? $totalCount . ' ' : '') . $h1Base;
  $desc = $site['description'] ?? '';

  $title = $h1;
  $metaDesc = $site['description'] ?? '';
  $canonical = 'https://coloring.g55.co/';
} else {
  $cat = null;
  foreach ($categories as $c) {
    if (($c['id'] ?? '') === $cid) { $cat = $c; break; }
  }

  list($_, $pages) = load_category_pages($cid);
  $pages = array_reverse($pages);

  foreach ($pages as $p) {
    if (!isset($p['id'], $p['title'], $p['image'])) continue;
    $gridItems[] = [
      'id' => $p['id'],
      'title' => $p['title'],
      'image' => $p['image'],
      'category' => $cid
    ];
  }

  $catName = $cat['name'] ?? 'Category';
  $catDesc = $cat['description'] ?? ($site['description'] ?? '');

  $count = count($gridItems);
  $h1 = ($count > 0 ? $count . ' ' : '') . $catName;
  $desc = $catDesc;

  $title = $h1;
  $metaDesc = $catDesc;
  $canonical = 'https://coloring.g55.co/?c=' . rawurlencode($cid);
}

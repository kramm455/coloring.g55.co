<?php
// app/common.php

if (!headers_sent()) {
  header('Content-Type: text/html; charset=utf-8');
}

function h($s) {
  return htmlspecialchars($s ?? '', ENT_QUOTES, 'UTF-8');
}

function read_json($path) {
  if (!file_exists($path)) return null;
  $raw = file_get_contents($path);
  if ($raw === false) return null;
  $data = json_decode($raw, true);
  return is_array($data) ? $data : null;
}

function load_site_index() {
  return read_json(__DIR__ . DIRECTORY_SEPARATOR . '..' . DIRECTORY_SEPARATOR . 'pages.json');
}

function load_category_pages($cid) {
  $cid = preg_replace('/[^a-z0-9_-]/i', '', (string)$cid);
  $path = __DIR__ . DIRECTORY_SEPARATOR . '..' . DIRECTORY_SEPARATOR . 'categories' . DIRECTORY_SEPARATOR . $cid . '.json';
  $data = read_json($path);
  $pages = ($data && isset($data['pages']) && is_array($data['pages'])) ? $data['pages'] : [];
  return [$cid, $pages];
}

function sort_categories_alpha($cats) {
  usort($cats, function($a, $b) {
    return strcasecmp($a['name'] ?? '', $b['name'] ?? '');
  });
  return $cats;
}

function newest_page($pages) {
  $n = count($pages);
  return $n ? $pages[$n - 1] : null;
}

function get_categories_sorted($index) {
  $categories = $index['categories'] ?? [];
  if (!is_array($categories)) $categories = [];
  return sort_categories_alpha($categories);
}

function clean_slug($s) {
  return preg_replace('/[^a-z0-9_-]/i', '', (string)$s);
}

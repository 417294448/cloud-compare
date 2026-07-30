const fs = require('fs');
const path = require('path');
const { buildRows, buildCategories } = require('./lib/transform');

const ROOT = __dirname;
const DATA_PATH = path.join(ROOT, 'product-mapping.json');
const TEMPLATE_PATH = path.join(ROOT, 'index.template.html');
const QUERY_LIB_PATH = path.join(ROOT, 'lib', 'query.js');
const OUTPUT_PATH = path.join(ROOT, 'index.html');
const PRODUCT_SOURCE_FILES = {
  aws: 'products-aws.json',
  azure: 'products-azure.json',
  gcp: 'products-gcp.json',
  alibaba: 'products-alibabacloud.json',
};

function escapeScriptClose(str) {
  return str.replace(/<\/script/gi, '<\\/script');
}

function main() {
  const raw = JSON.parse(fs.readFileSync(DATA_PATH, 'utf8'));
  const rows = buildRows(raw);

  // 按各类目下产品数量降序排列，并过滤掉没有产品的空分类
  const catCounts = {};
  rows.forEach(function (row) {
    catCounts[row.category] = (catCounts[row.category] || 0) + 1;
  });
  const categories = buildCategories(raw)
    .filter(function (cat) { return catCounts[cat.name] > 0; })
    .sort(function (a, b) {
      return (catCounts[b.name] || 0) - (catCounts[a.name] || 0);
    });

  const sources = {};
  Object.keys(PRODUCT_SOURCE_FILES).forEach(function (vendor) {
    const filePath = path.join(ROOT, PRODUCT_SOURCE_FILES[vendor]);
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    sources[vendor] = { url: data.source, fetchedAt: data.fetchedAt };
  });

  const payload = {
    generatedAt: raw.generatedAt,
    categories: categories,
    rows: rows,
    sources: sources,
  };

  const template = fs.readFileSync(TEMPLATE_PATH, 'utf8');
  const queryLibSource = fs.readFileSync(QUERY_LIB_PATH, 'utf8');

  const html = template
    .replace('/*__QUERY_LIB__*/', escapeScriptClose(queryLibSource))
    .replace('/*__DATA__*/', escapeScriptClose(JSON.stringify(payload)));

  fs.writeFileSync(OUTPUT_PATH, html);
  console.log('Wrote ' + OUTPUT_PATH + ' with ' + payload.rows.length + ' rows across ' + payload.categories.length + ' categories.');
}

main();

const fs = require('fs');
const path = require('path');
const { buildRows, buildCategories } = require('./lib/transform');

const ROOT = __dirname;
const DATA_PATH = path.join(ROOT, 'product-mapping.json');
const TEMPLATE_PATH = path.join(ROOT, 'index.template.html');
const QUERY_LIB_PATH = path.join(ROOT, 'lib', 'query.js');
const OUTPUT_PATH = path.join(ROOT, 'index.html');

function escapeScriptClose(str) {
  return str.replace(/<\/script/gi, '<\\/script');
}

function main() {
  const raw = JSON.parse(fs.readFileSync(DATA_PATH, 'utf8'));
  const payload = {
    generatedAt: raw.generatedAt,
    categories: buildCategories(raw),
    rows: buildRows(raw),
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

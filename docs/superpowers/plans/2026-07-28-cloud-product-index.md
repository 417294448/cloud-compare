# Cloud Product Atlas (index.html) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate a self-contained, offline-capable `index.html` from `product-mapping.json` that lets engineers search/filter cross-cloud AWS/Azure/GCP product mappings, with a full EN/中文 language toggle.

**Architecture:** A Node build script (`build-index.js`) reads `product-mapping.json`, flattens the 67 curated `groups` and 646 `unmapped.*.trulyUnmapped` single-vendor entries into one unified `rows` array (via `lib/transform.js`), then splices that data plus a small pure query/filter library (`lib/query.js`) into an HTML template (`index.template.html`) to produce the final `index.html`. `lib/transform.js` and `lib/query.js` are unit tested with Node's built-in test runner; the generated page's DOM/interaction behavior is verified manually in a browser (there is no DOM test harness in this repo, and adding one — jsdom/puppeteer — would be a disproportionate new dependency for a single internal tool page).

**Tech Stack:** Plain Node.js (v18+, built-in `node:test`/`node:assert`) for the build script and tests. Zero-dependency vanilla HTML/CSS/JS for the generated page (no framework, no CDN JS, no `fetch` — data is inlined so the page works when double-clicked as a `file://` URL). Google Fonts `<link>` is used for typography with a system-font fallback stack, so the page still works fully offline, just with a plainer font.

---

## File Structure

- `lib/transform.js` — Node-only. Converts the raw `product-mapping.json` shape into the unified `rows`/`categories` shape the page consumes.
- `lib/transform.test.js` — Tests for the above.
- `lib/query.js` — Pure filter/sort/group functions. Written so the exact same file can be `require()`'d by Node tests **and** have its raw source spliced verbatim into the browser `<script>` (it guards its `module.exports` behind `typeof module !== 'undefined'`, which is `false` in a browser, so the guard is a no-op there).
- `lib/query.test.js` — Tests for the above.
- `index.template.html` — The full page shell: HTML structure, CSS, static UI-wiring JS (rendering, event listeners, i18n strings), with two placeholders (`/*__QUERY_LIB__*/`, `/*__DATA__*/`) that `build-index.js` fills in.
- `build-index.js` — Reads `product-mapping.json` + `index.template.html` + `lib/query.js`, writes the final `index.html`.
- `index.html` — Generated output, committed to the repo root so it works standalone without running Node.

---

### Task 1: Data transform (`lib/transform.js`)

**Files:**
- Create: `lib/transform.js`
- Create: `lib/transform.test.js`

- [ ] **Step 1: Write the failing tests**

Create `lib/transform.test.js`:

```js
const test = require('node:test');
const assert = require('node:assert/strict');
const { buildRows, buildCategories, groupToRow, normalizeProducts } = require('./transform');

function makeFixture() {
  return {
    allCategories: ['Compute', 'Storage'],
    'categoryLabels-cn': { Compute: '计算服务' },
    groups: [
      {
        id: 'compute-vm',
        category: 'Compute',
        'category-cn': '计算服务',
        name: 'Virtual Machine',
        'name-cn': '虚拟机',
        confidence: 'high',
        notes: 'Flagship VM product.',
        'notes-cn': '旗舰虚拟机产品。',
        products: {
          aws: [{ name: 'EC2', link: 'https://aws.example/ec2', description: 'Run VMs', 'description-cn': '运行虚拟机' }],
          azure: [{ name: 'Virtual Machines', link: 'https://azure.example/vm', description: 'Provision VMs', 'description-cn': null }],
          gcp: [],
        },
      },
    ],
    unmapped: {
      Storage: {
        aws: {
          trulyUnmapped: [
            {
              id: 'unmapped-aws-glacier',
              category: 'Storage',
              'category-cn': '存储',
              name: 'Glacier',
              'name-cn': '',
              confidence: 'none',
              notes: 'No confirmed counterpart yet.',
              'notes-cn': '',
              products: {
                aws: [{ name: 'S3 Glacier', link: 'https://aws.example/glacier', description: 'Cold storage', 'description-cn': null }],
                azure: [],
                gcp: [],
              },
            },
          ],
          mappedUnderOtherCategory: ['Some Other Product'],
        },
        azure: { trulyUnmapped: [], mappedUnderOtherCategory: [] },
        gcp: { trulyUnmapped: [], mappedUnderOtherCategory: [] },
      },
    },
  };
}

test('buildCategories pairs english categories with cn labels, falling back to english name', () => {
  const categories = buildCategories(makeFixture());
  assert.deepEqual(categories, [
    { name: 'Compute', nameCn: '计算服务' },
    { name: 'Storage', nameCn: 'Storage' },
  ]);
});

test('normalizeProducts falls back to english description when description-cn is missing', () => {
  const products = normalizeProducts([
    { name: 'X', link: 'https://x', description: 'English desc', 'description-cn': null },
  ]);
  assert.equal(products[0].descriptionCn, 'English desc');
});

test('groupToRow falls back to english name/notes when the -cn field is empty', () => {
  const row = groupToRow({
    id: 'x', category: 'Storage', 'category-cn': '存储', name: 'Glacier', 'name-cn': '',
    confidence: 'none', notes: 'note', 'notes-cn': '',
    products: { aws: [], azure: [], gcp: [] },
  });
  assert.equal(row.nameCn, 'Glacier');
  assert.equal(row.notesCn, 'note');
});

test('buildRows combines curated groups with unmapped.trulyUnmapped entries, ignoring mappedUnderOtherCategory', () => {
  const rows = buildRows(makeFixture());
  assert.equal(rows.length, 2);
  const ids = rows.map((r) => r.id);
  assert.deepEqual(ids, ['compute-vm', 'unmapped-aws-glacier']);
  const unmappedRow = rows[1];
  assert.equal(unmappedRow.confidence, 'none');
  assert.equal(unmappedRow.products.aws.length, 1);
  assert.equal(unmappedRow.products.azure.length, 0);
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `node --test lib/transform.test.js`
Expected: fails with `Cannot find module './transform'` (file doesn't exist yet).

- [ ] **Step 3: Write the implementation**

Create `lib/transform.js`:

```js
function normalizeProduct(p) {
  return {
    name: p.name,
    link: p.link,
    description: p.description || '',
    descriptionCn: (p['description-cn'] && String(p['description-cn']).trim())
      ? p['description-cn']
      : (p.description || ''),
  };
}

function normalizeProducts(list) {
  return (list || []).map(normalizeProduct);
}

function groupToRow(g) {
  return {
    id: g.id,
    category: g.category,
    categoryCn: g['category-cn'] || g.category,
    name: g.name,
    nameCn: (g['name-cn'] && String(g['name-cn']).trim()) ? g['name-cn'] : g.name,
    confidence: g.confidence,
    notes: g.notes || '',
    notesCn: (g['notes-cn'] && String(g['notes-cn']).trim()) ? g['notes-cn'] : (g.notes || ''),
    products: {
      aws: normalizeProducts(g.products.aws),
      azure: normalizeProducts(g.products.azure),
      gcp: normalizeProducts(g.products.gcp),
    },
  };
}

function buildRows(data) {
  const rows = data.groups.map(groupToRow);
  const unmapped = data.unmapped || {};
  Object.keys(unmapped).forEach((category) => {
    ['aws', 'azure', 'gcp'].forEach((vendor) => {
      const bucket = unmapped[category][vendor];
      if (!bucket) return;
      (bucket.trulyUnmapped || []).forEach((g) => {
        rows.push(groupToRow(g));
      });
    });
  });
  return rows;
}

function buildCategories(data) {
  const labelsCn = data['categoryLabels-cn'] || {};
  return data.allCategories.map((name) => ({
    name,
    nameCn: labelsCn[name] || name,
  }));
}

module.exports = { normalizeProduct, normalizeProducts, groupToRow, buildRows, buildCategories };
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `node --test lib/transform.test.js`
Expected: `pass 4`, `fail 0`.

- [ ] **Step 5: Commit**

```bash
git add lib/transform.js lib/transform.test.js
git commit -m "feat: add product-mapping.json to unified rows transform"
```

---

### Task 2: Pure query/filter library (`lib/query.js`)

**Files:**
- Create: `lib/query.js`
- Create: `lib/query.test.js`

- [ ] **Step 1: Write the failing tests**

Create `lib/query.test.js`:

```js
const test = require('node:test');
const assert = require('node:assert/strict');
const {
  localize, rowMatchesVendors, rowMatchesQuery, filterRows, sortRows, groupByCategory,
} = require('./query');

function row(overrides) {
  return Object.assign({
    id: 'r1', category: 'Compute', categoryCn: '计算服务',
    name: 'Virtual Machine', nameCn: '虚拟机', confidence: 'high',
    notes: '', notesCn: '',
    products: {
      aws: [{ name: 'EC2', link: 'x', description: 'Run VMs', descriptionCn: '运行虚拟机' }],
      azure: [], gcp: [],
    },
  }, overrides);
}

test('localize prefers the chinese string, falling back to english when blank', () => {
  assert.equal(localize('English', '中文'), '中文');
  assert.equal(localize('English', ''), 'English');
  assert.equal(localize('English', null), 'English');
});

test('rowMatchesVendors requires every selected vendor to have at least one product (AND semantics)', () => {
  const r = row();
  assert.equal(rowMatchesVendors(r, []), true);
  assert.equal(rowMatchesVendors(r, ['aws']), true);
  assert.equal(rowMatchesVendors(r, ['azure']), false);
  assert.equal(rowMatchesVendors(r, ['aws', 'azure']), false);
});

test('rowMatchesQuery matches english or chinese fields case-insensitively', () => {
  const r = row();
  assert.equal(rowMatchesQuery(r, 'ec2'), true);
  assert.equal(rowMatchesQuery(r, '虚拟机'), true);
  assert.equal(rowMatchesQuery(r, 'nonexistent'), false);
  assert.equal(rowMatchesQuery(r, ''), true);
});

test('filterRows combines category, vendor and query filters', () => {
  const rows = [
    row({ id: 'a', category: 'Compute' }),
    row({
      id: 'b',
      category: 'Storage',
      products: { aws: [], azure: [{ name: 'Blob', link: 'x', description: 'Object storage', descriptionCn: '对象存储' }], gcp: [] },
    }),
  ];
  assert.deepEqual(filterRows(rows, { category: 'Storage' }).map((r) => r.id), ['b']);
  assert.deepEqual(filterRows(rows, { vendors: ['azure'] }).map((r) => r.id), ['b']);
  assert.deepEqual(filterRows(rows, { query: 'blob' }).map((r) => r.id), ['b']);
});

test('sortRows orders by confidence rank (high before none) then alphabetically', () => {
  const rows = [
    row({ id: 'z', name: 'Zeta', confidence: 'none' }),
    row({ id: 'a', name: 'Alpha', confidence: 'high' }),
    row({ id: 'm', name: 'Mid', confidence: 'medium' }),
  ];
  assert.deepEqual(sortRows(rows).map((r) => r.id), ['a', 'm', 'z']);
});

test('groupByCategory groups sorted rows and preserves the canonical category order', () => {
  const rows = [
    row({ id: 'a', category: 'Storage', name: 'Alpha', confidence: 'high' }),
    row({ id: 'b', category: 'Compute', name: 'Beta', confidence: 'high' }),
  ];
  const categories = [{ name: 'Compute', nameCn: '计算服务' }, { name: 'Storage', nameCn: '存储' }];
  const grouped = groupByCategory(rows, categories);
  assert.deepEqual(grouped.map((g) => g.category.name), ['Compute', 'Storage']);
  assert.equal(grouped[0].rows[0].id, 'b');
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `node --test lib/query.test.js`
Expected: fails with `Cannot find module './query'`.

- [ ] **Step 3: Write the implementation**

Create `lib/query.js`:

```js
function localize(en, cn) {
  return (cn && String(cn).trim()) ? cn : en;
}

function rowMatchesVendors(row, vendors) {
  if (!vendors || !vendors.length) return true;
  return vendors.every(function (vendor) {
    return row.products[vendor] && row.products[vendor].length > 0;
  });
}

function rowMatchesQuery(row, query) {
  if (!query) return true;
  var q = String(query).trim().toLowerCase();
  if (!q) return true;
  var haystacks = [row.name, row.nameCn, row.category, row.categoryCn];
  ['aws', 'azure', 'gcp'].forEach(function (vendor) {
    (row.products[vendor] || []).forEach(function (p) {
      haystacks.push(p.name, p.description, p.descriptionCn);
    });
  });
  return haystacks.some(function (text) {
    return text && String(text).toLowerCase().indexOf(q) !== -1;
  });
}

function filterRows(rows, filters) {
  filters = filters || {};
  var category = filters.category;
  var vendors = filters.vendors;
  var query = filters.query;
  return rows.filter(function (row) {
    if (category && category !== 'all' && row.category !== category) return false;
    if (!rowMatchesVendors(row, vendors)) return false;
    if (!rowMatchesQuery(row, query)) return false;
    return true;
  });
}

var CONFIDENCE_RANK = { high: 0, medium: 1, low: 2, none: 3 };

function sortRows(rows) {
  return rows.slice().sort(function (a, b) {
    var rankDiff = CONFIDENCE_RANK[a.confidence] - CONFIDENCE_RANK[b.confidence];
    if (rankDiff !== 0) return rankDiff;
    return a.name.localeCompare(b.name);
  });
}

function groupByCategory(rows, categories) {
  var sorted = sortRows(rows);
  var byCategory = {};
  sorted.forEach(function (row) {
    if (!byCategory[row.category]) byCategory[row.category] = [];
    byCategory[row.category].push(row);
  });
  return categories
    .filter(function (cat) { return byCategory[cat.name]; })
    .map(function (cat) { return { category: cat, rows: byCategory[cat.name] }; });
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    localize: localize,
    rowMatchesVendors: rowMatchesVendors,
    rowMatchesQuery: rowMatchesQuery,
    filterRows: filterRows,
    sortRows: sortRows,
    groupByCategory: groupByCategory,
    CONFIDENCE_RANK: CONFIDENCE_RANK,
  };
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `node --test lib/query.test.js`
Expected: `pass 6`, `fail 0`.

- [ ] **Step 5: Commit**

```bash
git add lib/query.js lib/query.test.js
git commit -m "feat: add pure filter/sort/group query library"
```

---

### Task 3: Page template (`index.template.html`)

**Files:**
- Create: `index.template.html`

Design direction: a dark "cloud console" aesthetic — deep charcoal-navy background, `IBM Plex Mono` for headings/labels/badges (technical, dashboard feel), `IBM Plex Sans` for body/description text. Each vendor column carries its own accent color (AWS amber `#ff9900`, Azure blue `#3aa0ff`, GCP green `#34a853`) via a left border + tinted link color, so scanning a row's color pattern shows vendor coverage at a glance. Category headers render as monospace `// Category Name` comment-style rows, sticky under the filter bar while scrolling.

- [ ] **Step 1: Write the HTML skeleton, CSS, and structure**

Create `index.template.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Cloud Product Atlas — AWS · Azure · GCP</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0b0f14;
    --bg-raised: #121820;
    --bg-header: #0e131a;
    --grid-line: #1e2733;
    --text-primary: #e8edf2;
    --text-muted: #8a97a6;
    --text-dim: #5b6875;
    --accent-aws: #ff9900;
    --accent-azure: #3aa0ff;
    --accent-gcp: #34a853;
    --badge-high-bg: rgba(52, 199, 132, 0.14);
    --badge-high-fg: #34c784;
    --badge-medium-bg: rgba(255, 176, 32, 0.14);
    --badge-medium-fg: #ffb020;
    --badge-low-bg: rgba(122, 139, 158, 0.16);
    --badge-low-fg: #9aabbd;
    --badge-none-bg: rgba(90, 100, 112, 0.14);
    --badge-none-fg: #6b7684;
    --font-mono: 'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    --font-sans: 'IBM Plex Sans', -apple-system, "Segoe UI", sans-serif;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; height: 100%; }
  body {
    background: var(--bg);
    background-image:
      radial-gradient(circle at 15% 0%, rgba(58, 160, 255, 0.07), transparent 40%),
      radial-gradient(circle at 85% 8%, rgba(255, 153, 0, 0.06), transparent 35%);
    color: var(--text-primary);
    font-family: var(--font-sans);
    -webkit-font-smoothing: antialiased;
  }
  a { color: inherit; }

  .topbar {
    position: sticky; top: 0; z-index: 30;
    display: flex; align-items: center; justify-content: space-between;
    gap: 16px; padding: 18px 28px;
    background: var(--bg-header);
    border-bottom: 1px solid var(--grid-line);
  }
  .brand { display: flex; align-items: baseline; gap: 12px; }
  .brand-mark { font-size: 22px; }
  .brand h1 {
    margin: 0; font-family: var(--font-mono); font-size: 18px; font-weight: 600;
    letter-spacing: 0.06em; text-transform: uppercase;
  }
  .subtitle { margin: 2px 0 0; font-size: 13px; color: var(--text-muted); }

  .lang-toggle { display: flex; border: 1px solid var(--grid-line); border-radius: 6px; overflow: hidden; }
  .lang-btn {
    font-family: var(--font-mono); font-size: 12px; letter-spacing: 0.04em;
    padding: 7px 14px; background: transparent; color: var(--text-muted);
    border: none; cursor: pointer; transition: background 0.15s, color 0.15s;
  }
  .lang-btn + .lang-btn { border-left: 1px solid var(--grid-line); }
  .lang-btn.is-active { background: var(--accent-azure); color: #051018; }
  .lang-btn:not(.is-active):hover { background: var(--bg-raised); color: var(--text-primary); }

  .filterbar {
    position: sticky; top: 61px; z-index: 25;
    display: flex; flex-wrap: wrap; align-items: center; gap: 20px;
    padding: 14px 28px; background: var(--bg-header);
    border-bottom: 1px solid var(--grid-line);
  }
  .filter-group { display: flex; align-items: center; gap: 10px; }
  .filter-group label, .filter-group > span:first-child {
    font-family: var(--font-mono); font-size: 11px; text-transform: uppercase;
    letter-spacing: 0.08em; color: var(--text-dim);
  }
  #category-select {
    background: var(--bg-raised); color: var(--text-primary);
    border: 1px solid var(--grid-line); border-radius: 6px;
    padding: 7px 10px; font-family: var(--font-sans); font-size: 13px;
  }
  .vendor-chips { display: flex; gap: 6px; }
  .vendor-chip {
    font-family: var(--font-mono); font-size: 12px; font-weight: 600;
    padding: 6px 12px; border-radius: 999px; cursor: pointer;
    background: transparent; color: var(--text-muted);
    border: 1px solid var(--grid-line); transition: all 0.15s;
  }
  .vendor-chip--aws.is-active { background: rgba(255,153,0,0.16); border-color: var(--accent-aws); color: var(--accent-aws); }
  .vendor-chip--azure.is-active { background: rgba(58,160,255,0.16); border-color: var(--accent-azure); color: var(--accent-azure); }
  .vendor-chip--gcp.is-active { background: rgba(52,168,83,0.16); border-color: var(--accent-gcp); color: var(--accent-gcp); }

  .filter-group--search { flex: 1 1 240px; min-width: 200px; }
  #search-input {
    width: 100%; background: var(--bg-raised); color: var(--text-primary);
    border: 1px solid var(--grid-line); border-radius: 6px;
    padding: 8px 12px; font-family: var(--font-sans); font-size: 13px;
  }
  #search-input:focus, #category-select:focus { outline: 2px solid var(--accent-azure); outline-offset: 1px; }

  .result-count {
    margin-left: auto; font-family: var(--font-mono); font-size: 12px; color: var(--text-dim);
    white-space: nowrap;
  }

  .table-wrap { padding: 0 28px 48px; animation: fade-in 0.4s ease-out; }
  @keyframes fade-in { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: none; } }

  .data-table { width: 100%; border-collapse: collapse; table-layout: fixed; margin-top: 18px; }
  thead th {
    text-align: left; font-family: var(--font-mono); font-size: 11px;
    text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-dim);
    padding: 10px 12px; border-bottom: 1px solid var(--grid-line);
  }
  .th-vendor--aws { color: var(--accent-aws); }
  .th-vendor--azure { color: var(--accent-azure); }
  .th-vendor--gcp { color: var(--accent-gcp); }

  .category-row td {
    position: sticky; top: 121px; z-index: 10;
    background: var(--bg); padding: 14px 12px 6px; border-bottom: 1px solid var(--grid-line);
  }
  .category-tag { font-family: var(--font-mono); font-size: 12px; color: var(--text-muted); letter-spacing: 0.02em; }
  .category-count {
    margin-left: 8px; font-family: var(--font-mono); font-size: 11px; color: var(--text-dim);
    background: var(--bg-raised); border-radius: 999px; padding: 1px 8px;
  }

  .data-row td { vertical-align: top; padding: 12px; border-bottom: 1px solid var(--grid-line); font-size: 13px; }
  .col-concept .concept-name { font-weight: 600; margin-bottom: 6px; }
  .notes-toggle {
    font-family: var(--font-mono); font-size: 11px; color: var(--accent-azure);
    background: none; border: none; padding: 0; cursor: pointer; text-decoration: underline dotted;
  }

  .product { padding-left: 10px; border-left: 3px solid var(--grid-line); margin-bottom: 10px; }
  .product:last-child { margin-bottom: 0; }
  .product--aws { border-left-color: var(--accent-aws); }
  .product--azure { border-left-color: var(--accent-azure); }
  .product--gcp { border-left-color: var(--accent-gcp); }
  .product-name { display: inline-block; font-weight: 600; text-decoration: none; }
  .product--aws .product-name { color: var(--accent-aws); }
  .product--azure .product-name { color: var(--accent-azure); }
  .product--gcp .product-name { color: var(--accent-gcp); }
  .product-name:hover { text-decoration: underline; }
  .product-desc { margin-top: 2px; font-size: 12px; color: var(--text-muted); line-height: 1.4; }
  .cell-empty { color: var(--text-dim); }

  .badge {
    display: inline-flex; align-items: center; gap: 6px;
    font-family: var(--font-mono); font-size: 11px; padding: 4px 10px; border-radius: 999px;
  }
  .badge::before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
  .badge--high { background: var(--badge-high-bg); color: var(--badge-high-fg); }
  .badge--medium { background: var(--badge-medium-bg); color: var(--badge-medium-fg); }
  .badge--low { background: var(--badge-low-bg); color: var(--badge-low-fg); }
  .badge--none { background: var(--badge-none-bg); color: var(--badge-none-fg); }

  .notes-row td { padding: 0 12px 14px; border-bottom: 1px solid var(--grid-line); }
  .notes-box {
    background: var(--bg-raised); border: 1px solid var(--grid-line); border-radius: 6px;
    padding: 10px 14px; font-size: 12px; color: var(--text-muted); line-height: 1.5;
  }
  .empty-row td { padding: 40px 12px; text-align: center; color: var(--text-dim); font-size: 13px; }

  .page-footer {
    padding: 18px 28px 32px; font-family: var(--font-mono); font-size: 11px; color: var(--text-dim);
  }

  @media (max-width: 860px) {
    .table-wrap { overflow-x: auto; }
    .data-table { min-width: 900px; }
    .filterbar { top: 0; position: relative; }
    .category-row td { position: static; }
    .topbar { position: relative; }
  }
</style>
</head>
<body>
  <header class="topbar">
    <div class="brand">
      <span class="brand-mark">☁</span>
      <div>
        <h1 id="page-title">Cloud Product Atlas</h1>
        <p id="page-subtitle" class="subtitle">Cross-cloud product mapping for AWS, Azure &amp; GCP</p>
      </div>
    </div>
    <div class="lang-toggle" role="group" aria-label="Language">
      <button type="button" class="lang-btn is-active" data-lang="en">EN</button>
      <button type="button" class="lang-btn" data-lang="cn">中文</button>
    </div>
  </header>

  <div class="filterbar">
    <div class="filter-group">
      <label id="category-label" for="category-select">Category</label>
      <select id="category-select"></select>
    </div>
    <div class="filter-group">
      <span id="vendor-label">Has product on</span>
      <div class="vendor-chips">
        <button type="button" class="vendor-chip vendor-chip--aws" data-vendor="aws">AWS</button>
        <button type="button" class="vendor-chip vendor-chip--azure" data-vendor="azure">Azure</button>
        <button type="button" class="vendor-chip vendor-chip--gcp" data-vendor="gcp">GCP</button>
      </div>
    </div>
    <div class="filter-group filter-group--search">
      <input id="search-input" type="search" placeholder="Search products, concepts, descriptions…" />
    </div>
    <div id="result-count" class="result-count"></div>
  </div>

  <main class="table-wrap">
    <table class="data-table">
      <colgroup>
        <col style="width: 24%">
        <col style="width: 21%">
        <col style="width: 21%">
        <col style="width: 21%">
        <col style="width: 13%">
      </colgroup>
      <thead>
        <tr>
          <th id="col-concept">Concept</th>
          <th class="th-vendor th-vendor--aws">AWS</th>
          <th class="th-vendor th-vendor--azure">Azure</th>
          <th class="th-vendor th-vendor--gcp">GCP</th>
          <th id="col-confidence">Match</th>
        </tr>
      </thead>
      <tbody id="data-body"></tbody>
    </table>
  </main>

  <footer class="page-footer">
    <span id="footer-text"></span>
  </footer>

  <script>
  /*__QUERY_LIB__*/
  </script>
</body>
</html>
```

- [ ] **Step 2: Add the data payload placeholder and UI-wiring JS**

Add a second `<script>` block right before `</body>`, after the query-lib `<script>` block added in Step 1:

```html
  <script>
  var PAYLOAD = /*__DATA__*/;

  var state = { lang: 'en', category: 'all', vendors: [], query: '' };
  var expanded = {};

  var UI_STRINGS = {
    en: {
      title: 'Cloud Product Atlas',
      subtitle: 'Cross-cloud product mapping for AWS, Azure & GCP',
      categoryAll: 'All categories',
      categoryLabel: 'Category',
      vendorLabel: 'Has product on',
      searchPlaceholder: 'Search products, concepts, descriptions…',
      resultCount: function (n, total) { return 'Showing ' + n + ' of ' + total; },
      noResults: 'No matching products. Try clearing a filter.',
      notesShow: 'Why this pairing?',
      notesHide: 'Hide notes',
      colConcept: 'Concept',
      colConfidence: 'Match',
      noEquivalent: '—',
      confidence: { high: 'High match', medium: 'Medium match', low: 'Low match', none: 'Unmatched' },
      footer: 'Generated from product-mapping.json · '
    },
    cn: {
      title: '云产品图谱',
      subtitle: 'AWS / Azure / GCP 跨云产品映射查询',
      categoryAll: '全部分类',
      categoryLabel: '分类',
      vendorLabel: '需包含厂商',
      searchPlaceholder: '搜索产品、概念、描述…',
      resultCount: function (n, total) { return '共命中 ' + n + ' / ' + total + ' 条'; },
      noResults: '没有匹配的产品，试试清空筛选条件。',
      notesShow: '配对说明',
      notesHide: '收起说明',
      colConcept: '概念',
      colConfidence: '匹配度',
      noEquivalent: '—',
      confidence: { high: '高置信度', medium: '中等置信度', low: '低置信度', none: '暂未匹配' },
      footer: '数据来自 product-mapping.json · 生成时间 '
    }
  };

  function currentStrings() { return UI_STRINGS[state.lang]; }

  function escapeHtml(str) {
    return String(str == null ? '' : str).replace(/[&<>"']/g, function (ch) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch];
    });
  }

  function renderProductCell(products, vendor) {
    var t = currentStrings();
    if (!products || !products.length) {
      return '<span class="cell-empty">' + t.noEquivalent + '</span>';
    }
    return products.map(function (p) {
      var desc = state.lang === 'cn' ? p.descriptionCn : p.description;
      return (
        '<div class="product product--' + vendor + '">' +
          '<a class="product-name" href="' + escapeHtml(p.link) + '" target="_blank" rel="noopener">' + escapeHtml(p.name) + '</a>' +
          '<div class="product-desc">' + escapeHtml(desc) + '</div>' +
        '</div>'
      );
    }).join('');
  }

  function renderRow(row) {
    var t = currentStrings();
    var name = state.lang === 'cn' ? row.nameCn : row.name;
    var notes = state.lang === 'cn' ? row.notesCn : row.notes;
    var isExpanded = !!expanded[row.id];
    var hasNotes = !!(notes && notes.trim());
    var html =
      '<tr class="data-row" data-id="' + row.id + '">' +
        '<td class="col-concept">' +
          '<div class="concept-name">' + escapeHtml(name) + '</div>' +
          (hasNotes ? '<button type="button" class="notes-toggle" data-toggle-id="' + row.id + '">' + (isExpanded ? t.notesHide : t.notesShow) + '</button>' : '') +
        '</td>' +
        '<td class="col-vendor">' + renderProductCell(row.products.aws, 'aws') + '</td>' +
        '<td class="col-vendor">' + renderProductCell(row.products.azure, 'azure') + '</td>' +
        '<td class="col-vendor">' + renderProductCell(row.products.gcp, 'gcp') + '</td>' +
        '<td class="col-confidence"><span class="badge badge--' + row.confidence + '">' + t.confidence[row.confidence] + '</span></td>' +
      '</tr>';
    if (hasNotes && isExpanded) {
      html +=
        '<tr class="notes-row" data-notes-for="' + row.id + '">' +
          '<td colspan="5"><div class="notes-box">' + escapeHtml(notes) + '</div></td>' +
        '</tr>';
    }
    return html;
  }

  function renderTable(groups, matchCount, totalCount) {
    var t = currentStrings();
    var tbody = document.getElementById('data-body');
    document.getElementById('result-count').textContent = t.resultCount(matchCount, totalCount);

    if (!groups.length) {
      tbody.innerHTML = '<tr class="empty-row"><td colspan="5">' + escapeHtml(t.noResults) + '</td></tr>';
      return;
    }

    var html = '';
    groups.forEach(function (group) {
      var catLabel = state.lang === 'cn' ? group.category.nameCn : group.category.name;
      html +=
        '<tr class="category-row">' +
          '<td colspan="5"><span class="category-tag">// ' + escapeHtml(catLabel) + '</span><span class="category-count">' + group.rows.length + '</span></td>' +
        '</tr>';
      group.rows.forEach(function (row) {
        html += renderRow(row);
      });
    });
    tbody.innerHTML = html;
  }

  function refresh() {
    var filtered = filterRows(PAYLOAD.rows, { category: state.category, vendors: state.vendors, query: state.query });
    var groups = groupByCategory(filtered, PAYLOAD.categories);
    renderTable(groups, filtered.length, PAYLOAD.rows.length);
  }

  function populateCategorySelect() {
    var select = document.getElementById('category-select');
    var t = currentStrings();
    var options = ['<option value="all">' + escapeHtml(t.categoryAll) + '</option>'];
    PAYLOAD.categories.forEach(function (cat) {
      var label = state.lang === 'cn' ? cat.nameCn : cat.name;
      options.push('<option value="' + escapeHtml(cat.name) + '"' + (state.category === cat.name ? ' selected' : '') + '>' + escapeHtml(label) + '</option>');
    });
    select.innerHTML = options.join('');
  }

  function applyStaticText() {
    var t = currentStrings();
    document.documentElement.lang = state.lang === 'cn' ? 'zh-CN' : 'en';
    document.getElementById('page-title').textContent = t.title;
    document.getElementById('page-subtitle').textContent = t.subtitle;
    document.getElementById('category-label').textContent = t.categoryLabel;
    document.getElementById('vendor-label').textContent = t.vendorLabel;
    document.getElementById('search-input').setAttribute('placeholder', t.searchPlaceholder);
    document.getElementById('col-concept').textContent = t.colConcept;
    document.getElementById('col-confidence').textContent = t.colConfidence;
    document.getElementById('footer-text').textContent = t.footer + PAYLOAD.generatedAt;
    populateCategorySelect();
  }

  document.querySelectorAll('.lang-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      state.lang = btn.getAttribute('data-lang');
      document.querySelectorAll('.lang-btn').forEach(function (b) {
        b.classList.toggle('is-active', b === btn);
      });
      applyStaticText();
      refresh();
    });
  });

  document.querySelectorAll('.vendor-chip').forEach(function (chip) {
    chip.addEventListener('click', function () {
      var vendor = chip.getAttribute('data-vendor');
      chip.classList.toggle('is-active');
      var idx = state.vendors.indexOf(vendor);
      if (chip.classList.contains('is-active') && idx === -1) {
        state.vendors.push(vendor);
      } else if (!chip.classList.contains('is-active') && idx !== -1) {
        state.vendors.splice(idx, 1);
      }
      refresh();
    });
  });

  document.getElementById('category-select').addEventListener('change', function (e) {
    state.category = e.target.value;
    refresh();
  });

  document.getElementById('search-input').addEventListener('input', function (e) {
    state.query = e.target.value;
    refresh();
  });

  document.getElementById('data-body').addEventListener('click', function (e) {
    var btn = e.target.closest('.notes-toggle');
    if (!btn) return;
    var id = btn.getAttribute('data-toggle-id');
    expanded[id] = !expanded[id];
    refresh();
  });

  applyStaticText();
  refresh();
  </script>
```

- [ ] **Step 3: Commit**

```bash
git add index.template.html
git commit -m "feat: add cloud product atlas page template"
```

---

### Task 4: Build script (`build-index.js`) and first generation

**Files:**
- Create: `build-index.js`
- Create (generated): `index.html`

- [ ] **Step 1: Write `build-index.js`**

```js
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
```

- [ ] **Step 2: Run the build and sanity-check the output**

Run: `node build-index.js`
Expected output: `Wrote .../index.html with 713 rows across 55 categories.` (row/category counts should match `node -e "const d=require('./product-mapping.json'); ..."` totals gathered during design — 67 curated groups + 646 trulyUnmapped entries = 713 rows, 55 categories).

Then sanity check the generated file is well-formed:

Run: `node -e "require('./index.html')" 2>&1 | head -1 || true` — not meaningful (it's HTML, not JS); instead verify manually:

Run: `node -e "const html = require('fs').readFileSync('index.html','utf8'); console.log(html.includes('/*__DATA__*/'), html.includes('/*__QUERY_LIB__*/'), html.length);"`
Expected: `false false <some large number>` — confirms both placeholders were replaced and the file has substantial content.

- [ ] **Step 3: Commit**

```bash
git add build-index.js index.html
git commit -m "feat: generate index.html from product-mapping.json"
```

---

### Task 5: Manual browser verification

**Files:** none (verification only; fix forward in `index.template.html` + re-run `node build-index.js` if any check fails, then amend the commit's follow-up with a new commit).

There is no automated DOM test harness in this repo. Verify the generated `index.html` by actually opening it, per the project's `verify` skill philosophy of exercising the real behavior rather than trusting static checks alone.

- [ ] **Step 1: Open the file directly as `file://`**

Double-click `index.html` (or run `start index.html` on Windows / `open index.html` on macOS) and confirm it renders with no blank page and no visible `/*__DATA__*/`-style leftover text — this is the actual double-click-to-use scenario the design targets.

- [ ] **Step 2: Check the browser console for errors**

Open DevTools console. Expected: zero errors. If `filterRows is not defined` or similar appears, the query-lib splice in Task 4 failed — re-check the placeholder string matches exactly between `index.template.html` and `build-index.js`.

- [ ] **Step 3: Verify category grouping and row count**

Confirm the table shows category headers (`// Compute`, `// Storage`, …) each with a count badge, and the total across all categories, when no filters are applied, matches the "Showing X of 713" counter with X = 713.

- [ ] **Step 4: Verify category filter**

Select "Compute" from the category dropdown. Expected: only the Compute category section remains, result count updates to the Compute row count, other category headers disappear.

- [ ] **Step 5: Verify vendor filter AND semantics**

Click the AWS chip, then also click the Azure chip. Expected: only rows that have **both** an AWS and an Azure product remain (rows with only AWS, or only Azure, disappear). Click AWS again to deactivate it — Azure-only rows reappear.

- [ ] **Step 6: Verify search**

Clear filters, type `ec2` into the search box. Expected: rows containing "EC2" (e.g., "General-Purpose Virtual Machine") remain; unrelated rows disappear. Clear the box — full list returns.

- [ ] **Step 7: Verify notes expand/collapse**

Find a row with a "Why this pairing?" link (curated groups all have `notes`), click it. Expected: a notes panel appears below the row with the pairing rationale. Click "Hide notes" (or the same toggle) to collapse it again.

- [ ] **Step 8: Verify language toggle**

Click "中文". Expected: page title, filter labels, search placeholder, table headers, badge labels, and all visible product/category/group descriptions switch to Chinese; product **names and links stay in English** (per design — they're not translated). Click "EN" to switch back.

- [ ] **Step 9: Verify unmatched (single-vendor) rows render correctly**

Filter category to one with no curated groups (e.g., "Blockchain" or another category outside Compute/Database/Serverless/Developer Tools/Management & Governance). Expected: rows show "Unmatched" badges, exactly one vendor column populated, the other two showing "—".

- [ ] **Step 10: Fix any issues found, regenerate, and commit**

If any check above failed, fix `index.template.html` (never hand-edit the generated `index.html` directly), then:

```bash
node build-index.js
git add index.template.html index.html
git commit -m "fix: address manual verification findings"
```

If everything passed with no changes needed, no commit is required for this task.

---

## Plan Self-Review Notes

- **Spec coverage:** category filter (Task 3/5), vendor AND-filter (Task 3/5), bilingual search (Task 3/5), table with per-vendor columns + confidence badges (Task 3), category grouping sorted by confidence (Task 2 `groupByCategory`/`sortRows` + Task 3 render), expandable notes (Task 3/5), full EN/中文 toggle for UI + data (Task 3/5), single-file offline-capable output (Task 4), regenerable via `build-index.js` (Task 4). All covered.
- **Explicitly out of scope per the design doc** (confirmed still absent from this plan): confidence filter control, dashboard/charts, pagination/virtual scroll, edits to existing `cloud-compare-*.md` files.
- **Type consistency check:** `row.products.{aws,azure,gcp}` arrays of `{name, link, description, descriptionCn}` are produced identically by `lib/transform.js` and consumed identically by `lib/query.js` and the template's `renderProductCell`/`rowMatchesQuery`. `categories` entries `{name, nameCn}` are produced by `buildCategories` and consumed the same way by `groupByCategory` and `populateCategorySelect`. Confirmed consistent across all tasks.

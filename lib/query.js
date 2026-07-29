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
  ['aws', 'azure', 'gcp', 'alibaba'].forEach(function (vendor) {
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

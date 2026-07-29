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

const VENDORS = ['aws', 'azure', 'gcp', 'alibaba'];

function groupToRow(g) {
  const products = {};
  VENDORS.forEach((vendor) => {
    products[vendor] = normalizeProducts(g.products && g.products[vendor]);
  });
  return {
    id: g.id,
    category: g.category,
    categoryCn: g['category-cn'] || g.category,
    name: g.name,
    nameCn: (g['name-cn'] && String(g['name-cn']).trim()) ? g['name-cn'] : g.name,
    confidence: g.confidence,
    products,
  };
}

function buildRows(data) {
  const rows = data.groups.map(groupToRow);
  const unmapped = data.unmapped || {};
  Object.keys(unmapped).forEach((category) => {
    VENDORS.forEach((vendor) => {
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

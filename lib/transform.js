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

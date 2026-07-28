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

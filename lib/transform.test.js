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

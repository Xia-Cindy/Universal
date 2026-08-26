import assert from 'node:assert/strict';
import test from 'node:test';

import { articleKind, techStackCategoryFor } from './techStackTaxonomy.js';

test('classifies current technology stacks without changing persisted categories', () => {
    assert.equal(techStackCategoryFor({ name: 'RAGFlow', category: 'Knowledge infrastructure' }).id, 'ai-knowledge');
    assert.equal(techStackCategoryFor({ name: 'Docker Compose', category: 'Runtime' }).id, 'runtime-cloud');
    assert.equal(techStackCategoryFor({ name: 'PostgreSQL', category: 'Data foundation' }).id, 'backend-data');
    assert.equal(techStackCategoryFor({ name: 'React + Three.js', category: 'Spatial frontend' }).id, 'frontend-experience');
    assert.equal(techStackCategoryFor({ name: '待学习的服务网格', category: '云原生与运行时' }).id, 'runtime-cloud');
});

test('treats historic knowledge records as learning notes and logs as practice articles', () => {
    assert.deepEqual(articleKind({ articleType: 'knowledge' }), { id: 'note', label: '学习笔记', shortLabel: '笔记' });
    assert.deepEqual(articleKind({ kind: 'practice' }), { id: 'practice', label: '实践复盘', shortLabel: '实践' });
});

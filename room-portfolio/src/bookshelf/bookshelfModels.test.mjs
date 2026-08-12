import assert from 'node:assert/strict';
import test from 'node:test';
import { readerPages } from './readerModel.js';
import { createShelfCatalog } from './shelfCatalog.js';

test('catalog filters a subject and keeps the three-book shelf page contract', () => {
    const books = [
        { id: '1', subject: '数据治理' },
        { id: '2', subject: '数据治理' },
        { id: '3', subject: '数据治理' },
        { id: '4', subject: 'English' }
    ];

    const catalog = createShelfCatalog(books, '数据治理', 5, 'knowledge');

    assert.deepEqual(new Set(catalog.subjects), new Set(['English', '数据治理']));
    assert.equal(catalog.totalPages, 1);
    assert.equal(catalog.shelfPage, 0);
    assert.deepEqual(catalog.visibleBooks.map((book) => book.id), ['1', '2', '3']);
});

test('reader pages preserve real chunks, annotations and local bookmarks', () => {
    const model = readerPages({
        document: { processingStatus: 'processed', provider: 'ragflow' },
        chunks: [{ content: 'A processed Knowledge chunk.' }],
        annotations: [{ id: 'card-1', annotationType: 'card' }, { id: 'ignored', annotationType: 'other' }]
    }, 'doc-1', { fileName: 'source.pdf', fileType: 'pdf' }, [], { 'doc-1': { page: 1 } });

    assert.equal(model.pages[0].content, 'A processed Knowledge chunk.');
    assert.deepEqual(model.cards.map((card) => card.id), ['card-1']);
    assert.deepEqual(model.bookmark, { page: 1 });
});

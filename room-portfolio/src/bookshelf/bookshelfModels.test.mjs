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
        annotations: [{ id: 'card-1', annotationType: 'card' }, { id: 'ignored', annotationType: 'other' }],
        recallSchedules: [{
            sourceType: 'knowledge_annotation',
            sourceId: 'card-1',
            nextReviewDate: '2026-08-14',
            rationale: '首次复习。'
        }]
    }, 'doc-1', { fileName: 'source.pdf', fileType: 'pdf' }, [], { 'doc-1': { page: 1 } });

    assert.equal(model.pages[0].content, 'A processed Knowledge chunk.');
    assert.deepEqual(model.cards.map((card) => card.id), ['card-1']);
    assert.equal(model.cards[0].recallSchedule.nextReviewDate, '2026-08-14');
    assert.deepEqual(model.bookmark, { page: 1 });
});

test('processing RAGFlow documents expose returned chunks before parsing completes', () => {
    const model = readerPages({
        document: { processingStatus: 'chunking', provider: 'ragflow', providerStatus: 'running' },
        chunks: [{ content: '已完成的 OCR 内容可以立即阅读。' }]
    }, 'doc-running', { fileName: 'long.pdf', fileType: 'pdf' });

    assert.equal(model.pages[0].content, '已完成的 OCR 内容可以立即阅读。');
    assert.match(model.book.readingStatus, /持续解析中/);
});

test('reader uses a newer synced reading position but retains a newer local fallback', () => {
    const detail = {
        document: { processingStatus: 'processed' },
        chunks: [{ content: 'A' }],
        readingProgress: {
            spreadIndex: 4,
            pageNumber: 5,
            bookmarkLabel: '同步位置',
            clientUpdatedAt: '2026-08-13T10:10:00+08:00',
            updatedAt: '2026-08-13T10:10:01+08:00'
        }
    };
    const remote = readerPages(detail, 'doc-sync', {}, [], {
        'doc-sync': { page: 1, updatedAt: '2026-08-13T10:00:00+08:00' }
    });
    const local = readerPages(detail, 'doc-sync', {}, [], {
        'doc-sync': { page: 3, spreadIndex: 2, updatedAt: '2026-08-13T10:20:00+08:00' }
    });

    assert.equal(remote.bookmark.page, 5);
    assert.equal(remote.bookmark.label, '同步位置');
    assert.equal(local.bookmark.page, 3);
    assert.equal(local.bookmark.spreadIndex, 2);
});

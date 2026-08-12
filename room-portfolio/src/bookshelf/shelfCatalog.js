const COVER_VARIANTS = [
    { backBg: '#6fa55f', backInk: '19,49,32', edge: '#e6efcf', spineBg: '#6fa55f', spineInk: '#143421' },
    { backBg: '#af3b2b', backInk: '253,230,184', edge: '#edcf91', spineBg: '#af3b2b', spineInk: '#f2c960' },
    { backBg: '#1687a4', backInk: '255,255,255', edge: '#d8e9e1', spineBg: '#1687a4', spineInk: '#f3d16d' }
];

export function asReferenceBook(book, index) {
    const variant = COVER_VARIANTS[index % COVER_VARIANTS.length];
    return {
        id: String(book.id || index),
        title: book.title || book.fileName || '学习资料',
        author: book.subtitle || book.fileType || 'KNOWLEDGE',
        year: book.status || book.processingStatus || 'READY',
        stars: 4,
        desc: book.description || book.summary || `${book.subject || '未分类'} · ${book.topic || '未分类主题'}\n${book.processingStatus || book.status || '资料已加入书架'}`,
        spineFont: '700 42px Georgia',
        universeVariant: index % COVER_VARIANTS.length,
        ...variant
    };
}

export function createShelfCatalog(books, subjectFilter, page, mode) {
    const subjects = [...new Set(books.map((book) => book.subject).filter(Boolean))]
        .sort((left, right) => left.localeCompare(right, mode === 'wordbook' ? 'en' : 'zh-CN'));
    const filteredBooks = subjectFilter ? books.filter((book) => book.subject === subjectFilter) : books;
    const totalPages = Math.max(1, Math.ceil(filteredBooks.length / 3));
    const shelfPage = Math.min(page, totalPages - 1);
    return {
        subjects,
        totalPages,
        shelfPage,
        visibleBooks: filteredBooks.slice(shelfPage * 3, shelfPage * 3 + 3)
    };
}

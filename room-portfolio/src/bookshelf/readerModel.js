export function readerPages(
    detail, documentId, book, goals = [], bookmarks = {}, recallSchedules = detail?.recallSchedules || []
) {
    const document = detail?.document || {};
    const isProcessing = ['parsing', 'chunking'].includes(document.processingStatus);
    const metadata = {
        title: book?.title || book?.fileName || '阅读',
        author: book?.subtitle || book?.fileType || 'KNOWLEDGE',
        ...(isProcessing
            ? {
                readingStatus: '持续解析中：已完成的内容现在可以阅读，剩余页面会继续同步。',
                author: `${book?.subtitle || book?.fileType || 'KNOWLEDGE'} · 持续解析中`
            }
            : {})
    };
    const bookmark = newestBookmark(bookmarks[documentId], detail?.readingProgress);
    if (Array.isArray(detail?.pages)) {
        return { id: documentId, bookmarkId: String(documentId), book: metadata, pages: detail.pages, cards: [], goals, bookmark };
    }
    const pages = (detail?.chunks || []).flatMap((chunk) => {
        const content = String(chunk.content || '').trim();
        return content.match(/[\s\S]{1,680}(?:\s|$)|[\s\S]{1,680}/g) || [];
    }).filter(Boolean).map((content) => ({ content }));
    const schedulesBySource = new Map((recallSchedules || []).map((schedule) => [
        `${schedule.sourceType}:${schedule.sourceId}`,
        schedule
    ]));
    const cards = (detail?.annotations || [])
        .filter((annotation) => annotation.annotationType === 'card' || annotation.annotationType === 'note')
        .map((annotation) => ({
            ...annotation,
            recallSchedule: schedulesBySource.get(`knowledge_annotation:${annotation.id}`) || null
        }));
    if (pages.length) {
        return { id: documentId, bookmarkId: String(documentId), book: metadata, pages, cards, goals, bookmark };
    }
    const provider = document.provider === 'ragflow' ? 'RAGFlow' : '本地知识库';
    return {
        id: documentId,
        bookmarkId: String(documentId),
        book: metadata,
        pages: [],
        cards,
        goals,
        bookmark,
        emptyMessage: isProcessing
            ? `${provider} 正在处理这本资料，尚未返回可翻阅的页面。\n状态：${document.providerStatus || document.processingStatus || '处理中'}。`
            : document.errorMessage || '这本资料还没有生成可翻阅的页面。'
    };
}

function newestBookmark(localBookmark, remoteProgress) {
    const remoteBookmark = remoteProgress ? {
        page: remoteProgress.pageNumber,
        spreadIndex: remoteProgress.spreadIndex,
        label: remoteProgress.bookmarkLabel || null,
        updatedAt: remoteProgress.clientUpdatedAt || remoteProgress.updatedAt,
        syncStatus: '已同步'
    } : null;
    const localTime = timestamp(localBookmark?.updatedAt);
    const remoteTime = timestamp(remoteBookmark?.updatedAt);
    return remoteTime > localTime ? remoteBookmark : localBookmark || remoteBookmark;
}

function timestamp(value) {
    if (typeof value === 'number') return value;
    const parsed = Date.parse(value || '');
    return Number.isFinite(parsed) ? parsed : 0;
}

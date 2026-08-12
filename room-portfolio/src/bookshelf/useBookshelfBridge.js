import { useEffect } from 'react';

import { readerPages } from './readerModel';

const BOOKMARKS_STORAGE_KEY = 'universe-books:reader-bookmarks';

/**
 * Owns the parent-side iframe protocol. The reference scene remains the
 * source of visual motion; this hook only translates its existing events into
 * the established Universe callbacks and state updates.
 */
export function useBookshelfBridge({
    frame,
    books,
    goals,
    bookmarks,
    totalPages,
    callbacks,
    state
}) {
    useEffect(() => {
        const receive = (event) => {
            if (event.source !== frame.current?.contentWindow || event.data?.source !== 'universe-books') return;
            const message = event.data;
            if (message.type === 'return') {
                callbacks.onReturn?.();
                return;
            }
            if (message.type === 'create') {
                state.setEditing(null);
                state.setComposerOpen(true);
                state.setStatus('');
                return;
            }
            if (message.type === 'wordbook') {
                callbacks.onOpenWordbook?.();
                return;
            }
            if (message.type === 'knowledge') {
                callbacks.onOpenKnowledge?.();
                return;
            }
            if (message.type === 'shelf-previous') {
                state.setShelfPage((page) => Math.max(0, page - 1));
                return;
            }
            if (message.type === 'shelf-next') {
                state.setShelfPage((page) => Math.min(totalPages - 1, page + 1));
                return;
            }
            if (message.type === 'shelf-filter') {
                state.setSubjectFilter(message.subject || '');
                state.setShelfPage(0);
                return;
            }
            if (message.type === 'speak') {
                callbacks.onSpeakWord?.(message.word);
                return;
            }
            if (message.type === 'manage-share-grants') {
                Promise.resolve(callbacks.onManageShareGrants?.(message.id))
                    .catch((error) => state.setStatus(error instanceof Error ? error.message : '无法更新 Work 授权。'));
                return;
            }
            if (message.type === 'create-annotation') {
                Promise.resolve(callbacks.onCreateAnnotation?.(message.id, {
                    selectedText: message.selectedText,
                    annotationType: message.annotationType,
                    prompt: message.prompt,
                    answer: message.answer,
                    goalId: message.goalId
                }))
                    .then((annotation) => {
                        if (!annotation) return;
                        state.setReader((current) => current?.id === message.id
                            ? { ...current, cards: [...(current.cards || []), annotation] }
                            : current);
                    })
                    .catch((error) => state.setStatus(error instanceof Error ? error.message : '无法保存划线内容。'));
                return;
            }
            if (message.type === 'master-annotation') {
                Promise.resolve(callbacks.onMarkAnnotationMastered?.(message.documentId, message.id, Boolean(message.remembered)))
                    .then((annotation) => {
                        if (!annotation) return;
                        state.setReader((current) => current?.id === message.documentId
                            ? { ...current, cards: (current.cards || []).map((card) => card.id === annotation.id ? annotation : card) }
                            : current);
                    })
                    .catch((error) => state.setStatus(error instanceof Error ? error.message : '无法记录背过状态。'));
                return;
            }
            if (message.type === 'review-word') {
                Promise.resolve(callbacks.onReviewWord?.(message.id, Boolean(message.remembered)))
                    .then((entry) => {
                        if (!entry?.recallSchedule) return;
                        state.setReader((current) => current ? {
                            ...current,
                            pages: (current.pages || []).map((page) => page.entryId === entry.id
                                ? { ...page, recallSchedule: entry.recallSchedule }
                                : page)
                        } : current);
                    })
                    .catch((error) => state.setStatus(error instanceof Error ? error.message : '无法记录单词记忆结果。'));
                return;
            }
            if (message.type === 'adjust-recall') {
                Promise.resolve(callbacks.onAdjustRecall?.(message.sourceType, message.sourceId, {
                    nextReviewDate: message.nextReviewDate,
                    reason: message.reason
                }))
                    .then((schedule) => {
                        if (!schedule) return;
                        state.setReader((current) => current ? {
                            ...current,
                            pages: (current.pages || []).map((page) => page.entryId === schedule.sourceId
                                ? { ...page, recallSchedule: schedule }
                                : page),
                            cards: (current.cards || []).map((card) => card.id === schedule.sourceId
                                ? { ...card, recallSchedule: schedule }
                                : card)
                        } : current);
                    })
                    .catch((error) => state.setStatus(error instanceof Error ? error.message : '无法调整复习日期。'));
                return;
            }
            if (message.type === 'save-bookmark') {
                const bookmark = message.bookmark;
                if (!message.id || !bookmark?.page) return;
                state.setBookmarks((current) => {
                    const next = { ...current, [String(message.id)]: bookmark };
                    try { window.localStorage.setItem(BOOKMARKS_STORAGE_KEY, JSON.stringify(next)); } catch {
                        // The current session still retains the bookmark when storage is unavailable.
                    }
                    return next;
                });
                state.setReader((current) => String(current?.id) === String(message.id) ? { ...current, bookmark } : current);
                return;
            }
            if (message.type === 'edit-word' || message.type === 'delete-word') {
                const entry = books.flatMap((item) => item.entries || []).find((item) => String(item.id) === String(message.id));
                if (!entry) return;
                if (message.type === 'delete-word') {
                    Promise.resolve(callbacks.onDeleteWord?.(entry))
                        .then(() => { state.setReader(null); state.setShelfPage(0); })
                        .catch((error) => state.setStatus(error instanceof Error ? error.message : '删除单词失败。'));
                    return;
                }
                state.setEditing({ kind: 'wordbook', item: entry });
                state.setWord(entry.word || '');
                state.setMeaning(entry.meaning || '');
                state.setLanguage(entry.language || 'English');
                state.setTags((entry.tags || []).join(', '));
                state.setGoalId(entry.goalId || '');
                state.setStatus('');
                state.setComposerOpen(true);
                return;
            }
            const book = books.find((item) => String(item.id) === String(message.id));
            if (!book) return;
            if (message.type === 'edit') {
                state.setEditing({ kind: 'knowledge', item: book });
                state.setBookTitle(book.title || book.fileName || '');
                state.setSubject(book.subject || '');
                state.setTopic(book.topic || '');
                state.setGoalId(book.goalId || '');
                state.setStatus('');
                state.setComposerOpen(true);
                return;
            }
            if (message.type === 'delete') {
                Promise.resolve(callbacks.onDelete?.(book))
                    .then(() => { state.setReader(null); state.setShelfPage(0); })
                    .catch((error) => state.setReader({ id: book.id, pages: [], emptyMessage: error instanceof Error ? error.message : '删除资料失败。' }));
                return;
            }
            Promise.resolve(callbacks.onOpen?.(book))
                .then((detail) => {
                    if (detail) state.setReader(readerPages(detail, book.id, book, goals, bookmarks));
                })
                .catch((error) => state.setReader({ pages: [], emptyMessage: error instanceof Error ? error.message : '无法读取这本资料。' }));
        };
        window.addEventListener('message', receive);
        return () => window.removeEventListener('message', receive);
    }, [bookmarks, books, callbacks, frame, goals, state, totalPages]);
}

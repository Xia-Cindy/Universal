/* eslint-disable react/prop-types */
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import { roomApi } from './api';

const PREVIEW_CARDS = [
    { id: 'preview-recall', annotationType: 'card', prompt: '把重点留下来，下一次由自己回答。', answer: '从知识书架打开资料，划线后即可制成知识卡片。', document: { fileName: '知识回忆卡', subject: '学习方法' } },
    { id: 'preview-note', annotationType: 'note', prompt: '笔记会和原始资料保持关联。', answer: '每一条笔记都能回到它来自的那本知识书。', document: { fileName: '阅读笔记', subject: '知识管理' } },
    { id: 'preview-goal', annotationType: 'card', prompt: '背过了，也会计入学习目标。', answer: '把复习变成可见的进度，而不是一次性的阅读。', document: { fileName: '目标进度', subject: '复习' } },
    { id: 'preview-word', annotationType: 'card', prompt: '英文在正面，中文留到翻面。', answer: 'Wordbook 也可以用相同的回忆方式复习。', document: { fileName: 'Wordbook', subject: '语言' } },
    { id: 'preview-source', annotationType: 'note', prompt: '资料不会消失，只会变成可回看的卡片。', answer: '导入的书、笔记与目标之间始终保留来源关系。', document: { fileName: '知识书架', subject: '资料' } },
    { id: 'preview-card', annotationType: 'card', prompt: '先回忆，再看答案。', answer: '这是比反复浏览更有效的学习节奏。', document: { fileName: '主动回忆', subject: '复习' } }
];

const clip = (text, length) => {
    const value = String(text || '');
    return value.length > length ? `${value.slice(0, length - 1)}…` : value;
};

const wrap = (value, span) => ((value % span) + span) % span;

const roomShortcuts = [
    ['study', 'Study Space'],
    ['library', '书架'],
    ['board', '记忆卡片'],
    ['work', 'Work Space'],
    ['novel', '作品展墙']
];

export default function KnowledgeCardsGallery({ onOpenSpace, onReturn }) {
    const [annotations, setAnnotations] = useState([]);
    const [mode, setMode] = useState('cards');
    const [selectedId, setSelectedId] = useState(null);
    const [revealed, setRevealed] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [viewportWidth, setViewportWidth] = useState(() => window.innerWidth);
    const offset = useRef(0);
    const velocity = useRef(0);
    const drag = useRef({ active: false, x: 0, time: 0, moved: false });
    const [, repaint] = useState(0);

    const load = useCallback(async () => {
        setLoading(true);
        setError('');
        try {
            const documents = await roomApi.knowledgeDocuments();
            const grouped = await Promise.all((documents || []).map(async (document) => ({
                document,
                annotations: await roomApi.knowledgeAnnotations(document.id)
            })));
            setAnnotations(grouped.flatMap(({ document, annotations: items }) =>
                (items || []).map((item) => ({ ...item, document }))
            ));
        } catch (requestError) {
            setError(requestError instanceof Error ? requestError.message : '无法读取知识卡片。');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { load(); }, [load]);
    useEffect(() => {
        const resize = () => setViewportWidth(window.innerWidth);
        const moveWithKey = (event) => {
            if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
            event.preventDefault();
            velocity.current += event.key === 'ArrowLeft' ? -10 : 10;
        };
        window.addEventListener('resize', resize);
        window.addEventListener('keydown', moveWithKey);
        return () => {
            window.removeEventListener('resize', resize);
            window.removeEventListener('keydown', moveWithKey);
        };
    }, []);
    useEffect(() => {
        let frame;
        const animate = () => {
            if (!drag.current.active && Math.abs(velocity.current) > 0.01) {
                offset.current += velocity.current;
                velocity.current *= 0.935;
                repaint((value) => value + 1);
            }
            frame = window.requestAnimationFrame(animate);
        };
        frame = window.requestAnimationFrame(animate);
        return () => window.cancelAnimationFrame(frame);
    }, []);

    const actual = annotations.filter((item) => item.annotationType === (mode === 'cards' ? 'card' : 'note'));
    const items = actual.length ? actual : PREVIEW_CARDS.filter((item) => item.annotationType === (mode === 'cards' ? 'card' : 'note'));
    const isPreview = !actual.length;
    const selectedIndex = items.findIndex((item) => item.id === selectedId);
    const selectedItem = selectedIndex >= 0 ? items[selectedIndex] : null;
    const cardWidth = Math.max(176, Math.min(242, viewportWidth * 0.19));
    const spacing = cardWidth * 1.19;
    const track = viewportWidth + spacing * 2;
    const slots = Math.max(8, Math.ceil(track / spacing) + 2);
    const cards = useMemo(() => Array.from({ length: slots }, (_, slot) => ({
        slot,
        item: items[slot % items.length]
    })), [items, slots]);

    useEffect(() => {
        if (selectedId && !items.some((item) => item.id === selectedId)) {
            setSelectedId(null);
            setRevealed(false);
        }
    }, [items, selectedId]);

    const openItem = (item) => {
        setSelectedId(item.id);
        setRevealed(false);
    };
    const moveSelected = (direction) => {
        if (!items.length) return;
        const from = selectedIndex >= 0 ? selectedIndex : 0;
        setSelectedId(items[(from + direction + items.length) % items.length].id);
        setRevealed(false);
    };
    const markMastered = async (item) => {
        if (item.id.startsWith('preview-')) {
            onOpenSpace('library');
            return;
        }
        const updated = await roomApi.markKnowledgeAnnotationMastered(item.document.id, item.id, !item.mastered);
        setAnnotations((current) => current.map((entry) => entry.id === updated.id ? { ...entry, ...updated } : entry));
    };
    const beginDrag = (event) => {
        if (!event.target.closest('.hanging-gallery__rope-zone') || event.target.closest('.hanging-gallery__card')) return;
        drag.current = { active: true, x: event.clientX, time: performance.now(), moved: false };
        velocity.current = 0;
        event.currentTarget.setPointerCapture?.(event.pointerId);
    };
    const moveDrag = (event) => {
        if (!drag.current.active) return;
        const now = performance.now();
        const delta = event.clientX - drag.current.x;
        const elapsed = Math.max(8, now - drag.current.time);
        offset.current += delta;
        velocity.current = velocity.current * 0.55 + (delta / elapsed) * 16;
        drag.current = { active: true, x: event.clientX, time: now, moved: drag.current.moved || Math.abs(delta) > 2 };
        repaint((value) => value + 1);
    };
    const endDrag = () => { drag.current.active = false; };

    return (
        <main className="hanging-gallery" onPointerCancel={endDrag} onPointerDown={beginDrag} onPointerMove={moveDrag} onPointerUp={endDrag} onWheel={(event) => { if (!event.target.closest('.hanging-gallery__rope-zone')) return; event.preventDefault(); velocity.current += -(Math.abs(event.deltaX) > Math.abs(event.deltaY) ? event.deltaX : event.deltaY) * 0.025; }}>
            <section className="hanging-gallery__canvas">
                <header className="hanging-gallery__header">
                    <button className="hanging-gallery__brand" onClick={onReturn} onPointerDown={(event) => event.stopPropagation()} type="button">UNIVERSE<sup>OS</sup></button>
                    <nav aria-label="知识卡片分类">
                        <button className={mode === 'cards' ? 'is-active' : ''} onClick={(event) => { event.stopPropagation(); setMode('cards'); setSelectedId(null); setRevealed(false); }} type="button">知识卡片</button>
                        <button className={mode === 'notes' ? 'is-active' : ''} onClick={(event) => { event.stopPropagation(); setMode('notes'); setSelectedId(null); setRevealed(false); }} type="button">学习笔记</button>
                    </nav>
                    <button className="hanging-gallery__return" onClick={onReturn} onPointerDown={(event) => event.stopPropagation()} type="button">返回房间</button>
                </header>

                <div className="hanging-gallery__hero">
                    <span>{mode === 'cards' ? 'Study recall' : 'Reading notes'}</span>
                    <h1>{mode === 'cards' ? <>REMEMBER<br />WHAT YOU <em>LEARN</em></> : <>MAKE NOTES<br />THAT <em>STAY</em></>}</h1>
                    <p>{isPreview ? '从知识书架划线，开始建立自己的回忆卡片。' : '拖动绳索，在下一次复习前先给自己一点回忆的空间。'}</p>
                </div>

                <div aria-label="可拖动的知识卡片绳索" className="hanging-gallery__rope-zone">
                    <div className="hanging-gallery__rope" />
                    {cards.map(({ item, slot }) => {
                        const x = wrap(slot * spacing + offset.current + spacing * 0.25, track) - spacing;
                        const centred = (x - viewportWidth * 0.5) / Math.max(viewportWidth * 0.5, 1);
                        const ropeY = 42 + centred ** 2 * 8;
                        const angle = centred * 11 + Math.sin(slot * 1.7) * 2.5;
                        const cardStyle = {
                            '--card-x': `${x}px`,
                            '--card-y': `${ropeY}px`,
                            '--card-rotate': `${angle}deg`,
                            '--card-width': `${cardWidth}px`
                        };
                        return (
                            <article className={`hanging-gallery__card ${item.annotationType === 'note' ? 'is-note' : ''}`} key={`${slot}-${item.id}`} style={cardStyle}>
                                <i className="hanging-gallery__clip" />
                                <button aria-label={`展开 ${clip(item.prompt || item.selectedText, 20)}`} className="hanging-gallery__card-inner" onClick={() => openItem(item)} onPointerDown={(event) => event.stopPropagation()} type="button">
                                    <span className="hanging-gallery__card-face hanging-gallery__card-front">
                                        <small>{isPreview ? 'YOUR FIRST CARD' : item.annotationType === 'note' ? 'READING NOTE' : 'RECALL CARD'}</small>
                                        <strong>{clip(item.prompt || item.selectedText, 56)}</strong>
                                        <b>{clip(item.document.fileName, 25)}</b>
                                    </span>
                                </button>
                            </article>
                        );
                    })}
                </div>

                {selectedItem && (
                    <section aria-label="知识卡片详情" className="hanging-gallery__detail" onPointerDown={(event) => event.stopPropagation()}>
                        <header>
                            <div>
                                <small>{selectedItem.annotationType === 'note' ? 'READING NOTE' : 'KNOWLEDGE CARD'} · {selectedIndex + 1} / {items.length}</small>
                                <p>{selectedItem.document.subject || '知识资料'} · {selectedItem.document.fileName}</p>
                            </div>
                            <button aria-label="关闭卡片详情" onClick={() => setSelectedId(null)} type="button">×</button>
                        </header>
                        <article>
                            <h2>{revealed || selectedItem.annotationType === 'note'
                                ? selectedItem.answer || selectedItem.note || selectedItem.selectedText
                                : selectedItem.prompt || selectedItem.selectedText}</h2>
                            {!revealed && selectedItem.annotationType === 'card' && <p>先在脑中回忆答案，再翻到背面确认。</p>}
                        </article>
                        <footer>
                            <button onClick={() => moveSelected(-1)} type="button">上一条</button>
                            {selectedItem.annotationType === 'card' && !revealed && <button className="is-primary" onClick={() => setRevealed(true)} type="button">翻到背面</button>}
                            <button onClick={() => moveSelected(1)} type="button">下一条</button>
                            <button className={selectedItem.mastered ? 'is-mastered' : ''} onClick={() => markMastered(selectedItem)} type="button">
                                {selectedItem.mastered ? '取消背过' : isPreview ? '去知识书架创建' : '背过了'}
                            </button>
                        </footer>
                    </section>
                )}

                <p className="hanging-gallery__status">
                    <span>{loading ? '正在读取你的卡片…' : error ? error : isPreview ? '预览模式 · 还没有保存的卡片' : `${actual.length} 张${mode === 'cards' ? '知识卡片' : '学习笔记'}`}</span>
                    <span>拖动绳索 · 滚轮 · ← →</span>
                </p>
                <nav aria-label="空间快捷入口" className="hanging-gallery__dock">
                    {roomShortcuts.map(([id, label]) => (
                        <button className={id === 'board' ? 'is-active' : ''} key={id} onClick={() => onOpenSpace(id)} onPointerDown={(event) => event.stopPropagation()} type="button">{label}</button>
                    ))}
                </nav>
            </section>
        </main>
    );
}

/* eslint-disable react/prop-types */
import { useCallback, useEffect, useMemo, useState } from 'react';

import { roomApi } from './api';

const emptyStack = {
    name: '',
    category: 'Engineering',
    description: '',
    tags: ''
};

const emptyEntry = {
    kind: 'principle',
    title: '',
    content: '',
    tags: '',
    minutes: '',
    attachments: [],
    sourceArticleId: '',
    selectedQuote: '',
    aiQuestion: '',
    sources: []
};

const maxAttachments = 4;
const maxAttachmentDataUrlLength = 1_500_000;

const splitTags = (value) => String(value || '')
    .split(/[,，\n]/)
    .map((item) => item.trim())
    .filter(Boolean);

const formatDate = (value) => value
    ? new Intl.DateTimeFormat('zh-CN', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(value))
    : '刚刚';

const stackMark = (name) => String(name || 'T').trim().slice(0, 2).toUpperCase();

const compressClipboardImage = (file) => new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const image = new Image();
    image.onload = () => {
        URL.revokeObjectURL(url);
        const longestSide = Math.max(image.naturalWidth, image.naturalHeight);
        const scale = Math.min(1, 1600 / Math.max(longestSide, 1));
        const canvas = document.createElement('canvas');
        canvas.width = Math.max(1, Math.round(image.naturalWidth * scale));
        canvas.height = Math.max(1, Math.round(image.naturalHeight * scale));
        const context = canvas.getContext('2d');
        if (!context) {
            reject(new Error('当前浏览器无法压缩图片。'));
            return;
        }
        context.drawImage(image, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL('image/webp', 0.82);
        if (dataUrl.length > maxAttachmentDataUrlLength) {
            reject(new Error('图片压缩后仍超过 1.5 MB，请裁剪后再粘贴。'));
            return;
        }
        resolve(dataUrl);
    };
    image.onerror = () => {
        URL.revokeObjectURL(url);
        reject(new Error('无法读取这张图片。'));
    };
    image.src = url;
});

export default function TechStackWorkspace({ onNavigate }) {
    const [stacks, setStacks] = useState([]);
    const [selectedId, setSelectedId] = useState('');
    const [detail, setDetail] = useState(null);
    const [loading, setLoading] = useState(true);
    const [loadingDetail, setLoadingDetail] = useState(false);
    const [error, setError] = useState('');
    const [showStackForm, setShowStackForm] = useState(false);
    const [showEntryForm, setShowEntryForm] = useState(false);
    const [stackForm, setStackForm] = useState(emptyStack);
    const [entryForm, setEntryForm] = useState(emptyEntry);
    const [saving, setSaving] = useState(false);
    const [aiStatus, setAiStatus] = useState(null);
    const [aiSelection, setAiSelection] = useState(null);
    const [aiQuestion, setAiQuestion] = useState('');
    const [aiResult, setAiResult] = useState(null);
    const [askingAi, setAskingAi] = useState(false);

    const loadStacks = useCallback(async () => {
        setLoading(true);
        setError('');
        try {
            const result = await roomApi.workTechStacks();
            setStacks(result);
            setSelectedId((current) => result.some((item) => item.id === current) ? current : (result[0]?.id || ''));
        } catch (cause) {
            setError(cause instanceof Error ? cause.message : '无法读取技术栈。');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { loadStacks(); }, [loadStacks]);

    useEffect(() => {
        roomApi.aiStatus().then(setAiStatus).catch(() => setAiStatus({ configured: false, message: '无法读取 AI Core 配置状态。' }));
    }, []);

    const loadDetail = useCallback(async () => {
        if (!selectedId) {
            setDetail(null);
            return;
        }
        setLoadingDetail(true);
        setError('');
        try {
            setDetail(await roomApi.workTechStack(selectedId));
        } catch (cause) {
            setError(cause instanceof Error ? cause.message : '无法读取技术空间。');
        } finally {
            setLoadingDetail(false);
        }
    }, [selectedId]);

    useEffect(() => { loadDetail(); }, [loadDetail]);

    const principles = useMemo(() => (detail?.articles || [])
        .filter((item) => item.articleType !== 'extension' && item.articleType !== 'exploration'), [detail]);

    const extensions = useMemo(() => (detail?.articles || [])
        .filter((item) => item.articleType === 'extension'), [detail]);

    const explorations = useMemo(() => (detail?.articles || [])
        .filter((item) => item.articleType === 'exploration'), [detail]);

    const timeline = useMemo(() => {
        if (!detail) return [];
        return (detail.learningRecords || [])
            .map((item) => ({ ...item, kind: 'practice', content: item.notes, date: item.updatedAt }))
            .sort((left, right) => new Date(right.date) - new Date(left.date));
    }, [detail]);

    const updateStackForm = (event) => {
        const { name, value } = event.target;
        setStackForm((current) => ({ ...current, [name]: value }));
    };

    const updateEntryForm = (event) => {
        const { name, value } = event.target;
        setEntryForm((current) => ({ ...current, [name]: value }));
    };

    const addPastedImages = async (event) => {
        const files = Array.from(event.clipboardData?.items || [])
            .filter((item) => item.kind === 'file' && item.type.startsWith('image/'))
            .map((item) => item.getAsFile())
            .filter(Boolean);
        if (!files.length) return;
        event.preventDefault();
        if (entryForm.attachments.length + files.length > maxAttachments) {
            setError(`每条技术记录最多保留 ${maxAttachments} 张图片。`);
            return;
        }
        setError('');
        try {
            const images = await Promise.all(files.map(compressClipboardImage));
            setEntryForm((current) => ({ ...current, attachments: [...current.attachments, ...images] }));
        } catch (cause) {
            setError(cause instanceof Error ? cause.message : '无法处理粘贴的图片。');
        }
    };

    const removeAttachment = (index) => {
        setEntryForm((current) => ({ ...current, attachments: current.attachments.filter((_, itemIndex) => itemIndex !== index) }));
    };

    const captureAiSelection = (event) => {
        const quote = window.getSelection?.().toString().trim();
        const article = event.target.closest?.('[data-article-id]');
        if (!quote || !article) return;
        setAiSelection({ articleId: article.dataset.articleId, articleTitle: article.dataset.articleTitle, quote });
        setAiQuestion(`请解释这段话中的「${quote.slice(0, 96)}」：它的机制、边界和一个真实应用是什么？`);
        setAiResult(null);
    };

    const askAi = async () => {
        if (!selectedId || !aiQuestion.trim()) return;
        setAskingAi(true);
        setError('');
        try {
            setAiResult(await roomApi.askWorkExploration(selectedId, {
                sourceArticleId: aiSelection?.articleId || '',
                selectedQuote: aiSelection?.quote || '',
                question: aiQuestion.trim()
            }));
        } catch (cause) {
            setError(cause instanceof Error ? cause.message : 'AI 暂时无法回答这个问题。');
        } finally {
            setAskingAi(false);
        }
    };

    const addAiResultToMap = () => {
        if (!aiResult) return;
        setEntryForm({
            ...emptyEntry,
            kind: 'exploration',
            title: `AI 探索：${aiQuestion.trim().slice(0, 72)}`,
            content: aiResult.answer,
            tags: 'AI探索',
            sourceArticleId: aiResult.sourceArticleId || aiSelection?.articleId || '',
            selectedQuote: aiResult.selectedQuote || aiSelection?.quote || '',
            aiQuestion: aiQuestion.trim(),
            sources: aiResult.sources || []
        });
        setShowEntryForm(true);
    };

    const createStack = async (event) => {
        event.preventDefault();
        setSaving(true);
        setError('');
        try {
            const created = await roomApi.createWorkTechStack({
                name: stackForm.name.trim(),
                category: stackForm.category.trim() || 'Engineering',
                proficiency: 'learning',
                description: stackForm.description.trim(),
                tags: splitTags(stackForm.tags)
            });
            setStacks((current) => [created, ...current]);
            setSelectedId(created.id);
            setStackForm(emptyStack);
            setShowStackForm(false);
        } catch (cause) {
            setError(cause instanceof Error ? cause.message : '无法创建技术空间。');
        } finally {
            setSaving(false);
        }
    };

    const createEntry = async (event) => {
        event.preventDefault();
        if (!selectedId) return;
        setSaving(true);
        setError('');
        try {
            if (entryForm.kind !== 'practice') {
                await roomApi.createWorkArticle(selectedId, {
                    title: entryForm.title.trim(),
                    articleType: entryForm.kind,
                    summary: entryForm.content.trim().slice(0, 140),
                    content: entryForm.content.trim(),
                    tags: splitTags(entryForm.tags),
                    attachments: entryForm.attachments,
                    sourceArticleId: entryForm.sourceArticleId,
                    selectedQuote: entryForm.selectedQuote,
                    aiQuestion: entryForm.aiQuestion,
                    sources: entryForm.sources,
                    status: 'published'
                });
            } else {
                await roomApi.createWorkLearningRecord(selectedId, {
                    title: entryForm.title.trim(),
                    notes: entryForm.content.trim(),
                    minutes: Number(entryForm.minutes) || 0,
                    tags: splitTags(entryForm.tags),
                    attachments: entryForm.attachments,
                    status: 'recorded'
                });
            }
            setEntryForm(emptyEntry);
            setShowEntryForm(false);
            await loadDetail();
            await loadStacks();
        } catch (cause) {
            setError(cause instanceof Error ? cause.message : '无法保存这条技术记录。');
        } finally {
            setSaving(false);
        }
    };

    return (
        <section className="work-tech-space" aria-live="polite">
            <header className="work-tech-space__hero">
                <div>
                    <p className="work-case-space__eyebrow">TECHNOLOGY FIELD · LIVE EVIDENCE</p>
                    <h1>技术不是履历，<em>是正在生长的能力。</em></h1>
                    <p>每一项技术都是一个自己的空间：把真实部署、理论理解、从原理推导出的延伸与落地应用放在一起。不会自动宣称“掌握”，只保留发生过的证据。</p>
                </div>
                <div className="work-tech-space__hero-actions">
                    <button className="work-tech-space__outline-button" onClick={() => onNavigate('/work')} type="button">← 能力入口</button>
                    <button className="work-tech-space__solid-button" onClick={() => setShowStackForm((value) => !value)} type="button">{showStackForm ? '收起新技术' : '+ 开通技术空间'}</button>
                </div>
            </header>

            {showStackForm && (
                <form className="work-tech-space__create-stack" onSubmit={createStack}>
                    <label>技术名称<input autoFocus name="name" onChange={updateStackForm} placeholder="例如 RAGFlow、Docker Compose、SRE" required value={stackForm.name} /></label>
                    <label>技术类别<input name="category" onChange={updateStackForm} placeholder="例如 Knowledge Infrastructure" value={stackForm.category} /></label>
                    <label>它在你的世界中做什么？<textarea name="description" onChange={updateStackForm} placeholder="写下你想理解的系统位置或学习目标。" value={stackForm.description} /></label>
                    <label>标签<input name="tags" onChange={updateStackForm} placeholder="例如 retrieval, docker, operations" value={stackForm.tags} /></label>
                    <div><span>创建后即可在该技术的 Tab 中持续沉淀理论与实践。</span><button className="work-tech-space__solid-button" disabled={saving} type="submit">{saving ? '创建中…' : '创建技术空间'}</button></div>
                </form>
            )}

            {error && <p className="work-tech-space__error" role="alert">{error}</p>}

            <div className="work-tech-space__stage">
                <aside className="work-tech-space__navigator" aria-label="技术栈 Tabs">
                    <div className="work-tech-space__navigator-heading"><span>YOUR STACKS</span><small>{loading ? '同步中' : `${stacks.length} 个空间`}</small></div>
                    <div className="work-tech-space__cube-field" role="tablist" aria-label="选择技术栈">
                        {stacks.map((stack, index) => (
                            <button
                                aria-selected={stack.id === selectedId}
                                className={`work-tech-space__cube ${stack.id === selectedId ? 'is-selected' : ''}`}
                                key={stack.id}
                                onClick={() => setSelectedId(stack.id)}
                                role="tab"
                                style={{ '--cube-delay': `${index * 70}ms` }}
                                type="button"
                            >
                                <i>{stackMark(stack.name)}</i><strong>{stack.name}</strong><small>{stack.category}</small>
                            </button>
                        ))}
                    </div>
                    {!loading && !stacks.length && <p className="work-tech-space__empty-tip">先开通一个技术空间。建议从正在构建 Universe 时真实用到的技术开始。</p>}
                </aside>

                <main className="work-tech-space__content" role="tabpanel">
                    {!selectedId && !loading && <EmptyTechSpace onCreate={() => setShowStackForm(true)} />}
                    {selectedId && (loadingDetail || !detail) && <p className="work-tech-space__loading">正在展开这个技术空间…</p>}
                    {detail && !loadingDetail && (
                        <>
                            <section className="work-tech-space__focus-card">
                                <div><span>{detail.techStack.category} · {detail.techStack.proficiency}</span><h2>{detail.techStack.name}</h2><p>{detail.techStack.description || '这是一项待你用真实行动逐步定义的技术。'}</p></div>
                                <div className="work-tech-space__tag-row">{detail.techStack.tags?.length ? detail.techStack.tags.map((tag) => <b key={tag}>#{tag}</b>) : <b>#学习中</b>}</div>
                            </section>

                            <section className="work-tech-space__learning-map">
                                <GuideColumn
                                    emptyText="还没有原理笔记。先写下它在系统中解决什么问题、关键组件如何协作。"
                                    items={principles}
                                    label="IMPLEMENTATION PRINCIPLES"
                                    onSelect={captureAiSelection}
                                    title="实现原理与系统位置"
                                />
                                <GuideColumn
                                    emptyText="还没有理论延伸。先写从当前原理可继续推导的命题，再补一个真实系统中的落地场景。"
                                    items={extensions}
                                    label="THEORY → APPLICATION"
                                    onSelect={captureAiSelection}
                                    title="理论延伸与落地应用"
                                />
                            </section>

                            <div className="work-tech-space__content-grid">
                                <section className="work-tech-space__timeline">
                                    <div className="work-tech-space__section-heading"><div><span>LIVE LOG</span><h3>这里发生过什么</h3></div><button className="work-tech-space__solid-button" onClick={() => setShowEntryForm((value) => !value)} type="button">{showEntryForm ? '收起记录' : '+ 添加内容'}</button></div>
                                    {showEntryForm && <EntryForm form={entryForm} onChange={updateEntryForm} onPasteImages={addPastedImages} onRemoveAttachment={removeAttachment} onSubmit={createEntry} saving={saving} />}
                                    {!timeline.length && <p className="work-tech-space__empty-log">还没有实践记录。完成一次真实操作、验证或复盘后，它会在这里留下证据。</p>}
                                    {timeline.map((item) => <article className={`work-tech-space__log-item is-${item.kind}`} key={`${item.kind}-${item.id}`}><span className="work-tech-space__log-kind">实践</span><div><small>{formatDate(item.date)}{item.minutes ? ` · ${item.minutes} 分钟` : ''}</small><h4>{item.title}</h4><p>{item.content || item.summary || '未附加文字。'}</p><AttachmentStrip attachments={item.attachments} />{item.tags?.length > 0 && <footer>{item.tags.map((tag) => <b key={tag}>#{tag}</b>)}</footer>}</div></article>)}
                                </section>
                                <AiExplorePanel
                                    aiQuestion={aiQuestion}
                                    aiResult={aiResult}
                                    aiSelection={aiSelection}
                                    aiStatus={aiStatus}
                                    asking={askingAi}
                                    explorations={explorations}
                                    knowledge={detail.relatedKnowledge || []}
                                    onAddToMap={addAiResultToMap}
                                    onAsk={askAi}
                                    onChangeQuestion={setAiQuestion}
                                    onNavigateKnowledge={() => onNavigate('/study/knowledge')}
                                />
                            </div>
                        </>
                    )}
                </main>
            </div>
        </section>
    );
}

function EmptyTechSpace({ onCreate }) {
    return <section className="work-tech-space__empty"><span>YOUR FIRST TECH SPACE</span><h2>从正在发生的构建开始。</h2><p>例如：React + Three.js、FastAPI、PostgreSQL、Docker Compose、Linux，或计划作为共享 Knowledge 基础设施的 RAGFlow。</p><button className="work-tech-space__solid-button" onClick={onCreate} type="button">开通第一项技术 →</button></section>;
}

function GuideColumn({ emptyText, items, label, onSelect, title }) {
    return <section className="work-tech-space__guide-column"><span>{label}</span><h3>{title}</h3>{items.length ? items.map((item) => <article data-article-id={item.id} data-article-title={item.title} key={item.id} onMouseUp={onSelect}><small>{formatDate(item.updatedAt)}</small><h4>{item.title}</h4><p>{item.content || item.summary || '未附加文字。'}</p><AttachmentStrip attachments={item.attachments} />{item.tags?.length > 0 && <footer>{item.tags.map((tag) => <b key={tag}>#{tag}</b>)}</footer>}</article>) : <p className="work-tech-space__guide-empty">{emptyText}</p>}</section>;
}

function AttachmentStrip({ attachments = [] }) {
    if (!attachments.length) return null;
    return <div className="work-tech-space__attachment-strip">{attachments.map((attachment, index) => <a href={attachment} key={`${index}-${attachment.length}`} rel="noreferrer" target="_blank"><img alt={`技术记录附件 ${index + 1}`} loading="lazy" src={attachment} /></a>)}</div>;
}

function AiExplorePanel({ aiQuestion, aiResult, aiSelection, aiStatus, asking, explorations, knowledge, onAddToMap, onAsk, onChangeQuestion, onNavigateKnowledge }) {
    return <section className="work-tech-space__ai-explore">
        <span>AI EXPLORE · SHARED CORE</span><h3>划线问 AI</h3>
        <p>选中左侧原理或延伸中的一句话后提问。AI 只会检索这项技术已授权的资料；回答不会自动写入 Knowledge。</p>
        {!aiStatus?.configured && <p className="work-tech-space__ai-status">{aiStatus?.message || '正在检查 AI Core 配置…'}</p>}
        {aiSelection && <div className="work-tech-space__selected-quote"><small>已选中 · {aiSelection.articleTitle}</small><q>{aiSelection.quote}</q></div>}
        <label className="work-tech-space__ai-question">想弄懂什么？<textarea onChange={(event) => onChangeQuestion(event.target.value)} placeholder="先划线，或直接写下你不理解的技术问题。" value={aiQuestion} /></label>
        <button className="work-tech-space__solid-button" disabled={asking || !aiQuestion.trim() || !aiStatus?.configured} onClick={onAsk} type="button">{asking ? 'AI 思考中…' : '问 AI →'}</button>
        {aiResult && <article className="work-tech-space__ai-answer"><small>{aiResult.sourceNotice}</small><p>{aiResult.answer}</p>{aiResult.sources?.length > 0 && <div className="work-tech-space__ai-sources">{aiResult.sources.map((source) => <a href={source.sourceUrl || '#'} key={source.sourceId} onClick={(event) => { if (!source.sourceUrl) event.preventDefault(); }}><strong>{source.title}</strong><span>{source.quote}</span></a>)}</div>}<button className="work-tech-space__outline-button" onClick={onAddToMap} type="button">加入学习地图</button></article>}
        <details className="work-tech-space__knowledge-fold"><summary>已授权资料 {knowledge.length ? `· ${knowledge.length}` : ''}</summary>{knowledge.length ? knowledge.map((document) => <button key={document.id} onClick={onNavigateKnowledge} type="button"><strong>{document.fileName}</strong><small>{document.topic || document.subject || 'Knowledge document'}</small></button>) : <p>暂无授权资料。可从 Study 书架为这项技术授权只读资料。</p>}</details>
        {explorations.length > 0 && <div className="work-tech-space__saved-explorations"><small>已保存探索</small>{explorations.map((item) => <article key={item.id}><strong>{item.aiQuestion || item.title}</strong><p>{item.selectedQuote ? `划线：${item.selectedQuote}` : item.content}</p></article>)}</div>}
    </section>;
}

function EntryForm({ form, onChange, onPasteImages, onRemoveAttachment, onSubmit, saving }) {
    return <form className="work-tech-space__entry-form" onPaste={onPasteImages} onSubmit={onSubmit}>
        <label>记录类型<select name="kind" onChange={onChange} value={form.kind}><option value="principle">实现原理 / 理论笔记</option><option value="practice">真实操作 / 实践</option><option value="extension">理论延伸 / 落地应用</option><option value="exploration">AI 探索 / 未理解点</option></select></label>
        <label>标题<input autoFocus name="title" onChange={onChange} placeholder={form.kind === 'practice' ? '例如：完成 Room 静态资源缓存发布' : form.kind === 'extension' ? '例如：分层缓存理论如何落地到 Web 服务' : '例如：RAGFlow 在 Universe 中的边界'} required value={form.title} /></label>
        <label>内容<textarea name="content" onChange={onChange} placeholder={form.kind === 'extension' ? '先写：从哪个原理推导出什么结论；再写：它可在哪个真实系统、约束和场景中落地。' : form.kind === 'exploration' ? '保留 AI 的解释，再改写成你自己理解的结论。' : '记录你理解到的原理、决策、命令结果或后续问题。'} required value={form.content} /></label>
        <section className="work-tech-space__image-paste" tabIndex="0"><strong>粘贴截图</strong><p>在内容框或此处按 ⌘V / Ctrl+V。最多 {maxAttachments} 张；会压缩为私有学习附件，不会进入共享 Knowledge。</p>{form.attachments.length > 0 && <div>{form.attachments.map((attachment, index) => <figure key={`${index}-${attachment.length}`}><img alt={`待保存附件 ${index + 1}`} src={attachment} /><button aria-label={`删除图片 ${index + 1}`} onClick={() => onRemoveAttachment(index)} type="button">×</button></figure>)}</div>}</section>
        <label>标签<input name="tags" onChange={onChange} placeholder="用逗号分隔" value={form.tags} /></label>
        {form.kind === 'practice' && <label>投入分钟<input min="0" name="minutes" onChange={onChange} placeholder="可选" type="number" value={form.minutes} /></label>}
        <div><span>{form.kind === 'practice' ? '保存后会成为此技术的真实实践证据。' : form.kind === 'extension' ? '先写理论推导，再写可落地的真实场景；平台待办不属于这里。' : form.kind === 'exploration' ? '保存后会保留划线、问题与 Knowledge 引用；它不是实践证据。' : '保存后会进入该技术的学习地图。'}</span><button className="work-tech-space__solid-button" disabled={saving} type="submit">{saving ? '保存中…' : '保存记录'}</button></div>
    </form>;
}

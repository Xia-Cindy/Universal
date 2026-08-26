/* eslint-disable react/prop-types */
import { useCallback, useEffect, useMemo, useState } from 'react';

import { roomApi } from './api';
import { ARTICLE_FILTERS, articleKind, TECH_STACK_CATEGORIES, techStackCategoryFor } from './techStackTaxonomy';

const emptyStack = { name: '', category: 'AI 与知识', description: '', tags: '' };
const emptyEntry = { kind: 'note', title: '', content: '', tags: '', minutes: '', attachments: [], sourceArticleId: '', selectedQuote: '', aiQuestion: '', sources: [] };
const maxAttachments = 4;
const maxAttachmentDataUrlLength = 1_500_000;
const splitTags = (value) => String(value || '').split(/[,，\n]/).map((item) => item.trim()).filter(Boolean);
const formatDate = (value) => value ? new Intl.DateTimeFormat('zh-CN', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(value)) : '刚刚';
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
        if (!context) return reject(new Error('当前浏览器无法压缩图片。'));
        context.drawImage(image, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL('image/webp', 0.82);
        if (dataUrl.length > maxAttachmentDataUrlLength) return reject(new Error('图片压缩后仍超过 1.5 MB，请裁剪后再粘贴。'));
        resolve(dataUrl);
    };
    image.onerror = () => { URL.revokeObjectURL(url); reject(new Error('无法读取这张图片。')); };
    image.src = url;
});

export default function TechStackWorkspace({ onNavigate }) {
    const [stacks, setStacks] = useState([]);
    const [selectedId, setSelectedId] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('all');
    const [articleFilter, setArticleFilter] = useState('all');
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
        setLoading(true); setError('');
        try {
            const result = await roomApi.workTechStacks();
            setStacks(result);
            setSelectedId((current) => result.some((item) => item.id === current) ? current : (result[0]?.id || ''));
        } catch (cause) { setError(cause instanceof Error ? cause.message : '无法读取技术专题。'); }
        finally { setLoading(false); }
    }, []);
    useEffect(() => { loadStacks(); }, [loadStacks]);
    useEffect(() => { roomApi.aiStatus().then(setAiStatus).catch(() => setAiStatus({ configured: false, message: '无法读取 AI Core 配置状态。' })); }, []);

    const categorizedStacks = useMemo(() => stacks.map((stack) => ({ ...stack, taxonomy: techStackCategoryFor(stack) })), [stacks]);
    const visibleStacks = useMemo(() => selectedCategory === 'all' ? categorizedStacks : categorizedStacks.filter((stack) => stack.taxonomy.id === selectedCategory), [categorizedStacks, selectedCategory]);
    const activeCategory = useMemo(() => TECH_STACK_CATEGORIES.find((item) => item.id === selectedCategory) || null, [selectedCategory]);
    useEffect(() => {
        if (visibleStacks.length && !visibleStacks.some((stack) => stack.id === selectedId)) setSelectedId(visibleStacks[0].id);
    }, [selectedId, visibleStacks]);

    const loadDetail = useCallback(async () => {
        if (!selectedId) { setDetail(null); return; }
        setLoadingDetail(true); setError('');
        try { setDetail(await roomApi.workTechStack(selectedId)); }
        catch (cause) { setError(cause instanceof Error ? cause.message : '无法读取技术专题。'); }
        finally { setLoadingDetail(false); }
    }, [selectedId]);
    useEffect(() => { loadDetail(); }, [loadDetail]);

    const articleFeed = useMemo(() => {
        if (!detail) return [];
        const articles = (detail.articles || []).map((item) => ({ ...item, storage: 'article', date: item.updatedAt }));
        const practices = (detail.learningRecords || []).map((item) => ({ ...item, articleType: 'practice', storage: 'record', content: item.notes, date: item.updatedAt }));
        return [...articles, ...practices].filter((item) => articleFilter === 'all' || articleKind(item).id === articleFilter).sort((left, right) => new Date(right.date) - new Date(left.date));
    }, [articleFilter, detail]);
    const explorations = useMemo(() => (detail?.articles || []).filter((item) => item.articleType === 'exploration'), [detail]);
    const totalUpdates = (detail?.articles?.length || 0) + (detail?.learningRecords?.length || 0);
    const updateStackForm = (event) => setStackForm((current) => ({ ...current, [event.target.name]: event.target.value }));
    const updateEntryForm = (event) => setEntryForm((current) => ({ ...current, [event.target.name]: event.target.value }));

    const addPastedImages = async (event) => {
        const files = Array.from(event.clipboardData?.items || []).filter((item) => item.kind === 'file' && item.type.startsWith('image/')).map((item) => item.getAsFile()).filter(Boolean);
        if (!files.length) return;
        event.preventDefault();
        if (entryForm.attachments.length + files.length > maxAttachments) return setError(`每篇文章最多保留 ${maxAttachments} 张图片。`);
        setError('');
        try {
            const images = await Promise.all(files.map(compressClipboardImage));
            setEntryForm((current) => ({ ...current, attachments: [...current.attachments, ...images] }));
        } catch (cause) { setError(cause instanceof Error ? cause.message : '无法处理粘贴的图片。'); }
    };
    const captureAiSelection = (event, article) => {
        if (article.storage !== 'article') return;
        const quote = window.getSelection?.().toString().trim();
        if (!quote) return;
        setAiSelection({ articleId: article.id, articleTitle: article.title, quote });
        setAiQuestion(`请解释这段话中的「${quote.slice(0, 96)}」：它的机制、边界和一个真实应用是什么？`);
        setAiResult(null);
    };
    const askAi = async () => {
        if (!selectedId || !aiQuestion.trim()) return;
        setAskingAi(true); setError('');
        try { setAiResult(await roomApi.askWorkExploration(selectedId, { sourceArticleId: aiSelection?.articleId || '', selectedQuote: aiSelection?.quote || '', question: aiQuestion.trim() })); }
        catch (cause) { setError(cause instanceof Error ? cause.message : 'AI 暂时无法回答这个问题。'); }
        finally { setAskingAi(false); }
    };
    const addAiResultToMap = () => {
        if (!aiResult) return;
        setEntryForm({ ...emptyEntry, kind: 'exploration', title: `AI 探索：${aiQuestion.trim().slice(0, 72)}`, content: aiResult.answer, tags: 'AI探索', sourceArticleId: aiResult.sourceArticleId || aiSelection?.articleId || '', selectedQuote: aiResult.selectedQuote || aiSelection?.quote || '', aiQuestion: aiQuestion.trim(), sources: aiResult.sources || [] });
        setShowEntryForm(true);
    };
    const createStack = async (event) => {
        event.preventDefault(); setSaving(true); setError('');
        try {
            const created = await roomApi.createWorkTechStack({ name: stackForm.name.trim(), category: stackForm.category.trim() || '工程方法', proficiency: 'learning', description: stackForm.description.trim(), tags: splitTags(stackForm.tags) });
            setStacks((current) => [created, ...current]); setSelectedCategory(techStackCategoryFor(created).id); setSelectedId(created.id); setStackForm(emptyStack); setShowStackForm(false);
        } catch (cause) { setError(cause instanceof Error ? cause.message : '无法创建技术专题。'); }
        finally { setSaving(false); }
    };
    const createEntry = async (event) => {
        event.preventDefault(); if (!selectedId) return;
        setSaving(true); setError('');
        try {
            if (entryForm.kind === 'practice') {
                await roomApi.createWorkLearningRecord(selectedId, { title: entryForm.title.trim(), notes: entryForm.content.trim(), minutes: Number(entryForm.minutes) || 0, tags: splitTags(entryForm.tags), attachments: entryForm.attachments, status: 'recorded' });
            } else {
                await roomApi.createWorkArticle(selectedId, { title: entryForm.title.trim(), articleType: entryForm.kind, summary: entryForm.content.trim().slice(0, 140), content: entryForm.content.trim(), tags: splitTags(entryForm.tags), attachments: entryForm.attachments, sourceArticleId: entryForm.sourceArticleId, selectedQuote: entryForm.selectedQuote, aiQuestion: entryForm.aiQuestion, sources: entryForm.sources, status: 'published' });
            }
            setEntryForm(emptyEntry); setShowEntryForm(false); await loadDetail(); await loadStacks();
        } catch (cause) { setError(cause instanceof Error ? cause.message : '无法保存这篇文章。'); }
        finally { setSaving(false); }
    };

    return <section className="work-tech-space work-tech-publication" aria-live="polite">
        <header className="work-tech-space__hero"><div><p className="work-case-space__eyebrow">PERSONAL TECH PUBLICATION · LEARNING EVIDENCE</p><h1>把技术写成文章，<em>而不是填成履历。</em></h1><p>这是你的个人技术主题站：按领域浏览，每次理解、部署、复盘或追问都留下一篇可回看的文章。没有哪一种栏目是所有技术都必须拥有的。</p></div><div className="work-tech-space__hero-actions"><button className="work-tech-space__outline-button" onClick={() => onNavigate('/work')} type="button">← 能力入口</button><button className="work-tech-space__solid-button" onClick={() => setShowStackForm((value) => !value)} type="button">{showStackForm ? '收起新专题' : '+ 新建技术专题'}</button></div></header>
        {showStackForm && <form className="work-tech-space__create-stack" onSubmit={createStack}><label>技术名称<input autoFocus name="name" onChange={updateStackForm} placeholder="例如 Kubernetes、RAGFlow、FastAPI" required value={stackForm.name} /></label><label>所属领域<select name="category" onChange={updateStackForm} value={stackForm.category}>{TECH_STACK_CATEGORIES.map((item) => <option key={item.id} value={item.label}>{item.label}</option>)}</select></label><label>为什么值得建立这个专题？<textarea name="description" onChange={updateStackForm} placeholder="写下想解决的问题、学习动机或想验证的假设；并非一定要填写系统位置。" value={stackForm.description} /></label><label>标签<input name="tags" onChange={updateStackForm} placeholder="例如 retrieval, docker, operations" value={stackForm.tags} /></label><div><span>创建后可持续写文章；文章类型由内容决定，不预设通用模板。</span><button className="work-tech-space__solid-button" disabled={saving} type="submit">{saving ? '创建中…' : '创建技术专题'}</button></div></form>}
        {error && <p className="work-tech-space__error" role="alert">{error}</p>}
        <nav className="work-tech-space__category-nav" aria-label="技术领域"><button className={selectedCategory === 'all' ? 'is-active' : ''} onClick={() => setSelectedCategory('all')} type="button">全部 <small>{stacks.length}</small></button>{TECH_STACK_CATEGORIES.map((category) => { const count = categorizedStacks.filter((stack) => stack.taxonomy.id === category.id).length; return <button className={selectedCategory === category.id ? 'is-active' : ''} key={category.id} onClick={() => setSelectedCategory(category.id)} type="button">{category.label} <small>{count}</small></button>; })}</nav>
        <section className="work-tech-space__topic-shelf" aria-label="技术专题"><div className="work-tech-space__navigator-heading"><span>{activeCategory ? activeCategory.label : '全部技术专题'}</span><small>{activeCategory?.description || '选择一个专题，阅读与写下你的技术文章。'}</small></div><div className="work-tech-space__cube-field" role="tablist" aria-label="选择技术专题">{visibleStacks.map((stack, index) => <button aria-selected={stack.id === selectedId} className={`work-tech-space__cube ${stack.id === selectedId ? 'is-selected' : ''}`} key={stack.id} onClick={() => setSelectedId(stack.id)} role="tab" style={{ '--cube-delay': `${index * 70}ms` }} type="button"><i>{stackMark(stack.name)}</i><strong>{stack.name}</strong><small>{stack.taxonomy.label}</small></button>)}</div>{!loading && !visibleStacks.length && <p className="work-tech-space__empty-tip">这个领域还没有专题。可以新建一个技术专题，再从第一篇学习笔记开始。</p>}</section>
        <main className="work-tech-space__content" role="tabpanel">{!selectedId && !loading && <EmptyTechSpace onCreate={() => setShowStackForm(true)} />}{selectedId && (loadingDetail || !detail) && <p className="work-tech-space__loading">正在打开技术专题…</p>}{detail && !loadingDetail && <><section className="work-tech-space__focus-card work-tech-space__publication-heading"><div><span>{techStackCategoryFor(detail.techStack).label} · {detail.techStack.proficiency}</span><h2>{detail.techStack.name}</h2><p>{detail.techStack.description || '这是一个等待你用文章、实践和问题逐步定义的技术专题。'}</p></div><div><strong>{totalUpdates}</strong><small>篇已记录更新</small><div className="work-tech-space__tag-row">{detail.techStack.tags?.length ? detail.techStack.tags.map((tag) => <b key={tag}>#{tag}</b>) : <b>#学习中</b>}</div></div></section><div className="work-tech-space__publication-grid"><section className="work-tech-space__article-feed"><div className="work-tech-space__section-heading"><div><span>ARTICLE STREAM</span><h3>专题文章</h3></div><button className="work-tech-space__solid-button" onClick={() => { setEntryForm(emptyEntry); setShowEntryForm((value) => !value); }} type="button">{showEntryForm ? '收起编辑器' : '+ 写文章'}</button></div><p className="work-tech-space__feed-intro">原理、架构、笔记、实践和 AI 探索使用同一条文章流；筛选只帮助阅读，不规定你的学习顺序。</p>{showEntryForm && <EntryForm form={entryForm} onChange={updateEntryForm} onPasteImages={addPastedImages} onRemoveAttachment={(index) => setEntryForm((current) => ({ ...current, attachments: current.attachments.filter((_, itemIndex) => itemIndex !== index) }))} onSubmit={createEntry} saving={saving} />}<div className="work-tech-space__article-filters">{ARTICLE_FILTERS.map((filter) => <button className={articleFilter === filter.id ? 'is-active' : ''} key={filter.id} onClick={() => setArticleFilter(filter.id)} type="button">{filter.label}</button>)}</div>{!articleFeed.length && <p className="work-tech-space__empty-log">这里还没有符合筛选条件的文章。写下一次理解、观察或真实操作，让它成为第一篇。</p>}{articleFeed.map((item) => <ArticleCard item={item} key={`${item.storage}-${item.id}`} onSelect={captureAiSelection} />)}</section><aside className="work-tech-space__publication-aside"><AiExplorePanel aiQuestion={aiQuestion} aiResult={aiResult} aiSelection={aiSelection} aiStatus={aiStatus} asking={askingAi} explorations={explorations} knowledge={detail.relatedKnowledge || []} onAddToMap={addAiResultToMap} onAsk={askAi} onChangeQuestion={setAiQuestion} onNavigateKnowledge={() => onNavigate('/study/knowledge')} /></aside></div></>}</main>
    </section>;
}

function EmptyTechSpace({ onCreate }) { return <section className="work-tech-space__empty"><span>YOUR FIRST TECH TOPIC</span><h2>从一篇真实文章开始。</h2><p>例如写下 RAGFlow 的检索边界、Docker Compose 的部署复盘，或一段尚未理解的 Kubernetes 原理。</p><button className="work-tech-space__solid-button" onClick={onCreate} type="button">创建技术专题 →</button></section>; }
function ArticleCard({ item, onSelect }) { const kind = articleKind(item); return <article className={`work-tech-space__article-card is-${kind.id}`} data-article-id={item.storage === 'article' ? item.id : undefined} onMouseUp={(event) => onSelect(event, item)}><header><span>{kind.label}</span><small>{formatDate(item.date)}{item.minutes ? ` · ${item.minutes} 分钟` : ''}</small></header><h4>{item.title}</h4><p>{item.content || item.summary || '未附加文字。'}</p><AttachmentStrip attachments={item.attachments} /><footer>{item.tags?.length > 0 && item.tags.map((tag) => <b key={tag}>#{tag}</b>)}{item.storage === 'article' && <small>划线可向 AI 追问</small>}</footer></article>; }
function AttachmentStrip({ attachments = [] }) { if (!attachments.length) return null; return <div className="work-tech-space__attachment-strip">{attachments.map((attachment, index) => <a href={attachment} key={`${index}-${attachment.length}`} rel="noreferrer" target="_blank"><img alt={`技术文章附件 ${index + 1}`} loading="lazy" src={attachment} /></a>)}</div>; }
function AiExplorePanel({ aiQuestion, aiResult, aiSelection, aiStatus, asking, explorations, knowledge, onAddToMap, onAsk, onChangeQuestion, onNavigateKnowledge }) { return <section className="work-tech-space__ai-explore"><span>AI EXPLORE · SHARED CORE</span><h3>划线问 AI</h3><p>在文章中选中一句话后提问。AI 只检索这个专题获授权的资料，回答不会自动写入 Shared Knowledge。</p>{!aiStatus?.configured && <p className="work-tech-space__ai-status">{aiStatus?.message || '正在检查 AI Core 配置…'}</p>}{aiSelection && <div className="work-tech-space__selected-quote"><small>已选中 · {aiSelection.articleTitle}</small><q>{aiSelection.quote}</q></div>}<label className="work-tech-space__ai-question">想弄懂什么？<textarea onChange={(event) => onChangeQuestion(event.target.value)} placeholder="先划线，或直接写下一个未理解的技术问题。" value={aiQuestion} /></label><button className="work-tech-space__solid-button" disabled={asking || !aiQuestion.trim() || !aiStatus?.configured} onClick={onAsk} type="button">{asking ? 'AI 思考中…' : '问 AI →'}</button>{aiResult && <article className="work-tech-space__ai-answer"><small>{aiResult.sourceNotice}</small><p>{aiResult.answer}</p>{aiResult.sources?.length > 0 && <div className="work-tech-space__ai-sources">{aiResult.sources.map((source) => <a href={source.sourceUrl || '#'} key={source.sourceId} onClick={(event) => { if (!source.sourceUrl) event.preventDefault(); }}><strong>{source.title}</strong><span>{source.quote}</span></a>)}</div>}<button className="work-tech-space__outline-button" onClick={onAddToMap} type="button">作为文章继续编辑</button></article>}<details className="work-tech-space__knowledge-fold"><summary>已授权资料 {knowledge.length ? `· ${knowledge.length}` : ''}</summary>{knowledge.length ? knowledge.map((document) => <button key={document.id} onClick={onNavigateKnowledge} type="button"><strong>{document.fileName}</strong><small>{document.topic || document.subject || 'Knowledge document'}</small></button>) : <p>暂无授权资料。可从 Study 书架为该专题授权只读资料。</p>}</details>{explorations.length > 0 && <div className="work-tech-space__saved-explorations"><small>已保存探索</small>{explorations.map((item) => <article key={item.id}><strong>{item.aiQuestion || item.title}</strong><p>{item.selectedQuote ? `划线：${item.selectedQuote}` : item.content}</p></article>)}</div>}</section>; }
function EntryForm({ form, onChange, onPasteImages, onRemoveAttachment, onSubmit, saving }) { const descriptions = { note: '写下阅读、课程、排障或日常观察。', principle: '写下一个机制、约束或概念之间的关系。', architecture: '写下某个系统在何种上下文中如何组织；它只在适用时使用。', extension: '先写理论推导，再写它在什么真实约束下如何落地。', practice: '记录真实命令、结果、失败与复盘；它会作为实践文章显示。', exploration: '把 AI 的回答改写为自己的理解，并保留问题与来源。' }; return <form className="work-tech-space__entry-form" onPaste={onPasteImages} onSubmit={onSubmit}><label>文章类型<select name="kind" onChange={onChange} value={form.kind}><option value="note">学习笔记</option><option value="principle">原理笔记</option><option value="architecture">架构观察</option><option value="extension">理论延伸 / 落地应用</option><option value="practice">实践复盘</option><option value="exploration">AI 探索 / 未理解点</option></select></label><label>文章标题<input autoFocus name="title" onChange={onChange} placeholder="例如：为什么 Docker Socket 等同于宿主机高权限入口" required value={form.title} /></label><label>正文<textarea name="content" onChange={onChange} placeholder={descriptions[form.kind]} required value={form.content} /></label><section className="work-tech-space__image-paste" tabIndex="0"><strong>粘贴截图</strong><p>在正文或此处按 ⌘V / Ctrl+V。最多 {maxAttachments} 张；会压缩为私有学习附件，不会进入共享 Knowledge。</p>{form.attachments.length > 0 && <div>{form.attachments.map((attachment, index) => <figure key={`${index}-${attachment.length}`}><img alt={`待保存文章附件 ${index + 1}`} src={attachment} /><button aria-label={`删除图片 ${index + 1}`} onClick={() => onRemoveAttachment(index)} type="button">×</button></figure>)}</div>}</section><label>标签<input name="tags" onChange={onChange} placeholder="用逗号分隔，例如 Docker, security" value={form.tags} /></label>{form.kind === 'practice' && <label>投入分钟<input min="0" name="minutes" onChange={onChange} placeholder="可选" type="number" value={form.minutes} /></label>}<div><span>{descriptions[form.kind]}</span><button className="work-tech-space__solid-button" disabled={saving} type="submit">{saving ? '保存中…' : '发布文章'}</button></div></form>; }

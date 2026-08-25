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
    kind: 'theory',
    title: '',
    content: '',
    tags: '',
    minutes: ''
};

const splitTags = (value) => String(value || '')
    .split(/[,，\n]/)
    .map((item) => item.trim())
    .filter(Boolean);

const formatDate = (value) => value
    ? new Intl.DateTimeFormat('zh-CN', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(value))
    : '刚刚';

const stackMark = (name) => String(name || 'T').trim().slice(0, 2).toUpperCase();

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

    const timeline = useMemo(() => {
        if (!detail) return [];
        return [
            ...(detail.articles || []).map((item) => ({ ...item, kind: 'theory', date: item.updatedAt })),
            ...(detail.learningRecords || []).map((item) => ({ ...item, kind: 'practice', content: item.notes, date: item.updatedAt }))
        ].sort((left, right) => new Date(right.date) - new Date(left.date));
    }, [detail]);

    const updateStackForm = (event) => {
        const { name, value } = event.target;
        setStackForm((current) => ({ ...current, [name]: value }));
    };

    const updateEntryForm = (event) => {
        const { name, value } = event.target;
        setEntryForm((current) => ({ ...current, [name]: value }));
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
            if (entryForm.kind === 'theory') {
                await roomApi.createWorkArticle(selectedId, {
                    title: entryForm.title.trim(),
                    articleType: 'knowledge',
                    summary: entryForm.content.trim().slice(0, 140),
                    content: entryForm.content.trim(),
                    tags: splitTags(entryForm.tags),
                    status: 'published'
                });
            } else {
                await roomApi.createWorkLearningRecord(selectedId, {
                    title: entryForm.title.trim(),
                    notes: entryForm.content.trim(),
                    minutes: Number(entryForm.minutes) || 0,
                    tags: splitTags(entryForm.tags),
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
                    <p>每一项技术都是一个自己的空间：把真实部署、理论理解、工作笔记和后续练习放在一起。不会自动宣称“掌握”，只保留发生过的证据。</p>
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

                            <div className="work-tech-space__content-grid">
                                <section className="work-tech-space__timeline">
                                    <div className="work-tech-space__section-heading"><div><span>LIVE LOG</span><h3>这里发生过什么</h3></div><button className="work-tech-space__solid-button" onClick={() => setShowEntryForm((value) => !value)} type="button">{showEntryForm ? '收起记录' : '+ 添加内容'}</button></div>
                                    {showEntryForm && <EntryForm form={entryForm} onChange={updateEntryForm} onSubmit={createEntry} saving={saving} />}
                                    {!timeline.length && <p className="work-tech-space__empty-log">还没有记录。完成一次真实操作，或把刚学到的理论写下来。</p>}
                                    {timeline.map((item) => <article className={`work-tech-space__log-item is-${item.kind}`} key={`${item.kind}-${item.id}`}><span className="work-tech-space__log-kind">{item.kind === 'practice' ? '实践' : '理论'}</span><div><small>{formatDate(item.date)}{item.minutes ? ` · ${item.minutes} 分钟` : ''}</small><h4>{item.title}</h4><p>{item.content || item.summary || '未附加文字。'}</p>{item.tags?.length > 0 && <footer>{item.tags.map((tag) => <b key={tag}>#{tag}</b>)}</footer>}</div></article>)}
                                </section>
                                <section className="work-tech-space__knowledge">
                                    <span>SHARED KNOWLEDGE</span><h3>关联资料</h3><p>资料仍属于共享 Knowledge；技术栈只引用已授权内容，不复制文档或 RAGFlow 数据。</p>
                                    <div>{detail.relatedKnowledge?.length ? detail.relatedKnowledge.map((document) => <button key={document.id} onClick={() => onNavigate('/study/knowledge')} type="button"><strong>{document.fileName}</strong><small>{document.topic || document.subject || 'Knowledge document'}</small></button>) : <p className="work-tech-space__knowledge-empty">暂未关联资料。后续可从 Study 书架为此技术栈授权只读资料。</p>}</div>
                                </section>
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

function EntryForm({ form, onChange, onSubmit, saving }) {
    return <form className="work-tech-space__entry-form" onSubmit={onSubmit}>
        <label>记录类型<select name="kind" onChange={onChange} value={form.kind}><option value="theory">理论 / 工作笔记</option><option value="practice">真实操作 / 实践</option></select></label>
        <label>标题<input autoFocus name="title" onChange={onChange} placeholder={form.kind === 'theory' ? '例如：RAGFlow 在 Universe 中的边界' : '例如：完成 Room 静态资源缓存发布'} required value={form.title} /></label>
        <label>内容<textarea name="content" onChange={onChange} placeholder="记录你理解到的原理、决策、命令结果或后续问题。" required value={form.content} /></label>
        <label>标签<input name="tags" onChange={onChange} placeholder="用逗号分隔" value={form.tags} /></label>
        {form.kind === 'practice' && <label>投入分钟<input min="0" name="minutes" onChange={onChange} placeholder="可选" type="number" value={form.minutes} /></label>}
        <div><span>保存后会成为此技术的真实动态。</span><button className="work-tech-space__solid-button" disabled={saving} type="submit">{saving ? '保存中…' : '保存记录'}</button></div>
    </form>;
}

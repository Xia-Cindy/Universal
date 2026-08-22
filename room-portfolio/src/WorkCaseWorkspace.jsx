/* eslint-disable react/prop-types */
import { useCallback, useEffect, useMemo, useState } from 'react';

import { roomApi } from './api';

const STAGES = ['discover', 'define', 'govern', 'validate', 'operate', 'review'];
const EMPTY_CASE = {
    title: '',
    problem: '',
    goal: '',
    scope: '',
    nonGoal: '',
    successMetrics: '',
    risks: '',
    dependencies: '',
    status: 'active',
    currentStage: 'discover'
};

const asLines = (value) => Array.isArray(value) ? value.join('\n') : '';
const listValue = (value) => String(value || '').split('\n').map((item) => item.trim()).filter(Boolean);
const casePath = (pathname) => pathname.match(/^\/work\/cases\/([^/]+)$/)?.[1] || null;
const titleCase = (value) => value.replace(/^./, (letter) => letter.toUpperCase());

export default function WorkCaseWorkspace({ onNavigate, onReturn, pathname }) {
    const selectedCaseId = casePath(pathname);
    const [home, setHome] = useState(null);
    const [cases, setCases] = useState([]);
    const [detail, setDetail] = useState(null);
    const [form, setForm] = useState(EMPTY_CASE);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');

    const load = useCallback(async () => {
        setLoading(true);
        setError('');
        try {
            const [nextHome, nextCases, nextDetail] = await Promise.all([
                roomApi.workHome(),
                roomApi.workCases(),
                selectedCaseId ? roomApi.workCase(selectedCaseId) : Promise.resolve(null)
            ]);
            setHome(nextHome);
            setCases(nextCases || []);
            setDetail(nextDetail);
            setForm(nextDetail ? {
                title: nextDetail.title || '',
                problem: nextDetail.problem || '',
                goal: nextDetail.goal || '',
                scope: nextDetail.scope || '',
                nonGoal: nextDetail.nonGoal || '',
                successMetrics: asLines(nextDetail.successMetrics),
                risks: asLines(nextDetail.risks),
                dependencies: asLines(nextDetail.dependencies),
                status: nextDetail.status || 'active',
                currentStage: nextDetail.currentStage || 'discover'
            } : EMPTY_CASE);
        } catch (cause) {
            setError(cause instanceof Error ? cause.message : '无法读取 Work Case。');
        } finally {
            setLoading(false);
        }
    }, [selectedCaseId]);

    useEffect(() => { load(); }, [load]);

    const payload = useMemo(() => ({
        ...form,
        successMetrics: listValue(form.successMetrics),
        risks: listValue(form.risks),
        dependencies: listValue(form.dependencies)
    }), [form]);

    const updateField = (event) => {
        const { name, value } = event.target;
        setForm((current) => ({ ...current, [name]: value }));
    };

    const saveCase = async (event) => {
        event.preventDefault();
        setSaving(true);
        setError('');
        try {
            const saved = detail
                ? await roomApi.updateWorkCase(detail.id, payload)
                : await roomApi.createWorkCase(payload);
            onNavigate(`/work/cases/${saved.id}`);
        } catch (cause) {
            setError(cause instanceof Error ? cause.message : '无法保存 Practice Case。');
        } finally {
            setSaving(false);
        }
    };

    const activeCase = home?.activeCase;
    const isList = pathname === '/work/cases';
    const isDetail = Boolean(selectedCaseId);

    return (
        <main className="work-case-space">
            <header className="work-case-space__header">
                <button className="work-case-space__home" onClick={onReturn} type="button">← Universe Home</button>
                <div><span>WORK PLANET</span><strong>Practice Case Workspace</strong></div>
                <button className="work-case-space__text-button" onClick={load} type="button">刷新</button>
            </header>

            <nav className="work-case-space__nav" aria-label="Work workspace">
                <button className={!isList && !isDetail ? 'is-active' : ''} onClick={() => onNavigate('/work')} type="button">Overview</button>
                <button className={isList || isDetail ? 'is-active' : ''} onClick={() => onNavigate('/work/cases')} type="button">Cases</button>
                <span>BA · PM · Governance · Labs · Operations 将随 Case 生命周期逐步开放</span>
            </nav>

            <div className="work-case-space__layout">
                <aside className="work-case-space__rail">
                    <div className="work-case-space__rail-heading"><span>PRACTICE CASES</span><button onClick={() => onNavigate('/work/cases')} type="button">+ New</button></div>
                    {loading && <p className="work-case-space__muted">Loading cases…</p>}
                    {!loading && !cases.length && <p className="work-case-space__muted">从一个真实问题开始，而不是先建立工具集合。</p>}
                    {cases.map((item) => (
                        <button className={`work-case-space__case-link ${item.id === selectedCaseId ? 'is-selected' : ''}`} key={item.id} onClick={() => onNavigate(`/work/cases/${item.id}`)} type="button">
                            <span className={`work-case-space__status is-${item.status}`} />
                            <span><strong>{item.title}</strong><small>{titleCase(item.currentStage)} · {item.status}</small></span>
                        </button>
                    ))}
                </aside>

                <section className="work-case-space__content" aria-live="polite">
                    {error && <div className="work-case-space__error" role="alert">{error}</div>}
                    {!isList && !isDetail && (
                        <Overview activeCase={activeCase} home={home} onNavigate={onNavigate} />
                    )}
                    {isList && <CaseList form={form} onChange={updateField} onSubmit={saveCase} saving={saving} />}
                    {isDetail && <CaseDetail caseItem={detail} form={form} onChange={updateField} onSubmit={saveCase} saving={saving} />}
                </section>
            </div>
        </main>
    );
}

function Overview({ activeCase, home, onNavigate }) {
    const progress = home?.caseProgress;
    const nextAction = home?.nextAction;
    return (
        <>
            <p className="work-case-space__eyebrow">CURRENT PRACTICE</p>
            <section className="work-case-space__active-card">
                {activeCase ? (
                    <>
                        <div><span>ACTIVE CASE</span><h1>{activeCase.title}</h1><p>{activeCase.problem || '先在 Case 中写下问题、目标与边界。'}</p></div>
                        <div className="work-case-space__stage"><strong>{titleCase(activeCase.currentStage)}</strong><span>{progress?.completedStages} / {progress?.totalStages} stages progressed</span></div>
                    </>
                ) : <div><span>NO ACTIVE CASE</span><h1>从一个真实的职业问题开始。</h1><p>Case 会串联 BA、PM、治理、验证、运行与复盘；当前先建立它的边界。</p></div>}
            </section>
            <section className="work-case-space__next-card">
                <div><span>NEXT ACTION · SERVER DECIDED</span><h2>{nextAction?.label || 'Loading next action…'}</h2><p>{nextAction?.description}</p></div>
                <button onClick={() => onNavigate(nextAction?.route || '/work/cases')} type="button">Open →</button>
            </section>
            <section className="work-case-space__stage-row" aria-label="Case lifecycle">
                {(progress?.stages || STAGES).map((stage, index) => <span className={index <= (progress?.completedStages || 0) ? 'is-reached' : ''} key={stage}>{titleCase(stage)}</span>)}
            </section>
        </>
    );
}

function CaseList({ form, onChange, onSubmit, saving }) {
    return <section className="work-case-space__editor"><div className="work-case-space__editor-heading"><p className="work-case-space__eyebrow">NEW PRACTICE CASE</p><h1>定义一个可验证的问题。</h1><p>第一阶段只记录 Case brief；BA、PM 与 Labs 会在后续阶段把它推进为真实证据。</p></div><CaseForm form={form} onChange={onChange} onSubmit={onSubmit} saving={saving} submitLabel="Create Case" /></section>;
}

function CaseDetail({ caseItem, form, onChange, onSubmit, saving }) {
    if (!caseItem) return <p className="work-case-space__muted">Loading selected Case…</p>;
    return <section className="work-case-space__editor"><div className="work-case-space__editor-heading"><p className="work-case-space__eyebrow">PRACTICE CASE · {caseItem.id.slice(0, 8)}</p><h1>{caseItem.title}</h1><p>{caseItem.nextAction?.description}</p></div><CaseForm form={form} onChange={onChange} onSubmit={onSubmit} saving={saving} submitLabel="Save Case" /></section>;
}

function CaseForm({ form, onChange, onSubmit, saving, submitLabel }) {
    return <form className="work-case-space__form" onSubmit={onSubmit}>
        <label className="work-case-space__full">Case title<input name="title" onChange={onChange} placeholder="例如：企业内部 AI 助手知识问答与运营方案" required value={form.title} /></label>
        <label>Problem<textarea name="problem" onChange={onChange} placeholder="要解决的真实问题是什么？" value={form.problem} /></label>
        <label>Goal<textarea name="goal" onChange={onChange} placeholder="完成后要证明什么？" value={form.goal} /></label>
        <label>Scope<textarea name="scope" onChange={onChange} placeholder="本轮包含什么？" value={form.scope} /></label>
        <label>Non-goal<textarea name="nonGoal" onChange={onChange} placeholder="本轮明确不做什么？" value={form.nonGoal} /></label>
        <label>Success metrics<textarea name="successMetrics" onChange={onChange} placeholder="一行一项" value={form.successMetrics} /></label>
        <label>Risks<textarea name="risks" onChange={onChange} placeholder="一行一项" value={form.risks} /></label>
        <label>Dependencies<textarea name="dependencies" onChange={onChange} placeholder="一行一项" value={form.dependencies} /></label>
        <label>Status<select name="status" onChange={onChange} value={form.status}><option value="active">Active</option><option value="draft">Draft</option><option value="paused">Paused</option><option value="completed">Completed</option></select></label>
        <label>Current stage<select name="currentStage" onChange={onChange} value={form.currentStage}>{STAGES.map((stage) => <option key={stage} value={stage}>{titleCase(stage)}</option>)}</select></label>
        <div className="work-case-space__form-actions"><span>阶段跳转由服务端限制为一次前进一阶段。</span><button disabled={saving} type="submit">{saving ? 'Saving…' : submitLabel}</button></div>
    </form>;
}

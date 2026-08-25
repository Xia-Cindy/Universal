/* eslint-disable react/prop-types */
import { useCallback, useEffect, useMemo, useState } from 'react';

import { roomApi } from './api';
import TechStackWorkspace from './TechStackWorkspace';

const STAGES = ['discover', 'define', 'govern', 'validate', 'operate', 'review'];
const EMPTY_CASE = { title: '', problem: '', goal: '', scope: '', nonGoal: '', successMetrics: '', risks: '', dependencies: '', status: 'active', currentStage: 'discover' };
const LEARNING_DOMAINS = [
    { id: 'ba', index: '01', eyebrow: 'Business analysis', title: 'BA', name: '业务分析', description: '把模糊的业务现象梳理成可沟通、可验证的问题。', prompt: '我正在理解谁的真实问题？', outcomes: ['问题定义', '利益相关者视图', '流程与需求表达'], path: ['识别业务语境', '拆解角色与流程', '形成需求与验收口径'] },
    { id: 'pm', index: '02', eyebrow: 'Product & project management', title: 'PM', name: '产品与项目管理', description: '练习在目标、范围、优先级和协作之间做出清楚的选择。', prompt: '下一步最值得推进的是什么？', outcomes: ['目标与范围', '优先级判断', '推进与复盘'], path: ['确认目标与约束', '设计优先级与节奏', '沟通交付并复盘'] },
    { id: 'sre', index: '03', eyebrow: 'Site reliability engineering', title: 'SRE', name: '可靠性工程', description: '从服务目标、可观测性到事件响应，学习让系统可靠运行。', prompt: '服务失效时，我如何发现、响应并改善？', outcomes: ['服务目标与 SLO', '可观测性', '事件响应与复盘'], path: ['定义服务与可靠性目标', '建立可观察信号', '演练响应与持续改善'] },
    { id: 'data-governance', index: '04', eyebrow: 'Data governance', title: '数据治理', name: '数据治理', description: '学习数据标准、质量、权限与血缘如何支撑可信决策。', prompt: '哪些数据可以被相信、使用和追溯？', outcomes: ['数据标准', '质量与权限', '血缘与治理机制'], path: ['定义数据对象与责任', '识别质量与权限边界', '建立治理与审视回路'] },
    { id: 'tech', index: '05', eyebrow: 'Technology practice', title: '技术栈', name: '技术基础与实践', description: '连接技术理论、架构理解与低资源的本地服务练习。', prompt: '这项技术在系统中解决什么问题？', outcomes: ['理论与架构笔记', '技术栈关联', '低资源练习服务'], path: ['掌握基础概念', '理解系统位置', '在本地沙箱做小型实践'], note: '低资源练习服务将在独立沙箱准备完成后开放，不会占用 Universe OS 主服务。' }
];

const asLines = (value) => Array.isArray(value) ? value.join('\n') : '';
const listValue = (value) => String(value || '').split('\n').map((item) => item.trim()).filter(Boolean);
const casePath = (pathname) => pathname.match(/^\/work\/cases\/([^/]+)$/)?.[1] || null;
const learningDomainId = (pathname) => pathname.match(/^\/work\/learning\/([^/]+)$/)?.[1] || null;
const titleCase = (value) => value.replace(/^./, (letter) => letter.toUpperCase());

export default function WorkCaseWorkspace({ onNavigate, onReturn, pathname }) {
    const selectedCaseId = casePath(pathname);
    const selectedDomain = LEARNING_DOMAINS.find((item) => item.id === learningDomainId(pathname));
    const isCaseRoute = pathname === '/work/cases' || Boolean(selectedCaseId);
    const isTechStackRoute = pathname === '/work/tech-stack';
    const [home, setHome] = useState(null);
    const [cases, setCases] = useState([]);
    const [detail, setDetail] = useState(null);
    const [form, setForm] = useState(EMPTY_CASE);
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');
    const load = useCallback(async () => {
        if (!isCaseRoute) return;
        setLoading(true); setError('');
        try {
            const [nextHome, nextCases, nextDetail] = await Promise.all([roomApi.workHome(), roomApi.workCases(), selectedCaseId ? roomApi.workCase(selectedCaseId) : Promise.resolve(null)]);
            setHome(nextHome); setCases(nextCases || []); setDetail(nextDetail); setForm(nextDetail ? toForm(nextDetail) : EMPTY_CASE);
        } catch (cause) { setError(cause instanceof Error ? cause.message : '无法读取 Practice Case。'); } finally { setLoading(false); }
    }, [isCaseRoute, selectedCaseId]);
    useEffect(() => { load(); }, [load]);
    const payload = useMemo(() => ({ ...form, successMetrics: listValue(form.successMetrics), risks: listValue(form.risks), dependencies: listValue(form.dependencies) }), [form]);
    const updateField = (event) => { const { name, value } = event.target; setForm((current) => ({ ...current, [name]: value })); };
    const saveCase = async (event) => {
        event.preventDefault(); setSaving(true); setError('');
        try { const saved = detail ? await roomApi.updateWorkCase(detail.id, payload) : await roomApi.createWorkCase(payload); onNavigate(`/work/cases/${saved.id}`); }
        catch (cause) { setError(cause instanceof Error ? cause.message : '无法保存 Practice Case。'); } finally { setSaving(false); }
    };
    return <main className="work-case-space work-learning-space">
        <WorkHeader caseRoute={isCaseRoute} onNavigate={onNavigate} onRefresh={load} onReturn={onReturn} />
        {isCaseRoute ? <CaseWorkspace activeCase={home?.activeCase} cases={cases} detail={detail} error={error} form={form} home={home} loading={loading} onChange={updateField} onNavigate={onNavigate} onSubmit={saveCase} saving={saving} selectedCaseId={selectedCaseId} /> : isTechStackRoute ? <TechStackWorkspace onNavigate={onNavigate} /> : selectedDomain ? <LearningDomain domain={selectedDomain} onNavigate={onNavigate} /> : <LearningHome onNavigate={onNavigate} />}
    </main>;
}

function WorkHeader({ caseRoute, onNavigate, onRefresh, onReturn }) {
    const techRoute = window.location.pathname === '/work/tech-stack';
    return <><header className="work-case-space__header"><button className="work-case-space__home" onClick={onReturn} type="button">← Universe Home</button><div><span>WORK PLANET</span><strong>Work Space</strong></div>{caseRoute ? <button className="work-case-space__text-button" onClick={onRefresh} type="button">刷新 Case</button> : <span className="work-learning-space__header-signal">Personal capability field</span>}</header><nav className="work-case-space__nav work-learning-space__nav" aria-label="Work Space"><button className={!caseRoute && !techRoute ? 'is-active' : ''} onClick={() => onNavigate('/work')} type="button">学习空间</button><button className={techRoute ? 'is-active' : ''} onClick={() => onNavigate('/work/tech-stack')} type="button">技术栈</button><button className={caseRoute ? 'is-active' : ''} onClick={() => onNavigate('/work/cases')} type="button">练习案例</button><span>{caseRoute ? '把真实案例作为可选练习，而非进入空间的前提。' : techRoute ? '每一项技术都有自己的空间，记录理论、实践与共享资料。' : 'PM、BA、SRE、数据治理与技术栈：选择一个能力域开始。'}</span></nav></>;
}

function LearningHome({ onNavigate }) {
    return <section className="work-learning-home"><div className="work-learning-home__intro"><p className="work-case-space__eyebrow">YOUR PROFESSIONAL LEARNING FIELD</p><h1>把职业能力<br /><em>慢慢长成自己的。</em></h1><p>这里不要求你先填写项目、目标或履历。先从一个想真正理解的能力域进入，再把知识、练习和反思连成自己的路径。</p></div><div className="work-learning-home__orbit" aria-hidden="true"><span className="work-learning-home__orbit-ring work-learning-home__orbit-ring--outer" /><span className="work-learning-home__orbit-ring work-learning-home__orbit-ring--inner" /><span className="work-learning-home__orbit-core">WORK<br />SPACE</span>{LEARNING_DOMAINS.map((domain, index) => <i className={`work-learning-home__orbit-dot is-dot-${index + 1}`} key={domain.id} />)}</div><div className="work-learning-home__statement"><span>Start with curiosity</span><strong>不制造虚假的进度。<br />你的学习记录会在真实行动发生后才出现。</strong></div><div className="work-learning-home__domains" aria-label="职业能力域">{LEARNING_DOMAINS.map((domain) => <button className={`work-learning-home__domain is-${domain.id}`} key={domain.id} onClick={() => onNavigate(domain.id === 'tech' ? '/work/tech-stack' : `/work/learning/${domain.id}`)} type="button"><span className="work-learning-home__domain-index">{domain.index}</span><span className="work-learning-home__domain-copy"><small>{domain.eyebrow}</small><strong>{domain.title}</strong><em>{domain.name}</em><b>{domain.description}</b></span><span className="work-learning-home__domain-arrow">↗</span></button>)}</div><aside className="work-learning-home__practice-note"><span>可选的练习层</span><p>当你准备好把一个真实问题走一遍，可以进入「练习案例」。它保留为验证能力的地方，不再占据首页。</p><button onClick={() => onNavigate('/work/cases')} type="button">打开练习案例 →</button></aside></section>;
}

function LearningDomain({ domain, onNavigate }) {
    return <section className={`work-learning-domain is-${domain.id}`}><button className="work-learning-domain__back" onClick={() => onNavigate('/work')} type="button">← 返回能力域</button><div className="work-learning-domain__hero"><p>{domain.eyebrow} · {domain.index}</p><h1>{domain.title}<small>{domain.name}</small></h1><strong>{domain.prompt}</strong><span className="work-learning-domain__shape" aria-hidden="true" /></div><div className="work-learning-domain__body"><section><p className="work-case-space__eyebrow">THIS SPACE IS FOR</p><h2>{domain.description}</h2><p>先用这条清晰的个人学习路径建立概念与判断。知识资料、笔记和真实练习会在后续阶段通过共享 Knowledge 与可选 Practice Case 接入，不另建一套内容库。</p></section><section className="work-learning-domain__path"><p className="work-case-space__eyebrow">YOUR LEARNING PATH</p>{domain.path.map((item, index) => <div key={item}><span>0{index + 1}</span><strong>{item}</strong></div>)}</section><section className="work-learning-domain__outcomes"><p className="work-case-space__eyebrow">WHAT YOU WILL COLLECT</p>{domain.outcomes.map((item) => <span key={item}>{item}</span>)}{domain.note && <small>{domain.note}</small>}</section></div></section>;
}

function CaseWorkspace({ activeCase, cases, detail, error, form, home, loading, onChange, onNavigate, onSubmit, saving, selectedCaseId }) {
    const isList = !selectedCaseId;
    return <div className="work-case-space__layout"><aside className="work-case-space__rail"><div className="work-case-space__rail-heading"><span>PRACTICE CASES</span><button onClick={() => onNavigate('/work/cases')} type="button">+ New</button></div>{loading && <p className="work-case-space__muted">Loading cases…</p>}{!loading && !cases.length && <p className="work-case-space__muted">当你想把一个真实问题完整走一遍时，再在这里建立 Case。</p>}{cases.map((item) => <button className={`work-case-space__case-link ${item.id === selectedCaseId ? 'is-selected' : ''}`} key={item.id} onClick={() => onNavigate(`/work/cases/${item.id}`)} type="button"><span className={`work-case-space__status is-${item.status}`} /><span><strong>{item.title}</strong><small>{titleCase(item.currentStage)} · {item.status}</small></span></button>)}</aside><section className="work-case-space__content" aria-live="polite">{error && <div className="work-case-space__error" role="alert">{error}</div>}{isList && <CaseList form={form} onChange={onChange} onSubmit={onSubmit} saving={saving} />}{!isList && <CaseDetail caseItem={detail} form={form} onChange={onChange} onSubmit={onSubmit} saving={saving} />}{isList && activeCase && <Overview activeCase={activeCase} home={home} onNavigate={onNavigate} />}</section></div>;
}

function Overview({ activeCase, home, onNavigate }) { const progress = home?.caseProgress; const nextAction = home?.nextAction; return <section className="work-case-space__case-overview"><p className="work-case-space__eyebrow">ACTIVE PRACTICE</p><div className="work-case-space__active-card"><div><span>ACTIVE CASE</span><h1>{activeCase.title}</h1><p>{activeCase.problem || '先在 Case 中写下问题、目标与边界。'}</p></div><div className="work-case-space__stage"><strong>{titleCase(activeCase.currentStage)}</strong><span>{progress?.completedStages} / {progress?.totalStages} stages progressed</span></div></div><section className="work-case-space__next-card"><div><span>NEXT ACTION · SERVER DECIDED</span><h2>{nextAction?.label || 'Loading next action…'}</h2><p>{nextAction?.description}</p></div><button onClick={() => onNavigate(nextAction?.route || '/work/cases')} type="button">Open →</button></section></section>; }
function CaseList({ form, onChange, onSubmit, saving }) { return <section className="work-case-space__editor"><div className="work-case-space__editor-heading"><p className="work-case-space__eyebrow">NEW PRACTICE CASE</p><h1>定义一个可验证的问题。</h1><p>这是可选的练习层。你可以先在学习空间建立理解，再回来把真实问题走完整。</p></div><CaseForm form={form} onChange={onChange} onSubmit={onSubmit} saving={saving} submitLabel="Create Case" /></section>; }
function CaseDetail({ caseItem, form, onChange, onSubmit, saving }) { if (!caseItem) return <p className="work-case-space__muted">Loading selected Case…</p>; return <section className="work-case-space__editor"><div className="work-case-space__editor-heading"><p className="work-case-space__eyebrow">PRACTICE CASE · {caseItem.id.slice(0, 8)}</p><h1>{caseItem.title}</h1><p>{caseItem.nextAction?.description}</p></div><CaseForm form={form} onChange={onChange} onSubmit={onSubmit} saving={saving} submitLabel="Save Case" /></section>; }
function CaseForm({ form, onChange, onSubmit, saving, submitLabel }) { return <form className="work-case-space__form" onSubmit={onSubmit}><label className="work-case-space__full">Case title<input name="title" onChange={onChange} placeholder="例如：企业内部 AI 助手知识问答与运营方案" required value={form.title} /></label><label>Problem<textarea name="problem" onChange={onChange} placeholder="要解决的真实问题是什么？" value={form.problem} /></label><label>Goal<textarea name="goal" onChange={onChange} placeholder="完成后要证明什么？" value={form.goal} /></label><label>Scope<textarea name="scope" onChange={onChange} placeholder="本轮包含什么？" value={form.scope} /></label><label>Non-goal<textarea name="nonGoal" onChange={onChange} placeholder="本轮明确不做什么？" value={form.nonGoal} /></label><label>Success metrics<textarea name="successMetrics" onChange={onChange} placeholder="一行一项" value={form.successMetrics} /></label><label>Risks<textarea name="risks" onChange={onChange} placeholder="一行一项" value={form.risks} /></label><label>Dependencies<textarea name="dependencies" onChange={onChange} placeholder="一行一项" value={form.dependencies} /></label><label>Status<select name="status" onChange={onChange} value={form.status}><option value="active">Active</option><option value="draft">Draft</option><option value="paused">Paused</option><option value="completed">Completed</option></select></label><label>Current stage<select name="currentStage" onChange={onChange} value={form.currentStage}>{STAGES.map((stage) => <option key={stage} value={stage}>{titleCase(stage)}</option>)}</select></label><div className="work-case-space__form-actions"><span>阶段跳转由服务端限制为一次前进一阶段。</span><button disabled={saving} type="submit">{saving ? 'Saving…' : submitLabel}</button></div></form>; }
function toForm(caseItem) { return { title: caseItem.title || '', problem: caseItem.problem || '', goal: caseItem.goal || '', scope: caseItem.scope || '', nonGoal: caseItem.nonGoal || '', successMetrics: asLines(caseItem.successMetrics), risks: asLines(caseItem.risks), dependencies: asLines(caseItem.dependencies), status: caseItem.status || 'active', currentStage: caseItem.currentStage || 'discover' }; }

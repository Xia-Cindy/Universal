/* eslint-disable react/display-name, react/prop-types */
import { Loader, Stars } from '@react-three/drei';
import { Canvas } from '@react-three/fiber';
import {
    Bloom,
    EffectComposer,
    Outline,
    Selection
} from '@react-three/postprocessing';
// import { Perf } from 'r3f-perf';
import React, { Suspense, useEffect, useMemo, useRef, useState } from 'react';

import { roomApi } from './api';
import AppShell from './AppShell';
import { CameraManager } from './CameraManager/CameraManager';
import DeployedBooks from './DeployedBooks';
import { useCameraStore } from './helper/CameraStore';
import KnowledgeCardsGallery from './KnowledgeCardsGallery';
import ModuleWorld from './ModuleWorld';
import RoomModel from './RoomModel/roomModel';
import { SPACE_GROUPS } from './spaces';
import WorkCaseWorkspace from './WorkCaseWorkspace';

const moduleRoute = (moduleId) => Object.values(SPACE_GROUPS)
    .flatMap((group) => group.modules)
    .find((module) => module.id === moduleId)?.path || '';

const moduleFromRoute = (pathname) => Object.entries(SPACE_GROUPS)
    .flatMap(([space, group]) => group.modules.map((module) => ({ space, module })))
    .find(({ module }) => module.path === pathname || module.aliases?.includes(pathname)) || null;

const asWordbookBooks = (entries) => {
    const groups = new Map();
    (entries || []).forEach((entry) => {
        const tags = entry.tags?.length ? entry.tags : ['未分类'];
        tags.forEach((tag) => {
            const key = String(tag || '未分类').trim() || '未分类';
            groups.set(key, [...(groups.get(key) || []), entry]);
        });
    });
    return [...groups.entries()]
        .sort(([left], [right]) => left.localeCompare(right, 'zh-CN'))
        .map(([tag, taggedEntries]) => {
            const languages = [...new Set(taggedEntries.map((entry) => entry.language).filter(Boolean))];
            return {
                id: `wordbook-tag:${tag}`,
                title: tag,
                subtitle: languages.length === 1 ? `${languages[0]} WORDS` : 'VOCABULARY TAG',
                status: `${taggedEntries.length} 个单词`,
                subject: languages.length === 1 ? languages[0] : languages.length ? '多语言' : '',
                description: `标签词汇书 · ${taggedEntries.length} 个单词\n${languages.join(' · ') || '未设置语言'}`,
                entries: taggedEntries
            };
        });
};

const wordbookPages = (book, recallSchedules = []) => {
    const schedulesByEntry = new Map((recallSchedules || []).map((schedule) => [schedule.sourceId, schedule]));
    return {
    pages: (book.entries || []).map((entry, index) => ({
        entryId: entry.id,
        eyebrow: `${entry.language || 'VOCABULARY'} · ${index + 1} / ${book.entries.length}`,
        title: entry.word || '未命名词条',
        subtitle: entry.pronunciation ? `/${entry.pronunciation.replace(/^\/+|\/+$/g, '')}/` : book.title,
        meaning: entry.meaning || '尚未填写个人释义。',
        recallSchedule: schedulesByEntry.get(entry.id) || entry.recallSchedule || null,
        content: [
            entry.meaning || '尚未填写个人释义。',
            entry.phrases?.length ? `短语：${entry.phrases.join(' · ')}` : '',
            entry.examples?.length ? `例句：${entry.examples.join('\n')}` : '',
            entry.notes ? `笔记：${entry.notes}` : ''
        ].filter(Boolean).join('\n\n')
    }))
    };
};

const KNOWLEDGE_RESOURCES = {
    study: {
        cacheKey: 'universe-room:study-knowledge-books',
        planetType: 'study',
        list: roomApi.knowledgeDocuments,
        detail: roomApi.knowledgeDocument,
        refresh: roomApi.refreshKnowledgeDocument,
        create: roomApi.createKnowledgeDocument,
        process: roomApi.processKnowledgeDocument,
        remove: roomApi.deleteKnowledgeDocument,
        update: roomApi.updateKnowledgeDocument
    },
    work: {
        cacheKey: 'universe-room:work-knowledge-books',
        planetType: 'work',
        list: roomApi.workKnowledgeDocuments,
        detail: roomApi.workKnowledgeDocument,
        refresh: roomApi.refreshWorkKnowledgeDocument,
        create: roomApi.createWorkKnowledgeDocument,
        process: roomApi.processWorkKnowledgeDocument
    }
};

const isWorkSpacePath = (pathname) => pathname === '/work' || pathname.startsWith('/work/');
const isStudySpacePath = (pathname) => pathname === '/study' || pathname === '/study/home';
const localSylvaEnabled = import.meta.env.VITE_ENABLE_LOCAL_SYLVA !== 'false';

const LocalSylvaSpace = () => (
    <main aria-label="Immersive Universe space" style={{ background: '#050b11', height: '100dvh', overflow: 'hidden' }}>
        <iframe
            src="/sylva/index.html"
            title="Sylva interactive landscape"
            style={{ border: 0, display: 'block', height: '100%', width: '100%' }}
        />
    </main>
);

const StudyEntryFallback = ({ onReturn }) => (
    <main className="study-entry-fallback" aria-label="Study Space">
        <div className="study-entry-fallback__glow" />
        <section>
            <span>STUDY PLANET</span>
            <h1>Study Space</h1>
            <p>在知识、词汇与记忆卡片之间，逐步建立自己的学习世界。</p>
            <button onClick={onReturn} type="button">← Universe Home</button>
        </section>
    </main>
);

const Experience = React.memo(() => {
    const [pathname, setPathname] = useState(() => window.location.pathname);
    const [activeSpace, setActiveSpace] = useState(null);
    const [activeModule, setActiveModule] = useState(null);
    const [knowledgeBooks, setKnowledgeBooks] = useState([]);
    const [knowledgeRevision, setKnowledgeRevision] = useState(0);
    const [knowledgeLoadError, setKnowledgeLoadError] = useState('');
    const [wordbookEntries, setWordbookEntries] = useState([]);
    const [wordbookRevision, setWordbookRevision] = useState(0);
    const [wordbookLoadError, setWordbookLoadError] = useState('');
    const [recallSchedules, setRecallSchedules] = useState([]);
    const [studyGoals, setStudyGoals] = useState([]);
    const [workTechStacks, setWorkTechStacks] = useState([]);
    const [shareDialog, setShareDialog] = useState(null);
    const [shareStatus, setShareStatus] = useState('');
    const portalTimer = useRef(null);
    const focusSpace = useCameraStore((state) => state.focusSpace);
    const focusModule = useCameraStore((state) => state.focusModule);
    const resetCamera = useCameraStore((state) => state.default);

    useEffect(
        () => () => {
            if (portalTimer.current) window.clearTimeout(portalTimer.current);
        },
        []
    );

    useEffect(() => {
        const updatePathname = () => setPathname(window.location.pathname);
        window.addEventListener('popstate', updatePathname);
        return () => window.removeEventListener('popstate', updatePathname);
    }, []);

    const selectModule = (moduleId, { replace = false } = {}) => {
        const route = moduleRoute(moduleId);
        setActiveModule(moduleId);
        focusModule(moduleId);
        if (route && window.location.pathname !== route) {
            window.history[replace ? 'replaceState' : 'pushState']({ moduleId }, '', route);
            setPathname(route);
        }
    };

    const openSpace = (space) => {
        if (space === 'study') {
            window.history.pushState({}, '', '/study');
            setPathname('/study');
            return;
        }
        if (space === 'work') {
            window.history.pushState({}, '', '/work');
            setPathname('/work');
            return;
        }
        const moduleId = SPACE_GROUPS[space]?.modules[0]?.id;
        if (!moduleId) return;
        if (portalTimer.current) window.clearTimeout(portalTimer.current);
        setActiveSpace(space);
        setActiveModule(null);
        focusSpace(space);
        portalTimer.current = window.setTimeout(() => {
            selectModule(moduleId);
            portalTimer.current = null;
        }, 620);
    };

    const closeSpace = () => {
        if (portalTimer.current) window.clearTimeout(portalTimer.current);
        portalTimer.current = null;
        setActiveSpace(null);
        setActiveModule(null);
        resetCamera();
        if (window.location.pathname !== '/') window.history.pushState({}, '', '/');
        setPathname('/');
    };

    const navigate = (route) => {
        const canonicalRoute = route === '/study/knowledge' ? '/knowledge' : route;
        if (window.location.pathname !== canonicalRoute) window.history.pushState({}, '', canonicalRoute);
        setPathname(canonicalRoute);
    };

    useEffect(() => {
        const openFromRoute = () => {
            const resolved = moduleFromRoute(window.location.pathname);
            if (!resolved) {
                setActiveSpace(null);
                setActiveModule(null);
                resetCamera();
                return;
            }
            setActiveSpace(resolved.space);
            setActiveModule(resolved.module.id);
            focusSpace(resolved.space);
            focusModule(resolved.module.id);
        };
        openFromRoute();
        window.addEventListener('popstate', openFromRoute);
        return () => window.removeEventListener('popstate', openFromRoute);
    }, [focusModule, focusSpace, resetCamera]);

    // Resolve a direct URL before the popstate effect runs. This lets the
    // bookshelf mount immediately and avoids starting the heavy room model or
    // its Loader overlay for a module that owns its own full-screen surface.
    const routedModule = moduleFromRoute(pathname)?.module.id || null;
    const effectiveModule = activeModule || routedModule;
    const isWordbookBooks = effectiveModule === 'study-wordbook';
    const isReferenceBooks = effectiveModule === 'study-knowledge' || effectiveModule === 'work-knowledge' || isWordbookBooks;
    const isWorkKnowledge = effectiveModule === 'work-knowledge';
    const isKnowledgeCardsGallery = effectiveModule === 'study-cards';
    const knowledgeResource = KNOWLEDGE_RESOURCES[isWorkKnowledge ? 'work' : 'study'];

    useEffect(() => {
        if (!isReferenceBooks) return undefined;
        let current = true;
        const load = isWordbookBooks ? roomApi.wordbook : knowledgeResource.list;
        const cacheKey = isWordbookBooks
            ? 'universe-room:study-wordbook-books' : knowledgeResource.cacheKey;
        try {
            const cached = window.localStorage.getItem(cacheKey);
            if (cached && current) {
                const cachedData = JSON.parse(cached);
                if (isWordbookBooks) setWordbookEntries(cachedData);
                else setKnowledgeBooks(cachedData);
            }
        } catch {
            // A cache miss or a blocked storage context must not hide the API result.
        }
        if (isWordbookBooks) setWordbookLoadError('');
        else setKnowledgeLoadError('');
        load()
            .then((items) => {
                if (current) {
                    if (isWordbookBooks) setWordbookEntries(items || []);
                    else setKnowledgeBooks(items || []);
                    try {
                        window.localStorage.setItem(cacheKey, JSON.stringify(items || []));
                    } catch {
                        // API data stays authoritative when storage is unavailable.
                    }
                    if (isWordbookBooks) setWordbookLoadError('');
                    else setKnowledgeLoadError('');
                }
            })
            .catch((error) => {
                if (current) {
                    if (isWordbookBooks) setWordbookLoadError(error instanceof Error ? error.message : '无法读取 Wordbook API。');
                    else setKnowledgeLoadError(error instanceof Error ? error.message : '无法读取 Knowledge API。');
                }
            });
        return () => {
            current = false;
        };
    }, [isReferenceBooks, isWordbookBooks, knowledgeResource, knowledgeRevision, wordbookRevision]);

    useEffect(() => {
        if (!isReferenceBooks || isWorkKnowledge) return undefined;
        let current = true;
        roomApi.studyWorkspace()
            .then((workspace) => {
                if (current) setStudyGoals(workspace.goals || []);
            })
            .catch(() => {
                if (current) setStudyGoals([]);
            });
        return () => {
            current = false;
        };
    }, [isReferenceBooks, isWorkKnowledge]);

    useEffect(() => {
        if (!isReferenceBooks || isWorkKnowledge) return undefined;
        let current = true;
        roomApi.recallSchedules()
            .then((items) => { if (current) setRecallSchedules(items || []); })
            .catch(() => { if (current) setRecallSchedules([]); });
        return () => { current = false; };
    }, [isReferenceBooks, isWorkKnowledge, knowledgeRevision, wordbookRevision]);

    const createKnowledge = async ({ file, goalId, goalIds = [], subject, topic }) => {
        const extension = file.name.split('.').pop()?.toLowerCase();
        const fileType = extension === 'pdf' ? 'pdf' : ['md', 'markdown'].includes(extension) ? 'markdown' : extension === 'txt' ? 'txt' : null;
        if (!fileType) throw new Error('仅支持 TXT、Markdown 与 PDF。');
        const runtime = await roomApi.verifyKnowledgeProviderRuntime();
        if (runtime.provider === 'ragflow' && runtime.status !== 'verified') {
            const code = runtime.errorCode ? `（${runtime.errorCode}）` : '';
            throw new Error(`RAGFlow 当前不可用${code}：${runtime.message || '请稍后重试。'}`);
        }
        const content = fileType === 'pdf'
            ? await new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = () => resolve(String(reader.result || '').split(',')[1] || '');
                reader.onerror = () => reject(reader.error || new Error('文件读取失败。'));
                reader.readAsDataURL(file);
            })
            : await file.text();
        const document = await knowledgeResource.create({
            fileName: file.name,
            fileType,
            subject,
            topic,
            goalId: isWorkKnowledge ? null : goalId,
            goalIds: isWorkKnowledge ? [] : goalIds,
            content,
            contentEncoding: fileType === 'pdf' ? 'base64' : 'text',
            storagePath: file.name,
            planetType: knowledgeResource.planetType
        });
        if (document.provider !== 'local' || document.fileType !== 'pdf') await knowledgeResource.process(document.id);
        setKnowledgeRevision((revision) => revision + 1);
    };

    const deleteKnowledge = async (book) => {
        if (!knowledgeResource.remove) throw new Error('Work Knowledge 暂不支持从书架删除。');
        await knowledgeResource.remove(book.id);
        setKnowledgeRevision((revision) => revision + 1);
    };

    const openKnowledgeBook = async (book) => {
        const detail = await knowledgeResource.detail(book.id);
        if (detail.document?.provider === 'ragflow' && ['parsing', 'chunking'].includes(detail.document.processingStatus)) {
            const refreshed = await knowledgeResource.refresh(book.id);
            setKnowledgeRevision((revision) => revision + 1);
            return isWorkKnowledge ? refreshed : { ...refreshed, readingProgress: await roomApi.knowledgeReadingProgress(book.id).catch(() => null) };
        }
        return isWorkKnowledge ? detail : { ...detail, readingProgress: await roomApi.knowledgeReadingProgress(book.id).catch(() => null) };
    };

    const saveKnowledgeReadingProgress = async (documentId, bookmark) => roomApi.saveKnowledgeReadingProgress(documentId, {
        spreadIndex: Number(bookmark.spreadIndex || 0),
        pageNumber: Number(bookmark.page || 1),
        bookmarkLabel: bookmark.label || null,
        clientUpdatedAt: typeof bookmark.updatedAt === 'number'
            ? new Date(bookmark.updatedAt).toISOString()
            : bookmark.updatedAt || new Date().toISOString()
    });

    const createWordbookEntry = async (payload) => {
        await roomApi.createWordbookEntry(payload);
        setWordbookRevision((revision) => revision + 1);
    };

    const editKnowledge = async (book, payload) => {
        if (!knowledgeResource.update) throw new Error('Work Knowledge 暂不支持从书架编辑。');
        await knowledgeResource.update(book.id, payload);
        setKnowledgeRevision((revision) => revision + 1);
    };

    const editWordbookEntry = async (entry, payload) => {
        await roomApi.updateWordbookEntry(entry.id, payload);
        setWordbookRevision((revision) => revision + 1);
    };

    const deleteWordbookEntry = async (entry) => {
        await roomApi.deleteWordbookEntry(entry.id);
        setWordbookRevision((revision) => revision + 1);
    };

    const createKnowledgeAnnotation = async (documentId, payload) => {
        const annotation = await roomApi.createKnowledgeAnnotation(documentId, payload);
        setKnowledgeRevision((revision) => revision + 1);
        return annotation;
    };

    const markKnowledgeAnnotationMastered = async (documentId, annotationId, mastered) => {
        const annotation = await roomApi.markKnowledgeAnnotationMastered(documentId, annotationId, mastered);
        setKnowledgeRevision((revision) => revision + 1);
        return annotation;
    };

    const reviewWordbookEntry = async (entryId, remembered) => {
        const entry = await roomApi.reviewWordbookEntry(entryId, remembered);
        setWordbookRevision((revision) => revision + 1);
        return entry;
    };

    const adjustRecallSchedule = async (sourceType, sourceId, payload) => {
        const schedule = await roomApi.adjustRecallSchedule(sourceType, sourceId, payload);
        setRecallSchedules((current) => [
            ...current.filter((item) => !(item.sourceType === schedule.sourceType && item.sourceId === schedule.sourceId)),
            schedule
        ]);
        return schedule;
    };

    const manageKnowledgeShareGrants = async (documentId) => {
        const document = knowledgeBooks.find((item) => item.id === documentId);
        if (!(document?.goalIds || (document?.goalId ? [document.goalId] : [])).length) {
            throw new Error('请先将这份 Study 资料关联到一个学习目标，才能授权给 Work。');
        }
        const [grants, stacks] = await Promise.all([
            roomApi.knowledgeShareGrants(documentId),
            roomApi.workTechStacks()
        ]);
        setWorkTechStacks(stacks.filter((stack) => stack.status !== 'archived'));
        setShareDialog({ document, grants });
        setShareStatus('');
    };

    const grantKnowledgeToWork = async (techStackId, sourceGoalId) => {
        if (!shareDialog || !techStackId) return;
        try {
            const grant = await roomApi.createKnowledgeShareGrant(shareDialog.document.id, {
                sourceGoalId,
                techStackId
            });
            setShareDialog((current) => current ? {
                ...current,
                grants: [...current.grants.filter((item) => item.id !== grant.id), grant]
            } : current);
            setShareStatus('已授权给对应 Work Tech Stack；资料仍只保存于 Study。');
            setKnowledgeRevision((revision) => revision + 1);
        } catch (error) {
            setShareStatus(error instanceof Error ? error.message : '无法创建 Work 授权。');
        }
    };

    const revokeKnowledgeShareGrant = async (grantId) => {
        try {
            await roomApi.revokeKnowledgeShareGrant(grantId);
            setShareDialog((current) => current ? {
                ...current,
                grants: current.grants.filter((grant) => grant.id !== grantId)
            } : current);
            setShareStatus('已撤销 Work 授权。');
            setKnowledgeRevision((revision) => revision + 1);
        } catch (error) {
            setShareStatus(error instanceof Error ? error.message : '无法撤销 Work 授权。');
        }
    };

    const speakWord = (word) => {
        if (!word || !('speechSynthesis' in window) || !('SpeechSynthesisUtterance' in window)) return;
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(word);
        const voices = window.speechSynthesis.getVoices();
        const naturalVoice = voices.find((voice) => /^en(-|_)/i.test(voice.lang) && /samantha|ava|allison|karen|moira|daniel|rishi|zira|jenny|aria|google us english/i.test(voice.name))
            || voices.find((voice) => /^en(-|_)/i.test(voice.lang));
        utterance.lang = naturalVoice?.lang || 'en-US';
        if (naturalVoice) utterance.voice = naturalVoice;
        utterance.rate = 0.9;
        utterance.pitch = 1;
        window.speechSynthesis.speak(utterance);
    };

    const wordbookBooks = useMemo(() => asWordbookBooks(wordbookEntries), [wordbookEntries]);

    if (isStudySpacePath(pathname)) {
        return localSylvaEnabled ? <LocalSylvaSpace /> : <StudyEntryFallback onReturn={closeSpace} />;
    }

    if (isWorkSpacePath(pathname)) {
        return <WorkCaseWorkspace onNavigate={navigate} onReturn={closeSpace} pathname={pathname} />;
    }

    return (
        <>
            {!isKnowledgeCardsGallery && !isReferenceBooks && (
                <>
                    <Canvas
                        dpr={[1, 1.5]}
                        shadows="soft"
                        camera={{
                            fov: 38,
                            near: 0.1,
                            far: 200,
                            position: [28, 18, -28]
                        }}
                        gl={{
                            antialias: true,
                            alpha: true,
                            powerPreference: 'high-performance'
                        }}
                    >
                        <Suspense fallback={null}>
                            <Selection>
                                <EffectComposer autoClear={false}>
                                    <Outline
                                        blur
                                        visibleEdgeColor="white"
                                        edgeStrength={60}
                                        width={2000}
                                    />
                                    <Bloom mipmapBlur intensity={0.9} />
                                </EffectComposer>
                                <CameraManager />
                                {!activeModule && (
                                    <RoomModel activeSpace={activeSpace} onOpen={openSpace} />
                                )}
                                <ModuleWorld
                                    activeModule={activeModule}
                                    activeSpace={activeSpace}
                                />
                                <Stars count={900} depth={40} factor={2.2} fade radius={80} speed={0.22} />
                            </Selection>
                        </Suspense>
                    </Canvas>
                    <Loader />
                    <AppShell
                        activeModule={activeModule}
                        activeSpace={activeSpace}
                        onClose={closeSpace}
                        onOpen={openSpace}
                        onSelectModule={selectModule}
                    />
                </>
            )}
            {isKnowledgeCardsGallery && (
                <KnowledgeCardsGallery
                    onOpenSpace={openSpace}
                    onReturn={closeSpace}
                />
            )}
            {isReferenceBooks && (
                <DeployedBooks
                    books={isWordbookBooks ? wordbookBooks : knowledgeBooks.map((document) => ({
                        ...document,
                        title: document.fileName,
                        subtitle: document.fileType?.toUpperCase() || 'KNOWLEDGE',
                        status: document.processingStatus || 'ready',
                        description: `${isWorkKnowledge ? 'Work Knowledge' : 'Study Knowledge'} · ${document.subject || '未分类'} · ${document.topic || '未分类主题'}${document.scopeName ? ` · 目标：${document.scopeName}` : ''}\n${document.errorMessage || document.processingStatus || '资料已加入书架'}`
                    }))}
                    loadError={isWordbookBooks ? wordbookLoadError : knowledgeLoadError}
                    mode={isWordbookBooks ? 'wordbook' : 'knowledge'}
                    onCreate={isWordbookBooks ? createWordbookEntry : createKnowledge}
                    onDelete={isWordbookBooks || isWorkKnowledge ? undefined : deleteKnowledge}
                    onDeleteWord={isWordbookBooks ? deleteWordbookEntry : undefined}
                    onManageShareGrants={isWordbookBooks || isWorkKnowledge ? undefined : manageKnowledgeShareGrants}
                    onEditKnowledge={isWordbookBooks || isWorkKnowledge ? undefined : editKnowledge}
                    onEditWord={isWordbookBooks ? editWordbookEntry : undefined}
                    onSpeakWord={isWordbookBooks ? speakWord : undefined}
                    onCreateAnnotation={isWorkKnowledge || isWordbookBooks ? undefined : createKnowledgeAnnotation}
                    onMarkAnnotationMastered={isWorkKnowledge || isWordbookBooks ? undefined : markKnowledgeAnnotationMastered}
                    onReviewWord={isWordbookBooks ? reviewWordbookEntry : undefined}
                    onAdjustRecall={isWorkKnowledge ? undefined : adjustRecallSchedule}
                    onSaveReadingProgress={isWordbookBooks || isWorkKnowledge ? undefined : saveKnowledgeReadingProgress}
                    onOpen={isWordbookBooks ? (book) => wordbookPages(book, recallSchedules) : async (book) => {
                        const detail = await openKnowledgeBook(book);
                        return { ...detail, recallSchedules };
                    }}
                    onOpenKnowledge={() => selectModule('study-knowledge')}
                    onOpenWordbook={() => selectModule('study-wordbook')}
                    onReturn={closeSpace}
                    onRetry={() => isWordbookBooks
                        ? setWordbookRevision((revision) => revision + 1)
                        : setKnowledgeRevision((revision) => revision + 1)}
                    goals={isWorkKnowledge ? [] : studyGoals}
                />
            )}
            {shareDialog && (
                <div className="knowledge-composer knowledge-share-dialog" role="dialog" aria-modal="true" aria-label="授权 Work Knowledge">
                    <section>
                        <button className="knowledge-composer-close" type="button" aria-label="关闭 Work 授权" onClick={() => setShareDialog(null)}>×</button>
                        <p>WORK KNOWLEDGE ACCESS</p>
                        <h2>授权「{shareDialog.document.fileName}」</h2>
                        <span>这份资料仍属于 Study Goal；授权只提供指定 Tech Stack 的只读引用。</span>
                        <div className="knowledge-share-options">
                            {workTechStacks.length ? workTechStacks.map((stack) => {
                                const grant = shareDialog.grants.find((item) => item.techStackId === stack.id);
                                const sourceGoals = shareDialog.document.goalIds || (shareDialog.document.goalId ? [shareDialog.document.goalId] : []);
                                return (
                                    <div key={stack.id}>
                                        <strong>{stack.name}</strong>
                                        <small>{grant ? '已授权为只读引用' : '尚未授权'}</small>
                                        {grant
                                            ? <button type="button" onClick={() => revokeKnowledgeShareGrant(grant.id)}>撤销</button>
                                            : sourceGoals.map((sourceGoalId) => (
                                                <button key={sourceGoalId} type="button" onClick={() => grantKnowledgeToWork(stack.id, sourceGoalId)}>
                                                    以 {studyGoals.find((goal) => goal.id === sourceGoalId)?.goalName || '关联目标'} 授权
                                                </button>
                                            ))}
                                    </div>
                                );
                            }) : <span>请先在 Work 中创建一个未归档的 Tech Stack。</span>}
                        </div>
                        {shareStatus && <small className="knowledge-share-status">{shareStatus}</small>}
                    </section>
                </div>
            )}
        </>
    );
});

export default Experience;

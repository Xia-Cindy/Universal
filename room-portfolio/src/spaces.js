export const SPACE_GROUPS = {
    study: {
        title: 'Study Space',
        eyebrow: 'Study Planet',
        entryLabel: 'Study Space',
        portal: { x: 1.75, stageZ: -12.5 },
        modules: [
            { id: 'study-home', label: 'Study Space', path: '/study' },
            { id: 'study-goals', label: 'Goals', path: '/study/goals' },
            { id: 'study-tutor', label: 'Tutor', path: '/study/tutor' }
        ]
    },
    plan: {
        title: 'Planning Table',
        eyebrow: 'Study rhythm',
        entryLabel: '计划桌',
        portal: { x: -5.15, stageZ: -12.5 },
        modules: [
            { id: 'study-plan', label: 'Plan', path: '/study/plan' },
            { id: 'study-review', label: 'Review', path: '/study/review' },
            {
                id: 'study-analytics',
                label: 'Analytics',
                path: '/study/analytics'
            }
        ]
    },
    library: {
        title: 'Knowledge Library',
        eyebrow: 'Study collection',
        entryLabel: '知识书架',
        portal: { x: 7.05, stageZ: -12.5 },
        modules: [
            {
                id: 'study-knowledge',
                label: 'Knowledge',
                path: '/study/knowledge'
            },
            {
                id: 'study-wordbook',
                label: 'Wordbook',
                path: '/study/wordbook'
            }
        ]
    },
    board: {
        title: 'Memory Cards',
        eyebrow: 'Study recall',
        entryLabel: '记忆卡片',
        portal: { x: -5.15, stageZ: -12.5 },
        modules: [
            {
                id: 'study-cards',
                label: '记忆卡片与笔记',
                path: '/study/cards'
            }
        ]
    },
    work: {
        title: 'Work Space',
        eyebrow: 'Work Planet',
        entryLabel: 'Work Space',
        portal: { x: 8.85, stageZ: -12.5 },
        modules: [
            { id: 'work-home', label: 'Home', path: '/work' },
            {
                id: 'work-tech-stack',
                label: 'Tech Stack',
                path: '/work/tech-stack'
            },
            { id: 'work-projects', label: 'Projects', path: '/work/projects' },
            { id: 'work-resume', label: 'Resume', path: '/work/resume' }
        ]
    },
    novel: {
        title: '作品展墙',
        eyebrow: 'Creative studio',
        entryLabel: '作品展墙',
        portal: { x: 10.92, stageZ: -12.5 },
        modules: [{ id: 'novel-studio', label: '小说草稿', kind: 'novel', path: '/novel' }]
    }
};

export const findSpaceByModule = (moduleId) =>
    Object.entries(SPACE_GROUPS).find(([, group]) =>
        group.modules.some((module) => module.id === moduleId)
    )?.[0] || null;

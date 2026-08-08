export const SPACE_GROUPS = {
    study: {
        title: 'Study Console',
        eyebrow: 'Study Planet',
        entryLabel: '学习电脑',
        portal: { x: 1.75, stageZ: -12.5 },
        modules: [
            { id: 'study-home', label: 'Home', path: '/study' },
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
        title: 'Knowledge Board',
        eyebrow: 'Study recall',
        entryLabel: '知识黑板',
        portal: { x: -5.15, stageZ: -12.5 },
        modules: [
            {
                id: 'study-cards',
                label: '知识卡片与笔记',
                path: '/study/cards'
            }
        ]
    },
    work: {
        title: 'Work Bench',
        eyebrow: 'Work Planet',
        entryLabel: 'Work Bench',
        portal: { x: 8.85, stageZ: -12.5 },
        modules: [
            { id: 'work-home', label: 'Home', path: '/work' },
            {
                id: 'work-tech-stack',
                label: 'Tech Stack',
                path: '/work/tech-stack'
            },
            {
                id: 'work-knowledge',
                label: 'Knowledge',
                path: '/work/knowledge'
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

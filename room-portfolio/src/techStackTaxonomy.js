export const TECH_STACK_CATEGORIES = [
    {
        id: 'ai-knowledge',
        label: 'AI 与知识',
        description: '模型应用、检索、知识工程与智能工作流',
        aliases: ['ai', 'knowledge', 'rag', 'llm', 'dify', 'ragflow', 'embedding', 'retrieval', '人工智能', '知识']
    },
    {
        id: 'runtime-cloud',
        label: '云原生与运行时',
        description: 'Linux、容器、交付、网络与可控的 Kubernetes 实验',
        aliases: ['runtime', 'sre', 'operation', 'operations', 'cloud', 'docker', 'linux', 'nginx', 'kubernetes', 'k8s', '云原生', '运行时', '容器']
    },
    {
        id: 'backend-data',
        label: '后端与数据',
        description: '服务接口、数据建模、存储与治理',
        aliases: ['backend', 'api', 'data', 'database', 'governance', 'fastapi', 'postgres', 'sql', '后端', '数据', '治理']
    },
    {
        id: 'frontend-experience',
        label: '前端与体验',
        description: '界面、交互、可视化与空间体验',
        aliases: ['frontend', 'ui', 'ux', 'react', 'three', 'web', 'interaction', '前端', '体验', '交互']
    },
    {
        id: 'engineering-methods',
        label: '工程方法',
        description: '开发工具、质量、协作方法与个人工程实践',
        aliases: ['engineering', 'devops', 'tool', 'testing', 'git', 'ci', 'quality', '工程', '方法']
    }
];

const normalized = (value) => String(value || '').trim().toLowerCase();

export const techStackCategoryFor = (stack = {}) => {
    const corpus = `${normalized(stack.name)} ${normalized(stack.category)} ${Array.isArray(stack.tags) ? stack.tags.map(normalized).join(' ') : ''}`;
    const match = TECH_STACK_CATEGORIES.find((category) => category.aliases.some((alias) => corpus.includes(alias)));
    return match || TECH_STACK_CATEGORIES[TECH_STACK_CATEGORIES.length - 1];
};

export const articleKind = (article = {}) => {
    if (article.kind === 'practice' || article.articleType === 'practice') {
        return { id: 'practice', label: '实践复盘', shortLabel: '实践' };
    }
    const articleType = article.articleType || 'note';
    const labels = {
        principle: { id: 'principle', label: '原理笔记', shortLabel: '原理' },
        architecture: { id: 'architecture', label: '架构观察', shortLabel: '架构' },
        extension: { id: 'extension', label: '理论延伸', shortLabel: '延伸' },
        exploration: { id: 'exploration', label: 'AI 探索', shortLabel: 'AI 探索' },
        note: { id: 'note', label: '学习笔记', shortLabel: '笔记' },
        knowledge: { id: 'note', label: '学习笔记', shortLabel: '笔记' }
    };
    return labels[articleType] || { id: 'note', label: '学习笔记', shortLabel: '笔记' };
};

export const ARTICLE_FILTERS = [
    { id: 'all', label: '全部文章' },
    { id: 'note', label: '学习笔记' },
    { id: 'principle', label: '原理' },
    { id: 'architecture', label: '架构' },
    { id: 'extension', label: '理论延伸' },
    { id: 'practice', label: '实践复盘' },
    { id: 'exploration', label: 'AI 探索' }
];

/* eslint-disable react/prop-types */
import { SPACE_GROUPS } from './spaces';

const roomZones = [
    ['study', '学习控制台'],
    ['plan', '计划桌'],
    ['library', '知识书架'],
    ['board', '知识黑板'],
    ['work', 'Work Bench'],
    ['novel', '作品展墙']
];

export default function AppShell({
    activeModule,
    activeSpace,
    onClose,
    onOpen,
    onSelectModule
}) {
    const group = activeSpace ? SPACE_GROUPS[activeSpace] : null;
    const current = group?.modules.find((module) => module.id === activeModule);
    const isReferenceBookExperience = activeModule === 'study-knowledge' || activeModule === 'study-wordbook' || activeModule === 'work-knowledge';

    if (isReferenceBookExperience) return null;

    return (
        <>
            <header className="room-header">
                <div>
                    <span>UNIVERSE OS</span>
                    <strong>
                        {current
                            ? `${group.eyebrow} · ${current.label}`
                            : group
                              ? `${group.eyebrow} · ${group.entryLabel}`
                              : 'Personal Intelligence Room'}
                    </strong>
                </div>
                <p>
                    {current
                        ? `从${group.entryLabel}进入 · 当前模块为独立 3D 空间`
                        : group
                          ? `正在靠近${group.entryLabel}…`
                          : '点击家具进入对应工作空间'}
                </p>
            </header>

            {activeSpace && (
                <button
                    aria-label="返回主房间"
                    className="room-return"
                    onClick={onClose}
                    type="button"
                >
                    <span>←</span>
                    返回房间
                </button>
            )}

            {group && group.modules.length > 1 && (
                <nav aria-label={`${group.title} modules`} className="module-dock">
                    {group.modules.map((module) => (
                        <button
                            aria-label={module.label}
                            className={module.id === activeModule ? 'is-active' : ''}
                            key={module.id}
                            onClick={() => onSelectModule(module.id)}
                            title={module.label}
                            type="button"
                        >
                            {module.label}
                        </button>
                    ))}
                </nav>
            )}

            <nav aria-label="Room zones" className="room-dock">
                {roomZones.map(([id, label]) => (
                    <button
                        className={id === activeSpace ? 'is-active' : ''}
                        key={id}
                        onClick={() => onOpen(id)}
                        type="button"
                    >
                        <span>{label}</span>
                    </button>
                ))}
            </nav>
        </>
    );
}

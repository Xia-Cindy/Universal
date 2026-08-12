/* eslint-disable react/prop-types */
import { ContactShadows, Float, Html, RoundedBox, Sparkles, Text, useGLTF } from '@react-three/drei';
import { useFrame } from '@react-three/fiber';
import { Select } from '@react-three/postprocessing';
import { useEffect, useMemo, useRef, useState } from 'react';
import { BufferGeometry, CanvasTexture, DoubleSide, Float32BufferAttribute, SRGBColorSpace } from 'three';

import { roomApi } from './api';
import { roomMaterial, roomPalette as palette } from './roomTheme';

const loadKnowledgeBoard = async () => {
    const documents = await roomApi.knowledgeDocuments();
    const annotations = await Promise.all(
        (documents || []).map(async (document) => ({
            document,
            annotations: await roomApi.knowledgeAnnotations(document.id)
        }))
    );
    return annotations.flatMap(({ document, annotations: items }) =>
        (items || []).map((item) => ({ ...item, document }))
    );
};

const moduleLoader = (moduleId) => {
    if (moduleId === 'study-review') return roomApi.reviewQueue;
    if (moduleId === 'study-analytics') return roomApi.analytics;
    if (moduleId === 'study-knowledge') return roomApi.knowledgeDocuments;
    if (moduleId === 'study-cards') return loadKnowledgeBoard;
    if (moduleId === 'study-wordbook') return roomApi.wordbook;
    if (moduleId === 'work-knowledge') return roomApi.workKnowledgeDocuments;
    if (moduleId.startsWith('work-')) return roomApi.workHome;
    if (moduleId === 'novel-studio') return roomApi.novelDrafts;
    if (moduleId === 'study-tutor') return null;
    return roomApi.studyWorkspace;
};

const truncate = (value, length = 48) => {
    const text = String(value || '');
    return text.length > length ? `${text.slice(0, length - 1)}…` : text;
};

function usePointer(hovered) {
    useEffect(() => {
        if (hovered) document.body.style.cursor = 'pointer';
        return () => {
            document.body.style.cursor = 'auto';
        };
    }, [hovered]);
}

function Interactive({ children, onClick, selected = false, scale = 1 }) {
    const [hovered, setHovered] = useState(false);
    usePointer(hovered);
    return (
        <Select enabled={hovered || selected}>
            <group
                onClick={(event) => {
                    event.stopPropagation();
                    onClick?.();
                }}
                onPointerOut={() => setHovered(false)}
                onPointerOver={(event) => {
                    event.stopPropagation();
                    setHovered(true);
                }}
                scale={(hovered || selected) ? scale * 1.06 : scale}
            >
                {children}
            </group>
        </Select>
    );
}

function SoftMaterial({
    color,
    emissive = '#000000',
    emissiveIntensity = 0,
    opacity = 1
}) {
    return (
        <meshStandardMaterial
            color={color}
            emissive={emissive}
            emissiveIntensity={emissiveIntensity}
            opacity={opacity}
            transparent={opacity < 1}
            {...roomMaterial}
        />
    );
}

function WorldLabel({
    children,
    className = '',
    onClick,
    position = [0, 0, 0],
    scale = 0.34
}) {
    const Component = onClick ? 'button' : 'div';
    return (
        <Html center position={position} scale={scale} transform zIndexRange={[40, 1]}>
            <Component
                className={`world-label ${onClick ? 'is-interactive' : ''} ${className}`}
                onClick={(event) => {
                    event.stopPropagation();
                    onClick?.();
                }}
                type={onClick ? 'button' : undefined}
            >
                {children}
            </Component>
        </Html>
    );
}

function WorldButton({
    children,
    disabled = false,
    onClick,
    position = [0, 0, 0],
    tone = 'cyan'
}) {
    const activate = (event) => {
        event.stopPropagation();
        if (event.currentTarget.dataset.pointerActivated === 'true') {
            delete event.currentTarget.dataset.pointerActivated;
            return;
        }
        onClick?.();
    };
    return (
        <Html center position={position} scale={0.34} transform zIndexRange={[55, 10]}>
            <button
                className={`world-action is-${tone}`}
                disabled={disabled}
                onClick={activate}
                onPointerDown={(event) => {
                    // drei Html may swallow the synthetic click while the canvas is moving.
                    // Activate on pointer down and mark it so the following click is ignored.
                    event.stopPropagation();
                    event.currentTarget.dataset.pointerActivated = 'true';
                    onClick?.();
                }}
                type="button"
            >
                {children}
            </button>
        </Html>
    );
}

function RoomStage({ accent = palette.cyan, secondary = palette.pink }) {
    const dust = useRef();
    useFrame((_, delta) => {
        if (dust.current) dust.current.rotation.y += delta * 0.015;
    });
    return (
        <>
            <RoundedBox
                args={[17.5, 0.38, 10]}
                position={[0, -0.28, 0]}
                radius={0.12}
                receiveShadow
                smoothness={4}
            >
                <SoftMaterial color={palette.deskWoodDark} />
            </RoundedBox>
            {Array.from({ length: 12 }, (_, index) => (
                <mesh
                    key={`floor-${index}`}
                    position={[-7.8 + index * 1.42, -0.065, 0]}
                    receiveShadow
                >
                    <boxGeometry args={[1.34, 0.06, 9.5]} />
                    <SoftMaterial
                        color={index % 3 === 0 ? palette.deskWood : palette.woodDark}
                    />
                </mesh>
            ))}
            <RoundedBox
                args={[17.5, 8.6, 0.38]}
                position={[0, 4.02, -4.65]}
                radius={0.12}
                receiveShadow
                smoothness={4}
            >
                <SoftMaterial color={palette.wallInset} />
            </RoundedBox>
            <RoundedBox
                args={[17.1, 0.22, 0.5]}
                position={[0, 7.95, -4.42]}
                radius={0.06}
                smoothness={3}
            >
                <SoftMaterial color={palette.trim} />
            </RoundedBox>
            {[-7.85, 7.85].map((x) => (
                <RoundedBox
                    args={[0.35, 8.15, 0.55]}
                    key={x}
                    position={[x, 3.82, -4.36]}
                    radius={0.08}
                    smoothness={3}
                >
                    <SoftMaterial color={palette.wall} />
                </RoundedBox>
            ))}
            <mesh position={[-6.1, 6.5, -4.3]}>
                <sphereGeometry args={[0.08, 16, 16]} />
                <SoftMaterial
                    color={accent}
                    emissive={accent}
                    emissiveIntensity={3}
                />
            </mesh>
            <mesh position={[6.1, 6.5, -4.3]}>
                <sphereGeometry args={[0.08, 16, 16]} />
                <SoftMaterial
                    color={secondary}
                    emissive={secondary}
                    emissiveIntensity={3}
                />
            </mesh>
            <pointLight color={palette.deskGlow} distance={16} intensity={10} position={[-6, 6, 3]} />
            <pointLight color={accent} distance={13} intensity={8} position={[6, 4, 2]} />
            <group ref={dust}>
                <Sparkles
                    color={accent}
                    count={34}
                    opacity={0.35}
                    position={[0, 4, 0]}
                    scale={[16, 8, 8]}
                    size={1.2}
                    speed={0.18}
                />
            </group>
            <ContactShadows
                blur={2.8}
                far={12}
                opacity={0.45}
                position={[0, 0.01, 0]}
                scale={18}
            />
        </>
    );
}

function LoadingWorld() {
    const beacon = useRef();
    useFrame((_, delta) => {
        if (beacon.current) beacon.current.rotation.y += delta * 0.7;
    });
    return (
        <group ref={beacon} position={[0, 3, 0]}>
            <mesh>
                <icosahedronGeometry args={[0.75, 1]} />
                <SoftMaterial
                    color={palette.cyan}
                    emissive={palette.cyan}
                    emissiveIntensity={1.4}
                    opacity={0.65}
                />
            </mesh>
            <mesh rotation={[Math.PI / 2, 0, 0]}>
                <torusGeometry args={[1.25, 0.035, 10, 72]} />
                <SoftMaterial
                    color={palette.pink}
                    emissive={palette.pink}
                    emissiveIntensity={1.5}
                />
            </mesh>
            <WorldLabel position={[0, -1.25, 0]}>正在连接你的 Universe</WorldLabel>
        </group>
    );
}

function ErrorWorld({ error, onRetry }) {
    return (
        <group position={[0, 3, 0]}>
            <mesh rotation={[0, 0, Math.PI / 4]}>
                <boxGeometry args={[1.1, 1.1, 1.1]} />
                <SoftMaterial color={palette.pink} emissive={palette.pink} emissiveIntensity={0.7} />
            </mesh>
            <WorldLabel className="is-error" position={[0, -1.2, 0]}>
                <strong>空间暂时离线</strong>
                <span>{truncate(error, 80)}</span>
            </WorldLabel>
            <WorldButton onClick={onRetry} position={[0, -2.05, 0]} tone="pink">
                重试
            </WorldButton>
        </group>
    );
}

function GoalPlanet({ goal, index, current, onClick }) {
    const pivot = useRef();
    const radius = 2.15 + index * 1.12;
    const angle = index * 2.2;
    useFrame(({ clock }) => {
        if (pivot.current) {
            pivot.current.rotation.z =
                angle + clock.elapsedTime * (0.06 + index * 0.015);
        }
    });
    return (
        <group ref={pivot} rotation={[0.12, index * 0.12, angle]}>
            <mesh>
                <torusGeometry args={[radius, 0.018, 8, 96]} />
                <SoftMaterial color={current ? palette.cyan : palette.violet} opacity={0.35} />
            </mesh>
            <group position={[radius, 0, 0]}>
                <Interactive onClick={onClick} selected={current}>
                    <Float floatIntensity={0.35} rotationIntensity={0.18} speed={1.2}>
                        <mesh castShadow>
                            <icosahedronGeometry args={[current ? 0.72 : 0.56, 2]} />
                            <SoftMaterial
                                color={current ? palette.cyan : palette.violet}
                                emissive={current ? palette.cyan : palette.violet}
                                emissiveIntensity={current ? 0.55 : 0.2}
                            />
                        </mesh>
                        <WorldLabel position={[0, -1.02, 0]} scale={0.28}>
                            <strong>{truncate(goal.goalName, 22)}</strong>
                            <span>{current ? '当前目标' : goal.goalType}</span>
                        </WorldLabel>
                    </Float>
                </Interactive>
            </group>
        </group>
    );
}

function StudyGoalsWorld({ payload, reload }) {
    const [activeGoal, setActiveGoal] = useState(payload.currentGoal);
    const switchGoal = async (goal) => {
        if (goal.id === activeGoal?.id) return;
        await roomApi.switchGoal(goal.id);
        setActiveGoal(goal);
        reload();
    };
    return (
        <group position={[0, 3.4, -0.8]}>
            <Float floatIntensity={0.45} rotationIntensity={0.08} speed={1.4}>
                <mesh castShadow>
                    <sphereGeometry args={[1.12, 40, 40]} />
                    <SoftMaterial
                        color={palette.gold}
                        emissive={palette.deskGlow}
                        emissiveIntensity={0.3}
                    />
                </mesh>
                <WorldLabel position={[0, 1.6, 0]}>
                    <strong>Goal 星系</strong>
                    <span>点击行星切换当前目标</span>
                </WorldLabel>
            </Float>
            {(payload.goals || []).slice(0, 5).map((goal, index) => (
                <GoalPlanet
                    current={goal.id === activeGoal?.id}
                    goal={goal}
                    index={index}
                    key={goal.id}
                    onClick={() => switchGoal(goal)}
                />
            ))}
        </group>
    );
}

function TaskCrystal({ task, index, onComplete, onSelect, selected }) {
    const x = (index - 1) * 3.35;
    const color = task.status === 'completed' ? palette.green : palette.cyan;
    return (
        <group position={[x, 1.3, 1.5]}>
            <Interactive onClick={() => onSelect(task)} selected={selected}>
                <Float floatIntensity={0.22} rotationIntensity={0.06} speed={1 + index * 0.12}>
                    <mesh castShadow rotation={[0, Math.PI / 4, 0]}>
                        <octahedronGeometry args={[0.78, 0]} />
                        <SoftMaterial color={color} emissive={color} emissiveIntensity={0.35} />
                    </mesh>
                    <WorldLabel position={[0, -1.08, 0]} scale={0.27}>
                        <strong>{truncate(task.topic, 28)}</strong>
                        <span>{task.estimatedMinutes || 0} 分钟 · {task.status}</span>
                    </WorldLabel>
                </Float>
            </Interactive>
            {selected && task.status !== 'completed' && (
                <WorldButton onClick={() => onComplete(task.id)} position={[0, -2.0, 0]}>
                    完成任务
                </WorldButton>
            )}
        </group>
    );
}

function StudyHomeWorld({ onOpenSpace, payload, reload }) {
    const tasks = payload.todayTasks?.length
        ? payload.todayTasks
        : payload.plans?.dailyTasks?.slice(-3) || [];
    const [selected, setSelected] = useState(tasks[0] || null);
    const goal = payload.currentGoal;
    const complete = async (taskId) => {
        await roomApi.completeTask(taskId);
        reload();
    };
    return (
        <>
            <group position={[0, 4.5, -1.8]}>
                <Float floatIntensity={0.38} rotationIntensity={0.08} speed={1.1}>
                    <mesh castShadow>
                        <sphereGeometry args={[1.35, 48, 48]} />
                        <SoftMaterial
                            color={palette.blue}
                            emissive={palette.cyan}
                            emissiveIntensity={0.3}
                        />
                    </mesh>
                    <mesh rotation={[Math.PI / 2, 0, 0]}>
                        <torusGeometry args={[1.8, 0.035, 10, 96]} />
                        <SoftMaterial
                            color={palette.gold}
                            emissive={palette.deskGlow}
                            emissiveIntensity={0.8}
                        />
                    </mesh>
                </Float>
                <WorldLabel position={[0, 2.0, 0]}>
                    <strong>{goal?.goalName || '创建你的第一个 Goal'}</strong>
                    <span>{goal?.description || 'Study Planet 正在等待方向'}</span>
                </WorldLabel>
            </group>
            {tasks.slice(0, 3).map((task, index) => (
                <TaskCrystal
                    index={index}
                    key={task.id}
                    onComplete={complete}
                    onSelect={setSelected}
                    selected={selected?.id === task.id}
                    task={task}
                />
            ))}
            {!tasks.length && (
                <group position={[0, 1.25, 1.5]}>
                    <mesh castShadow rotation={[0, Math.PI / 4, 0]}>
                        <octahedronGeometry args={[0.75, 0]} />
                        <SoftMaterial color={palette.gold} emissive={palette.gold} emissiveIntensity={0.35} />
                    </mesh>
                    <WorldLabel position={[0, -1.1, 0]}>
                        <strong>今天还没有任务</strong>
                        <span>前往计划桌安排下一步</span>
                    </WorldLabel>
                </group>
            )}
            <WorldButton onClick={() => onOpenSpace('plan')} position={[0, 0.35, 3.1]}>
                {payload.primaryAction?.label || '打开计划桌'}
            </WorldButton>
        </>
    );
}

function monthCells(tasks) {
    const taskDate = tasks.find((task) => task.taskDate)?.taskDate;
    const anchor = taskDate ? new Date(`${taskDate}T12:00:00`) : new Date();
    const year = anchor.getFullYear();
    const month = anchor.getMonth();
    const first = new Date(year, month, 1);
    const mondayOffset = (first.getDay() + 6) % 7;
    const start = new Date(year, month, 1 - mondayOffset);
    return Array.from({ length: 42 }, (_, index) => {
        const date = new Date(start);
        date.setDate(start.getDate() + index);
        const key = [
            date.getFullYear(),
            String(date.getMonth() + 1).padStart(2, '0'),
            String(date.getDate()).padStart(2, '0')
        ].join('-');
        return {
            currentMonth: date.getMonth() === month,
            date,
            key,
            tasks: tasks.filter((task) => task.taskDate === key)
        };
    });
}

const PLAN_DYNAMIC_PARTS = new Set([
    'Plan_Task_Ribbon',
    'Plan_Task_Ribbon_Edge',
    'Plan_Task_Pin_Left',
    'Plan_Task_Pin_Right'
]);

const planDateTextures = new Map();

function dateTexture(value) {
    if (planDateTextures.has(value)) return planDateTextures.get(value);
    const canvas = document.createElement('canvas');
    canvas.width = 128;
    canvas.height = 128;
    const context = canvas.getContext('2d');
    context.clearRect(0, 0, 128, 128);
    context.fillStyle = '#f7ffff';
    context.font = '700 66px Manrope, sans-serif';
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.shadowColor = 'rgba(109, 208, 201, 0.9)';
    context.shadowBlur = 10;
    context.fillText(String(value), 64, 68);
    const texture = new CanvasTexture(canvas);
    texture.colorSpace = SRGBColorSpace;
    planDateTextures.set(value, texture);
    return texture;
}

function PlanDateNumber({ value }) {
    const texture = useMemo(() => dateTexture(value), [value]);
    return (
        <mesh position={[0, 0, 0.125]}>
            <planeGeometry args={[0.25, 0.25]} />
            <meshBasicMaterial
                depthTest={false}
                depthWrite={false}
                map={texture}
                side={DoubleSide}
                toneMapped={false}
                transparent
            />
        </mesh>
    );
}

function PlanNodeMesh({ node }) {
    if (!node?.geometry) return null;
    return (
        <mesh
            castShadow
            geometry={node.geometry}
            material={node.material}
            position={node.position.toArray()}
            quaternion={node.quaternion.toArray()}
            receiveShadow
            scale={node.scale.toArray()}
        />
    );
}

function PlanTaskRibbon({ cell, nodes, onComplete }) {
    const ribbon = useRef();
    useFrame((_, delta) => {
        if (!ribbon.current) return;
        ribbon.current.position.y += (0 - ribbon.current.position.y) * Math.min(1, delta * 5.2);
        ribbon.current.position.z += (0 - ribbon.current.position.z) * Math.min(1, delta * 5.2);
    });
    const task = cell.tasks[0];
    return (
        <group key={cell.key} ref={ribbon} position={[0, -0.62, -0.35]}>
            {[...PLAN_DYNAMIC_PARTS].map((name) => (
                <PlanNodeMesh key={name} node={nodes[name]} />
            ))}
            <WorldLabel className="plan-ribbon-copy" position={[0, 1.56, 1.08]} scale={0.4}>
                <strong>
                    {cell.date.getMonth() + 1} 月 {cell.date.getDate()} 日
                </strong>
                <span>
                    {task
                        ? `${truncate(task.topic, 34)} · ${task.subject} · ${task.estimatedMinutes} 分钟`
                        : '这一天留给休息、复盘或自由探索'}
                </span>
                {cell.tasks.length > 1 && <small>另有 {cell.tasks.length - 1} 项任务</small>}
            </WorldLabel>
            {task && task.status !== 'completed' && (
                <WorldButton onClick={() => onComplete(task.id)} position={[0, 0.88, 1.2]}>
                    完成任务
                </WorldButton>
            )}
        </group>
    );
}

function PlanOrbitCalendar({ cells, onComplete, onSelect, selected }) {
    const { nodes, scene } = useGLTF('/assets/PlanOrbit.glb');
    const staticScene = useMemo(() => {
        const clone = scene.clone(true);
        clone.traverse((child) => {
            if (
                child.name.startsWith('Plan_Date_') ||
                child.name === 'Plan_Title' ||
                PLAN_DYNAMIC_PARTS.has(child.name)
            ) {
                child.visible = false;
            }
            if (child.isMesh) {
                child.castShadow = true;
                child.receiveShadow = true;
            }
        });
        return clone;
    }, [scene]);

    return (
        <group position={[0, -0.02, -1.35]} scale={1.03}>
            <primitive object={staticScene} />
            {[1.02, 1.45, 1.88, 2.31, 2.74, 3.17].map((radius, index) => (
                <WorldLabel
                    key={radius}
                    position={[radius, 4.35, 0.15]}
                    scale={0.12}
                >
                    <small>W{index + 1}</small>
                </WorldLabel>
            ))}
            {cells.map((cell, index) => {
                const node = nodes[`Plan_Date_${String(index).padStart(2, '0')}`];
                if (!node) return null;
                const isSelected = selected?.key === cell.key;
                const completed = cell.tasks.length > 0 &&
                    cell.tasks.every((task) => task.status === 'completed');
                const color = !cell.currentMonth
                    ? palette.woodDark
                    : completed
                      ? palette.green
                      : cell.tasks.length
                        ? palette.cyan
                        : palette.blue;
                const position = node.position.toArray();
                position[2] += isSelected ? 0.48 : 0.08;
                return (
                    <group
                        key={cell.key}
                        position={position}
                        scale={node.scale.toArray()}
                    >
                        <Interactive onClick={() => onSelect(cell)} selected={isSelected} scale={isSelected ? 1.2 : 1}>
                            <group quaternion={node.quaternion.toArray()}>
                                <mesh castShadow geometry={node.geometry} receiveShadow>
                                    <SoftMaterial
                                        color={color}
                                        emissive={isSelected || cell.tasks.length ? color : '#000000'}
                                        emissiveIntensity={isSelected ? 1.15 : cell.tasks.length ? 0.35 : 0}
                                    />
                                </mesh>
                                {isSelected && (
                                    <mesh position={[0, 0, 0.1]}>
                                        <torusGeometry args={[0.23, 0.025, 10, 64]} />
                                        <SoftMaterial color={palette.gold} emissive={palette.gold} emissiveIntensity={1.4} />
                                    </mesh>
                                )}
                            </group>
                            <PlanDateNumber value={cell.date.getDate()} />
                            <WorldLabel
                                className="plan-date-label"
                                onClick={() => onSelect(cell)}
                                position={[0, 0, 0.13]}
                                scale={cell.currentMonth ? 0.3 : 0.22}
                            >
                                <strong>{cell.date.getDate()}</strong>
                            </WorldLabel>
                        </Interactive>
                    </group>
                );
            })}
            <WorldLabel position={[0, 7.25, 0.55]} scale={0.3}>
                <strong>
                    {selected.date.getFullYear()} 年 {selected.date.getMonth() + 1} 月
                </strong>
                <span>从内到外是 6 周轨道，点击日期唤起任务纸带</span>
            </WorldLabel>
            <PlanTaskRibbon cell={selected} nodes={nodes} onComplete={onComplete} />
        </group>
    );
}

function StudyPlanWorld({ payload, reload }) {
    const tasks = useMemo(
        () => payload.plans?.dailyTasks || [],
        [payload.plans?.dailyTasks]
    );
    const cells = useMemo(() => monthCells(tasks), [tasks]);
    const initial = cells.find((cell) => cell.tasks.length) || cells[0];
    const [selected, setSelected] = useState(initial);
    const complete = async (taskId) => {
        await roomApi.completeTask(taskId);
        reload();
    };
    return (
        <PlanOrbitCalendar
            cells={cells}
            onComplete={complete}
            onSelect={setSelected}
            selected={selected}
        />
    );
}

function StudyTutorWorld() {
    const core = useRef();
    const [question, setQuestion] = useState('');
    const [response, setResponse] = useState(null);
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState('');
    useFrame(({ clock }) => {
        if (!core.current) return;
        core.current.rotation.y = clock.elapsedTime * 0.22;
        core.current.position.y = 3.7 + Math.sin(clock.elapsedTime * 1.2) * 0.14;
    });
    const ask = async () => {
        if (!question.trim()) return;
        setBusy(true);
        setError('');
        try {
            setResponse(await roomApi.tutorAsk(question.trim()));
        } catch (requestError) {
            setError(requestError.message);
        } finally {
            setBusy(false);
        }
    };
    return (
        <>
            <group ref={core} position={[0, 3.7, -0.6]}>
                <mesh castShadow>
                    <icosahedronGeometry args={[1.35, 2]} />
                    <SoftMaterial
                        color={palette.violet}
                        emissive={palette.cyan}
                        emissiveIntensity={0.46}
                        opacity={0.82}
                    />
                </mesh>
                {[0, 1, 2].map((index) => (
                    <mesh
                        key={index}
                        rotation={[Math.PI / 2 + index * 0.35, index * 0.5, 0]}
                    >
                        <torusGeometry args={[2 + index * 0.45, 0.035, 10, 96]} />
                        <SoftMaterial
                            color={index % 2 ? palette.pink : palette.cyan}
                            emissive={index % 2 ? palette.pink : palette.cyan}
                            emissiveIntensity={1}
                        />
                    </mesh>
                ))}
            </group>
            <group position={[0, 0.7, 2.35]}>
                <RoundedBox args={[7.2, 1.05, 1.6]} castShadow radius={0.18} smoothness={4}>
                    <SoftMaterial color={palette.deskWood} />
                </RoundedBox>
                <Html center position={[0, 0.12, 0.84]} scale={0.3} transform>
                    <form
                        className="tutor-instrument"
                        onSubmit={(event) => {
                            event.preventDefault();
                            ask();
                        }}
                    >
                        <input
                            aria-label="向 Tutor 提问"
                            onChange={(event) => setQuestion(event.target.value)}
                            placeholder="对当前学习内容提问"
                            value={question}
                        />
                        <button disabled={busy || !question.trim()} type="submit">
                            {busy ? '思考中' : '唤醒 Tutor'}
                        </button>
                    </form>
                </Html>
            </group>
            <WorldLabel className="world-quote" position={[0, 6.55, -1.6]} scale={0.31}>
                <strong>{response ? 'Tutor 回答' : 'Study Tutor'}</strong>
                <span>
                    {response
                        ? truncate(response.answer, 150)
                        : '问题会进入 AI Core，并结合当前 Goal、Plan 与可用 Knowledge。'}
                </span>
                {response?.suggestedNextAction && (
                    <small>{truncate(response.suggestedNextAction, 80)}</small>
                )}
                {error && <small>{truncate(error, 80)}</small>}
            </WorldLabel>
        </>
    );
}

function ReviewWorld({ payload, reload }) {
    const [selected, setSelected] = useState(payload[0] || null);
    const complete = async () => {
        if (!selected) return;
        await roomApi.completeReview(selected.review.id);
        setSelected(null);
        reload();
    };
    return (
        <>
            {(payload || []).slice(0, 7).map((item, index) => {
                const angle = (index / Math.max(payload.length, 1)) * Math.PI * 2;
                const position = [Math.cos(angle) * 4.3, 2.8 + (index % 2) * 0.7, Math.sin(angle) * 2.2 - 0.8];
                return (
                    <group key={item.review.id} position={position}>
                        <Interactive
                            onClick={() => setSelected(item)}
                            selected={selected?.review.id === item.review.id}
                        >
                            <Float floatIntensity={0.4} rotationIntensity={0.2} speed={1 + index * 0.1}>
                                <mesh castShadow>
                                    <dodecahedronGeometry args={[0.68, 0]} />
                                    <SoftMaterial
                                        color={index % 2 ? palette.violet : palette.green}
                                        emissive={index % 2 ? palette.violet : palette.green}
                                        emissiveIntensity={0.28}
                                    />
                                </mesh>
                            </Float>
                        </Interactive>
                    </group>
                );
            })}
            <WorldLabel position={[0, 6.8, -1]}>
                <strong>Review Memory Orbit</strong>
                <span>点击记忆晶体查看复习事实</span>
            </WorldLabel>
            {selected && (
                <group position={[0, 1.2, 2.3]}>
                    <RoundedBox args={[6.7, 1.1, 1.5]} castShadow radius={0.18} smoothness={4}>
                        <SoftMaterial color={palette.paper} emissive={palette.gold} emissiveIntensity={0.1} />
                    </RoundedBox>
                    <WorldLabel className="is-dark" position={[0, 0.12, 0.8]}>
                        <strong>{truncate(selected.wrongQuestion.question, 55)}</strong>
                        <span>
                            {selected.wrongQuestion.subject} · 第 {selected.review.stage} 次 · {selected.review.dueDate}
                        </span>
                    </WorldLabel>
                    <WorldButton onClick={complete} position={[0, -1, 0.4]}>
                        完成复习
                    </WorldButton>
                </group>
            )}
        </>
    );
}

function AnalyticsWorld({ payload }) {
    const summary = payload.progressSummary || {};
    const metrics = [
        ['任务完成率', Math.round((summary.taskCompletionRate || 0) * 100), '%', palette.cyan],
        ['学习分钟', summary.totalStudyMinutes || 0, 'm', palette.gold],
        ['学习场次', summary.finishedSessions || 0, '', palette.pink],
        ['学习事件', summary.learningEvents || 0, '', palette.violet]
    ];
    const [selected, setSelected] = useState(0);
    return (
        <>
            <group position={[0.38, 0, -0.8]}>
                {metrics.map(([label, value, unit, color], index) => {
                    const height = 1.1 + Math.min(Number(value), 100) * 0.027;
                    const x = (index - 1.5) * 2.3;
                    return (
                        <group key={label} position={[x, 0, 0]}>
                            <Interactive onClick={() => setSelected(index)} selected={selected === index}>
                                <RoundedBox
                                    args={[1.25, height, 1.25]}
                                    castShadow
                                    position={[0, height / 2, 0]}
                                    radius={0.18}
                                    smoothness={4}
                                >
                                    <SoftMaterial color={color} emissive={color} emissiveIntensity={0.24} />
                                </RoundedBox>
                                <WorldLabel position={[0, height + 0.55, 0]} scale={0.26}>
                                    <strong>{value}{unit}</strong>
                                    <span>{label}</span>
                                </WorldLabel>
                            </Interactive>
                        </group>
                    );
                })}
            </group>
            <group position={[0, 5.7, -1.5]}>
                <mesh rotation={[Math.PI / 2, 0, 0]}>
                    <torusGeometry args={[2.15, 0.08, 12, 96]} />
                    <SoftMaterial
                        color={metrics[selected][3]}
                        emissive={metrics[selected][3]}
                        emissiveIntensity={1}
                    />
                </mesh>
                <WorldLabel position={[0, 0, 0.2]}>
                    <strong>{metrics[selected][0]}</strong>
                    <span>
                        {payload.learningInsights?.[selected] ||
                            payload.recommendedActions?.[0] ||
                            '继续积累真实学习数据'}
                    </span>
                </WorldLabel>
            </group>
        </>
    );
}

const bookColors = [palette.cyan, palette.pink, palette.gold, palette.blue, palette.violet, palette.green];

const CAROUSEL_GAP = 3.28;

const videoBookPalettes = [
    { accent: '#70936b', art: '#1d422b', cover: '#c9e6a8', ink: '#173522', label: '#f0f5ce', kind: 'botanical' },
    { accent: '#8c3428', art: '#d8a44d', cover: '#d46441', ink: '#4b251f', label: '#f6d878', kind: 'alchemist' },
    { accent: '#27677b', art: '#dfc58d', cover: '#75b8cf', ink: '#173c51', label: '#dfeeda', kind: 'orbital' }
];

function stableBookHash(value) {
    return Array.from(String(value || 'knowledge')).reduce((hash, character) => {
        const next = hash ^ character.charCodeAt(0);
        return Math.imul(next, 16777619) >>> 0;
    }, 2166136261);
}

function coverStyleFor(book) {
    const seed = `${book?.id || ''}:${book?.fileName || book?.title || ''}:${book?.topic || ''}:${book?.fileType || ''}`;
    return videoBookPalettes[stableBookHash(seed) % videoBookPalettes.length];
}

function CoverArtwork({ style }) {
    if (style.kind === 'botanical') {
        return (
            <>
                <RoundedBox args={[2.28, 3.62, 0.035]} position={[0, 0, 0.18]} radius={0.05} smoothness={3}>
                    <SoftMaterial color={style.label} />
                </RoundedBox>
                {[-0.64, -0.28, 0.18, 0.58].map((x, index) => (
                    <mesh key={x} position={[x, -0.84 + (index % 2) * 0.28, 0.215]} rotation={[0, 0, index % 2 ? 0.72 : -0.72]} scale={[0.12, 0.25, 0.035]}>
                        <sphereGeometry args={[1, 18, 18]} />
                        <meshStandardMaterial color={style.art} roughness={0.84} />
                    </mesh>
                ))}
            </>
        );
    }
    if (style.kind === 'alchemist') {
        return (
            <>
                <RoundedBox args={[2.3, 3.64, 0.035]} position={[0, 0, 0.18]} radius={0.05} smoothness={3}>
                    <SoftMaterial color={style.accent} />
                </RoundedBox>
                <mesh position={[0, -0.34, 0.22]} rotation={[Math.PI / 2, 0, 0]}>
                    <cylinderGeometry args={[0.83, 0.83, 0.04, 48]} />
                    <meshStandardMaterial color={style.art} roughness={0.72} metalness={0.14} />
                </mesh>
                <mesh position={[0, -0.34, 0.245]} rotation={[Math.PI / 2, 0, 0]}>
                    <torusGeometry args={[0.62, 0.035, 12, 48]} />
                    <meshStandardMaterial color={style.label} emissive={style.label} emissiveIntensity={0.08} />
                </mesh>
            </>
        );
    }
    return (
        <>
            <RoundedBox args={[2.3, 3.64, 0.035]} position={[0, 0, 0.18]} radius={0.05} smoothness={3}>
                <SoftMaterial color="#d5ecdf" />
            </RoundedBox>
            <mesh position={[0, -0.22, 0.22]} rotation={[Math.PI / 2, 0, 0]}>
                <cylinderGeometry args={[0.84, 0.84, 0.04, 48]} />
                <meshStandardMaterial color={style.art} roughness={0.62} />
            </mesh>
            <mesh position={[0.18, -0.12, 0.245]} rotation={[Math.PI / 2, 0, 0]}>
                <torusGeometry args={[0.48, 0.04, 12, 48]} />
                <meshStandardMaterial color={style.label} emissive={style.label} emissiveIntensity={0.12} />
            </mesh>
        </>
    );
}

function BookCover({ book, color, onPick, position, selected, subtitle }) {
    const style = coverStyleFor(book);
    return (
        <group position={position} rotation={[0, position[0] * -0.035, 0]}>
            <Interactive onClick={onPick} selected={selected} scale={1}>
                <RoundedBox args={[2.7, 4.05, 0.32]} castShadow radius={0.1} smoothness={4}>
                    <SoftMaterial color={style.cover || color} emissive={selected ? style.cover : '#000000'} emissiveIntensity={selected ? 0.34 : 0} />
                </RoundedBox>
                <CoverArtwork style={style} />
                <Text anchorX="center" anchorY="middle" color={style.ink} fontSize={0.13} letterSpacing={0.045} maxWidth={1.85} position={[0, 1.18, 0.26]}>
                    {String(subtitle || 'KNOWLEDGE').toUpperCase()}
                </Text>
                <Text anchorX="center" anchorY="middle" color={style.ink} fontSize={0.3} lineHeight={0.9} maxWidth={1.82} position={[0, 0.46, 0.27]}>
                    {truncate(book.title, 32)}
                </Text>
                <Text anchorX="center" anchorY="middle" color={style.ink} fontSize={0.12} letterSpacing={0.035} maxWidth={1.75} position={[0, -1.26, 0.26]}>
                    {truncate(book.status, 22)}
                </Text>
            </Interactive>
        </group>
    );
}

function PhysicalWorldButton({ children, disabled = false, onClick, position, tone = 'cyan' }) {
    const color = tone === 'pink' ? palette.pink : palette.cyan;
    return (
        <group position={position}>
            <Interactive onClick={disabled ? undefined : onClick} selected={false} scale={1}>
                <RoundedBox args={[1.46, 0.48, 0.18]} castShadow radius={0.08} smoothness={3}>
                    <SoftMaterial
                        color={disabled ? palette.wallInset : palette.deskWoodDark}
                        emissive={disabled ? '#000000' : color}
                        emissiveIntensity={disabled ? 0 : 0.22}
                    />
                </RoundedBox>
            </Interactive>
            <Text
                anchorX="center"
                anchorY="middle"
                color={disabled ? '#8d7a86' : '#eafffc'}
                fontSize={0.16}
                maxWidth={1.2}
                position={[0, 0, 0.13]}
            >
                {children}
            </Text>
        </group>
    );
}

function BookCarousel({ activeBook, books, carouselIndex, emptyCopy, onMove, onPick, phase, subtitle, title }) {
    const rail = useRef();
    useFrame((_, delta) => {
        if (!rail.current) return;
        rail.current.position.x += (-carouselIndex * CAROUSEL_GAP - rail.current.position.x) * Math.min(1, delta * 8);
    });
    const canMovePrevious = carouselIndex > 0;
    const canMoveNext = carouselIndex < books.length - 1;
    return (
        <>
            <WorldLabel position={[-5.65, 5.85, -2.0]} scale={0.28}>
                <strong>{title}</strong>
                <span>{subtitle}</span>
            </WorldLabel>
            <group ref={rail}>
                {books.filter((book) => phase === 'browse' || book.id !== activeBook?.id).map((book) => (
                    <BookCover
                        book={book}
                        color={bookColors[book.carouselIndex % bookColors.length]}
                        key={book.id}
                        onPick={() => onPick(book)}
                        position={[book.carouselIndex * CAROUSEL_GAP, 2.2, -1.55]}
                        selected={activeBook?.id === book.id && phase !== 'browse'}
                        subtitle={book.subtitle}
                    />
                ))}
            </group>
            <pointLight color={palette.paper} distance={13} intensity={13} position={[0, 4.2, 2.4]} />
            {!books.length && <WorldLabel position={[0, 2.7, -1.85]}><strong>这里还没有书</strong><span>{emptyCopy}</span></WorldLabel>}
            {books.length > 1 && <>
                <PhysicalWorldButton disabled={!canMovePrevious || phase !== 'browse'} onClick={() => onMove(-1)} position={[-5.2, 0.95, -1.25]}>← 左滑</PhysicalWorldButton>
                <WorldLabel className="is-dark" position={[0, 0.98, -1.25]} scale={0.2}><span>{carouselIndex + 1} / {books.length} · 横向浏览</span></WorldLabel>
                <PhysicalWorldButton disabled={!canMoveNext || phase !== 'browse'} onClick={() => onMove(1)} position={[5.2, 0.95, -1.25]}>右滑 →</PhysicalWorldButton>
            </>}
        </>
    );
}

function BookPickup({ book, color, onComplete, startPosition = [-4.7, 1.45, -3.25] }) {
    const group = useRef();
    const finished = useRef(false);
    const style = coverStyleFor(book);
    useFrame((_, delta) => {
        const node = group.current;
        if (!node) return;
        const progress = Math.min(1, (node.userData.progress || 0) + delta * 1.75);
        node.userData.progress = progress;
        node.position.set(
            startPosition[0] * (1 - progress),
            startPosition[1] * (1 - progress) + 1.1 * progress,
            startPosition[2] * (1 - progress) + 3 * progress
        );
        node.rotation.set(0.1 - progress * 0.25, progress * 0.4, 0);
        node.scale.setScalar(0.82 + progress * 1.4);
        if (progress >= 1 && !finished.current) {
            finished.current = true;
            onComplete();
        }
    });
    return (
        <group ref={group} position={startPosition}>
            <RoundedBox args={[1.56, 2.32, 0.3]} castShadow radius={0.08} smoothness={4}>
                <SoftMaterial color={style.cover || color} emissive={style.cover || color} emissiveIntensity={0.3} />
            </RoundedBox>
            <RoundedBox args={[1.22, 1.88, 0.035]} position={[0, 0, 0.17]} radius={0.04} smoothness={3}>
                <SoftMaterial color={style.label} />
            </RoundedBox>
            <Text anchorX="center" anchorY="middle" color={style.ink} fontSize={0.17} maxWidth={1.08} position={[0, 0.08, 0.21]}>
                {truncate(book.title, 22)}
            </Text>
        </group>
    );
}

function TurningLeaf({ direction, turnKey }) {
    const hinge = useRef();
    const leaf = useRef();
    useFrame((_, delta) => {
        if (!hinge.current || !leaf.current) return;
        const progress = Math.min(1, (hinge.current.userData.progress || 0) + delta * 2.15);
        hinge.current.userData.progress = progress;
        hinge.current.rotation.y = (direction === 'next' ? -Math.PI : Math.PI) * progress;
        leaf.current.material.opacity = Math.max(0, 0.84 - progress * 0.56);
    });
    return (
        <group key={turnKey} ref={hinge} position={[0.02, 1.45, 2.38]}>
            <mesh
                ref={leaf}
                position={[direction === 'next' ? 1.8 : -1.8, 0, 0]}
                rotation={[0, direction === 'next' ? 0.035 : -0.035, 0]}
            >
                <boxGeometry args={[3.6, 2.12, 0.026]} />
                <meshStandardMaterial color="#fff7e8" opacity={0.84} side={DoubleSide} transparent {...roomMaterial} />
            </mesh>
        </group>
    );
}

function BookReader({ book, onBack, onPageChange, pages }) {
    const [pageIndex, setPageIndex] = useState(0);
    const [flip, setFlip] = useState(null);
    const left = pages[pageIndex] || pages[0];
    const right = pages[pageIndex + 1] || null;
    const canPrevious = pageIndex > 0;
    const canNext = pageIndex < pages.length - 1;
    const flipPage = (direction) => {
        if (direction === 'next' && !canNext) return;
        if (direction === 'previous' && !canPrevious) return;
        const nextPageIndex = pageIndex + (direction === 'next' ? 1 : -1);
        setFlip({ direction, key: `${direction}-${pageIndex}-${Date.now()}` });
        setPageIndex(nextPageIndex);
        onPageChange?.(pages[nextPageIndex]);
    };
    return (
        <group position={[0, 1.2, 2.15]} rotation={[-0.16, 0, 0]}>
            <RoundedBox args={[3.72, 2.25, 0.14]} position={[-1.78, 0, 0]} radius={0.06} rotation={[0.03, 0.2, 0.05]} smoothness={3}>
                <SoftMaterial color={palette.paper} emissive={palette.paper} emissiveIntensity={0.16} />
            </RoundedBox>
            <RoundedBox args={[3.72, 2.25, 0.14]} position={[1.78, 0, 0]} radius={0.06} rotation={[0.03, -0.2, -0.05]} smoothness={3}>
                <SoftMaterial color={palette.paperShadow} emissive={palette.paper} emissiveIntensity={0.12} />
            </RoundedBox>
            <RoundedBox args={[0.12, 2.24, 0.12]} position={[0, 0, 0.08]} radius={0.03} smoothness={2}>
                <SoftMaterial color={palette.deskWoodDark} />
            </RoundedBox>
            {flip && <TurningLeaf direction={flip.direction} key={flip.key} turnKey={flip.key} />}
            <Interactive onClick={() => flipPage('previous')} scale={1}>
                <mesh position={[-1.78, 0, 0.18]}>
                    <planeGeometry args={[3.42, 2.02]} />
                    <meshBasicMaterial color="#ffffff" opacity={0.001} transparent />
                </mesh>
            </Interactive>
            <Interactive onClick={() => flipPage('next')} scale={1}>
                <mesh position={[1.78, 0, 0.18]}>
                    <planeGeometry args={[3.42, 2.02]} />
                    <meshBasicMaterial color="#ffffff" opacity={0.001} transparent />
                </mesh>
            </Interactive>
            <WorldLabel className="is-dark book-copy" onClick={() => flipPage('previous')} position={[-1.78, 0.08, 0.25]} scale={0.31}>
                <small>{left?.eyebrow || book.subtitle}</small>
                <strong>{left?.title || book.title}</strong>
                <span>{left?.body || '尚未读取到页面内容。'}</span>
            </WorldLabel>
            <WorldLabel className="is-dark book-copy" onClick={() => flipPage('next')} position={[1.78, 0.08, 0.25]} scale={0.31}>
                <small>{right?.eyebrow || '阅读提示'}</small>
                <strong>{right?.title || '点击右页翻到下一页'}</strong>
                <span>{right?.body || '点击左页可返回上一页。'}</span>
            </WorldLabel>
            <WorldLabel className="is-dark" position={[0, -1.43, 0.27]} scale={0.21}>
                <span>{pageIndex + 1} / {pages.length} · 左页返回 · 右页翻页</span>
            </WorldLabel>
            <pointLight color={palette.paper} distance={7.5} intensity={8} position={[0, 2.3, 3.6]} />
            <WorldButton disabled={!canPrevious} onClick={() => flipPage('previous')} position={[-2.55, -1.95, 0.35]} tone="cyan">上一页</WorldButton>
            <WorldButton disabled={!canNext} onClick={() => flipPage('next')} position={[2.55, -1.95, 0.35]} tone="cyan">下一页</WorldButton>
            <WorldButton onClick={onBack} position={[0, -2.0, 0.35]} tone="pink">放回书架</WorldButton>
        </group>
    );
}

function LanguageMarker({ active, label, onSelect, position }) {
    return (
        <group position={position}>
            <Interactive onClick={onSelect} selected={active} scale={1}>
                <RoundedBox args={[1.65, 0.48, 0.16]} castShadow radius={0.1} smoothness={4}>
                    <SoftMaterial
                        color={active ? palette.cyan : palette.wallInset}
                        emissive={active ? palette.cyan : '#000000'}
                        emissiveIntensity={active ? 0.24 : 0}
                    />
                </RoundedBox>
            </Interactive>
            <WorldLabel onClick={onSelect} position={[0, 0, 0.11]} scale={0.22}>
                <strong>{label}</strong>
            </WorldLabel>
        </group>
    );
}

function WordDetailStand({ entry, onUpdated }) {
    const [editing, setEditing] = useState(false);
    const [syncing, setSyncing] = useState(false);
    const [saving, setSaving] = useState(false);
    const [speaking, setSpeaking] = useState(false);
    const [message, setMessage] = useState('');
    const phrases = entry.phrases?.length ? entry.phrases.slice(0, 2) : ['还没有词组记录'];
    const examples = entry.examples?.length ? entry.examples.slice(0, 2) : ['还没有例句记录'];
    const dictionary = entry.dictionary || {};
    const dictionaryUsages = dictionary.usages?.slice(0, 2) || [];
    const dictionaryStatus = dictionary.status === 'available'
        ? `${dictionary.sourceName || 'English-English Dictionary'} · ${dictionary.pronunciations?.join(' · ') || '暂无词典音标'}`
        : dictionary.status === 'not_found'
            ? '词典暂未找到这个单词。'
            : dictionary.status === 'unavailable'
                ? (dictionary.errorMessage || '词典服务暂不可用。')
                : '可同步英英词典参考。';
    const saveUsage = async (event) => {
        event.preventDefault();
        event.stopPropagation();
        if (saving) return;
        const form = new FormData(event.currentTarget);
        setSaving(true);
        setMessage('正在保存你的用法记录…');
        try {
            const updated = await roomApi.updateWordbookEntry(entry.id, {
                phrases: splitLineList(String(form.get('phrases') || '')),
                examples: splitLineList(String(form.get('examples') || '')),
                notes: String(form.get('notes') || '').trim()
            });
            setMessage('个人用法已保存。');
            setEditing(false);
            await onUpdated(updated);
        } catch (error) {
            setMessage(`保存失败：${error.message || '请稍后重试。'}`);
        } finally {
            setSaving(false);
        }
    };
    const syncDictionary = async () => {
        if (syncing) return;
        setSyncing(true);
        setMessage('正在同步英英词典…');
        try {
            const updated = await roomApi.refreshWordbookDictionary(entry.id);
            setMessage(updated.dictionary?.status === 'available' ? '词典参考已同步。' : '没有找到可同步的词典记录。');
            await onUpdated(updated);
        } catch (error) {
            setMessage(`同步失败：${error.message || '词典服务暂不可用。'}`);
        } finally {
            setSyncing(false);
        }
    };
    const speakWord = () => {
        if (typeof window === 'undefined' || !window.speechSynthesis || !window.SpeechSynthesisUtterance) {
            setMessage('当前浏览器不支持本地发音。');
            return;
        }
        window.speechSynthesis.cancel();
        const utterance = new window.SpeechSynthesisUtterance(entry.word);
        const voices = window.speechSynthesis.getVoices();
        const naturalVoice = voices.find((voice) => /^en(-|_)/i.test(voice.lang) && /samantha|ava|allison|karen|moira|daniel|rishi|zira|jenny|aria|google us english/i.test(voice.name))
            || voices.find((voice) => /^en(-|_)/i.test(voice.lang));
        utterance.lang = naturalVoice?.lang || 'en-US';
        if (naturalVoice) utterance.voice = naturalVoice;
        utterance.rate = 0.9;
        utterance.pitch = 1;
        utterance.onstart = () => setSpeaking(true);
        utterance.onend = () => setSpeaking(false);
        utterance.onerror = () => {
            setSpeaking(false);
            setMessage('发音未能播放，请检查浏览器语音设置。');
        };
        window.speechSynthesis.speak(utterance);
    };
    return (
        <group position={[3.55, 2.6, 0.7]}>
            <RoundedBox args={[5.35, 4.45, 0.3]} castShadow radius={0.16} smoothness={4}>
                <SoftMaterial color={palette.deskWoodDark} />
            </RoundedBox>
            <RoundedBox
                args={[4.95, 4.05, 0.16]}
                castShadow
                position={[0, 0, 0.2]}
                radius={0.1}
                smoothness={4}
            >
                <SoftMaterial color={palette.paper} emissive={palette.gold} emissiveIntensity={0.06} />
            </RoundedBox>
            <Html center position={[0, 0, 0.32]} zIndexRange={[65, 15]}>
                <article className="wordbook-detail-instrument" key={entry.id} onClick={(event) => event.stopPropagation()}>
                    <header>
                        <small>{entry.language || '未分类语言'}</small>
                        <h2>{entry.word}</h2>
                        <button
                            aria-label={`朗读 ${entry.word}`}
                            className="wordbook-pronunciation-button"
                            onClick={speakWord}
                            title="点击朗读单词"
                            type="button"
                        >
                            <span aria-hidden="true">{speaking ? '◌' : '◉'}</span>
                            {entry.pronunciation || '点击朗读'}
                        </button>
                    </header>
                    <section>
                        <strong>我的释义</strong>
                        <p>{entry.meaning || '还没有释义，稍后可在 Wordbook 中补充。'}</p>
                    </section>
                    <section className="wordbook-dictionary-panel">
                        <strong>English-English Dictionary</strong>
                        <p>{dictionaryStatus}</p>
                        {dictionaryUsages.map((usage) => (
                            <p key={`${usage.partOfSpeech}-${usage.definition}`}>
                                <b>{usage.partOfSpeech}</b> {usage.definition}
                                {usage.example ? ` Example: ${usage.example}` : ''}
                            </p>
                        ))}
                    </section>
                    <div className="wordbook-detail-columns">
                        <section>
                            <strong>词组</strong>
                            {phrases.map((phrase) => <p key={phrase}>{phrase}</p>)}
                        </section>
                        <section>
                            <strong>用法 / 例句</strong>
                            {examples.map((example) => <p key={example}>{example}</p>)}
                        </section>
                    </div>
                    <footer>
                        {(entry.tags?.length ? entry.tags : ['暂无标签']).map((tag) => (
                            <span key={tag}>{tag}</span>
                        ))}
                        {entry.notes && <p>{truncate(entry.notes, 90)}</p>}
                        <button onClick={syncDictionary} type="button">{syncing ? '同步中…' : '同步词典'}</button>
                        <button onClick={() => setEditing((value) => !value)} type="button">{editing ? '收起编辑' : '编辑个人用法'}</button>
                        {message && <p className="wordbook-detail-message">{message}</p>}
                    </footer>
                    {editing && (
                        <form
                            className="wordbook-usage-editor"
                            onCompositionEnd={(event) => event.stopPropagation()}
                            onCompositionStart={(event) => event.stopPropagation()}
                            onKeyDown={(event) => event.stopPropagation()}
                            onKeyUp={(event) => event.stopPropagation()}
                            onPointerDown={(event) => event.stopPropagation()}
                            onSubmit={saveUsage}
                        >
                            <label>我的词组<textarea defaultValue={(entry.phrases || []).join('\n')} name="phrases" placeholder="每行一个词组" /></label>
                            <label>我的例句<textarea defaultValue={(entry.examples || []).join('\n')} name="examples" placeholder="每行一个例句" /></label>
                            <label>学习笔记<textarea defaultValue={entry.notes || ''} name="notes" placeholder="记下自己的理解" /></label>
                            <button disabled={saving} type="submit">{saving ? '保存中…' : '保存个人用法'}</button>
                        </form>
                    )}
                </article>
            </Html>
            <pointLight color={palette.gold} distance={6} intensity={5} position={[0, 2.5, 2]} />
        </group>
    );
}

const WORDBOOK_LANGUAGES = ['English', 'Chinese', 'Japanese', 'French', 'German', 'Spanish'];

const splitCommaList = (value) => value
    .split(/[,，;]/)
    .map((item) => item.trim())
    .filter(Boolean);

const splitLineList = (value) => value
    .split('\n')
    .map((item) => item.trim())
    .filter(Boolean);

function WordbookCreateStand({ language, onClose, onCreated }) {
    const [message, setMessage] = useState('填写单词和已知信息，释义以外的字段都可稍后补充。');
    const [messageTone, setMessageTone] = useState('neutral');
    const [submitting, setSubmitting] = useState(false);

    const submit = async (event) => {
        event.preventDefault();
        event.stopPropagation();
        if (submitting) return;
        const form = new FormData(event.currentTarget);
        const value = (field) => String(form.get(field) || '').trim();
        const word = value('word');
        if (!word) {
            setMessage('请先填写单词。');
            setMessageTone('error');
            return;
        }
        setSubmitting(true);
        setMessage('正在保存单词…');
        setMessageTone('loading');
        try {
            const entry = await roomApi.createWordbookEntry({
                word,
                meaning: value('meaning'),
                pronunciation: value('pronunciation'),
                language: value('language'),
                tags: splitCommaList(value('tags')),
                phrases: splitLineList(value('phrases')),
                examples: splitLineList(value('examples')),
                notes: value('notes')
            });
            setMessage(`${entry.word} 已种入词汇花园。`);
            setMessageTone('success');
            await onCreated(entry);
        } catch (error) {
            const detail = error.message === 'HTTP 500'
                ? '保存失败：后端数据库暂时不可用，请恢复服务后重试。'
                : `保存失败：${error.message || '请稍后重试。'}`;
            setMessage(detail);
            setMessageTone('error');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <group position={[0, 3.05, 2.4]}>
            <RoundedBox args={[10.4, 5.5, 0.42]} castShadow radius={0.2} smoothness={4}>
                <SoftMaterial color={palette.deskWoodDark} emissive={palette.cyan} emissiveIntensity={0.08} />
            </RoundedBox>
            <Html center position={[0, 0, 0.28]} zIndexRange={[80, 30]}>
                <form
                    className="wordbook-create-instrument"
                    onClick={(event) => event.stopPropagation()}
                    onCompositionEnd={(event) => event.stopPropagation()}
                    onCompositionStart={(event) => event.stopPropagation()}
                    onKeyDown={(event) => event.stopPropagation()}
                    onKeyUp={(event) => event.stopPropagation()}
                    onPointerDown={(event) => event.stopPropagation()}
                    onSubmit={submit}
                >
                    <header>
                        <div>
                            <small>NEW WORD</small>
                            <h2>新建单词</h2>
                        </div>
                        <button aria-label="关闭新建单词" className="is-quiet" onClick={onClose} type="button">关闭</button>
                    </header>
                    <div className="wordbook-create-grid">
                        <label>
                            单词
                            <input autoFocus name="word" required />
                        </label>
                        <label>
                            语言
                            <select defaultValue={language === '全部' ? 'English' : language} name="language">
                                {WORDBOOK_LANGUAGES.map((item) => <option key={item}>{item}</option>)}
                            </select>
                        </label>
                        <label>
                            释义
                            <input name="meaning" />
                        </label>
                        <label>
                            发音
                            <input name="pronunciation" placeholder="例如 /rɪˈzɪliənt/" />
                        </label>
                        <label>
                            标签
                            <input name="tags" placeholder="逗号分隔" />
                        </label>
                        <label>
                            词组
                            <textarea name="phrases" placeholder="每行一个词组" />
                        </label>
                        <label>
                            例句
                            <textarea name="examples" placeholder="每行一个例句" />
                        </label>
                        <label>
                            笔记
                            <textarea name="notes" />
                        </label>
                    </div>
                    <p aria-live="polite" className={`wordbook-form-status is-${messageTone}`}>{message}</p>
                    <button disabled={submitting} type="submit">
                        {submitting ? '保存中…' : '保存单词'}
                    </button>
                </form>
            </Html>
        </group>
    );
}

function WordbookImportStand({ language, onClose, onImported }) {
    const [file, setFile] = useState(null);
    const [importLanguage, setImportLanguage] = useState(language === '全部' ? 'English' : language);
    const [message, setMessage] = useState('支持 TXT（单词 + Tab + 释义）或 CSV（word, meaning, tags）。');
    const [submitting, setSubmitting] = useState(false);

    const selectFile = async (event) => {
        const selectedFile = event.target.files?.[0];
        if (!selectedFile) return;
        if (!/\.(txt|csv)$/i.test(selectedFile.name)) {
            setFile(null);
            setMessage('请选择 .txt 或 .csv 文件。');
            event.target.value = '';
            return;
        }
        setFile({ fileName: selectedFile.name, content: await selectedFile.text() });
        setMessage(`${selectedFile.name} 已就绪。`);
    };

    const submit = async (event) => {
        event.preventDefault();
        event.stopPropagation();
        if (!file || submitting) return;
        setSubmitting(true);
        try {
            const result = await roomApi.importWordbook({
                fileName: file.fileName,
                content: file.content,
                language: importLanguage
            });
            setMessage(`已导入 ${result.importedCount} 个词${result.skippedCount ? `，跳过 ${result.skippedCount} 个重复词` : ''}。`);
            await onImported();
        } catch (error) {
            setMessage(error.message || '导入失败，请稍后重试。');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <group position={[0, 3.05, 2.4]}>
            <RoundedBox args={[9.2, 4.5, 0.42]} castShadow radius={0.2} smoothness={4}>
                <SoftMaterial color={palette.deskWoodDark} emissive={palette.cyan} emissiveIntensity={0.08} />
            </RoundedBox>
            <Html center position={[0, 0, 0.28]} zIndexRange={[80, 30]}>
                <form
                    className="wordbook-import-instrument"
                    onClick={(event) => event.stopPropagation()}
                    onSubmit={submit}
                >
                    <header>
                        <div>
                            <small>WORDBOOK IMPORT</small>
                            <h2>导入词表</h2>
                        </div>
                        <button aria-label="关闭导入" className="is-quiet" onClick={onClose} type="button">关闭</button>
                    </header>
                    <label>
                        语言
                        <select value={importLanguage} onChange={(event) => setImportLanguage(event.target.value)}>
                            {WORDBOOK_LANGUAGES.map((item) => <option key={item}>{item}</option>)}
                        </select>
                    </label>
                    <label>
                        词表文件
                        <input accept=".txt,.csv,text/plain,text/csv" onChange={selectFile} type="file" />
                    </label>
                    <p aria-live="polite">{message}</p>
                    <button disabled={!file || submitting} type="submit">
                        {submitting ? '导入中…' : '开始导入'}
                    </button>
                </form>
            </Html>
        </group>
    );
}

// Retained as the in-canvas fallback while Wordbook uses the shared reference bookshelf overlay.
// eslint-disable-next-line no-unused-vars
function WordbookWorld({ payload, reload }) {
    const entries = useMemo(() => payload || [], [payload]);
    const languages = useMemo(
        () => ['全部', ...new Set(entries.map((entry) => entry.language).filter(Boolean))],
        [entries]
    );
    const [language, setLanguage] = useState('全部');
    const [query, setQuery] = useState('');
    const [tag, setTag] = useState('全部标签');
    const [activeTool, setActiveTool] = useState(null);
    const [activeBook, setActiveBook] = useState(null);
    const [bookPhase, setBookPhase] = useState('browse');
    const [tagCarouselIndex, setTagCarouselIndex] = useState(0);
    const tags = useMemo(
        () => ['全部标签', ...new Set(entries.flatMap((entry) => entry.tags || []))],
        [entries]
    );
    const filtered = useMemo(
        () => entries.filter((entry) => {
            const matchesLanguage = language === '全部' || entry.language === language;
            const matchesTag = tag === '全部标签' || entry.tags?.includes(tag);
            const normalizedQuery = query.trim().toLocaleLowerCase();
            const matchesQuery = !normalizedQuery || [entry.word, entry.meaning, entry.pronunciation]
                .some((value) => String(value || '').toLocaleLowerCase().includes(normalizedQuery));
            return matchesLanguage && matchesTag && matchesQuery;
        }),
        [entries, language, query, tag]
    );
    const [selected, setSelected] = useState(entries[0] || null);
    const tagBooks = useMemo(() => {
        const scoped = entries.filter((entry) => language === '全部' || entry.language === language);
        const counts = new Map();
        scoped.forEach((entry) => (entry.tags || []).forEach((item) => counts.set(item, (counts.get(item) || 0) + 1)));
        return [
            { id: 'all', title: '全部单词', tag: '全部标签', status: `${scoped.length} 个词`, subtitle: 'WORD INDEX', carouselIndex: 0 },
            ...Array.from(counts.entries()).sort(([left], [right]) => left.localeCompare(right)).map(([item, count]) => ({
                id: item,
                title: item,
                tag: item,
                status: `${count} 个词`,
                subtitle: 'VOCABULARY TAG'
            })).map((book, index) => ({ ...book, carouselIndex: index + 1 }))
        ];
    }, [entries, language]);
    useEffect(() => {
        if (tagCarouselIndex >= tagBooks.length) setTagCarouselIndex(Math.max(0, tagBooks.length - 1));
    }, [tagBooks.length, tagCarouselIndex]);
    const bookEntries = useMemo(
        () => entries.filter((entry) => {
            const matchesLanguage = language === '全部' || entry.language === language;
            const matchesTag = activeBook?.tag === '全部标签' || entry.tags?.includes(activeBook?.tag);
            return matchesLanguage && matchesTag;
        }),
        [activeBook?.tag, entries, language]
    );
    const bookPages = useMemo(() => {
        if (!bookEntries.length) return [{
            eyebrow: 'EMPTY TAG',
            title: '这本词汇书还没有内容',
            body: '可通过“新建单词”或“导入词表”补充这一主题。'
        }];
        return bookEntries.map((entry, index) => ({
            eyebrow: `${entry.language || 'WORD'} · ${index + 1}/${bookEntries.length}`,
            title: entry.word,
            body: [entry.meaning, entry.phrases?.[0], entry.examples?.[0]].filter(Boolean).join('\n') || '点击词条后可补充个人释义、词组和例句。',
            entryId: entry.id
        }));
    }, [bookEntries]);

    const selectLanguage = (nextLanguage) => {
        setLanguage(nextLanguage);
        setTag('全部标签');
    };

    const pickTagBook = (book) => {
        setTag(book.tag);
        setActiveBook({ ...book, carouselPosition: [(book.carouselIndex - tagCarouselIndex) * CAROUSEL_GAP, 2.2, -1.55] });
        setSelected(entries.find((entry) =>
            (language === '全部' || entry.language === language) &&
            (book.tag === '全部标签' || entry.tags?.includes(book.tag))
        ) || null);
        setBookPhase('pickup');
    };

    const returnToTagShelf = () => {
        setBookPhase('browse');
        setActiveBook(null);
        setSelected(null);
    };

    const handleCreated = async (entry) => {
        setLanguage('全部');
        setTag('全部标签');
        setQuery(entry.word);
        setSelected(entry);
        await reload();
    };

    const handleUpdated = async (entry) => {
        setSelected(entry);
        await reload();
    };

    return (
        <>
            <group position={[2.65, 6.2, -4.28]}>
                {languages.slice(0, 7).map((item, index) => (
                    <LanguageMarker
                        active={language === item}
                        key={item}
                        label={item}
                        onSelect={() => selectLanguage(item)}
                        position={[(index - (Math.min(languages.length, 7) - 1) / 2) * 1.92, 0, 0]}
                    />
                ))}
            </group>

            <Html center position={[0, 5.48, -4.22]} zIndexRange={[68, 18]}>
                <div className="wordbook-index-instrument" onClick={(event) => event.stopPropagation()}>
                    <input
                        aria-label="搜索单词或释义"
                        onChange={(event) => setQuery(event.target.value)}
                        placeholder="搜索单词或释义"
                        type="search"
                        value={query}
                    />
                    <select
                        aria-label="按标签筛选"
                        onChange={(event) => setTag(event.target.value)}
                        value={tag}
                    >
                        {tags.map((item) => <option key={item}>{item}</option>)}
                    </select>
                    <span>{filtered.length} 个匹配词</span>
                    <button className="is-primary" onClick={() => setActiveTool('create')} type="button">新建单词</button>
                    <button onClick={() => setActiveTool('import')} type="button">导入词表</button>
                </div>
            </Html>

            <BookCarousel
                activeBook={activeBook}
                books={tagBooks}
                carouselIndex={tagCarouselIndex}
                emptyCopy="使用“导入词表”开始建立第一本词汇书。"
                onMove={(delta) => setTagCarouselIndex((index) => Math.max(0, Math.min(tagBooks.length - 1, index + delta)))}
                onPick={pickTagBook}
                phase={bookPhase}
                subtitle="每个标签都是一本词汇书 · 左右滑动浏览 · 点击取书"
                title="词汇书架"
            />
            {bookPhase === 'pickup' && activeBook && (
                <BookPickup book={activeBook} color={bookColors[activeBook.carouselIndex % bookColors.length] || palette.cyan} onComplete={() => setBookPhase('reading')} startPosition={activeBook.carouselPosition} />
            )}
            {bookPhase === 'reading' && activeBook && (
                <>
                    <BookReader
                        book={activeBook}
                        onBack={returnToTagShelf}
                        onPageChange={(nextPage) => setSelected(bookEntries.find((entry) => entry.id === nextPage?.entryId) || null)}
                        pages={bookPages}
                    />
                    {selected && <WordDetailStand entry={selected} onUpdated={handleUpdated} />}
                </>
            )}
            {activeTool === 'create' && (
                <WordbookCreateStand
                    language={language}
                    onClose={() => setActiveTool(null)}
                    onCreated={handleCreated}
                />
            )}
            {activeTool === 'import' && (
                <WordbookImportStand
                    language={language}
                    onClose={() => setActiveTool(null)}
                    onImported={reload}
                />
            )}
        </>
    );
}

function WorkHomeWorld({ payload }) {
    const summary = payload.summary || {};
    const objects = [
        ['技术栈', summary.techStackCount || 0, palette.cyan, 'stack'],
        ['项目', summary.projectCount || 0, palette.gold, 'project'],
        ['Evidence', summary.articleCount || 0, palette.pink, 'evidence'],
        ['简历', summary.resumeCount || 0, palette.violet, 'resume']
    ];
    return (
        <>
            <group position={[0.36, 1.2, 0.2]}>
                <RoundedBox args={[13.8, 0.42, 4.5]} castShadow radius={0.2} smoothness={4}>
                    <SoftMaterial color={palette.deskWood} />
                </RoundedBox>
                {objects.map(([label, value, color], index) => (
                    <group key={label} position={[(index - 1.5) * 2.55, 1.2, 0]}>
                        <Float floatIntensity={0.2} rotationIntensity={0.08} speed={1 + index * 0.1}>
                            <mesh castShadow>
                                <dodecahedronGeometry args={[0.72 + value * 0.05, 0]} />
                                <SoftMaterial color={color} emissive={color} emissiveIntensity={0.24} />
                            </mesh>
                        </Float>
                        <WorldLabel position={[0, -1.15, 0]}>
                            <strong>{value}</strong>
                            <span>{label}</span>
                        </WorldLabel>
                    </group>
                ))}
            </group>
            <WorldLabel position={[0, 6.1, -2]}>
                <strong>{payload.primaryAction?.label || 'Work Planet'}</strong>
                <span>{payload.primaryAction?.description || '把知识沉淀成可验证的工作证据'}</span>
            </WorldLabel>
        </>
    );
}

function TechStackWorld({ payload }) {
    const stacks = payload.techStacks || [];
    const [selected, setSelected] = useState(stacks[0] || null);
    return (
        <>
            {stacks.slice(0, 8).map((stack, index) => {
                const x = (index - (Math.min(stacks.length, 8) - 1) / 2) * 2.15;
                const levels = Math.max(2, Math.min(6, (stack.tags?.length || 0) + 3));
                return (
                    <group key={stack.id} position={[x, 0.2, -0.8]}>
                        <Interactive onClick={() => setSelected(stack)} selected={selected?.id === stack.id}>
                            {Array.from({ length: levels }, (_, level) => (
                                <RoundedBox
                                    args={[1.35 - level * 0.08, 0.55, 1.35 - level * 0.08]}
                                    castShadow
                                    key={level}
                                    position={[0, 0.35 + level * 0.58, 0]}
                                    radius={0.1}
                                    smoothness={3}
                                >
                                    <SoftMaterial
                                        color={level % 2 ? palette.cyan : palette.blue}
                                        emissive={selected?.id === stack.id ? palette.cyan : '#000000'}
                                        emissiveIntensity={selected?.id === stack.id ? 0.22 : 0}
                                    />
                                </RoundedBox>
                            ))}
                            <WorldLabel position={[0, levels * 0.6 + 0.75, 0]}>
                                <strong>{stack.name}</strong>
                                <span>{stack.category}</span>
                            </WorldLabel>
                        </Interactive>
                    </group>
                );
            })}
            {selected && (
                <group position={[0, 5.9, -1.8]}>
                    <mesh rotation={[Math.PI / 2, 0, 0]}>
                        <torusGeometry args={[2.2, 0.055, 10, 96]} />
                        <SoftMaterial color={palette.cyan} emissive={palette.cyan} emissiveIntensity={0.9} />
                    </mesh>
                    <WorldLabel>
                        <strong>{selected.name}</strong>
                        <span>{selected.description || `${selected.proficiency} · ${selected.tags?.join(' · ') || '暂无标签'}`}</span>
                    </WorldLabel>
                </group>
            )}
        </>
    );
}

function ProjectsWorld({ payload }) {
    const projects = payload.projects || [];
    const [selected, setSelected] = useState(projects[0] || null);
    return (
        <>
            {projects.slice(0, 6).map((project, index) => {
                const x = (index - (projects.length - 1) / 2) * 3.3;
                return (
                    <group key={project.id} position={[x, 0, -0.6]}>
                        <Interactive onClick={() => setSelected(project)} selected={selected?.id === project.id}>
                            <RoundedBox args={[2.3, 0.5, 2.3]} castShadow position={[0, 0.28, 0]} radius={0.16} smoothness={4}>
                                <SoftMaterial color={palette.deskWood} />
                            </RoundedBox>
                            <mesh castShadow position={[0, 1.45, 0]}>
                                <icosahedronGeometry args={[0.85, 1]} />
                                <SoftMaterial
                                    color={index % 2 ? palette.gold : palette.cyan}
                                    emissive={index % 2 ? palette.gold : palette.cyan}
                                    emissiveIntensity={0.24}
                                />
                            </mesh>
                            <WorldLabel position={[0, 2.75, 0]}>
                                <strong>{truncate(project.title, 24)}</strong>
                                <span>{project.status}</span>
                            </WorldLabel>
                        </Interactive>
                    </group>
                );
            })}
            {selected && (
                <WorldLabel className="world-quote" position={[0, 6.35, -2.4]}>
                    <strong>{selected.title}</strong>
                    <span>{truncate(selected.description, 140)}</span>
                </WorldLabel>
            )}
        </>
    );
}

function ResumeWorld({ payload }) {
    const resumes = payload.resumes || [];
    const [selected, setSelected] = useState(resumes[0] || null);
    return (
        <>
            <group position={[0, 3.35, -2.1]}>
                {resumes.slice(0, 5).map((resume, index) => {
                    const x = (index - (resumes.length - 1) / 2) * 2.7;
                    return (
                        <group key={resume.id} position={[x, 0, index * 0.18]}>
                            <Interactive onClick={() => setSelected(resume)} selected={selected?.id === resume.id}>
                                <RoundedBox args={[2.15, 3.25, 0.16]} castShadow radius={0.08} smoothness={3}>
                                    <SoftMaterial
                                        color={palette.paper}
                                        emissive={selected?.id === resume.id ? palette.gold : '#000000'}
                                        emissiveIntensity={0.18}
                                    />
                                </RoundedBox>
                                {[0.72, 0.28, -0.16, -0.6].map((y, line) => (
                                    <mesh key={y} position={[0, y, 0.12]}>
                                        <boxGeometry args={[1.45 - line * 0.12, 0.07, 0.04]} />
                                        <SoftMaterial color={line ? palette.blue : palette.pink} />
                                    </mesh>
                                ))}
                                <WorldLabel className="is-dark" position={[0, 1.08, 0.16]} scale={0.22}>
                                    <strong>{truncate(resume.roleTarget, 18)}</strong>
                                </WorldLabel>
                            </Interactive>
                        </group>
                    );
                })}
            </group>
            {selected && (
                <WorldLabel className="world-quote" position={[0, 0.9, 2.15]}>
                    <strong>{selected.title}</strong>
                    <span>{truncate(selected.content, 180)}</span>
                    <small>{selected.evidenceRefs?.length || 0} 条 Evidence</small>
                </WorldLabel>
            )}
        </>
    );
}

function NovelWorld({ payload, reload }) {
    const [active, setActive] = useState(payload[0] || null);
    const [saving, setSaving] = useState(false);
    const update = (field, value) => setActive((draft) => ({ ...draft, [field]: value }));
    const create = () =>
        setActive({
            id: '',
            title: '未命名作品',
            synopsis: '',
            content: '# 第一章\n\n',
            status: 'draft'
        });
    const save = async () => {
        if (!active?.title?.trim()) return;
        setSaving(true);
        try {
            const saved = active.id
                ? await roomApi.updateNovelDraft(active.id, active)
                : await roomApi.createNovelDraft(active);
            setActive(saved);
            reload();
        } finally {
            setSaving(false);
        }
    };
    return (
        <>
            <group position={[0, 0.75, 0.2]}>
                <RoundedBox args={[13.4, 0.4, 4.8]} castShadow radius={0.2} smoothness={4}>
                    <SoftMaterial color={palette.deskWood} />
                </RoundedBox>
                <group position={[1.35, 2.55, -0.55]} rotation={[-0.12, 0, 0.04]}>
                    <RoundedBox
                        args={[7.25, 4.05, 0.18]}
                        castShadow
                        radius={0.1}
                        smoothness={3}
                    >
                        <SoftMaterial color={palette.paper} />
                    </RoundedBox>
                    <Html
                        center
                        position={[0, 0, 0.13]}
                        scale={0.24}
                        transform
                        zIndexRange={[50, 5]}
                    >
                        <div className="manuscript-instrument">
                            {active ? (
                                <>
                                    <input
                                        aria-label="作品标题"
                                        onChange={(event) => update('title', event.target.value)}
                                        value={active.title}
                                    />
                                    <input
                                        aria-label="作品简介"
                                        onChange={(event) => update('synopsis', event.target.value)}
                                        placeholder="一句话描述这个故事"
                                        value={active.synopsis}
                                    />
                                    <textarea
                                        aria-label="小说正文"
                                        onChange={(event) => update('content', event.target.value)}
                                        value={active.content}
                                    />
                                </>
                            ) : (
                                <p>选择左侧手稿，或创建一个新作品。</p>
                            )}
                        </div>
                    </Html>
                </group>
                {(payload || []).slice(0, 4).map((draft, index) => (
                    <group key={draft.id} position={[-2.9, 0.62 + index * 0.52, 0.1 - index * 0.08]}>
                        <Interactive onClick={() => setActive(draft)} selected={active?.id === draft.id}>
                            <RoundedBox args={[2.4, 0.34, 3.0]} castShadow radius={0.08} smoothness={3}>
                                <SoftMaterial
                                    color={[palette.pink, palette.violet, palette.cyan, palette.gold][index % 4]}
                                    emissive={active?.id === draft.id ? palette.pink : '#000000'}
                                    emissiveIntensity={0.24}
                                />
                            </RoundedBox>
                        </Interactive>
                    </group>
                ))}
            </group>
            <WorldLabel position={[-2.9, 3.65, -0.4]}>
                <strong>{active?.title || '作品手稿'}</strong>
                <span>{active?.synopsis || '在真实写作桌上继续你的故事'}</span>
            </WorldLabel>
            <WorldButton onClick={create} position={[-2.2, 0.3, 3.1]} tone="pink">
                新建手稿
            </WorldButton>
            <WorldButton
                disabled={saving || !active}
                onClick={save}
                position={[1.2, 0.3, 3.1]}
                tone="pink"
            >
                {saving ? '保存中' : '保存手稿'}
            </WorldButton>
        </>
    );
}

const concealKeyTerms = (value, terms = []) => {
    const candidates = terms.length
        ? terms
        : String(value || '').match(/[A-Za-z]{5,}|[\u4e00-\u9fff]{3,}/g) || [];
    return candidates.slice(0, 2).reduce(
        (text, term) => text.replace(term, '＿＿＿＿'),
        String(value || '')
    );
};

const ROPE_GALLERY = {
    halfSpan: 8.9,
    spacing: 2.2,
    nodes: 20,
    samples: 68,
    sides: 6,
    cardWidth: 2.06,
    cardHeight: 1.56,
    cardDrop: 1.32,
    ropeRadius: 0.035
};

const wrapRopePosition = (value) => value - Math.floor((value + ROPE_GALLERY.halfSpan) / (ROPE_GALLERY.halfSpan * 2)) * ROPE_GALLERY.halfSpan * 2;

function HangingRopeGallery({ items, onChoose, selected }) {
    const slotCount = Math.max(5, Math.ceil((2.75 * ROPE_GALLERY.halfSpan) / ROPE_GALLERY.spacing));
    const ropeGeometry = useMemo(() => {
        const geometry = new BufferGeometry();
        const vertexCount = ROPE_GALLERY.samples * ROPE_GALLERY.sides;
        const positions = new Float32Array(vertexCount * 3);
        const normals = new Float32Array(vertexCount * 3);
        const indices = [];
        for (let sample = 0; sample < ROPE_GALLERY.samples - 1; sample += 1) {
            for (let side = 0; side < ROPE_GALLERY.sides; side += 1) {
                const current = sample * ROPE_GALLERY.sides + side;
                const next = sample * ROPE_GALLERY.sides + (side + 1) % ROPE_GALLERY.sides;
                const below = (sample + 1) * ROPE_GALLERY.sides + side;
                const belowNext = (sample + 1) * ROPE_GALLERY.sides + (side + 1) % ROPE_GALLERY.sides;
                indices.push(current, below, next, next, below, belowNext);
            }
        }
        geometry.setAttribute('position', new Float32BufferAttribute(positions, 3));
        geometry.setAttribute('normal', new Float32BufferAttribute(normals, 3));
        geometry.setIndex(indices);
        return geometry;
    }, []);
    const input = useRef({ offset: 0, velocity: 0, acceleration: 0, previousVelocity: 0, wheel: 0, dragging: false, lastX: 0, lastTime: 0, dragged: false });
    const rope = useRef({
        dy: new Float32Array(ROPE_GALLERY.nodes),
        vy: new Float32Array(ROPE_GALLERY.nodes),
        dz: new Float32Array(ROPE_GALLERY.nodes),
        vz: new Float32Array(ROPE_GALLERY.nodes)
    });
    const cardRefs = useRef([]);
    const slotPhysics = useRef(Array.from({ length: slotCount }, (_, slot) => ({
        slot,
        lag: 0,
        lagVelocity: 0,
        angle: 0,
        angularVelocity: 0,
        tilt: 0,
        tiltVelocity: 0,
        bounce: 0,
        bounceVelocity: 0,
        previousX: null,
        velocityX: 0,
        previousSpeed: 0,
        phase: slot * 1.7,
        mass: 0.92 + ((slot * 0.137) % 1) * 0.3,
        assignedIndex: slot % Math.max(items.length, 1)
    })));
    const [slotItems, setSlotItems] = useState(() => Array.from({ length: slotCount }, (_, slot) => slot % Math.max(items.length, 1)));
    const [hovered, setHovered] = useState(false);
    usePointer(hovered);

    useEffect(() => () => ropeGeometry.dispose(), [ropeGeometry]);
    useEffect(() => {
        const next = Array.from({ length: slotCount }, (_, slot) => slot % Math.max(items.length, 1));
        slotPhysics.current.forEach((physics, slot) => { physics.assignedIndex = next[slot]; });
        setSlotItems(next);
    }, [items, slotCount]);
    useEffect(() => {
        const moveWithKey = (event) => {
            if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
            event.preventDefault();
            input.current.offset += (event.key === 'ArrowLeft' ? -1 : 1) * ROPE_GALLERY.spacing;
            input.current.velocity = (event.key === 'ArrowLeft' ? -1 : 1) * 3.8;
        };
        window.addEventListener('keydown', moveWithKey);
        return () => window.removeEventListener('keydown', moveWithKey);
    }, []);

    const ropePoint = (normalisedX, target = [0, 0, 0]) => {
        const dynamics = rope.current;
        const nodePosition = ((normalisedX + 1) * 0.5) * (ROPE_GALLERY.nodes - 1);
        const left = Math.max(0, Math.min(ROPE_GALLERY.nodes - 2, Math.floor(nodePosition)));
        const mix = nodePosition - left;
        const interpolate = (values) => values[left] * (1 - mix) + values[left + 1] * mix;
        target[0] = ROPE_GALLERY.halfSpan * (normalisedX + 0.18 * normalisedX ** 3) / 1.18;
        target[1] = 2.16 - 0.8 * normalisedX ** 2 + interpolate(dynamics.dy);
        target[2] = 0.42 + 0.12 * normalisedX ** 2 + interpolate(dynamics.dz);
        return target;
    };

    const finishDrag = () => {
        input.current.dragging = false;
    };
    const startDrag = (event) => {
        event.stopPropagation();
        input.current.dragging = true;
        input.current.dragged = false;
        input.current.lastX = event.clientX;
        input.current.lastTime = performance.now();
        input.current.velocity = 0;
        event.target.setPointerCapture?.(event.pointerId);
    };
    const drag = (event) => {
        if (!input.current.dragging) return;
        event.stopPropagation();
        const now = performance.now();
        const elapsed = Math.max(8, now - input.current.lastTime) / 1000;
        const delta = (event.clientX - input.current.lastX) / 105;
        input.current.offset += delta;
        input.current.velocity = input.current.velocity * 0.55 + (delta / elapsed) * 0.45;
        input.current.dragged ||= Math.abs(event.clientX - input.current.lastX) > 2;
        input.current.lastX = event.clientX;
        input.current.lastTime = now;
    };

    useFrame((state, delta) => {
        const dt = Math.min(1 / 30, delta);
        const control = input.current;
        const wheelMotion = control.wheel * Math.min(1, dt * 14);
        control.wheel -= wheelMotion;
        control.offset += wheelMotion;
        if (!control.dragging) {
            control.offset += control.velocity * dt;
            control.velocity *= Math.exp(-6.2 * dt);
        }
        control.acceleration = control.acceleration * 0.7 + ((control.velocity - control.previousVelocity) / Math.max(dt, 0.001)) * 0.3;
        control.previousVelocity = control.velocity;

        const physicsNodes = rope.current;
        const tension = 22;
        const rest = 2.5;
        const damping = 4.9;
        for (let node = 1; node < ROPE_GALLERY.nodes - 1; node += 1) {
            physicsNodes.vy[node] += (tension * (physicsNodes.dy[node - 1] + physicsNodes.dy[node + 1] - 2 * physicsNodes.dy[node]) - rest * physicsNodes.dy[node] - damping * physicsNodes.vy[node]) * dt;
            physicsNodes.vz[node] += (tension * (physicsNodes.dz[node - 1] + physicsNodes.dz[node + 1] - 2 * physicsNodes.dz[node]) - rest * physicsNodes.dz[node] - damping * physicsNodes.vz[node]) * dt;
            physicsNodes.dy[node] = Math.max(-0.45, Math.min(0.45, physicsNodes.dy[node] + physicsNodes.vy[node] * dt));
            physicsNodes.dz[node] = Math.max(-0.25, Math.min(0.25, physicsNodes.dz[node] + physicsNodes.vz[node] * dt));
        }
        physicsNodes.dy[0] = physicsNodes.dy[ROPE_GALLERY.nodes - 1] = 0;
        physicsNodes.dz[0] = physicsNodes.dz[ROPE_GALLERY.nodes - 1] = 0;

        let nextItems = null;
        slotPhysics.current.forEach((card, slot) => {
            const spring = (-6.8 * card.lag - 4.2 * card.lagVelocity - 0.38 * control.velocity) / card.mass - control.acceleration * 0.08;
            card.lagVelocity += spring * dt;
            card.lag = Math.max(-ROPE_GALLERY.spacing * 0.7, Math.min(ROPE_GALLERY.spacing * 0.7, card.lag + card.lagVelocity * dt));
            card.along = wrapRopePosition(slot * ROPE_GALLERY.spacing + control.offset + card.lag);
            const normalised = Math.max(-1, Math.min(1, card.along / ROPE_GALLERY.halfSpan));
            const point = ropePoint(normalised);
            const group = cardRefs.current[slot];
            if (!group) return;
            group.position.set(point[0], point[1], point[2]);
            if (card.previousX === null) card.previousX = point[0];
            const speed = (point[0] - card.previousX) / Math.max(dt, 0.001);
            const acceleration = (speed - card.velocityX) / Math.max(dt, 0.001);
            card.velocityX = card.velocityX * 0.4 + speed * 0.6;
            card.previousX = point[0];
            const gravity = -(2.8 / ROPE_GALLERY.cardDrop) * Math.sin(card.angle) - acceleration / ROPE_GALLERY.cardDrop * Math.cos(card.angle) - 1.8 * card.angularVelocity + Math.sin(state.clock.elapsedTime * 0.63 + card.phase) * 0.07;
            card.angularVelocity += gravity * dt / card.mass;
            card.angle = Math.max(-0.62, Math.min(0.62, card.angle + card.angularVelocity * dt));
            const tiltTarget = -Math.min(0.18, Math.abs(card.velocityX) * 0.008);
            card.tiltVelocity += ((tiltTarget - card.tilt) * 70 - card.tiltVelocity * 12) * dt;
            card.tilt += card.tiltVelocity * dt;
            const currentSpeed = Math.abs(card.velocityX);
            card.bounceVelocity += (card.previousSpeed - currentSpeed) * 0.01 + (-8 * card.bounce - 2.8 * card.bounceVelocity) * dt;
            card.bounce = Math.max(-0.06, Math.min(0.06, card.bounce + card.bounceVelocity * dt));
            card.previousSpeed = currentSpeed;
            group.rotation.set(card.tilt, 0, (slot * 0.618 % 1 - 0.5) * 0.075 + card.angle);
            group.children[0].position.y = -ROPE_GALLERY.cardDrop + card.bounce;

            const cycle = Math.floor((slot * ROPE_GALLERY.spacing + control.offset + card.lag + ROPE_GALLERY.halfSpan) / (ROPE_GALLERY.halfSpan * 2));
            const nextIndex = items.length ? ((slot - cycle * slotCount) % items.length + items.length) % items.length : 0;
            if (nextIndex !== card.assignedIndex) {
                card.assignedIndex = nextIndex;
                nextItems ||= [...slotItems];
                nextItems[slot] = nextIndex;
            }
            const node = Math.max(1, Math.min(ROPE_GALLERY.nodes - 2, Math.round((normalised + 1) * 0.5 * (ROPE_GALLERY.nodes - 1))));
            physicsNodes.vy[node] += -0.0038 * card.mass - control.acceleration * 0.0005;
            physicsNodes.vz[node] += -Math.max(-5, Math.min(5, control.velocity)) * 0.002;
        });
        if (nextItems) setSlotItems(nextItems);

        const positions = ropeGeometry.attributes.position.array;
        const normals = ropeGeometry.attributes.normal.array;
        const sampleStep = 2 / (ROPE_GALLERY.samples - 1);
        for (let sample = 0; sample < ROPE_GALLERY.samples; sample += 1) {
            const t = -1 + sample * sampleStep;
            const center = ropePoint(t);
            const before = ropePoint(Math.max(-1, t - sampleStep));
            const after = ropePoint(Math.min(1, t + sampleStep));
            const tangentX = after[0] - before[0];
            const tangentY = after[1] - before[1];
            const tangentZ = after[2] - before[2];
            const tangentLength = Math.hypot(tangentX, tangentY, tangentZ) || 1;
            const tx = tangentX / tangentLength;
            const ty = tangentY / tangentLength;
            const tz = tangentZ / tangentLength;
            let nx = ty;
            let ny = -tx;
            let nz = 0;
            const normalLength = Math.hypot(nx, ny, nz) || 1;
            nx /= normalLength;
            ny /= normalLength;
            nz /= normalLength;
            const bx = ty * nz - tz * ny;
            const by = tz * nx - tx * nz;
            const bz = tx * ny - ty * nx;
            for (let side = 0; side < ROPE_GALLERY.sides; side += 1) {
                const theta = side / ROPE_GALLERY.sides * Math.PI * 2;
                const ox = (nx * Math.cos(theta) + bx * Math.sin(theta)) * ROPE_GALLERY.ropeRadius;
                const oy = (ny * Math.cos(theta) + by * Math.sin(theta)) * ROPE_GALLERY.ropeRadius;
                const oz = (nz * Math.cos(theta) + bz * Math.sin(theta)) * ROPE_GALLERY.ropeRadius;
                const offset = (sample * ROPE_GALLERY.sides + side) * 3;
                positions[offset] = center[0] + ox;
                positions[offset + 1] = center[1] + oy;
                positions[offset + 2] = center[2] + oz;
                normals[offset] = ox / ROPE_GALLERY.ropeRadius;
                normals[offset + 1] = oy / ROPE_GALLERY.ropeRadius;
                normals[offset + 2] = oz / ROPE_GALLERY.ropeRadius;
            }
        }
        ropeGeometry.attributes.position.needsUpdate = true;
        ropeGeometry.attributes.normal.needsUpdate = true;
    });

    if (!items.length) return null;
    return (
        <group
            onPointerCancel={finishDrag}
            onPointerDown={startDrag}
            onPointerMove={drag}
            onPointerOut={() => setHovered(false)}
            onPointerOver={() => setHovered(true)}
            onPointerUp={finishDrag}
            onWheel={(event) => {
                event.stopPropagation();
                input.current.wheel += -(Math.abs(event.deltaX) > Math.abs(event.deltaY) ? event.deltaX : event.deltaY) / 105;
            }}
        >
            <mesh geometry={ropeGeometry} frustumCulled={false}>
                <meshStandardMaterial color="#b6925f" emissive="#6a4e2d" emissiveIntensity={0.12} metalness={0.12} roughness={0.58} />
            </mesh>
            {slotItems.map((itemIndex, slot) => {
                const item = items[itemIndex];
                if (!item) return null;
                const cardColor = item.annotationType === 'note' ? '#d6c08d' : ['#345552', '#4c3b58', '#6a5036'][itemIndex % 3];
                const inkColor = item.annotationType === 'note' ? '#2b3026' : '#f3ecdb';
                return (
                    <group key={slot} ref={(node) => { cardRefs.current[slot] = node; }}>
                        <group>
                            <mesh position={[0, 0.01, 0.08]}>
                                <cylinderGeometry args={[0.07, 0.07, 0.18, 12]} />
                                <SoftMaterial color="#20bf49" emissive="#176c2f" emissiveIntensity={0.14} />
                            </mesh>
                            <mesh position={[0, -0.65, 0]}>
                                <cylinderGeometry args={[0.013, 0.013, 1.22, 6]} />
                                <SoftMaterial color="#b6925f" emissive="#6a4e2d" emissiveIntensity={0.08} />
                            </mesh>
                            <RoundedBox args={[ROPE_GALLERY.cardWidth, ROPE_GALLERY.cardHeight, 0.13]} castShadow radius={0.045} smoothness={2}>
                                <SoftMaterial color={cardColor} emissive={selected?.id === item.id ? '#d7b86d' : cardColor} emissiveIntensity={selected?.id === item.id ? 0.18 : 0.025} />
                            </RoundedBox>
                            <RoundedBox args={[1.84, 1.32, 0.035]} position={[0, 0, 0.082]} radius={0.025} smoothness={2}>
                                <SoftMaterial color={item.annotationType === 'note' ? '#e6d9b3' : '#20302e'} />
                            </RoundedBox>
                            <WorldLabel className="knowledge-board-sticky" position={[0, 0, 0.13]} scale={0.18}>
                                <small style={{ color: item.annotationType === 'note' ? '#53625a' : '#8edbd1' }}>{item.annotationType === 'note' ? 'FIELD NOTE' : 'RECALL CARD'}</small>
                                <strong style={{ color: inkColor }}>{truncate(item.prompt || item.selectedText, 25)}</strong>
                                <span style={{ color: item.annotationType === 'note' ? '#64756b' : '#a7b8ad' }}>{truncate(item.document.fileName, 16)}</span>
                            </WorldLabel>
                            <mesh
                                onClick={(event) => {
                                    event.stopPropagation();
                                    if (!input.current.dragged) onChoose(item);
                                }}
                                position={[0, 0, 0.17]}
                            >
                                <planeGeometry args={[ROPE_GALLERY.cardWidth, ROPE_GALLERY.cardHeight]} />
                                <meshBasicMaterial opacity={0} transparent />
                            </mesh>
                        </group>
                    </group>
                );
            })}
        </group>
    );
}

function KnowledgeBoardWorld({ payload, reload }) {
    const annotations = payload || [];
    const cards = annotations.filter((item) => item.annotationType === 'card');
    const notes = annotations.filter((item) => item.annotationType === 'note');
    const [mode, setMode] = useState('cards');
    const [selected, setSelected] = useState(cards[0] || notes[0] || null);
    const [revealed, setRevealed] = useState(false);
    const [saving, setSaving] = useState(false);
    const visible = mode === 'cards' ? cards : notes;

    useEffect(() => {
        const available = mode === 'cards' ? cards : notes;
        const matching = available.find((item) => item.id === selected?.id);
        if (!matching) {
            setSelected(available[0] || null);
            setRevealed(false);
        } else if (matching !== selected) {
            setSelected(matching);
        }
    }, [cards, mode, notes, selected]);

    const choose = (item) => {
        setSelected(item);
        setRevealed(false);
    };
    const markMastered = async () => {
        if (!selected || saving) return;
        setSaving(true);
        try {
            await roomApi.markKnowledgeAnnotationMastered(
                selected.document.id,
                selected.id,
                !selected.mastered
            );
            await reload();
        } finally {
            setSaving(false);
        }
    };

    return (
        <>
            <group position={[0, 3.2, -0.15]}>
                <RoundedBox args={[13.6, 6.15, 0.28]} castShadow radius={0.18} smoothness={4}>
                    <SoftMaterial color="#1d2630" emissive={palette.cyan} emissiveIntensity={0.045} />
                </RoundedBox>
                <RoundedBox args={[13.15, 5.7, 0.09]} position={[0, 0, 0.2]} radius={0.08} smoothness={3}>
                    <SoftMaterial color="#27323a" />
                </RoundedBox>
                <mesh position={[0, 2.96, 0.29]}>
                    <boxGeometry args={[12.6, 0.07, 0.07]} />
                    <SoftMaterial color="#b6925f" emissive="#b6925f" emissiveIntensity={0.13} />
                </mesh>
                <HangingRopeGallery items={visible} onChoose={choose} selected={selected} />
            </group>
            <Html center position={[0, 0.28, 3.18]} transform scale={0.32} zIndexRange={[70, 20]}>
                <section className="knowledge-board-instrument" onClick={(event) => event.stopPropagation()}>
                    <header>
                        <div>
                            <small>STUDY RECALL BOARD</small>
                            <h2>知识黑板</h2>
                        </div>
                        <p>{cards.length} 张卡片 · {notes.length} 条笔记</p>
                    </header>
                    <nav aria-label="知识黑板内容">
                        <button className={mode === 'cards' ? 'is-active' : ''} onClick={() => setMode('cards')} type="button">知识卡片</button>
                        <button className={mode === 'notes' ? 'is-active' : ''} onClick={() => setMode('notes')} type="button">笔记</button>
                    </nav>
                    {visible.length > 0 && <p className="knowledge-board-gesture">左右拖动、滚轮或 ← → 可连续浏览</p>}
                    {selected ? (
                        <article>
                            <small>{selected.document.subject || '知识资料'} · {selected.document.fileName}</small>
                            <h3>{selected.annotationType === 'card' && !revealed
                                ? concealKeyTerms(selected.prompt || selected.selectedText, selected.hiddenTerms)
                                : selected.prompt || selected.selectedText}</h3>
                            {(revealed || selected.annotationType === 'note') && (
                                <p>{selected.answer || selected.note || selected.selectedText}</p>
                            )}
                            <footer>
                                {selected.annotationType === 'card' && !revealed && (
                                    <button onClick={() => setRevealed(true)} type="button">翻到背面</button>
                                )}
                                <button className={selected.mastered ? 'is-mastered' : ''} disabled={saving} onClick={markMastered} type="button">
                                    {saving ? '保存中…' : selected.mastered ? '取消背过' : '背过了'}
                                </button>
                            </footer>
                        </article>
                    ) : (
                        <p className="knowledge-board-empty">从知识书架打开一本资料，划线后选择“添加到笔记”或“制成知识卡”，内容就会贴到这里。</p>
                    )}
                </section>
            </Html>
            <WorldLabel position={[-5.9, 6.45, -0.28]}>
                <strong>知识黑板</strong>
                <span>点击卡片复习，笔记与资料保持关联</span>
            </WorldLabel>
        </>
    );
}

function ModuleContent({ moduleId, onOpenSpace, payload, reload }) {
    if (moduleId === 'study-home') {
        return <StudyHomeWorld onOpenSpace={onOpenSpace} payload={payload} reload={reload} />;
    }
    if (moduleId === 'study-goals') {
        return <StudyGoalsWorld payload={payload} reload={reload} />;
    }
    if (moduleId === 'study-plan') {
        return <StudyPlanWorld payload={payload} reload={reload} />;
    }
    if (moduleId === 'study-tutor') return <StudyTutorWorld />;
    if (moduleId === 'study-review') return <ReviewWorld payload={payload || []} reload={reload} />;
    if (moduleId === 'study-analytics') return <AnalyticsWorld payload={payload || {}} />;
    if (moduleId === 'study-knowledge') return null;
    if (moduleId === 'study-cards') return <KnowledgeBoardWorld payload={payload || []} reload={reload} />;
    if (moduleId === 'study-wordbook') return null;
    if (moduleId === 'work-home') return <WorkHomeWorld payload={payload || {}} />;
    if (moduleId === 'work-tech-stack') return <TechStackWorld payload={payload || {}} />;
    if (moduleId === 'work-knowledge') return null;
    if (moduleId === 'work-projects') return <ProjectsWorld payload={payload || {}} />;
    if (moduleId === 'work-resume') return <ResumeWorld payload={payload || {}} />;
    if (moduleId === 'novel-studio') {
        return <NovelWorld payload={payload || []} reload={reload} />;
    }
    return null;
}

export default function SpatialModuleScene({ moduleId, onOpenSpace }) {
    const [payload, setPayload] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [revision, setRevision] = useState(0);
    const loader = moduleLoader(moduleId);

    useEffect(() => {
        let current = true;
        setPayload(null);
        setError('');
        if (!loader) {
            setLoading(false);
            return () => {
                current = false;
            };
        }
        setLoading(true);
        loader()
            .then((result) => {
                if (current) setPayload(result);
            })
            .catch((requestError) => {
                if (current) setError(requestError.message);
            })
            .finally(() => {
                if (current) setLoading(false);
            });
        return () => {
            current = false;
        };
    }, [loader, moduleId, revision]);

    const accent = moduleId.startsWith('work-')
        ? palette.green
        : moduleId === 'novel-studio'
          ? palette.pink
          : palette.cyan;

    return (
        <>
            <RoomStage accent={accent} secondary={palette.pink} />
            {loading ? (
                <LoadingWorld />
            ) : error ? (
                <ErrorWorld error={error} onRetry={() => setRevision((value) => value + 1)} />
            ) : (
                <ModuleContent
                    moduleId={moduleId}
                    onOpenSpace={onOpenSpace}
                    payload={payload}
                    reload={() => setRevision((value) => value + 1)}
                />
            )}
        </>
    );
}

useGLTF.preload('/assets/PlanOrbit.glb');

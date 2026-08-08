/* eslint-disable react/prop-types */
import { ContactShadows, Html, RoundedBox } from '@react-three/drei';
import { useFrame } from '@react-three/fiber';
import { Select } from '@react-three/postprocessing';
import { useEffect, useMemo, useRef, useState } from 'react';

import { roomMaterial, roomPalette as palette } from '../roomTheme';

const standard = roomMaterial;

function FocusBeacon({ active, color, position }) {
    const ring = useRef();
    useFrame((state, delta) => {
        if (!ring.current) return;
        ring.current.rotation.z += delta * 0.45;
        const pulse = 1 + Math.sin(state.clock.elapsedTime * 2.2) * 0.05;
        ring.current.scale.setScalar(pulse);
    });

    if (!active) return null;
    return (
        <group position={position} rotation={[-Math.PI / 2, 0, 0]}>
            <mesh ref={ring}>
                <torusGeometry args={[1.25, 0.018, 10, 96]} />
                <meshBasicMaterial color={color} transparent opacity={0.72} />
            </mesh>
            <mesh>
                <ringGeometry args={[0.92, 0.94, 64]} />
                <meshBasicMaterial color={color} transparent opacity={0.28} />
            </mesh>
            <pointLight color={color} distance={4} intensity={3.2} position={[0, 0, 0.5]} />
        </group>
    );
}

function Hotspot({ label, hint, position, onOpen, children }) {
    const [hovered, setHovered] = useState(false);

    useEffect(() => {
        if (hovered) document.body.style.cursor = 'pointer';
        return () => {
            document.body.style.cursor = 'auto';
        };
    }, [hovered]);

    return (
        <group position={position}>
            <Select enabled={hovered}>
                <group
                    scale={hovered ? 1.018 : 1}
                    onClick={(event) => {
                        event.stopPropagation();
                        onOpen();
                    }}
                    onPointerOver={(event) => {
                        event.stopPropagation();
                        setHovered(true);
                    }}
                    onPointerOut={() => setHovered(false)}
                >
                    {children}
                </group>
            </Select>
            <Html center distanceFactor={13} position={[0, 2.45, -0.35]}>
                <button
                    className={`scene-label ${hovered ? 'is-hovered' : ''}`}
                    onClick={onOpen}
                    tabIndex={hovered ? 0 : -1}
                    type="button"
                >
                    <strong>{label}</strong>
                    <span>{hint}</span>
                </button>
            </Html>
        </group>
    );
}

function Bookshelf({ active, onOpen }) {
    const books = useMemo(
        () =>
            Array.from({ length: 36 }, (_, index) => ({
                x: -1.42 + (index % 9) * 0.35,
                y: -1.8 + Math.floor(index / 9) * 1.02,
                width: 0.2 + (index % 2) * 0.06,
                height: 0.56 + (index % 3) * 0.1,
                color: [palette.cyan, palette.pink, palette.blue, palette.gold][
                    index % 4
                ]
            })),
        []
    );

    return (
        <Hotspot
            hint="Knowledge · Wordbook"
            label="知识书架"
            onOpen={onOpen}
            position={[7.05, 2.68, 3.73]}
        >
            <RoundedBox
                args={[3.9, 5.2, 0.56]}
                castShadow
                radius={0.09}
                scale={active ? 1.025 : 1}
                smoothness={3}
            >
                <meshStandardMaterial
                    color={palette.deskWood}
                    emissive={active ? palette.deskGlow : '#000000'}
                    emissiveIntensity={active ? 0.12 : 0}
                    {...standard}
                />
            </RoundedBox>
            <RoundedBox
                args={[3.5, 4.8, 0.3]}
                position={[0, 0, -0.34]}
                radius={0.05}
                smoothness={2}
            >
                <meshStandardMaterial color={palette.deskWoodDark} {...standard} />
            </RoundedBox>
            {Array.from({ length: 5 }, (_, index) => (
                <RoundedBox
                    args={[3.62, 0.12, 0.66]}
                    castShadow
                    key={`shelf-${index}`}
                    position={[0, -2.02 + index * 1.02, -0.63]}
                    radius={0.035}
                    smoothness={2}
                >
                    <meshStandardMaterial color={palette.deskWoodEdge} {...standard} />
                </RoundedBox>
            ))}
            {books.map((book, index) => (
                <RoundedBox
                    args={[book.width, book.height, 0.28]}
                    castShadow
                    key={`book-${index}`}
                    position={[book.x, book.y, -0.87]}
                    radius={0.025}
                    rotation={[0, 0, (index % 5 - 2) * 0.018]}
                    smoothness={2}
                >
                    <meshStandardMaterial color={book.color} {...standard} />
                </RoundedBox>
            ))}
            <pointLight color={palette.deskGlow} distance={5} intensity={4.2} position={[0, 0, -1.25]} />
        </Hotspot>
    );
}

function GalleryWall({ active, onOpen }) {
    const frames = [
        [-1.0, 1.12, 1.15, 1.42, '#c47794'],
        [0.78, 1.22, 1.42, 1.15, '#68aeb8'],
        [-0.9, -0.96, 1.4, 1.08, '#d6a768'],
        [0.92, -0.87, 1.08, 1.42, '#927cbc']
    ];

    return (
        <Hotspot
            hint="进入小说写作空间"
            label="作品展墙"
            onOpen={onOpen}
            position={[10.92, 2.62, 3.75]}
        >
            <RoundedBox
                args={[3.55, 5.0, 0.3]}
                castShadow
                radius={0.1}
                scale={active ? 1.025 : 1}
                smoothness={4}
            >
                <meshStandardMaterial
                    color="#7c3d5c"
                    emissive={active ? '#d87e9c' : '#000000'}
                    emissiveIntensity={active ? 0.12 : 0}
                    {...standard}
                />
            </RoundedBox>
            {frames.map(([x, y, width, height, color], index) => (
                <group key={`frame-${index}`} position={[x, y, -0.26]}>
                    <RoundedBox
                        args={[width + 0.2, height + 0.2, 0.14]}
                        castShadow
                        radius={0.045}
                        smoothness={2}
                    >
                        <meshStandardMaterial color="#bd856b" {...standard} />
                    </RoundedBox>
                    <RoundedBox
                        args={[width, height, 0.08]}
                        position={[0, 0, -0.09]}
                        radius={0.03}
                        smoothness={2}
                    >
                        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.06} {...standard} />
                    </RoundedBox>
                </group>
            ))}
            <RoundedBox
                args={[2.1, 0.3, 0.3]}
                position={[0, -2.12, -0.35]}
                radius={0.08}
                smoothness={3}
            >
                <meshStandardMaterial color={palette.paper} {...standard} />
            </RoundedBox>
            <pointLight color="#f09ab8" distance={5} intensity={6.5} position={[0, 0.5, -1.35]} />
        </Hotspot>
    );
}

function Workbench({ active, onOpen }) {
    return (
        <Hotspot
            hint="Stacks · Projects · Resume"
            label="Work Bench"
            onOpen={onOpen}
            position={[8.85, 2.0, 0.55]}
        >
            <RoundedBox
                args={[4.65, 0.3, 1.95]}
                castShadow
                radius={0.12}
                scale={active ? 1.025 : 1}
                smoothness={4}
            >
                <meshStandardMaterial
                    color="#696077"
                    emissive={active ? '#6dd0c9' : '#000000'}
                    emissiveIntensity={active ? 0.1 : 0}
                    {...standard}
                />
            </RoundedBox>
            <RoundedBox
                args={[1.28, 1.02, 1.02]}
                castShadow
                position={[-1.35, 0.66, 0.18]}
                radius={0.12}
                smoothness={4}
            >
                <meshStandardMaterial color="#506176" {...standard} />
            </RoundedBox>
            <group position={[0.82, 0.58, 0.28]} rotation={[-0.25, 0, 0]}>
                <RoundedBox args={[1.74, 0.98, 0.12]} castShadow radius={0.06} smoothness={3}>
                    <meshStandardMaterial color="#203744" {...standard} />
                </RoundedBox>
                <mesh position={[0, 0, -0.07]}>
                    <planeGeometry args={[1.48, 0.73]} />
                    <meshStandardMaterial color="#59b8ba" emissive="#3aa3aa" emissiveIntensity={0.28} />
                </mesh>
            </group>
            {[-1.8, 1.8].map((x) => (
                <RoundedBox
                    args={[0.2, 1.85, 0.2]}
                    castShadow
                    key={x}
                    position={[x, -0.94, 0]}
                    radius={0.05}
                    smoothness={2}
                >
                    <meshStandardMaterial color="#37404f" {...standard} />
                </RoundedBox>
            ))}
        </Hotspot>
    );
}

export default function UniverseWing({ activeSpace, onOpen }) {
    return (
        <group>
            <hemisphereLight color="#efc9ce" groundColor="#172637" intensity={0.65} />
            <pointLight castShadow color="#ffb5a2" distance={18} intensity={32} position={[9, 6.5, 0]} />
            <pointLight color="#8d8cff" distance={15} intensity={13} position={[5, 4.5, -1]} />

            <Bookshelf active={activeSpace === 'library'} onOpen={() => onOpen('library')} />
            <GalleryWall active={activeSpace === 'novel'} onOpen={() => onOpen('novel')} />
            <Workbench active={activeSpace === 'work'} onOpen={() => onOpen('work')} />
            <FocusBeacon
                active={activeSpace === 'study'}
                color={palette.cyan}
                position={[1.75, 0.18, 2.4]}
            />
            <FocusBeacon
                active={activeSpace === 'plan'}
                color={palette.violet}
                position={[-5.15, 0.18, -1.8]}
            />
            <FocusBeacon
                active={activeSpace === 'library'}
                color={palette.deskGlow}
                position={[7.05, 0.18, 3.73]}
            />
            <FocusBeacon
                active={activeSpace === 'board'}
                color={palette.gold}
                position={[-5.15, 0.18, -1.8]}
            />
            <FocusBeacon
                active={activeSpace === 'work'}
                color={palette.cyan}
                position={[8.85, 0.18, 0.55]}
            />
            <FocusBeacon
                active={activeSpace === 'novel'}
                color={palette.pink}
                position={[10.92, 0.18, 3.75]}
            />
            <ContactShadows
                blur={2.3}
                color="#1a1020"
                far={7}
                opacity={0.52}
                position={[9, 0.16, 0.65]}
                resolution={512}
                scale={12}
            />
        </group>
    );
}

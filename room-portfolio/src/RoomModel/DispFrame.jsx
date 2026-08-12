/* eslint-disable react/display-name */
/* eslint-disable react/prop-types */
import { useTexture, useVideoTexture } from '@react-three/drei';
import { Select } from '@react-three/postprocessing';
import React, { useCallback, useEffect, useState } from 'react';

import { useCameraStore } from '../helper/CameraStore';
import DesktopiFrame from './iframes/desktopiFrame';
import SmartphoneiFrame from './iframes/smartphoneiFrame';
import TvEmulator from './iframes/tvEmulator';
import LaptopDisp from './laptopDisp';

const DispFrame = React.memo(({ nodes, onOpen }) => {
    // Retrieve camera states from the store
    const cameraState = useCameraStore((state) => state.cameraState);
    const laptopState = useCameraStore((state) => state.laptop);
    const tvState = useCameraStore((state) => state.tv);
    const smartphoneState = useCameraStore((state) => state.smartphone);

    const [hovered, setHover] = useState(false);
    const [hoveredLaptop, setHoveredLaptop] = useState(null);
    const [hoveredTv, setHoveredTv] = useState(null);
    const [hoveredSmartphone, setHoveredSmartphone] = useState(null);

    // Change cursor style based on hover state
    useEffect(() => {
        document.body.style.cursor = hovered ? 'pointer' : 'auto';
    }, [hovered]);

    // Callbacks for hover events
    const onPointerOver = useCallback(() => setHover(true), []);
    const onPointerOut = useCallback(() => setHover(false), []);

    // Load video and image textures
    const desktopWallpaper = useVideoTexture('/assets/desktopWallpaper.mp4');
    const tvWallpaper = useVideoTexture('/assets/marioWallpaper.mp4');
    const smartphoneWallpaper = useTexture('/assets/smartphoneWallpaper.webp');
    const musicBg = useTexture('/assets/SpotifyClone.webp');

    return (
        <>
            {/* Render various iFrames and display components */}
            <LaptopDisp nodes={nodes} />
            <SmartphoneiFrame />
            <DesktopiFrame />
            <TvEmulator />

            {/* The study space opens only from the visible monitor screen.
                It deliberately is not wrapped in Select, so the desk never receives a white outline. */}
            <mesh
                geometry={nodes.monitor.geometry}
                position={nodes.monitor.position}
                rotation={nodes.monitor.rotation}
                onClick={(event) => {
                    event.stopPropagation();
                    onOpen?.('study');
                    onPointerOut();
                }}
                onPointerOver={() => {
                    onPointerOver();
                }}
                onPointerOut={() => {
                    onPointerOut();
                }}
            >
                <meshBasicMaterial
                    map={desktopWallpaper}
                    toneMapped={false}
                />
            </mesh>

            {/* Laptop display */}
            <Select enabled={hoveredLaptop}>
                <mesh
                    geometry={nodes.laptop.geometry}
                    position={nodes.laptop.position}
                    rotation={nodes.laptop.rotation}
                    onClick={
                        cameraState !== 'laptop'
                            ? () => {
                                  laptopState();
                                  setHoveredLaptop(false);
                                  onPointerOut();
                              }
                            : undefined
                    }
                    onPointerOver={
                        cameraState === 'default'
                            ? () => {
                                  onPointerOver();
                                  setHoveredLaptop(true);
                              }
                            : undefined
                    }
                    onPointerOut={
                        cameraState === 'default'
                            ? () => {
                                  onPointerOut();
                                  setHoveredLaptop(false);
                              }
                            : undefined
                    }
                >
                    <meshBasicMaterial map={musicBg} toneMapped={false} />
                </mesh>
            </Select>

            {/* TV display */}
            <Select enabled={hoveredTv}>
                <mesh
                    geometry={nodes.tvdisplay.geometry}
                    position={nodes.tvdisplay.position}
                    rotation={nodes.tvdisplay.rotation}
                    onClick={
                        cameraState !== 'tv'
                            ? () => {
                                  tvState();
                                  setHoveredTv(false);
                                  onPointerOut();
                              }
                            : undefined
                    }
                    onPointerOver={
                        cameraState === 'default'
                            ? () => {
                                  onPointerOver();
                                  setHoveredTv(true);
                              }
                            : undefined
                    }
                    onPointerOut={
                        cameraState === 'default'
                            ? () => {
                                  onPointerOut();
                                  setHoveredTv(false);
                              }
                            : undefined
                    }
                >
                    <meshBasicMaterial map={tvWallpaper} toneMapped={false} />
                </mesh>
            </Select>

            {/* Smartphone display */}
            <Select enabled={hoveredSmartphone}>
                <mesh
                    geometry={nodes.smartphoneDisp.geometry}
                    position={nodes.smartphoneDisp.position}
                    rotation={nodes.smartphoneDisp.rotation}
                    onClick={
                        cameraState !== 'smartphone'
                            ? () => {
                                  smartphoneState();
                                  setHoveredSmartphone(false);
                                  onPointerOut();
                              }
                            : undefined
                    }
                    onPointerOver={
                        cameraState === 'default'
                            ? () => {
                                  onPointerOver();
                                  setHoveredSmartphone(true);
                              }
                            : undefined
                    }
                    onPointerOut={
                        cameraState === 'default'
                            ? () => {
                                  onPointerOut();
                                  setHoveredSmartphone(false);
                              }
                            : undefined
                    }
                >
                    <meshBasicMaterial map={smartphoneWallpaper} />
                </mesh>
            </Select>

            {/* Blackboard is a direct entry to learner-owned notes and recall cards.
                It intentionally has no Select wrapper so the room keeps no white outline. */}
            <mesh
                position={[-5.2, 2.95, -1.95]}
                rotation={[0, Math.PI / 2, 0]}
                scale={[2.8, 1.6, 1]}
                onClick={() => {
                    onOpen?.('board');
                    onPointerOut();
                }}
                onPointerOver={() => {
                    onPointerOver();
                }}
                onPointerOut={() => {
                    onPointerOut();
                }}
            >
                <meshBasicMaterial transparent opacity={0} />
                <planeGeometry />
            </mesh>
        </>
    );
});

export default DispFrame;

// Preload textures
useTexture.preload('/assets/smartphoneWallpaper.webp');
useTexture.preload('/assets/SpotifyClone.webp');

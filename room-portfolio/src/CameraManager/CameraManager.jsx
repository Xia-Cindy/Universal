import { CameraControls } from '@react-three/drei';
import { useThree } from '@react-three/fiber';
import { useRef } from 'react';
import { useEffect } from 'react';

import { useCameraStore } from '../helper/CameraStore';
import { findSpaceByModule, SPACE_GROUPS } from '../spaces';

export const CameraManager = () => {
    const cameraControle = useRef();
    const { size } = useThree();

    const cameraState = useCameraStore((state) => state.cameraState);
    const activeFocus = useCameraStore((state) => state.activeFocus);
    const activeModule = useCameraStore((state) => state.activeModule);

    const maxDistancce = useCameraStore((state) => state.maxDistancce);
    const minDistance = useCameraStore((state) => state.minDistance);
    const maxAzimuthAngle = useCameraStore((state) => state.maxAzimuthAngle);
    const minAzimuthAngle = useCameraStore((state) => state.minAzimuthAngle);
    const minPolarAngle = useCameraStore((state) => state.minPolarAngle);
    const maxPolarAngle = useCameraStore((state) => state.maxPolarAngle);
    const truckSpeed = useCameraStore((state) => state.truckSpeed);
    const dollyToCursor = useCameraStore((state) => state.dollyToCursor);
    const enable = useCameraStore((state) => state.enable);

    useEffect(() => {
        if (cameraState === 'default') {
            const aspect = size.width / Math.max(size.height, 1);
            const responsiveDistance = aspect < 0.75 ? 32 : aspect < 1.15 ? 26 : 24;
            useCameraStore.setState({ truckSpeed: 0.5 });
            useCameraStore.setState({ dollyToCursor: true });
            useCameraStore.setState({ minDistance: 2 });
            useCameraStore.setState({ maxDistancce: 45 });
            useCameraStore.setState({ minPolarAngle: Math.PI * 0.1 });
            useCameraStore.setState({ maxPolarAngle: Math.PI * 0.45 });
            useCameraStore.setState({ minAzimuthAngle: Math.PI * 0.5 });
            useCameraStore.setState({ maxAzimuthAngle: Math.PI });
            cameraControle.current.setLookAt(
                responsiveDistance,
                responsiveDistance * 0.64,
                -responsiveDistance,
                0,
                -0.5,
                0,
                true
            );
        }

        if (cameraState === 'space') {
            const focus = {
                study: {
                    camera: [12.5, 7.4, -11.5],
                    target: [1.4, 1.9, 1.2]
                },
                plan: {
                    camera: [-12.5, 7.8, -10.5],
                    target: [-1.2, 2.0, -1.1]
                },
                library: {
                    camera: [14.5, 7.6, -4.8],
                    target: [7.0, 2.6, 3.1]
                },
                work: {
                    camera: [16.0, 7.6, -7.8],
                    target: [8.8, 1.8, 0.4]
                },
                novel: {
                    camera: [17.5, 7.5, -3.4],
                    target: [10.8, 2.5, 3.3]
                }
            }[activeFocus];

            if (focus) {
                useCameraStore.setState({ truckSpeed: 0.25 });
                useCameraStore.setState({ dollyToCursor: false });
                useCameraStore.setState({ minDistance: 3 });
                useCameraStore.setState({ maxDistancce: 28 });
                useCameraStore.setState({ minPolarAngle: Math.PI * 0.08 });
                useCameraStore.setState({ maxPolarAngle: Math.PI * 0.48 });
                useCameraStore.setState({ minAzimuthAngle: -Infinity });
                useCameraStore.setState({ maxAzimuthAngle: Infinity });
                cameraControle.current.setLookAt(
                    ...focus.camera,
                    ...focus.target,
                    true
                );
            }
        }

        if (cameraState === 'module' && activeModule) {
            const moduleSpace = findSpaceByModule(activeModule);
            const portal = SPACE_GROUPS[moduleSpace]?.portal || {
                x: 0,
                stageZ: -12.5
            };
            const aspect = size.width / Math.max(size.height, 1);
            const distance = aspect < 0.72 ? 24 : aspect < 1.05 ? 20 : 15.5;
            const verticalOffset = aspect < 0.72 ? 5.4 : 4.7;
            const horizontalOffset = aspect < 1.05 ? 1.55 : 0;
            useCameraStore.setState({ truckSpeed: 0.16 });
            useCameraStore.setState({ dollyToCursor: false });
            useCameraStore.setState({ minDistance: 10 });
            useCameraStore.setState({ maxDistancce: 30 });
            useCameraStore.setState({ minPolarAngle: Math.PI * 0.2 });
            useCameraStore.setState({ maxPolarAngle: Math.PI * 0.48 });
            useCameraStore.setState({ minAzimuthAngle: -Math.PI * 0.14 });
            useCameraStore.setState({ maxAzimuthAngle: Math.PI * 0.14 });
            cameraControle.current.setLookAt(
                portal.x + horizontalOffset,
                verticalOffset,
                portal.stageZ + distance,
                portal.x + horizontalOffset,
                3.1,
                portal.stageZ,
                true
            );
        }

        if (cameraState === 'desktop') {
            useCameraStore.setState({ truckSpeed: 0 });
            useCameraStore.setState({ dollyToCursor: false });
            useCameraStore.setState({ minDistance: 5.65 });
            useCameraStore.setState({ maxDistancce: 7.1 });
            useCameraStore.setState({ minPolarAngle: Math.PI * 0.5 });
            useCameraStore.setState({ maxPolarAngle: Math.PI * 0.5 });
            useCameraStore.setState({ minAzimuthAngle: Math.PI });
            useCameraStore.setState({ maxAzimuthAngle: Math.PI });
            cameraControle.current.setLookAt(2.1, 0.3, 2, 2.1, 0.3, 8, true);
        }

        if (cameraState === 'laptop') {
            useCameraStore.setState({ truckSpeed: 0 });
            useCameraStore.setState({ dollyToCursor: false });
            useCameraStore.setState({ minDistance: 4.2 });
            useCameraStore.setState({ maxDistancce: 6 });
            useCameraStore.setState({ minPolarAngle: Math.PI * 0.435 });
            useCameraStore.setState({ maxPolarAngle: Math.PI * 0.435 });
            useCameraStore.setState({ minAzimuthAngle: Math.PI * 0.689 });
            useCameraStore.setState({ maxAzimuthAngle: Math.PI * 0.689 });
            cameraControle.current.setLookAt(2, 0, 2.5, -2, -1, 5.2, true);
        }

        if (cameraState === 'tv') {
            useCameraStore.setState({ truckSpeed: 0 });
            useCameraStore.setState({ dollyToCursor: false });
            useCameraStore.setState({ minDistance: 5.6 });
            useCameraStore.setState({ maxDistancce: 6.5 });
            useCameraStore.setState({ minPolarAngle: Math.PI * 0.5 });
            useCameraStore.setState({ maxPolarAngle: Math.PI * 0.5 });
            useCameraStore.setState({ minAzimuthAngle: 0 });
            useCameraStore.setState({ maxAzimuthAngle: 0 });
            cameraControle.current.setLookAt(2.5, -0.1, 1, 2.5, -0.1, -5, true);
        }

        if (cameraState === 'smartphone') {
            useCameraStore.setState({ truckSpeed: 0 });
            useCameraStore.setState({ dollyToCursor: false });
            useCameraStore.setState({ minDistance: 8.8 });
            useCameraStore.setState({ maxDistancce: 9.2 });
            useCameraStore.setState({ minPolarAngle: Math.PI * 0.03 });
            useCameraStore.setState({ maxPolarAngle: Math.PI * 0.036 });
            useCameraStore.setState({ minAzimuthAngle: Math.PI * 0.83 });
            useCameraStore.setState({ maxAzimuthAngle: Math.PI * 0.845 });
            cameraControle.current.setLookAt(
                1.7,
                -0.3,
                -0.85,
                1.25,
                -9,
                -0.1,
                true
            );
        }

        if (cameraState === 'displayBoard') {
            useCameraStore.setState({ truckSpeed: 0 });
            useCameraStore.setState({ dollyToCursor: true });
            useCameraStore.setState({ minDistance: 4 });
            useCameraStore.setState({ maxDistancce: 8 });
            useCameraStore.setState({ minPolarAngle: Math.PI * 0.4999 });
            useCameraStore.setState({ maxPolarAngle: Math.PI * 0.5 });
            useCameraStore.setState({ minAzimuthAngle: Math.PI * 0.5 });
            useCameraStore.setState({ maxAzimuthAngle: Math.PI * 0.50001 });
            cameraControle.current.setLookAt(
                -2,
                0.12,
                -1.5,
                -8,
                0.12,
                -1.5,
                true
            );
        }
    }, [activeFocus, activeModule, cameraState, size.height, size.width]);

    return (
        <CameraControls
            makeDefault={true}
            ref={cameraControle}
            dollyToCursor={dollyToCursor}
            dollySpeed={1.2}
            truckSpeed={truckSpeed}
            minDistance={minDistance}
            maxDistance={maxDistancce}
            smoothTime={0.8}
            maxAzimuthAngle={maxAzimuthAngle}
            minAzimuthAngle={minAzimuthAngle}
            minPolarAngle={minPolarAngle}
            maxPolarAngle={maxPolarAngle}
            polarRotateSpeed={0.3}
            azimuthRotateSpeed={0.3}
            maxSpeed={20}
            enableTransition={true}
            boundaryFriction={0}
            boundaryEnclosesCamera={true}
            interactiveArea={[0.5, 0.5, 1, 1]}
            enabled={enable}
        />
    );
};

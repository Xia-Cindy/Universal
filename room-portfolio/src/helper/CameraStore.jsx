import { create } from 'zustand';

export const useCameraStore = create((set) => ({
    // Camer State
    cameraState: 'default',
    activeFocus: null,
    activeModule: null,

    default: () => {
        set({ cameraState: 'default', activeFocus: null, activeModule: null });
    },
    focusSpace: (space) => {
        set({ cameraState: 'space', activeFocus: space, activeModule: null });
    },
    focusModule: (moduleId) => {
        set({
            cameraState: 'module',
            activeFocus: null,
            activeModule: moduleId
        });
    },
    desktop: () => {
        set((state) => ({
            cameraState: (state.cameraState = 'desktop')
        }));
    },
    laptop: () => {
        set((state) => ({
            cameraState: (state.cameraState = 'laptop')
        }));
    },
    tv: () => {
        set((state) => ({
            cameraState: (state.cameraState = 'tv')
        }));
    },
    smartphone: () => {
        set((state) => ({
            cameraState: (state.cameraState = 'smartphone')
        }));
    },
    displayBoard: () => {
        set((state) => ({
            cameraState: (state.cameraState = 'displayBoard')
        }));
    },

    // camera properties

    maxDistancce: 45,
    minDistance: 2,
    maxAzimuthAngle: Math.PI,
    minAzimuthAngle: Math.PI * 0.5,
    minPolarAngle: Math.PI * 0.1,
    maxPolarAngle: Math.PI * 0.45,
    truckSpeed: 0.5,
    dollyToCursor: true,
    enable: true
}));

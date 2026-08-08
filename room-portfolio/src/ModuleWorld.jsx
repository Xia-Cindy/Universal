/* eslint-disable react/prop-types */
import { SPACE_GROUPS } from './spaces';
import SpatialModuleScene from './SpatialModuleScene';

export default function ModuleWorld({ activeModule, activeSpace, onOpenSpace }) {
    if (!activeModule) return null;
    const portal = SPACE_GROUPS[activeSpace]?.portal || { x: 0, stageZ: -12.5 };

    return (
        <group
            key={activeModule}
            position={[portal.x, 0, portal.stageZ]}
        >
            <SpatialModuleScene
                moduleId={activeModule}
                onOpenSpace={onOpenSpace}
            />
        </group>
    );
}

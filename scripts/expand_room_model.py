"""Build the expanded Universe room from the untouched portfolio GLB.

Run with Blender:
  blender --background --python scripts/expand_room_model.py

Only the original baked floor and back-wall geometry are stretched. UVs and
node names remain intact so the existing Three.js shader can render the asset.
"""

from pathlib import Path

import bmesh
import bpy


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "room-portfolio/public/assets/RoomModel.glb"
OUTPUT = ROOT / "room-portfolio/public/assets/RoomModelExpanded.glb"
ROOM_WIDTH_FACTOR = 2.0
LEFT_WALL_X = -5.557


def connected_components(vertices):
    remaining = set(vertices)
    while remaining:
        seed = remaining.pop()
        stack = [seed]
        component = {seed}
        while stack:
            vertex = stack.pop()
            for edge in vertex.link_edges:
                other = edge.other_vert(vertex)
                if other in remaining:
                    remaining.remove(other)
                    component.add(other)
                    stack.append(other)
        yield component


def is_floor_or_back_wall(obj, component) -> bool:
    world = [obj.matrix_world @ vertex.co for vertex in component]
    minimum = [min(point[index] for point in world) for index in range(3)]
    maximum = [max(point[index] for point in world) for index in range(3)]
    size = [maximum[index] - minimum[index] for index in range(3)]

    is_floor = (
        maximum[2] < 0.19
        and minimum[2] > 0.12
        and size[2] < 0.03
        and 0.60 < size[1] < 0.66
    )
    is_back_wall = (
        size[0] > 10.0
        and size[1] < 0.3
        and size[2] > 5.0
        and minimum[1] < -4.25
    )
    return is_floor or is_back_wall


def main() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(SOURCE))

    room = bpy.data.objects["roomFurniture"]
    mesh = room.data
    editable = bmesh.new()
    editable.from_mesh(mesh)
    editable.verts.ensure_lookup_table()

    selected = set()
    for component in connected_components(editable.verts):
        if is_floor_or_back_wall(room, component):
            selected.update(component)

    inverse = room.matrix_world.inverted()
    for vertex in selected:
        world = room.matrix_world @ vertex.co
        world.x = LEFT_WALL_X + (world.x - LEFT_WALL_X) * ROOM_WIDTH_FACTOR
        vertex.co = inverse @ world

    editable.to_mesh(mesh)
    editable.free()
    mesh.update()

    bpy.ops.object.select_all(action="SELECT")
    bpy.context.view_layer.objects.active = room
    bpy.ops.export_scene.gltf(
        filepath=str(OUTPUT),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_draco_mesh_compression_enable=True,
        export_draco_mesh_compression_level=6,
    )
    print(
        f"Expanded room written to {OUTPUT} "
        f"({len(bpy.context.scene.objects)} objects, {len(selected)} modified vertices)"
    )


if __name__ == "__main__":
    main()

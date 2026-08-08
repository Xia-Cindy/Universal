from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
BLENDER_DIR = ROOT / "room-portfolio" / "blender"
ASSET_DIR = ROOT / "room-portfolio" / "public" / "assets"
BLEND_PATH = BLENDER_DIR / "PlanOrbit.blend"
GLB_PATH = ASSET_DIR / "PlanOrbit.glb"


PALETTE = {
    "wood": "5B3340",
    "wood_dark": "2A1722",
    "wood_edge": "A66A59",
    "paper": "E8D7C5",
    "paper_shadow": "B99FA0",
    "cyan": "6DD0C9",
    "blue": "416B87",
    "pink": "D87E9C",
    "gold": "D5A75E",
    "metal": "3E3547",
}


def rgba(hex_value: str, alpha: float = 1.0) -> tuple[float, float, float, float]:
    value = hex_value.lstrip("#")
    return tuple(int(value[index:index + 2], 16) / 255 for index in (0, 2, 4)) + (alpha,)


def material(
    name: str,
    color: str,
    *,
    roughness: float = 0.48,
    metallic: float = 0.0,
    emission: str | None = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    item = bpy.data.materials.new(name)
    item.use_nodes = True
    shader = item.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = rgba(color)
    shader.inputs["Roughness"].default_value = roughness
    shader.inputs["Metallic"].default_value = metallic
    if emission and "Emission Color" in shader.inputs:
        shader.inputs["Emission Color"].default_value = rgba(emission)
        shader.inputs["Emission Strength"].default_value = emission_strength
    return item


def assign(obj: bpy.types.Object, mat: bpy.types.Material) -> bpy.types.Object:
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj


def bevelled_box(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    mat: bpy.types.Material,
    bevel: float = 0.08,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (scale[0] / 2, scale[1] / 2, scale[2] / 2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    modifier = obj.modifiers.new("Soft room edge", "BEVEL")
    modifier.width = bevel
    modifier.segments = 3
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    assign(obj, mat)
    return obj


def torus(
    name: str,
    radius: float,
    thickness: float,
    z: float,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius,
        minor_radius=thickness,
        major_segments=128,
        minor_segments=12,
        location=(0, 0.05, z),
        rotation=(math.pi / 2, 0, 0),
    )
    obj = bpy.context.object
    obj.name = name
    assign(obj, mat)
    return obj


def cylinder_between(
    name: str,
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    radius: float,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    sx, sy, sz = start
    ex, ey, ez = end
    dx, dy, dz = ex - sx, ey - sy, ez - sz
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=length)
    obj = bpy.context.object
    obj.name = name
    obj.location = ((sx + ex) / 2, (sy + ey) / 2, (sz + ez) / 2)
    direction = Vector((dx, dy, dz))
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = direction.to_track_quat("Z", "Y")
    assign(obj, mat)
    return obj


def add_text(name: str, text: str, location: tuple[float, float, float], mat: bpy.types.Material) -> None:
    bpy.ops.object.text_add(location=location, rotation=(math.pi / 2, 0, 0))
    obj = bpy.context.object
    obj.name = name
    obj.data.body = text
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.size = 0.34
    obj.data.extrude = 0.018
    obj.data.bevel_depth = 0.006
    assign(obj, mat)
    bpy.ops.object.convert(target="MESH")


def build() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in list(bpy.data.materials):
        bpy.data.materials.remove(block)

    wood = material("Room_Warm_Wood", PALETTE["wood"], roughness=0.58)
    wood_dark = material("Room_Wood_Shadow", PALETTE["wood_dark"], roughness=0.62)
    wood_edge = material("Room_Wood_Edge", PALETTE["wood_edge"], roughness=0.5)
    paper = material("Planner_Paper", PALETTE["paper"], roughness=0.72)
    paper_shadow = material("Planner_Paper_Shadow", PALETTE["paper_shadow"], roughness=0.72)
    metal = material("Planner_Dark_Metal", PALETTE["metal"], roughness=0.28, metallic=0.74)
    gold = material("Planner_Gold", PALETTE["gold"], roughness=0.3, metallic=0.62)
    cyan = material(
        "Planner_Cyan_Light",
        PALETTE["cyan"],
        roughness=0.26,
        metallic=0.18,
        emission=PALETTE["cyan"],
        emission_strength=1.4,
    )
    pink = material(
        "Planner_Pink_Accent",
        PALETTE["pink"],
        roughness=0.36,
        emission=PALETTE["pink"],
        emission_strength=0.48,
    )
    neutral = material("Planner_Date_Neutral", PALETTE["blue"], roughness=0.42, metallic=0.24)

    base = bevelled_box("Plan_Base", (0, 0.65, 0.42), (8.8, 3.0, 0.5), wood, 0.18)
    bevelled_box("Plan_Base_Inset", (0, -0.53, 0.68), (7.8, 0.42, 0.12), wood_edge, 0.04)
    bevelled_box("Plan_Base_Shadow", (0, 0.78, 0.14), (7.5, 2.2, 0.22), wood_dark, 0.08)

    # A small open planner at the front makes the object read as a planning instrument.
    left_page = bevelled_box("Plan_Page_Left", (-1.45, -0.45, 0.86), (2.75, 1.28, 0.1), paper, 0.05)
    right_page = bevelled_box("Plan_Page_Right", (1.45, -0.45, 0.86), (2.75, 1.28, 0.1), paper_shadow, 0.05)
    left_page.rotation_euler = (math.radians(-4), math.radians(4), math.radians(-2))
    right_page.rotation_euler = (math.radians(-4), math.radians(-4), math.radians(2))
    cylinder_between("Plan_Page_Spine", (0, -1.04, 0.78), (0, 0.16, 0.91), 0.035, gold)

    center_z = 4.35
    bevelled_box("Plan_Support_Left", (-3.78, 0.34, 3.95), (0.28, 0.38, 6.7), wood_edge, 0.08)
    bevelled_box("Plan_Support_Right", (3.78, 0.34, 3.95), (0.28, 0.38, 6.7), wood_edge, 0.08)
    bevelled_box("Plan_Header_Beam", (0, 0.34, 7.32), (7.8, 0.38, 0.28), wood_edge, 0.08)

    torus("Plan_Outer_Frame", 3.55, 0.095, center_z, gold)
    torus("Plan_Outer_Light", 3.36, 0.026, center_z, cyan)

    week_radii = [1.02, 1.45, 1.88, 2.31, 2.74, 3.17]
    for week_index, radius in enumerate(week_radii):
        torus(f"Plan_Week_Ring_{week_index + 1:02d}", radius, 0.025, center_z, metal if week_index % 2 else cyan)

    for day_index in range(7):
        angle = math.radians(90 - day_index * (360 / 7))
        end = (
            math.cos(angle) * 3.38,
            0.08,
            center_z + math.sin(angle) * 3.38,
        )
        cylinder_between(
            f"Plan_Day_Spoke_{day_index + 1:02d}",
            (0, 0.08, center_z),
            end,
            0.016,
            metal,
        )

    for week_index, radius in enumerate(week_radii):
        for day_index in range(7):
            index = week_index * 7 + day_index
            angle = math.radians(90 - day_index * (360 / 7))
            x = math.cos(angle) * radius
            z = center_z + math.sin(angle) * radius
            bpy.ops.mesh.primitive_cylinder_add(
                vertices=40,
                radius=0.155 if week_index < 5 else 0.17,
                depth=0.15,
                location=(x, -0.08, z),
                rotation=(math.pi / 2, 0, 0),
            )
            token = bpy.context.object
            token.name = f"Plan_Date_{index:02d}"
            assign(token, neutral if index % 3 else pink)
            token["calendar_index"] = index
            token["week_index"] = week_index
            token["day_index"] = day_index

    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=0.56, location=(0, -0.05, center_z))
    core = bpy.context.object
    core.name = "Plan_Goal_Core"
    assign(core, cyan)
    torus("Plan_Goal_Orbit", 0.72, 0.035, center_z, gold)

    # The selected task emerges onto this shallow paper ribbon, rather than a drawer.
    ribbon = bevelled_box("Plan_Task_Ribbon", (0, -0.72, 1.42), (5.9, 0.2, 0.78), paper, 0.12)
    ribbon.rotation_euler.x = math.radians(-7)
    bevelled_box("Plan_Task_Ribbon_Edge", (0, -0.84, 1.29), (6.1, 0.08, 0.08), gold, 0.025)
    cylinder_between("Plan_Task_Pin_Left", (-3.08, -0.73, 1.08), (-3.08, -0.73, 1.78), 0.045, pink)
    cylinder_between("Plan_Task_Pin_Right", (3.08, -0.73, 1.08), (3.08, -0.73, 1.78), 0.045, cyan)

    add_text("Plan_Title", "PLAN ORBIT", (0, -0.18, 7.72), paper)

    # Presentation lighting and camera are saved in the .blend for human inspection.
    bpy.ops.object.light_add(type="AREA", location=(0, -5.5, 7.5))
    key = bpy.context.object
    key.name = "Plan_Key_Light"
    key.data.energy = 850
    key.data.shape = "DISK"
    key.data.size = 5.5
    key.data.color = rgba(PALETTE["pink"])[:3]
    key.rotation_euler = (math.radians(58), 0, 0)

    bpy.ops.object.light_add(type="AREA", location=(-4.2, -2.4, 4.2))
    fill = bpy.context.object
    fill.name = "Plan_Cyan_Fill"
    fill.data.energy = 620
    fill.data.size = 3.0
    fill.data.color = rgba(PALETTE["cyan"])[:3]
    fill.rotation_euler = (math.radians(72), 0, math.radians(-32))

    bpy.ops.object.camera_add(location=(10.8, -15.5, 10.5))
    camera = bpy.context.object
    camera.name = "Plan_Preview_Camera"
    direction = Vector((0, 0, 3.65)) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    camera.data.lens = 58
    bpy.context.scene.camera = camera

    world = bpy.context.scene.world or bpy.data.worlds.new("Plan_World")
    bpy.context.scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = rgba("120C20")
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.22

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1200
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(BLENDER_DIR / "PlanOrbit-preview.png")

    BLENDER_DIR.mkdir(parents=True, exist_ok=True)
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_PATH))
    bpy.ops.export_scene.gltf(
        filepath=str(GLB_PATH),
        export_format="GLB",
        export_apply=True,
        export_cameras=False,
        export_lights=False,
        export_extras=True,
    )
    bpy.ops.render.render(write_still=True)
    print(f"Saved {BLEND_PATH}")
    print(f"Exported {GLB_PATH}")


if __name__ == "__main__":
    build()

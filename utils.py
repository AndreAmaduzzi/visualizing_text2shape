"""
Module containing generic utils.

Author: Riccardo Spezialetti
Mail: riccardo.spezialetti@unibo.it
"""
from pathlib import Path
from typing import List, Optional, Tuple

import bpy  # type: ignore
import numpy as np

import bmesh  # isort: skip

def remove_objects() -> None:
    """
    Remove all the objects in the scene.
    """
    for item in bpy.data.objects:
        bpy.data.objects.remove(item)


def set_render_params(
    scene: bpy.types.Scene,
    path_render: Path,
    use_transparent_bg: bool = False,
    resolution_x: int = 1920,
    resolution_y: int = 1080,
    percentage_resolution: int = 100,
) -> None:
    """Set Renderer Properties.

    Args:
        scene: the scene to render.
        path_render: the to the rendered image.
        use_transparent_bg: If True render with trasparent background. Defaults to False.
        resolution_x: the width for the image. Defaults to 1920.
        resolution_y: the height for the image. Defaults to 1080.
        percentage_resolution: the scale percentage for the resolutio of the image. Defaults to 100.
    """
    scene.render.resolution_percentage = percentage_resolution
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.filepath = str(path_render)
    scene.render.image_settings.file_format = path_render.suffix[1:].upper()
    scene.render.engine = "CYCLES"
    scene.render.use_motion_blur = False
    scene.render.film_transparent = use_transparent_bg


def set_engine_params(
    scene: bpy.types.Scene,
    num_samples: int = 4096,
    ids_cuda_devices: List[int] = [],
    use_adaptive_sampling: bool = False,
    use_denoiser: bool = True,
) -> None:
    """Set Engine properties.

    Args:
        scene: the scene to render.
        num_samples: The number of samples to render for cycles. Defaults to 4096.
        ids_cuda_devices: Ids to use for rendering, if empty use all the availabe devices. Defaults to [].
        use_adaptive_sampling: If True use adaptive sampling. Defaults to False.
        use_denoiser: If True use optix denoiser. Defaults to True.

    Raises:
        ValueError: if adaptive sampling is False and the number of samples is zero.
    """

    if not use_adaptive_sampling:
        if num_samples == 0:
            raise ValueError("Use adaptive sampling is false but num samples is zero.")

    scene.view_layers[0].cycles.use_denoising = True

    scene.cycles.use_adaptive_sampling = use_adaptive_sampling
    if not use_adaptive_sampling:
        scene.cycles.samples = num_samples

    cuda_devices = []
    bpy.context.preferences.addons["cycles"].preferences.get_devices()
    for dev in bpy.context.preferences.addons["cycles"].preferences.devices:
        name = dev["name"]
        dev["use"] = 0
        if "NVIDIA" in name:
            if name not in cuda_devices:
                cuda_devices.append(name)

    if len(ids_cuda_devices):
        bpy.context.scene.cycles.device = "GPU"
        bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA"

        for id_dev in ids_cuda_devices:
            for dev in bpy.context.preferences.addons["cycles"].preferences.devices:
                if cuda_devices[id_dev] == dev["name"]:
                    dev["use"] = 1
    else:
        for dev in bpy.context.preferences.addons["cycles"].preferences.devices:
            dev["use"] = 1

    devices_enable = []
    for dev in bpy.context.preferences.addons["cycles"].preferences.devices:
        if dev["use"]:
            devices_enable.append(dev["name"])

    if use_denoiser:
        scene.cycles.use_denoising = True
        scene.cycles.denoiser = "OPTIX"

    print(f"Devices for rendering: {devices_enable}")


def add_track_to_constraint(
    camera_object: bpy.types.Object, track_to_target_object: bpy.types.Object
) -> None:
    constraint = camera_object.constraints.new(type="TRACK_TO")
    constraint.target = track_to_target_object
    constraint.track_axis = "TRACK_NEGATIVE_Z"
    constraint.up_axis = "UP_Y"


def create_camera(location: Tuple[float, float, float]) -> bpy.types.Object:
    bpy.ops.object.camera_add(location=location)
    cam = bpy.data.objects["Camera"]

    return cam


def set_camera_params(
    camera: bpy.types.Camera, focus_target_object: bpy.types.Object, lens: float = 85.0
) -> None:

    camera.sensor_fit = "HORIZONTAL"
    camera.lens = lens
    camera.dof.use_dof = True
    camera.dof.focus_object = focus_target_object


def create_light(
    location: Tuple[float, float, float] = (0.0, 0.0, 5.0),
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    energy: float = 4.0,
    name: Optional[str] = None,
) -> bpy.types.Object:
    # Create a light
    light_data = bpy.data.lights.new("light", type="SUN")
    light_data.use_shadow = True
    light_data.specular_factor = 1.0
    light_data.energy = energy
    light_data.use_shadow = True

    light = bpy.data.objects.new("light", light_data)
    light.location = location
    light.rotation_euler = rotation

    return light


def create_light_area_vox(
    location: Tuple[float, float, float] = (0.0, 0.0, 5.0),
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    energy: float = 50.0,
    name: Optional[str] = None,
) -> bpy.types.Object:
    # Create a light
    light_data = bpy.data.lights.new("light", type="AREA")
    light_data.energy = energy
    light_data.shape = "DISK"
    light_data.size = 1.50

    light = bpy.data.objects.new(name, light_data)
    light.location = location
    light.rotation_euler = rotation

    return light


def create_light_area(
    location: Tuple[float, float, float] = (0.0, 0.0, 5.0),
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    energy: float = 50.0,
    name: Optional[str] = None,
) -> bpy.types.Object:
    # Create a light
    light_data = bpy.data.lights.new("light", type="AREA")
    light_data.energy = energy

    light = bpy.data.objects.new(name, light_data)
    light.location = location
    light.rotation_euler = rotation

    return light


def create_plane(
    location: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    size: float = 2.0,
    name: Optional[str] = None,
) -> bpy.types.Object:

    bpy.ops.mesh.primitive_plane_add(size=size, location=location, rotation=rotation)
    current_object = bpy.context.object

    if name is not None:
        current_object.name = name

    return current_object


def create_new_image_material(name="asd", alpha=1.0):
    """Create a new material.
    Args:
        name: name of material
        fname: path to image to load
    Returns:
        The new material.
    """

    nodescale = 300

    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf.location = 2 * nodescale, 0
    # bsdf.inputs[0].default_value = color
    bsdf.inputs["Alpha"].default_value = alpha
    bsdf.inputs["Specular"].default_value = 0.0

    node_output = nodes.new(type="ShaderNodeOutputMaterial")
    node_output.location = 3 * nodescale, 0

    links = mat.node_tree.links
    link = links.new(bsdf.outputs[0], node_output.inputs[0])
    return mat


def create_material(
    name: str = "Material", use_nodes: bool = False, make_node_tree_empty: bool = False
) -> bpy.types.Material:
    """
    https://docs.blender.org/api/current/bpy.types.BlendDataMaterials.html
    https://docs.blender.org/api/current/bpy.types.Material.html
    """

    # TODO: Check whether the name is already used or not
    material = bpy.data.materials.new(name)
    material.use_nodes = use_nodes

    if use_nodes and make_node_tree_empty:
        clean_nodes(material.node_tree.nodes)

    return material


def clean_nodes(nodes: bpy.types.Nodes) -> None:
    for node in nodes:
        nodes.remove(node)


def set_principled_node_as_rough_blue(principled_node: bpy.types.Node) -> None:
    set_principled_node(
        principled_node=principled_node,
        metallic=0.5,
        specular=1.0,
        roughness=1.0,
    )


def set_principled_node_as_glass(principled_node: bpy.types.Node) -> None:
    set_principled_node(
        principled_node=principled_node,
        base_color=(1.0, 0, 0, 1.0),
        metallic=0.0,
        specular=0.5,
        roughness=0.0,
        clearcoat=0.5,
        clearcoat_roughness=0.030,
        ior=1.45,
        transmission=0.98,
    )


def set_principled_node(
    principled_node: bpy.types.Node,
    base_color: Tuple[float, float, float, float] = (1.0, 0.0, 0.0, 1.0),
    subsurface: float = 0.0,
    subsurface_color: Tuple[float, float, float, float] = (0.8, 0.8, 0.8, 1.0),
    subsurface_radius: Tuple[float, float, float] = (1.0, 0.2, 0.1),
    metallic: float = 0.0,
    specular: float = 0.5,
    specular_tint: float = 0.0,
    roughness: float = 0.5,
    anisotropic: float = 0.0,
    anisotropic_rotation: float = 0.0,
    sheen: float = 0.0,
    sheen_tint: float = 0.5,
    clearcoat: float = 0.0,
    clearcoat_roughness: float = 0.03,
    ior: float = 1.45,
    transmission: float = 0.0,
    transmission_roughness: float = 0.0,
) -> None:
    principled_node.inputs["Base Color"].default_value = base_color
    principled_node.inputs["Subsurface"].default_value = subsurface
    principled_node.inputs["Subsurface Color"].default_value = subsurface_color
    principled_node.inputs["Subsurface Radius"].default_value = subsurface_radius
    principled_node.inputs["Metallic"].default_value = metallic
    principled_node.inputs["Specular"].default_value = specular
    principled_node.inputs["Specular Tint"].default_value = specular_tint
    principled_node.inputs["Roughness"].default_value = roughness
    principled_node.inputs["Anisotropic"].default_value = anisotropic
    principled_node.inputs["Anisotropic Rotation"].default_value = anisotropic_rotation
    principled_node.inputs["Sheen"].default_value = sheen
    principled_node.inputs["Sheen Tint"].default_value = sheen_tint
    principled_node.inputs["Clearcoat"].default_value = clearcoat
    principled_node.inputs["Clearcoat Roughness"].default_value = clearcoat_roughness
    principled_node.inputs["IOR"].default_value = ior
    principled_node.inputs["Transmission"].default_value = transmission
    principled_node.inputs["Transmission Roughness"].default_value = transmission_roughness


def set_principled_node_as_gold(principled_node: bpy.types.Node) -> None:
    set_principled_node(
        principled_node=principled_node,
        base_color=(1.00, 0.71, 0.22, 1.0),
        metallic=1.0,
        specular=0.5,
        roughness=0.1,
    )


def load_mesh(path_mesh: Path) -> bpy.types.Object:

    bpy.ops.import_mesh.ply(filepath=str(path_mesh))
    current_object = bpy.context.object
    current_object.name = "object"
    mat = create_material("Material_Right", use_nodes=True, make_node_tree_empty=True)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    output_node = nodes.new(type="ShaderNodeOutputMaterial")
    principled_node = nodes.new(type="ShaderNodeBsdfPrincipled")
    set_principled_node(principled_node, base_color=(0.5, 0.5, 0.5, 1))
    links.new(principled_node.outputs["BSDF"], output_node.inputs["Surface"])
    current_object.data.materials.append(mat)

    bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
    focus_target = current_object

    return focus_target


def pcd_to_sphere(
    pcd: np.ndarray, radius, offset=(0.0, 0.0, 0.0), scale: float = 1.0, subdivision: int = 2
) -> bpy.types.Object:

    remove_objects()
    mesh = bmesh.new()

    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivision)
    sphere_base_mesh = bpy.context.scene.objects["Icosphere"].data

    for face in sphere_base_mesh.polygons:
        face.use_smooth = True

    step = 0

    for p in pcd:
        location = (p[0] * scale + offset[0], p[1] * scale + offset[1], p[2] * scale + offset[2])

        m = sphere_base_mesh.copy()

        for vertex in m.vertices:
            vertex.co[0] = vertex.co[0] * radius + location[0]
            vertex.co[1] = vertex.co[1] * radius + location[1]
            vertex.co[2] = vertex.co[2] * radius + location[2]
            step += 1

        if pcd.shape[1] > 3:
            m.vertex_colors.new(name="Col")
            for vertex_color in m.vertex_colors["Col"].data:
                vertex_color.color = (p[3], p[4], p[5], 1.0)

        mesh.from_mesh(m)
        del m

    mesh_spheres = bpy.data.meshes.new("Mesh")
    mesh.to_mesh(mesh_spheres)

    obj = bpy.data.objects.new("BRC_Point_Cloud", mesh_spheres)
    obj.name = "object"
    bpy.context.collection.objects.link(obj)

    bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
    focus_target = obj

    bpy.data.objects.remove(bpy.context.scene.objects["Icosphere"])

    return focus_target


def voxels_to_cube(
    voxels: np.ndarray, radius: float, offset=(0.0, 0.0, 0.0), scale: float = 1.0
) -> bpy.types.Object:

    points = np.where(voxels)
    locations = np.zeros((points[0].shape[0], 3), dtype=float)
    locations[:, 0] = (points[0][:] + 0.5) / voxels.shape[0]
    locations[:, 1] = (points[1][:] + 0.5) / voxels.shape[1]
    locations[:, 2] = (points[2][:] + 0.5) / voxels.shape[2]
    locations[:, 0] -= 0.5
    locations[:, 1] -= 0.5
    locations[:, 2] -= 0.5

    locations[:, 0] = locations[:, 0] * scale + offset[0]
    locations[:, 1] = locations[:, 1] * scale + offset[1]
    locations[:, 2] = locations[:, 2] * scale + offset[2]

    mesh = bmesh.new()

    bpy.ops.mesh.primitive_cube_add()
    cube_base_mesh = bpy.context.scene.objects["Cube"].data

    for i in range(locations.shape[0]):
        m = cube_base_mesh.copy()
        for vertex in m.vertices:
            vertex.co[0] = vertex.co[0] * radius + locations[i, 0]
            vertex.co[1] = vertex.co[1] * radius + locations[i, 1]
            vertex.co[2] = vertex.co[2] * radius + locations[i, 2]

        mesh.from_mesh(m)

    bpy.data.objects.remove(bpy.context.scene.objects["Cube"])

    mesh_cubes = bpy.data.meshes.new("Mesh")
    mesh.to_mesh(mesh_cubes)

    obj = bpy.data.objects.new("BRC_Occupancy", mesh_cubes)
    obj.name = "object"

    bpy.context.collection.objects.link(obj)
    focus_target = obj
    return focus_target

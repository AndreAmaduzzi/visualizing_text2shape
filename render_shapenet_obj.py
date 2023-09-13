import argparse, sys, os, math, re
import bpy
from glob import glob

class_to_class_id = {
    'Table': '04379243',
    'Jar': '03593526',
    'Skateboard': '04225987',
    'Car': '02958343',
    'Bottle': '02876657',
    'Tower': '04460130',
    'Chair': '03001627',
    'Bookshelf': '02871439',
    'Camera': '02942699',
    'Airplane': '02691156',
    'Laptop': '03642806',
    'Basket': '02801938',
    'Sofa': '04256520',
    'Knife': '03624134',
    'Can': '02946921',
    'Rifle': '04090263',
    'Train': '04468005',
    'Pillow': '03938244',
    'Lamp': '03636649',
    'Trash bin': '02747177',
    'Mailbox': '03710193',
    'Watercraft': '04530566',
    'Motorbike': '03790512',
    'Dishwasher': '03207941',
    'Bench': '02828884',
    'Pistol': '03948459',
    'Rocket': '04099429',
    'Loudspeaker': '03691459',
    'File cabinet': '03337140',
    'Bag': '02773838',
    'Cabinet': '02933112',
    'Bed': '02818832',
    'Birdhouse': '02843684',
    'Display': '03211117',
    'Piano': '03928116',
    'Earphone': '03261776',
    'Telephone': '04401088',
    'Stove': '04330267',
    'Microphone': '03759954',
    'Bus': '02924116',
    'Mug': '03797390',
    'Remote': '04074963',
    'Bathtub': '02808440',
    'Bowl': '02880940',
    'Keyboard': '03085013',
    'Guitar': '03467517',
    'Washer': '04554684',
    'Bicycle': '02834778',
    'Faucet': '03325088',
    'Printer': '04004475',
    'Cap': '02954340'
}

def get_obj_paths(root_directory):
    obj_paths = []
    for dirpath, _, filenames in os.walk(root_directory):
        for filename in filenames:
            if filename.endswith(".obj"):
                obj_paths.append(os.path.join(dirpath, filename))
    return obj_paths

def parse_args():
    parser = argparse.ArgumentParser(description='Renders given obj file by rotation a camera around it.')
    parser.add_argument('--views', type=int, default=20,
                        help='number of views to be rendered')
    parser.add_argument('--data_root', type=str, default='/media/data2/aamaduzzi/datasets/ShapeNetCore.v2',
                        help='The path to the dataset folder')
    parser.add_argument('--category', type=str, default='chair',
                        help='The name of the category of shapes to render.')
    parser.add_argument('--obj_path', type=str, default=None,
                        help='The path of the single .obj file to render')    
    parser.add_argument('--output_folder', type=str, default='./output_renders',
                        help='The path the output will be dumped to.')
    parser.add_argument('--scale', type=float, default=1,
                        help='Scaling factor applied to model. Depends on size of mesh.')
    parser.add_argument('--remove_doubles', type=bool, default=True,
                        help='Remove double vertices to improve mesh quality.')
    parser.add_argument('--edge_split', type=bool, default=True,
                        help='Adds edge split filter.')
    parser.add_argument('--depth_scale', type=float, default=1.4,
                        help='Scaling that is applied to depth. Depends on size of mesh. Try out various values until you get a good result. Ignored if format is OPEN_EXR.')
    parser.add_argument('--color_depth', type=str, default='8',
                        help='Number of bit per channel used for output. Either 8 or 16.')
    parser.add_argument('--format', type=str, default='PNG',
                        help='Format of files generated. Either PNG or OPEN_EXR')
    parser.add_argument('--resolution', type=int, default=600,
                        help='Resolution of the images.')
    parser.add_argument('--engine', type=str, default='CYCLES',
                        help='Blender internal engine for rendering. E.g. CYCLES, BLENDER_EEVEE, ...')

    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    # Set up rendering
    context = bpy.context
    scene = bpy.context.scene
    render = bpy.context.scene.render

    render.engine = args.engine
    render.image_settings.color_mode = 'RGBA' # ('RGB', 'RGBA', ...)
    render.image_settings.color_depth = args.color_depth # ('8', '16')
    render.image_settings.file_format = args.format # ('PNG', 'OPEN_EXR', 'JPEG, ...)
    render.resolution_x = args.resolution
    render.resolution_y = args.resolution
    render.resolution_percentage = 100
    render.film_transparent = True

    scene.use_nodes = True
    scene.view_layers["View Layer"].use_pass_normal = True
    scene.view_layers["View Layer"].use_pass_diffuse_color = True
    scene.view_layers["View Layer"].use_pass_object_index = True

    nodes = bpy.context.scene.node_tree.nodes
    links = bpy.context.scene.node_tree.links

    # Clear default nodes
    for n in nodes:
        nodes.remove(n)

    # Create input render layer node
    render_layers = nodes.new('CompositorNodeRLayers')

    # Create depth output nodes
    depth_file_output = nodes.new(type="CompositorNodeOutputFile")
    depth_file_output.label = 'Depth Output'
    depth_file_output.base_path = ''
    depth_file_output.file_slots[0].use_node_format = True
    depth_file_output.format.file_format = args.format
    depth_file_output.format.color_depth = args.color_depth
    if args.format == 'OPEN_EXR':
        links.new(render_layers.outputs['Depth'], depth_file_output.inputs[0])
    else:
        depth_file_output.format.color_mode = "BW"

        # Remap as other types can not represent the full range of depth.
        map = nodes.new(type="CompositorNodeMapValue")
        # Size is chosen kind of arbitrarily, try out until you're satisfied with resulting depth map.
        map.offset = [-0.7]
        map.size = [args.depth_scale]
        map.use_min = True
        map.min = [0]

        links.new(render_layers.outputs['Depth'], map.inputs[0])
        links.new(map.outputs[0], depth_file_output.inputs[0])

    # Create normal output nodes
    scale_node = nodes.new(type="CompositorNodeMixRGB")
    scale_node.blend_type = 'MULTIPLY'
    # scale_node.use_alpha = True
    scale_node.inputs[2].default_value = (0.5, 0.5, 0.5, 1)
    links.new(render_layers.outputs['Normal'], scale_node.inputs[1])

    bias_node = nodes.new(type="CompositorNodeMixRGB")
    bias_node.blend_type = 'ADD'
    # bias_node.use_alpha = True
    bias_node.inputs[2].default_value = (0.5, 0.5, 0.5, 0)
    links.new(scale_node.outputs[0], bias_node.inputs[1])

    normal_file_output = nodes.new(type="CompositorNodeOutputFile")
    normal_file_output.label = 'Normal Output'
    normal_file_output.base_path = ''
    normal_file_output.file_slots[0].use_node_format = True
    normal_file_output.format.file_format = args.format
    links.new(bias_node.outputs[0], normal_file_output.inputs[0])

    # Create albedo output nodes
    alpha_albedo = nodes.new(type="CompositorNodeSetAlpha")
    links.new(render_layers.outputs['DiffCol'], alpha_albedo.inputs['Image'])
    links.new(render_layers.outputs['Alpha'], alpha_albedo.inputs['Alpha'])

    albedo_file_output = nodes.new(type="CompositorNodeOutputFile")
    albedo_file_output.label = 'Albedo Output'
    albedo_file_output.base_path = ''
    albedo_file_output.file_slots[0].use_node_format = True
    albedo_file_output.format.file_format = args.format
    albedo_file_output.format.color_mode = 'RGBA'
    albedo_file_output.format.color_depth = args.color_depth
    links.new(alpha_albedo.outputs['Image'], albedo_file_output.inputs[0])

    # Create id map output nodes
    id_file_output = nodes.new(type="CompositorNodeOutputFile")
    id_file_output.label = 'ID Output'
    id_file_output.base_path = ''
    id_file_output.file_slots[0].use_node_format = True
    id_file_output.format.file_format = args.format
    id_file_output.format.color_depth = args.color_depth

    if args.format == 'OPEN_EXR':
        links.new(render_layers.outputs['IndexOB'], id_file_output.inputs[0])
    else:
        id_file_output.format.color_mode = 'BW'

        divide_node = nodes.new(type='CompositorNodeMath')
        divide_node.operation = 'DIVIDE'
        divide_node.use_clamp = False
        divide_node.inputs[1].default_value = 2**int(args.color_depth)

        links.new(render_layers.outputs['IndexOB'], divide_node.inputs[0])
        links.new(divide_node.outputs[0], id_file_output.inputs[0])

    # Delete default cube
    context.active_object.select_set(True)
    bpy.ops.object.delete()

    if args.obj_path is not None:
        paths = [args.obj_path]
    else:
        # Iterate over all the paths of the models
        root_directory = os.path.join(args.data_root, class_to_class_id[args.category])
        paths = get_obj_paths(root_directory) 
    
    print('paths: ', paths)
    count = 0
    for path in paths:
        count +=1
        # Import textured mesh
        bpy.ops.object.select_all(action='DESELECT')

        bpy.ops.import_scene.obj(filepath=path)

        obj = bpy.context.selected_objects[0]

        context.view_layer.objects.active = obj

        # Possibly disable specular shading
        for slot in obj.material_slots:
            node = slot.material.node_tree.nodes['Principled BSDF']
            node.inputs['Specular'].default_value = 0.05

        if args.scale != 1:
            bpy.ops.transform.resize(value=(args.scale,args.scale,args.scale))
            bpy.ops.object.transform_apply(scale=True)
        if args.remove_doubles:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.remove_doubles()
            bpy.ops.object.mode_set(mode='OBJECT')
        if args.edge_split:
            bpy.ops.object.modifier_add(type='EDGE_SPLIT')
            context.object.modifiers["EdgeSplit"].split_angle = 1.32645
            bpy.ops.object.modifier_apply(modifier="EdgeSplit")

        # Set objekt IDs
        obj.pass_index = 1

        # Make light just directional, disable shadows.
        light = bpy.data.lights['Light']
        light.type = 'SUN'
        light.use_shadow = False
        # Possibly disable specular shading:
        light.specular_factor = 1.0
        light.energy = 10.0

        # Add another light source so stuff facing away from light is not completely dark
        bpy.ops.object.light_add(type='SUN')
        light2 = bpy.data.lights['Sun']
        light2.use_shadow = False
        light2.specular_factor = 1.0
        light2.energy = 0.015
        bpy.data.objects['Sun'].rotation_euler = bpy.data.objects['Light'].rotation_euler
        bpy.data.objects['Sun'].rotation_euler[0] += 180

        # Place camera
        cam = scene.objects['Camera']
        cam.location = (0, 1, 0.6)
        cam.data.lens = 35
        cam.data.sensor_width = 32

        cam_constraint = cam.constraints.new(type='TRACK_TO')
        cam_constraint.track_axis = 'TRACK_NEGATIVE_Z'
        cam_constraint.up_axis = 'UP_Y'

        cam_empty = bpy.data.objects.new("Empty", None)
        cam_empty.location = (0, 0, 0)
        cam.parent = cam_empty

        scene.collection.objects.link(cam_empty)
        context.view_layer.objects.active = cam_empty
        cam_constraint.target = cam_empty

        stepsize = 360.0 / args.views
        rotation_mode = 'XYZ'

        if args.obj_path is not None:
            model_identifier = os.path.splitext(os.path.basename(path))[0]
            fp = os.path.join(os.path.abspath(args.output_folder), model_identifier)
        else:
            model_identifier = os.path.normpath(path).split(os.sep)[-3]
            class_identifier = os.path.normpath(path).split(os.sep)[-4]
            fp = os.path.join(os.path.abspath(args.output_folder), class_identifier, model_identifier)

        print('model identifier: ', model_identifier)
        for i in range(0, args.views):
            print("Rotation {}, {}".format((stepsize * i), math.radians(stepsize * i)))

            render_file_path = os.path.join(fp, model_identifier + '_r_{0:03d}'.format(int(i * stepsize)))

            scene.render.filepath = render_file_path
            print('render file path: ', render_file_path)
            #depth_file_output.file_slots[0].path = render_file_path + "_depth"
            #normal_file_output.file_slots[0].path = render_file_path + "_normal"
            #albedo_file_output.file_slots[0].path = render_file_path + "_albedo"
            #id_file_output.file_slots[0].path = render_file_path + "_id"

            print('rendering...')
            bpy.ops.render.render(write_still=True)  # render still
            print('save')
            bpy.ops.wm.save_mainfile()

            cam_empty.rotation_euler[2] += math.radians(stepsize)
        
        # Delete the current mesh from the scene
        for obj in bpy.context.scene.objects:
            # If the object type is 'MESH', it is likely the imported mesh
            if obj.type == 'MESH':
                mesh_name = obj.name
                break
        bpy.data.objects[mesh_name].select_set(True)
        bpy.ops.object.delete()
        
        # For debugging the workflow
        #bpy.ops.wm.save_as_mainfile(filepath='debug.blend')
        if count == 2:
            break

if __name__ == "__main__":
    main()
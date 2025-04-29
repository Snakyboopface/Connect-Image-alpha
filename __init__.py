bl_info = {
    'name': 'Connect Alpha',
    'author': 'Snakyboopface',
    'version': (0, 0, 6),
    'blender': (4, 3, 2),
    'location': '3D Viewport > Sidebar > Connect Alpha',
    'description': 'Connect image alpha',
    'category': 'Node',
}

import bpy

# Functions
def set_name_prio(sep_alph: str, incl_alph: str, bsdf: str)-> list:
    '''
    Converts name priority str to list

    prio_list[0] = prioritises connecting nodes with these labels first. Will connect the "color" output to the "alpha" input of the BSDF shader
    prio_list[1] = prioritises connecting these nodes second. will connect the "alpha" output of these nodes to the "alpha" input of the BSDF shader
    prio_list[2] = prioritises connecting the image node(s) to BSDF nodes with these labels

    :param: sep_alph
    if sep_alpha is empty then it will be set to 'alpha' if incl_alph doesn't have 'alpha' 

    :param: incl_alph
    if incl_alpha is empty then it will be set to 'base color, base colour, color, colour'

    :param: bsdf
    if bsdf is empty then it will be set to 'main'

    :return: prio_list
    '''

    prio_list = []

    # If any parts are empty or just space then set them to these defults
    if sep_alph.strip() == '' and 'alpha' not in incl_alph.lower():
        sep_alph = 'alpha'

    if incl_alph.strip() == '':
        incl_alph = 'base color, base colour, color, colour'

    """if bsdf.strip() == '':
        bsdf = 'main'"""

    # Turn strings into lists
    sep_alph = list(map(str, sep_alph.lower().strip().split(',')))
    incl_alph = list(map(str, incl_alph.lower().strip().split(',')))
    bsdf = list(map(str, bsdf.lower().strip().split(',')))

    # Appends the lists into the full list
    prio_list.append(sep_alph)
    prio_list.append(incl_alph)
    prio_list.append(bsdf)

    return prio_list

def connect_alpha(coll, name_prio: list):
        '''
        Connects image alpha output to principled BSDF alpha input
        :param: collection
        :param: name_prio
        '''

        # What to connect from the image texture to the shader
        image_out = 'Alpha'

        for collection in bpy.data.collections:
            if collection.name == coll.name:
                for obj in collection.all_objects:
                    mat = obj.active_material

                    if mat is not None:
                        # Ensure the material has a node tree
                        if mat.use_nodes:
                            nodes = mat.node_tree.nodes
                            links = mat.node_tree.links
                            
                            # Locate the Image Texture and Principled BSDF nodes
                            image_texture_node = None
                            principled_bsdf_node = None

                            for node in nodes:
                                if node.type == 'TEX_IMAGE' and node.image is not None:
                                    image_texture_node = node
                                    # Checks if the image node is in the priority list
                                    if node.label.lower() in name_prio[0]:
                                        image_out = 'Color'
                                        break

                                    elif node.label.lower() in name_prio[1]:
                                        break
                                        
                            for node in nodes:
                                if node.type == 'BSDF_PRINCIPLED':
                                    principled_bsdf_node = node
                                    # Checks if the BSDF node is in the priority list
                                    if node.label.lower() in name_prio[2]:
                                        break
                                    
                            # Ensure both nodes exist
                            if image_texture_node and principled_bsdf_node:
                                # Check if Alpha is not already connected
                                
                                already_connected = False
                                for link in links:
                                    if link.to_socket == principled_bsdf_node.inputs['Alpha']:
                                        already_connected = True
                                        break
                                
                                if not already_connected:
                                    # Create the link from Alpha to BSDF Alpha
                                    links.new(image_texture_node.outputs[image_out], principled_bsdf_node.inputs['Alpha'])


# Properties
class Props(bpy.types.PropertyGroup):
    '''Menu of collections'''

    coll_list : bpy.props.PointerProperty(
        name= 'Collections', 
        description= 'Select a collection',
        type=bpy.types.Collection
        )

    sep_alph_prio : bpy.props.StringProperty(
        name= 'Alpha image name',
        description= 'Prioritise connecting image nodes with these labels.' \
        '\nWill connect the "Colour" output of the image to the "Alpha" of the BSDF' \
        '\nSeperate by comma ","'
        )
    
    incl_alph_prio : bpy.props.StringProperty(
        name= 'Image name',
        description= 'Prioritise connecting image nodes with these labels.' \
        '\nWill connect the "Alpha" output of the image to the "Alpha" of the BSDF' \
        '\nSeperate by comma ","'
        )
    
    bsdf_prio :  bpy.props.StringProperty(
        name= 'BSDF name',
        description= 'Prioritise connecting to BSDF nodes with these labels.' \
        '\nSeperate by comma ","'
        )
    
# Operators
class NODE_OT_connect_alpha(bpy.types.Operator):
    '''
    Connects the alpha of image textures in selected collection to the principled bsdf node
    '''
    bl_idname = 'node.connect_alpha'
    bl_label = 'Set Collection'

    # Connect alpha function
    def execute(self, context):
        scene = bpy.context.scene
        propstool = scene.props_tool
        
        prio_name = set_name_prio(propstool.sep_alph_prio, propstool.incl_alph_prio, propstool.bsdf_prio)

        connect_alpha(propstool.coll_list, prio_name)
    
        return {"FINISHED"}


# Panel
class VIEW3D_PT_connect_alpha(bpy.types.Panel):
    '''ui panel'''
    # Where to add panel in the UI
    bl_space_type = 'VIEW_3D' # 3D viewport area
    bl_region_type = 'UI' # Sidebar region

    # Add labels
    bl_category = 'Connect alpha'
    bl_label = 'Connect alpha' # found at the top of the panel

    def draw(self, context):
        '''Define the layout of the panel'''
        layout = self.layout
        scene = context.scene
        propstool = scene.props_tool
        row = layout.row()

        layout.label(text= 'Priority labels:')

        layout.prop(propstool, 'sep_alph_prio')
        layout.prop(propstool, 'incl_alph_prio')
        layout.prop(propstool, 'bsdf_prio')

        layout.separator()

        layout.prop(propstool, 'coll_list')

        # Adds a seperator
        layout.separator()

        row = layout.row()
        row.operator('node.connect_alpha', text= 'Connect Alpha')


# Registering/Unregistering
CLASSES = [Props, NODE_OT_connect_alpha, VIEW3D_PT_connect_alpha]

# Register the panel with blender
def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)

        bpy.types.Scene.props_tool = bpy.props.PointerProperty(type= Props)


def unregister():
    for cls in CLASSES:
        bpy.utils.unregister_class(cls)

        del bpy.types.Scene.props_tool


if __name__ == '__main__':
    register()
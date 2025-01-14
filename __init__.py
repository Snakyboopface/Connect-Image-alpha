bl_info = {
    'name': 'Connect Alpha',
    'author': 'Snakyboopface',
    'version': (0, 0, 4),
    'blender': (4, 3, 2),
    'location': '3D Viewport > Sidebar > Connect Alpha',
    'description': 'Connect image alpha',
    'category': 'Node',
}

import bpy

def connect_alpha(coll):
        '''
        Connects image alpha to principled BSDF
        :param: collection
        '''

        # Prioritise connecting ALPHA of ndoes with labels in node_priority
        node_priority = ['alpha', ['base color', 'base colour', 'color', 'colour']]

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
                                    if node.label.lower() == node_priority[0]:
                                        image_out = 'Color'
                                        break

                                    elif node.label.lower() in node_priority[1]:
                                        break
                                    
                                if node.type == 'BSDF_PRINCIPLED':
                                    principled_bsdf_node = node
                            
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


class CollectionsMenu(bpy.types.PropertyGroup):
    '''Menu of collections'''

    coll_list : bpy.props.PointerProperty(
        name= 'Collections', 
        description= 'Select a collection',
        type=bpy.types.Collection
        )
    
class NODE_OT_connect_alpha(bpy.types.Operator):
    '''
    Connects the alpha of image textures in selected collection to the principled bsdf node
    '''
    bl_idname = 'node.connect_alpha'
    bl_label = 'Set Collection'

    # Connect alpha function
    def execute(self, context):
        scene = bpy.context.scene
        listtool = scene.list_tool
        connect_alpha(listtool.coll_list)
    
        return {"FINISHED"}

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
        listtool = scene.list_tool
        row = layout.row()

        layout.prop(listtool, 'coll_list')

        # Adds a seperator
        layout.separator()

        row = layout.row()
        row.operator('node.connect_alpha', text= 'Connect Alpha')


CLASSES = [CollectionsMenu, NODE_OT_connect_alpha, VIEW3D_PT_connect_alpha]

# Register the panel with blender
def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)

        bpy.types.Scene.list_tool = bpy.props.PointerProperty(type= CollectionsMenu)


def unregister():
    for cls in CLASSES:
        bpy.utils.unregister_class(cls)

        del bpy.types.Scene.list_tool


if __name__ == '__main__':
    register()

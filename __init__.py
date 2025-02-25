bl_info = {
    "name": "Batch Material Helper",
    "author": "maylog",
    "version": (1, 6),
    "blender": (4, 4, 0),
    "location": "View3D > Sidebar > Batch Material",
    "description": "After batch changing your imported FBX or XPS, thousands of shaders in the scene display errors.",
    "category": "Material",
}

import bpy
from bpy.types import Operator, Panel
from bpy.props import FloatProperty, FloatVectorProperty, BoolProperty, EnumProperty

class MATERIAL_OT_batch_material_helper(Operator):
    """Batch set material and BSDF properties for selected objects"""
    bl_idname = "material.batch_material_helper"
    bl_label = "Batch Material Helper"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        # BSDF 属性
        base_color = scene.batch_base_color
        metallic_value = scene.batch_metallic_value
        roughness_value = scene.batch_roughness_value
        ior_value = scene.batch_ior_value
        alpha_value = scene.batch_alpha_value
        ior_level_value = scene.batch_ior_level_value
        # 材质设置
        render_method = scene.batch_render_method
        displacement_method = scene.batch_displacement_method
        backface_culling = scene.batch_backface_culling
        backface_culling_shadow = scene.batch_backface_culling_shadow
        backface_culling_lightprobe = scene.batch_backface_culling_lightprobe
        transparent_shadow = scene.batch_transparent_shadow  # 光线追踪透射
        # 视图显示
        diffuse_color = scene.batch_diffuse_color
        display_metallic = scene.batch_display_metallic
        display_roughness = scene.batch_display_roughness

        selected_objects = context.selected_objects
        
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected!")
            return {'CANCELLED'}

        applied_properties = []
        for obj in selected_objects:
            if obj.type == 'MESH' and obj.data.materials:
                for mat_slot in obj.material_slots:
                    material = mat_slot.material
                    if material:
                        # 材质设置（独立于 BSDF）
                        if scene.use_render_method:
                            material.surface_render_method = render_method
                            applied_properties.append(f"Render Method={render_method}")
                        if scene.use_displacement_method:
                            material.displacement_method = displacement_method
                            applied_properties.append(f"Displacement Method={displacement_method}")
                        if scene.use_backface_culling:
                            material.use_backface_culling = backface_culling
                            applied_properties.append(f"Backface Culling (Camera)={backface_culling}")
                        if scene.use_backface_culling_shadow:
                            material.use_backface_culling_shadow = backface_culling_shadow
                            applied_properties.append(f"Backface Culling (Shadow)={backface_culling_shadow}")
                        if scene.use_backface_culling_lightprobe:
                            material.use_backface_culling_lightprobe_volume = backface_culling_lightprobe
                            applied_properties.append(f"Backface Culling (Lightprobe)={backface_culling_lightprobe}")
                        if scene.use_transparent_shadow:
                            material.use_transparent_shadow = transparent_shadow
                            applied_properties.append(f"Raytrace Transmission={transparent_shadow}")
                        # 视图显示
                        if scene.use_diffuse_color:
                            material.diffuse_color = diffuse_color
                            applied_properties.append(f"Diffuse Color={diffuse_color[:3]}")
                        if scene.use_display_metallic:
                            material.metallic = display_metallic
                            applied_properties.append(f"Display Metallic={display_metallic}")
                        if scene.use_display_roughness:
                            material.roughness = display_roughness
                            applied_properties.append(f"Display Roughness={display_roughness}")
                        # BSDF 属性
                        if material.use_nodes:
                            node_tree = material.node_tree
                            principled_node = next((node for node in node_tree.nodes if node.type == 'BSDF_PRINCIPLED'), None)
                            if principled_node:
                                if scene.use_base_color:
                                    principled_node.inputs['Base Color'].default_value = base_color
                                    applied_properties.append(f"Base Color={base_color[:3]}")
                                if scene.use_metallic:
                                    principled_node.inputs['Metallic'].default_value = metallic_value
                                    applied_properties.append(f"Metallic={metallic_value}")
                                if scene.use_roughness:
                                    principled_node.inputs['Roughness'].default_value = roughness_value
                                    applied_properties.append(f"Roughness={roughness_value}")
                                if scene.use_ior:
                                    principled_node.inputs['IOR'].default_value = ior_value
                                    applied_properties.append(f"IOR={ior_value}")
                                if scene.use_alpha:
                                    principled_node.inputs['Alpha'].default_value = alpha_value
                                    applied_properties.append(f"Alpha={alpha_value}")
                                if scene.use_ior_level:
                                    try:
                                        if 'IOR Level' in principled_node.inputs:
                                            principled_node.inputs['IOR Level'].default_value = ior_level_value
                                        else:
                                            principled_node.inputs[13].default_value = ior_level_value
                                        applied_properties.append(f"IOR Level={ior_level_value}")
                                    except (KeyError, IndexError):
                                        self.report({'WARNING'}, "IOR Level input not found in some materials!")
        
        if applied_properties:
            self.report({'INFO'}, f"Applied to selected objects: {', '.join(applied_properties)}")
        else:
            self.report({'WARNING'}, "No properties selected to apply!")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class VIEW3D_PT_batch_material_helper(Panel):
    """Panel to batch adjust material and BSDF properties for selected objects"""
    bl_label = "Batch Material Helper"
    bl_idname = "VIEW3D_PT_batch_material_helper"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Batch Material"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.label(text="click on the checkbox that needs to be modified.")
        col = layout.column(align=True)
        col.label(text="BSDF Properties")
        row = col.row()
        row.prop(scene, "use_base_color", text="")
        row.prop(scene, "batch_base_color", text="Base Color")
        row = col.row()
        row.prop(scene, "use_metallic", text="")
        row.prop(scene, "batch_metallic_value", text="Metallic")
        row = col.row()
        row.prop(scene, "use_roughness", text="")
        row.prop(scene, "batch_roughness_value", text="Roughness")
        row = col.row()
        row.prop(scene, "use_ior", text="")
        row.prop(scene, "batch_ior_value", text="IOR")
        row = col.row()
        row.prop(scene, "use_alpha", text="")
        row.prop(scene, "batch_alpha_value", text="Alpha")
        row = col.row()
        row.prop(scene, "use_ior_level", text="")
        row.prop(scene, "batch_ior_level_value", text="IOR Level")

        col = layout.column(align=True)
        col.label(text="Material Settings（EEVEE）")
        row = col.row()
        row.prop(scene, "use_render_method", text="")
        row.prop(scene, "batch_render_method", text="Render Method")
        row = col.row()
        row.prop(scene, "use_displacement_method", text="")
        row.prop(scene, "batch_displacement_method", text="Displacement Method")
        row = col.row()
        row.prop(scene, "use_backface_culling", text="")
        row.prop(scene, "batch_backface_culling", text="Backface Culling (Camera)")
        row = col.row()
        row.prop(scene, "use_backface_culling_shadow", text="")
        row.prop(scene, "batch_backface_culling_shadow", text="Backface Culling (Shadow)")
        row = col.row()
        row.prop(scene, "use_backface_culling_lightprobe", text="")
        row.prop(scene, "batch_backface_culling_lightprobe", text="Backface Culling (Lightprobe)")
        row = col.row()
        row.prop(scene, "use_transparent_shadow", text="")
        row.prop(scene, "batch_transparent_shadow", text="Raytrace Transmission")

        col = layout.column(align=True)
        col.label(text="Viewport Display")
        row = col.row()
        row.prop(scene, "use_diffuse_color", text="")
        row.prop(scene, "batch_diffuse_color", text="Diffuse Color")
        row = col.row()
        row.prop(scene, "use_display_metallic", text="")
        row.prop(scene, "batch_display_metallic", text="Metallic")
        row = col.row()
        row.prop(scene, "use_display_roughness", text="")
        row.prop(scene, "batch_display_roughness", text="Roughness")
        
        layout.operator("material.batch_material_helper", text="Apply to Selected Objects")

def update_properties(self, context):
    pass

def register():
    bpy.utils.register_class(MATERIAL_OT_batch_material_helper)
    bpy.utils.register_class(VIEW3D_PT_batch_material_helper)
    
    # BSDF 属性
    bpy.types.Scene.batch_base_color = FloatVectorProperty(
        name="Base Color",
        description="Base color for Principled BSDF",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0, 1.0),
        min=0.0,
        max=1.0,
        size=4,
        update=update_properties
    )
    bpy.types.Scene.use_base_color = BoolProperty(
        name="Use Base Color",
        description="Apply Base Color to selected objects",
        default=False
    )
    bpy.types.Scene.batch_metallic_value = FloatProperty(
        name="Metallic",
        description="Value to set for metallic property",
        default=0.0,
        min=0.0,
        max=1.0,
        update=update_properties
    )
    bpy.types.Scene.use_metallic = BoolProperty(
        name="Use Metallic",
        description="Apply Metallic to selected objects",
        default=False
    )
    bpy.types.Scene.batch_roughness_value = FloatProperty(
        name="Roughness",
        description="Value to set for roughness property",
        default=0.5,
        min=0.0,
        max=1.0,
        update=update_properties
    )
    bpy.types.Scene.use_roughness = BoolProperty(
        name="Use Roughness",
        description="Apply Roughness to selected objects",
        default=False
    )
    bpy.types.Scene.batch_ior_value = FloatProperty(
        name="IOR",
        description="Value to set for IOR property",
        default=1.45,
        min=1.0,
        max=1000.0,
        update=update_properties
    )
    bpy.types.Scene.use_ior = BoolProperty(
        name="Use IOR",
        description="Apply IOR to selected objects",
        default=False
    )
    bpy.types.Scene.batch_alpha_value = FloatProperty(
        name="Alpha",
        description="Value to set for alpha property",
        default=1.0,
        min=0.0,
        max=1.0,
        update=update_properties
    )
    bpy.types.Scene.use_alpha = BoolProperty(
        name="Use Alpha",
        description="Apply Alpha to selected objects",
        default=False
    )
    bpy.types.Scene.batch_ior_level_value = FloatProperty(
        name="IOR Level",
        description="Value to set for IOR Level property",
        default=0.5,
        min=0.0,
        max=1.0,
        update=update_properties
    )
    bpy.types.Scene.use_ior_level = BoolProperty(
        name="Use IOR Level",
        description="Apply IOR Level to selected objects",
        default=False
    )
    # 材质设置
    bpy.types.Scene.batch_render_method = EnumProperty(
        name="Render Method",
        description="Surface render method for materials",
        items=[
            ('DITHERED', "Dithered", "Render surface with dithered transparency"),
            ('BLENDED', "Blended", "Render surface with blended transparency")
        ],
        default='DITHERED',
        update=update_properties
    )
    bpy.types.Scene.use_render_method = BoolProperty(
        name="Use Render Method",
        description="Apply Render Method to selected objects",
        default=False
    )
    bpy.types.Scene.batch_displacement_method = EnumProperty(
        name="Displacement Method",
        description="Displacement method for materials",
        items=[
            ('BUMP', "Bump", "Use bump mapping only"),
            ('DISPLACEMENT', "Displacement", "Use true displacement"),
            ('BOTH', "Displacement and Bump", "Use both displacement and bump")
        ],
        default='BUMP',
        update=update_properties
    )
    bpy.types.Scene.use_displacement_method = BoolProperty(
        name="Use Displacement Method",
        description="Apply Displacement Method to selected objects",
        default=False
    )
    bpy.types.Scene.batch_backface_culling = BoolProperty(
        name="Backface Culling (Camera)",
        description="Enable backface culling for camera",
        default=False,
        update=update_properties
    )
    bpy.types.Scene.use_backface_culling = BoolProperty(
        name="Use Backface Culling (Camera)",
        description="Apply Backface Culling (Camera) to selected objects",
        default=False
    )
    bpy.types.Scene.batch_backface_culling_shadow = BoolProperty(
        name="Backface Culling (Shadow)",
        description="Enable backface culling for shadows",
        default=False,
        update=update_properties
    )
    bpy.types.Scene.use_backface_culling_shadow = BoolProperty(
        name="Use Backface Culling (Shadow)",
        description="Apply Backface Culling (Shadow) to selected objects",
        default=False
    )
    bpy.types.Scene.batch_backface_culling_lightprobe = BoolProperty(
        name="Backface Culling (Lightprobe)",
        description="Enable backface culling for lightprobe volume",
        default=False,
        update=update_properties
    )
    bpy.types.Scene.use_backface_culling_lightprobe = BoolProperty(
        name="Use Backface Culling (Lightprobe)",
        description="Apply Backface Culling (Lightprobe) to selected objects",
        default=False
    )
    bpy.types.Scene.batch_transparent_shadow = BoolProperty(
        name="Raytrace Transmission",
        description="Enable transparent shadows in raytracing",
        default=False,
        update=update_properties
    )
    bpy.types.Scene.use_transparent_shadow = BoolProperty(
        name="Use Raytrace Transmission",
        description="Apply Raytrace Transmission to selected objects",
        default=False
    )
    # 视图显示
    bpy.types.Scene.batch_diffuse_color = FloatVectorProperty(
        name="Diffuse Color",
        description="Viewport display color",
        subtype='COLOR',
        default=(0.8, 0.8, 0.8, 1.0),
        min=0.0,
        max=1.0,
        size=4,
        update=update_properties
    )
    bpy.types.Scene.use_diffuse_color = BoolProperty(
        name="Use Diffuse Color",
        description="Apply Diffuse Color to viewport display",
        default=False
    )
    bpy.types.Scene.batch_display_metallic = FloatProperty(
        name="Display Metallic",
        description="Viewport display metallic value",
        default=0.0,
        min=0.0,
        max=1.0,
        update=update_properties
    )
    bpy.types.Scene.use_display_metallic = BoolProperty(
        name="Use Display Metallic",
        description="Apply Metallic to viewport display",
        default=False
    )
    bpy.types.Scene.batch_display_roughness = FloatProperty(
        name="Display Roughness",
        description="Viewport display roughness value",
        default=0.5,
        min=0.0,
        max=1.0,
        update=update_properties
    )
    bpy.types.Scene.use_display_roughness = BoolProperty(
        name="Use Display Roughness",
        description="Apply Roughness to viewport display",
        default=False
    )

def unregister():
    bpy.utils.unregister_class(MATERIAL_OT_batch_material_helper)
    bpy.utils.unregister_class(VIEW3D_PT_batch_material_helper)
    
    # 移除属性
    del bpy.types.Scene.batch_base_color
    del bpy.types.Scene.use_base_color
    del bpy.types.Scene.batch_metallic_value
    del bpy.types.Scene.use_metallic
    del bpy.types.Scene.batch_roughness_value
    del bpy.types.Scene.use_roughness
    del bpy.types.Scene.batch_ior_value
    del bpy.types.Scene.use_ior
    del bpy.types.Scene.batch_alpha_value
    del bpy.types.Scene.use_alpha
    del bpy.types.Scene.batch_ior_level_value
    del bpy.types.Scene.use_ior_level
    del bpy.types.Scene.batch_render_method
    del bpy.types.Scene.use_render_method
    del bpy.types.Scene.batch_displacement_method
    del bpy.types.Scene.use_displacement_method
    del bpy.types.Scene.batch_backface_culling
    del bpy.types.Scene.use_backface_culling
    del bpy.types.Scene.batch_backface_culling_shadow
    del bpy.types.Scene.use_backface_culling_shadow
    del bpy.types.Scene.batch_backface_culling_lightprobe
    del bpy.types.Scene.use_backface_culling_lightprobe
    del bpy.types.Scene.batch_transparent_shadow
    del bpy.types.Scene.use_transparent_shadow
    del bpy.types.Scene.batch_diffuse_color
    del bpy.types.Scene.use_diffuse_color
    del bpy.types.Scene.batch_display_metallic
    del bpy.types.Scene.use_display_metallic
    del bpy.types.Scene.batch_display_roughness
    del bpy.types.Scene.use_display_roughness

if __name__ == "__main__":
    register()
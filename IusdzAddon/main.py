bl_info = {
    "name": "Interactive Usdz",
    "author": "PalTarasч",
    "version": (0, 1),
    "blender": (4, 1, 0),
    "location": "View3D > N",
    "description": "Allows to add interactivity to single usdz file",
    "warning": "",
    "doc_url": "",
    'category': 'Import-Export'
}

import bpy
from bpy.utils import register_class, unregister_class
import sys
import os

module_path = os.path.dirname("D:\\_projects\\interactive_usd_addon\\IusdzAddon")
if module_path not in sys.path:
    sys.path.append(module_path)

from IusdzAddon.ui.Models import Trigger, Action, Interaction, IUsdzScene, IUsdzSceneReference
from IusdzAddon.ui.Operators import \
    InteractionsEnumOperator, AddInteractionButton, \
        TriggerEnumOperator, AddTriggerButton, \
            ActionEnumOperator, AddActionButton, \
                IUsdzScenesEnumOperator, AddIUsdzSceneButton, RemoveIUsdzSceneButton, \
                AddElementButton
from IusdzAddon.ui.StaticFuncs import get_active_interaction, get_active_trigger, get_active_action, get_active_iUsdzScene, get_object_iUsdzScenes
from IusdzAddon.ui.StaticVars import is_active_obj_selected

class IUPanel(bpy.types.Panel):
    bl_label = "Interactive Usdz"
    bl_idname = "OBJECT_PT_IUPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "I-USDZ"

    def draw(self, context):
        layout = self.layout
        # reload button
        #layout.row().operator("object.exit_iusdz", icon='X')


        layout.row().label(text="IUsdz Scenes")
        row = layout.row()
        column = row.column()
        column.alignment = 'LEFT'
        operator = row.operator("object.add_element_button", icon='ADD')
        operator.element_name = "iusdzscene"
        row.operator("object.remove_iusdzscene_button", icon='REMOVE')

        if len(bpy.context.selected_objects)==0:
            if len(bpy.context.scene.allIUsdzScenes)>0:
                IUsdzScene_available = True
                text = bpy.context.scene.activeIUsdzSceneName if bpy.context.scene.activeIUsdzSceneName != "" else bpy.context.scene.allIUsdzScenes[0].name
            else:
                IUsdzScene_available = False
                text = "--"
        if is_active_obj_selected():
            obj_iUsdzScenes = get_object_iUsdzScenes(bpy.context.active_object)
            if len(obj_iUsdzScenes)>0:
                IUsdzScene_available = True
                text = obj_iUsdzScenes[0].name
            else:
                IUsdzScene_available = False
                text = "--"
        
        row.operator_menu_enum("object.iusdzscenes_enum_operator",
                                  property="iUsdzScenes",
                                  text=text)
        
        if IUsdzScene_available:
            active_iUsdzScene = get_active_iUsdzScene()

            box = layout.box()
            box.row().label(text="Interaction")
            row = box.row()
            column = row.column()
            column.alignment = 'LEFT'
            operator = column.operator("object.add_element_button", icon='ADD')
            operator.element_name = "interaction"
            # add a list of interactions
            row.operator_menu_enum("object.inter_enum_operator",
                                    property="interactions",
                                    text=active_iUsdzScene.usdzActiveInteractionName if len(active_iUsdzScene.interactions)!=0 else "--")
            
            box = box.box()
            # Interraction setting field
            box.enabled = get_active_interaction() is not None
            # trigger
            box.row().label(text="Triggers")
            row = box.row()
            column = row.column()
            column.alignment = 'LEFT'
            column.operator("object.add_trigger_button", icon='ADD')
            # add a list of triggers
            row.operator_menu_enum("object.trigger_enum_operator",
                                    property="triggers",
                                    text= f'{get_active_trigger().triggerType}-{get_active_trigger().name}'
                                        if get_active_interaction() and len(get_active_interaction().triggers)!=0 else "--")

            # Trigger setting field
            #if get_active_trigger() is not None:
            # action
            box.row().label(text="Actions")
            row = box.row()
            column = row.column()
            column.alignment = 'LEFT'
            column.operator("object.add_action_button", icon='ADD')
            # add a list of actions
            row.operator_menu_enum("object.action_enum_operator",
                                    property="actions",
                                    text= f'{get_active_action().actionType}-{get_active_action().name}'
                                        if get_active_interaction() and len(get_active_interaction().actions)!=0 else "--")


# class exit_iusdz(bpy.types.Operator):
#     bl_idname = "object.exit_iusdz"
#     bl_label = "Exit iusdz"
#     bl_options = {'REGISTER', 'UNDO'}

#     def execute(self, context):
#         unregister()
        
#         return {'FINISHED'}


ui_classes = [
    IUPanel, 
    InteractionsEnumOperator, AddInteractionButton, 
    TriggerEnumOperator, AddTriggerButton, 
    ActionEnumOperator, AddActionButton, 
    IUsdzScenesEnumOperator, AddIUsdzSceneButton, RemoveIUsdzSceneButton, 
    AddElementButton
]
properties = [
    Trigger, Action, Interaction, IUsdzScene, IUsdzSceneReference
]
        
def register():
    for cls in properties:
        try:
            unregister_class(cls)
        except RuntimeError:
            pass
        register_class(cls)

    bpy.types.Object.objectIUsdzScenesNames = bpy.props.CollectionProperty(type=IUsdzSceneReference)
    bpy.types.Scene.allIUsdzScenes = bpy.props.CollectionProperty(type=IUsdzScene)
    bpy.types.Scene.activeIUsdzSceneName = bpy.props.StringProperty(name="Active IUsdz Scene Name")

    for cls in ui_classes:
        try:
            unregister_class(cls)
        except RuntimeError:
            pass
        register_class(cls)

def unregister():
    for cls in ui_classes+properties:
        unregister_class(cls)
    
    del bpy.types.Object.objectIUsdzScenesNames
    del bpy.types.Scene.allIUsdzScenes
    del bpy.types.Scene.activeIUsdzSceneName


if __name__ == "__main__":
    register()

        

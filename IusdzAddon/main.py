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

from IusdzAddon.ui.Models import Trigger, Action, Interaction, IUsdzScene, NameReference
from IusdzAddon.ui.Operators import \
    SelectObjectsOperator, CancelSelectObjectsOperator, EditAffectedObjectsButton,\
    InteractionsEnumOperator, TriggerEnumOperator, ActionEnumOperator, IUsdzScenesEnumOperator, \
        AddElementButton, RemoveElementButton
from IusdzAddon.ui.StaticFuncs import get_active_interaction, get_active_trigger, get_active_action, get_active_iUsdzScene, get_object_iUsdzScenes
from IusdzAddon.ui.StaticVars import is_active_obj_selected, get_object_selection_status
from IusdzAddon.ui.Exceptions import ElementNotCreated

class IUPanel(bpy.types.Panel):
    bl_label = "Interactive Usdz"
    bl_idname = "OBJECT_PT_IUPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "I-USDZ"

    def draw(self, context):
        layout = self.layout
        if get_object_selection_status() is not None:
            affected_element = get_object_selection_status()

            if affected_element == "iusdzscene":
                layout.label(text=f"{get_active_iUsdzScene().name} IUsdz Scene")
            elif affected_element == "trigger":
                layout.label(text=f"{get_active_trigger().name} Trigger")
            elif affected_element == "action":
                layout.label(text=f"{get_active_action().name} Action")
            layout.separator()
            layout.label(text="Select objects to be affected.")
            box = layout.box()
            box.label(text=f"{len(bpy.context.selected_objects)} Selected objects")
            layout.operator("object.select_objects", text="Pick", icon='RESTRICT_SELECT_OFF')
            layout.operator("object.cancel_select_objects", text="Cancel", icon='CANCEL')
            return


        selected_element_text = "--"
        available_iUsdzScenes = "--"
        hints = None 
        errors = None
        if len(bpy.context.selected_objects)==0:
            if len(bpy.context.scene.allIUsdzScenes)>0:
                IUsdzScene_available = True
                selected_element_text = bpy.context.scene.activeIUsdzSceneName if bpy.context.scene.activeIUsdzSceneName != "" else bpy.context.scene.allIUsdzScenes[0].name
                available_iUsdzScenes = "All IUsdz Scenes"
                hints = "Select an object to see its IUsdz Scenes"
            else:
                IUsdzScene_available = False
                selected_element_text = "--"
                available_iUsdzScenes = "IUsdz Scene"
                errors = "No IUsdz Scenes available"
                hints = "Create a new IUsdz Scene"
        if is_active_obj_selected():
            obj_iUsdzScenes = get_object_iUsdzScenes(bpy.context.active_object)
            available_iUsdzScenes = f"IUsdz Scenes with '{bpy.context.active_object.name}'"
            if len(obj_iUsdzScenes)>0:
                IUsdzScene_available = True
                selected_element_text = obj_iUsdzScenes[0].name
            else:
                IUsdzScene_available = False
                selected_element_text = "--"
                errors = "No IUsdz Scenes available for this object"
                hints = "Deselect objects to see all IUsdz Scenes"
        
        row = layout.row()
        row.label(text=available_iUsdzScenes)
        row.operator("object.add_element_button", icon='ADD').element_type = "iusdzscene"
        row.operator("object.remove_element_button", icon='REMOVE').element_type = "iusdzscene"

        row = layout.row()
        row.operator_menu_enum("object.iusdzscenes_enum_operator",
                                  property="iUsdzScenes",
                                  text=selected_element_text)
        
        if IUsdzScene_available:
            create_affected_objects_layout(layout, "iusdzscene")

            active_iUsdzScene = get_active_iUsdzScene()

            inter_box = layout.box()
            row = inter_box.row()
            row.label(text="Interaction")
            row.operator("object.add_element_button", icon='ADD').element_type = "interaction"
            row.operator("object.remove_element_button", icon='REMOVE').element_type = "interaction"
            # add a list of interactions
            row = inter_box.row()
            row.operator_menu_enum("object.inter_enum_operator",
                                    property="interactions",
                                    text=active_iUsdzScene.usdzActiveInteractionName if len(active_iUsdzScene.interactions)!=0 else "--")
            
            # trigger
            trig_box = inter_box.box()
            act_box = inter_box.box()
            try:
                get_active_interaction()
                errors = None
                hints = None
            except ElementNotCreated:
                trig_box.enabled = False
                act_box.enabled = False
                errors = "No Interaction selected"
                
            row = trig_box.row()
            row.label(text="Triggers")
            row.operator("object.add_element_button", icon='ADD').element_type = "trigger"
            row.operator("object.remove_element_button", icon='REMOVE').element_type = "trigger"
            # add a list of triggers
            row = trig_box.row()
            text = "--"
            try:
                get_active_interaction()
                if len(get_active_interaction().triggers)!=0:
                    text = f'{get_active_trigger().triggerType}-{get_active_trigger().name}'
                else:
                    if errors is None:
                        errors = "No Trigger selected"

            except ElementNotCreated:
                text = "--"


            row.operator_menu_enum("object.trigger_enum_operator",
                                    property="triggers",
                                    text= text)
            # edit affected objects
            create_affected_objects_layout(trig_box, "trigger")

            # action
            
            row = act_box.row()
            row.label(text="Actions")
            row.operator("object.add_element_button", icon='ADD').element_type = "action"
            row.operator("object.remove_element_button", icon='REMOVE').element_type = "action"
            # add a list of actions
            row = act_box.row()
            text = "--"
            try:
                get_active_interaction()
                if len(get_active_interaction().actions)!=0:
                    text = f'{get_active_action().actionType}-{get_active_action().name}'
                else:
                    if errors is None:
                        errors = "No Action selected"
            except ElementNotCreated:
                text = "--"

            row.operator_menu_enum("object.action_enum_operator",
                                    property="actions",
                                    text= text)
            # edit affected objects
            create_affected_objects_layout(act_box, "action")

        if errors is not None or hints is not None:
            layout.separator()

        if errors is not None:
            layout.row().label(text=errors, icon='ERROR')
        else:
            layout.row().label(text="Ready for export", icon='CHECKMARK')

        if hints is not None:
            layout.row().label(text=hints, icon='INFO')
            


def create_affected_objects_layout(layout, element_type):
    row = layout.row()
    left_col = row.column()
    right_col = row.column()
    right_col.alignment = 'RIGHT'
    if element_type == "iusdzscene":
        affected_objects_count = len(get_active_iUsdzScene().objects)
        left_col.label(text=f"{affected_objects_count} Objects in scene")
        right_col.operator("object.edit_affected_objects", text='Pick', icon='RESTRICT_SELECT_OFF').element_type = "iusdzscene"
    else: # for action and trigger
        try:
            affected_objects_count = len(get_active_action().affectedObjects if element_type == "action" else get_active_trigger().affectedObjects)
        except ElementNotCreated:
            affected_objects_count = 0
        left_col.label(text=f"{affected_objects_count} Objects affected")
        right_col.operator("object.edit_affected_objects", text='Pick', icon='RESTRICT_SELECT_OFF').element_type = element_type
    layout.separator()

ui_classes = [
    IUPanel, 
    SelectObjectsOperator, CancelSelectObjectsOperator, EditAffectedObjectsButton,
    InteractionsEnumOperator, TriggerEnumOperator, ActionEnumOperator, IUsdzScenesEnumOperator, 
    AddElementButton, RemoveElementButton
]
properties = [
    Trigger, Action, Interaction, IUsdzScene, NameReference
]
        
def register():
    for cls in properties:
        try:
            unregister_class(cls)
        except RuntimeError:
            pass
        register_class(cls)

    bpy.types.Object.objectIUsdzScenesNames = bpy.props.CollectionProperty(type=NameReference)
    bpy.types.Object.objectTriggerNames = bpy.props.CollectionProperty(type=NameReference)
    bpy.types.Object.objectActionsNames = bpy.props.CollectionProperty(type=NameReference)
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
    del bpy.types.Object.objectTriggerNames
    del bpy.types.Object.objectActionsNames
    del bpy.types.Scene.allIUsdzScenes
    del bpy.types.Scene.activeIUsdzSceneName


if __name__ == "__main__":
    register()

        

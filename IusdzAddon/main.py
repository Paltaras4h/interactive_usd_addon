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
#module_path = os.path.dirname(__file__).split("IusdzAddon")[0]+"IusdzAddon"
print(module_path)
if module_path not in sys.path:
    sys.path.append(module_path)

from IusdzAddon.ui.Models import Trigger, Action, Interaction, IUsdzScene, NameReference, ObjectPointerProperty
from IusdzAddon.ui.Operators import \
    SelectObjectsOperator, CancelSelectObjectsOperator, EditAffectedObjectsButton,\
    InteractionsEnumOperator, TriggerEnumOperator, ActionEnumOperator, IUsdzScenesEnumOperator, ExportActiveIUsdzSceneOperator, \
        AddElementButton, RemoveElementButton
from IusdzAddon.ui.StaticFuncs import get_active_interaction, get_active_trigger, get_active_action, get_active_iUsdzScene, get_object_iUsdzScenes
from IusdzAddon.ui.StaticVars import is_active_obj_selected, get_object_selection_status, is_simulating_iusdz_scene
from IusdzAddon.ui.Exceptions import ElementNotCreated

# object selection handler
def my_handler(scene):
    print("Active object:", scene.objects.active.name)


class IUPanel(bpy.types.Panel):
    bl_label = "Interactive Usdz"
    bl_idname = "OBJECT_PT_IUPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "I-USDZ"

    def draw(self, context):
        layout = self.layout
        #is_simulating_iusdz_scene = True
        if is_simulating_iusdz_scene:
            layout.label(text="Simulation mode")
            #layout.label(text=get_active_iUsdzScene().name)
            #layout.operator("object.stop_simulation", text="Stop", icon='CANCEL')
            if is_active_obj_selected():
                print("active object selected")
            return
        
        if get_object_selection_status() is not None:
            affected_element = get_object_selection_status()

            if affected_element == "iusdzscene":
                layout.label(text="Select objects to be included in the scene.")
                layout.separator()
                layout.label(text=f"{get_active_iUsdzScene().name} IUsdz Scene")
            elif affected_element == "trigger":
                layout.label(text="Select objects to be triggered.")
                layout.separator()
                layout.label(text=f"{get_active_trigger().name}-{get_active_trigger().triggerType} Trigger")
            elif affected_element == "action":
                layout.label(text="Select objects to be affected.")
                layout.separator()
                layout.label(text=f"{get_active_action().name}-{get_active_action().actionType} Action")

            box = layout.box()
            box.label(text=f"{len(bpy.context.selected_objects)} Selected objects")
            layout.operator("object.select_objects", text="Pick", icon='RESTRICT_SELECT_OFF')
            layout.operator("object.cancel_select_objects", text="Cancel", icon='CANCEL')
            return

        # for area in bpy.context.screen.areas:
        #     if area.type == 'VIEW_3D':
        #         print(1) # bpy.ops.view3d.localview()

        selected_element_text = "--"
        available_iUsdzScenes = "--"
        hints = None 
        errors = []
        IUsdzScene_available = False
        if len(bpy.context.selected_objects)==0:
            if len(bpy.context.scene.allIUsdzScenes)>0:
                available_iUsdzScenes = "All IUsdz Scenes"
                if get_active_iUsdzScene().icludes_removed_objects():
                    errors.append("Removed objects from IUsdz Scene")
                    hints = "Select IUsdz Scene to update objects"
                    selected_element_text = "Select IUsdz Scene"
                else:
                    IUsdzScene_available = True
                    selected_element_text = bpy.context.scene.activeIUsdzSceneName if bpy.context.scene.activeIUsdzSceneName != "" else bpy.context.scene.allIUsdzScenes[0].name
                    hints = "Select an object to see its IUsdz Scenes"
            else:
                selected_element_text = "--"
                available_iUsdzScenes = "IUsdz Scene"
                errors.append("No IUsdz Scenes available")
                hints = "Create a new IUsdz Scene"
        elif is_active_obj_selected():
            obj_iUsdzScenes = get_object_iUsdzScenes(bpy.context.active_object)
            available_iUsdzScenes = f"IUsdz Scenes with '{bpy.context.active_object.name}'"
            if len(obj_iUsdzScenes)>0:
                IUsdzScene_available = True
                selected_element_text = obj_iUsdzScenes[0].name if bpy.context.scene.activeIUsdzSceneName not in bpy.context.active_object.objectIUsdzScenesNames else bpy.context.scene.activeIUsdzSceneName
            else:
                selected_element_text = "--"
                errors.append("No IUsdz Scenes available for this object")
            hints = "Deselect objects to see all IUsdz Scenes"
        else:
            selected_element_text = "--"
            available_iUsdzScenes = "IUsdz Scene"
            errors.append("No active object selected")
        
        row = layout.row()
        row.label(text=available_iUsdzScenes)
        row.operator("object.add_element_button", icon='ADD', text='').element_type = "iusdzscene"
        row.operator("object.remove_element_button", icon='REMOVE', text='').element_type = "iusdzscene"

        row = layout.row()
        row.operator_menu_enum("object.iusdzscenes_enum_operator",
                                  property="iUsdzScenes",
                                  text=selected_element_text)
        
        if IUsdzScene_available:
            create_affected_objects_layout(layout, "iusdzscene")

            active_iUsdzScene = get_active_iUsdzScene()

            inter_box = layout.box()
            row = inter_box.row()
            row.label(text=f"Interactions ({len(active_iUsdzScene.interactions)})")
            row.operator("object.add_element_button", icon='ADD', text='').element_type = "interaction"
            row.operator("object.remove_element_button", icon='REMOVE', text='').element_type = "interaction"
            # add a list of interactions
            row = inter_box.row()
            
            interaction_name_text = "--"
            if len(active_iUsdzScene.interactions)!=0:
                try:
                    trigger = get_active_interaction().triggers[0] if len(get_active_interaction().triggers)!=0 else None
                    if trigger is not None:
                        trigger_affected_objects = [obj.name for obj in trigger.get_affected_objects()]
                        if trigger.triggerType == 'on_load':
                            interaction_name_text = f"{active_iUsdzScene.usdzActiveInteractionName}-{trigger.triggerType}..."
                        elif len(trigger_affected_objects) != 0:
                            interaction_name_text = f"{active_iUsdzScene.usdzActiveInteractionName}-{trigger.triggerType}-{trigger_affected_objects[0]}..."
                        else:
                            interaction_name_text = active_iUsdzScene.usdzActiveInteractionName
                    else:
                        interaction_name_text = active_iUsdzScene.usdzActiveInteractionName
                except ElementNotCreated:
                    interaction_name_text = active_iUsdzScene.usdzActiveInteractionName
            row.operator_menu_enum("object.inter_enum_operator",
                                    property="interactions",
                                    text=interaction_name_text)
            
            # trigger
            trig_box = inter_box.box()
            act_box = inter_box.box()
            try:
                if len(active_iUsdzScene.objects)==0:
                    errors.append("No objects in IUsdz Scene")
                get_active_interaction()
                hints = None
            except ElementNotCreated:
                trig_box.enabled = False
                act_box.enabled = False
                errors.append("No Interaction selected")
                
            row = trig_box.row()
            row.label(text=f"Triggers ({len(get_active_interaction().triggers)})")
            row.operator("object.add_element_button", icon='ADD', text='').element_type = "trigger"
            row.operator("object.remove_element_button", icon='REMOVE', text='').element_type = "trigger"
            # add a list of triggers
            row = trig_box.row()
            text = "--"
            trigger_requires_affection = False
            try:
                get_active_interaction()
                active_trigger = get_active_trigger()
                if active_trigger.require_affection():
                    trigger_requires_affection = True
                    if len(active_trigger.affectedObjects)==0:
                        errors.append("No objects affected by Trigger")
                if len(get_active_interaction().triggers)!=0:
                    text = f'{active_trigger.triggerType}-{active_trigger.name}'

            except ElementNotCreated:
                text = "--"
                errors.append("No Trigger selected")

            row.operator_menu_enum("object.trigger_enum_operator",
                                    property="triggers",
                                    text = text)
            # edit affected objects
            if trigger_requires_affection:
                create_affected_objects_layout(trig_box, "trigger")

            # action
            
            row = act_box.row()
            row.label(text=f"Actions ({str(len(get_active_interaction().actions))})")
            row.operator("object.add_element_button", icon='ADD', text='').element_type = "action"
            row.operator("object.remove_element_button", icon='REMOVE', text='').element_type = "action"
            # add a list of actions
            row = act_box.row()
            text = "--"
            try:
                get_active_interaction()
                if len(get_active_action().affectedObjects)==0:
                    errors.append("No objects affected by Action")
                if len(get_active_interaction().actions)!=0:
                    text = f'{get_active_action().actionType}-{get_active_action().name}'
            except ElementNotCreated:
                text = "--"
                errors.append("No Action selected")

            row.operator_menu_enum("object.action_enum_operator",
                                    property="actions",
                                    text= text)
            
            # duration slider
            try:
                if get_active_action().actionType == "show" or get_active_action().actionType == "hide":
                    act_box.prop(get_active_action(),"duration", text="Animation duration (s)")
            except ElementNotCreated:
                pass
            # edit affected objects
            create_affected_objects_layout(act_box, "action")


        if len(errors)!=0 or hints is not None:
            layout.separator()

        if hints is not None:
            layout.row().label(text=hints, icon='INFO')

        for error in errors:
            layout.row().label(text=error, icon='CANCEL')
        if len(errors)==0:
            layout.row().label(text="Ready for export", icon='CHECKMARK')
            layout.operator("object.export_active_iusdz_scene", icon='EXPORT')
        #else:
        #    layout.row().label(text="Not Ready for export", icon='CANCEL')

            

def update_frame_index():
    wm = bpy.context.window_manager
    if bpy.context.area.type == 'VIEW_3D':
        print("updating frame index")
        if hasattr(wm, 'my_tool'):
            my_tool = wm.my_tool
            my_tool.frame_index = (my_tool.frame_index + 1) % len(image_sequence)
            bpy.context.area.tag_redraw()

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
    InteractionsEnumOperator, TriggerEnumOperator, ActionEnumOperator, IUsdzScenesEnumOperator, ExportActiveIUsdzSceneOperator,
    AddElementButton, RemoveElementButton,
]
properties = [
    ObjectPointerProperty, Trigger, Action, Interaction, IUsdzScene, NameReference, 
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

    bpy.app.handlers.frame_change_pre.append(my_handler)

def unregister():
    for cls in ui_classes+properties:
        unregister_class(cls)
    
    del bpy.types.Object.objectIUsdzScenesNames
    del bpy.types.Object.objectTriggerNames
    del bpy.types.Object.objectActionsNames
    del bpy.types.Scene.allIUsdzScenes
    del bpy.types.Scene.activeIUsdzSceneName

    bpy.app.handlers.frame_change_pre.remove(my_handler)


if __name__ == "__main__":
    register()

        

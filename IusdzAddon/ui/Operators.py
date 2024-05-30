import bpy
from IusdzAddon.ui.StaticFuncs import addIUsdzScene, addInteraction, addAction, addTrigger,\
        get_active_iUsdzScene, get_active_interaction, get_active_trigger, get_active_action, \
        removeIUsdzScene, removeInteraction, removeAction, removeTrigger, \
        get_object_iUsdzScenes, get_active_element_by_type
from IusdzAddon.ui.StaticVars import trigger_types, action_types, is_active_obj_selected, get_object_selection_status, set_object_selection_status, \
        get_tmp_selected_objects, set_tmp_selected_objects, get_tmp_active_object, set_tmp_active_object
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator
from json import dumps
import os


class AddElementButton(Operator):
    bl_idname = "object.add_element_button"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = f'Add a new element'

    element_type: StringProperty("element type", default="element")
    input_field: StringProperty(f"Element name")
    triggerType: EnumProperty(name="Trigger Type", items=trigger_types)
    actionType: EnumProperty(name="Action Type", items=action_types)

    def invoke(self, context, event):
        if (self.element_type == "iusdzscene"):
            self.input_field = f"IUScene{len(bpy.context.scene.allIUsdzScenes)}"
        elif (self.element_type == "interaction"):
            self.input_field = f"Inter{len(get_active_iUsdzScene().interactions)}"
        elif (self.element_type == "trigger"):
            self.input_field = f"Trigger{len(get_active_interaction().triggers)}"
        elif (self.element_type == "action"):
            self.input_field = f"Action{len(get_active_interaction().actions)}"
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        try:
            if (self.element_type == "iusdzscene"):
                scene = addIUsdzScene(self.input_field, bpy.context.selected_objects)
                context.scene.activeIUsdzSceneName = scene.name
            elif (self.element_type == "interaction"):
                interaction = addInteraction(self.input_field)
                get_active_iUsdzScene().usdzActiveInteractionName = interaction.name
            elif (self.element_type == "trigger"):
                trigger = addTrigger(self.input_field, self.triggerType)
                get_active_iUsdzScene().usdzActiveTriggerName = trigger.name
            elif (self.element_type == "action"):
                action = addAction(self.input_field, self.actionType)
                get_active_iUsdzScene().usdzActiveActionName = action.name
            # update the panel
            bpy.context.area.tag_redraw()
        except ValueError as e:
            bpy.context.window_manager.popup_menu(lambda self, context: self.layout.label(text=str(e)), title="Error", icon='ERROR')
        
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        # input field for interaction name
        layout.prop(self, "input_field", text="Name")
        if (self.element_type == "trigger"):
            row = layout.row()
            row.label(text="Trigger Type")
            row.prop_menu_enum(self, property="triggerType", text=self.triggerType)
        elif (self.element_type == "action"):
            row = layout.row()
            row.label(text="Action Type")
            row.prop_menu_enum(self, property="actionType", text=self.actionType)


class RemoveElementButton(Operator):
    bl_idname = "object.remove_element_button"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    element_type: StringProperty("element name", default="element")
    bl_description = 'Remove element'

    def invoke(self, context, event):
        element = get_active_element_by_type(self.element_type)
        if element is None:
            return {'CANCELLED'}
        return context.window_manager.invoke_props_dialog(self, title=f"Remove {element.name} {self.element_type}?")
    
    def execute(self, context):
        try:
            if (self.element_type == "iusdzscene"):
                removeIUsdzScene(get_active_iUsdzScene())
            elif (self.element_type == "interaction"):
                removeInteraction(get_active_interaction())
            elif (self.element_type == "trigger"):
                removeTrigger(get_active_trigger())
            elif (self.element_type == "action"):
                removeAction(get_active_action())

            # update the panel
            bpy.context.area.tag_redraw()
        except ValueError as e:
            bpy.context.window_manager.popup_menu(lambda self, context: self.layout.label(text=str(e)), title="Error", icon='ERROR')
        
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        # confirmation message

        layout.label(text="All its interactions will be removed as well.")
        
        

class IUsdzScenesEnumOperator(Operator):
    bl_label = ''
    bl_idname = 'object.iusdzscenes_enum_operator'
    bl_description = 'Select an IUsdz Scene'
    def get_iUsdzScenes(self, context):
        print("get_iUsdzScenes")
        for iUsdzScene in bpy.context.scene.allIUsdzScenes:
            for object in iUsdzScene.get_objects():
                if object not in bpy.context.scene.objects.values():
                    iUsdzScene.remove_object_by_ref(object)
                    for interaction in iUsdzScene.interactions:
                        for trigger in interaction.triggers:
                            trigger.remove_object_by_ref(object)
                        for action in interaction.actions:
                            action.remove_object_by_ref(object)
                                
        if len(bpy.context.selected_objects)==0:
            if context.scene.activeIUsdzSceneName == "":
                context.scene.activeIUsdzSceneName = bpy.context.scene.allIUsdzScenes[0].name if len(bpy.context.scene.allIUsdzScenes)>0 else ""
            bpy.context.area.tag_redraw()
            return [(iUsdzScene.name, iUsdzScene.name, iUsdzScene.name) for iUsdzScene in bpy.context.scene.allIUsdzScenes if iUsdzScene is not None]
        if is_active_obj_selected():
            result = [(iUsdzScene.name, iUsdzScene.name, iUsdzScene.name) for iUsdzScene in get_object_iUsdzScenes(bpy.context.active_object) if iUsdzScene is not None]
            #context.scene.activeIUsdzSceneName = "" if len(result)==0 else result[0][0]
            bpy.context.area.tag_redraw()
            return result
    iUsdzScenes : EnumProperty(name="IUsdzScenes", items=get_iUsdzScenes)

    def execute(self, context):
        context.scene.activeIUsdzSceneName = self.iUsdzScenes
        bpy.context.area.tag_redraw()
        
        return {'FINISHED'}



class InteractionsEnumOperator(Operator):
    bl_label = ''
    bl_idname = 'object.inter_enum_operator'
    bl_description = 'Select an interaction'
    def get_interactions(self, context):
        return [(interaction.name, interaction.name, interaction.name) for interaction in get_active_iUsdzScene().interactions]
    interactions : EnumProperty(name="Interactions", items=get_interactions)

    def execute(self, context):
        get_active_iUsdzScene().usdzActiveInteractionName = self.interactions
        
        return {'FINISHED'}


class TriggerEnumOperator(Operator):
    bl_label = ''
    bl_idname = 'object.trigger_enum_operator'
    bl_description = 'Select a trigger'
    def get_triggers(self, context):
        print(type(get_active_interaction()))
        return [(trigger.name, f'{trigger.triggerType}-{trigger.name}', trigger.name) for trigger in get_active_interaction().triggers]# if get_active_interaction() is not None else [("--", "--", "add a trigger")]
    triggers : EnumProperty(name="Triggers", items=get_triggers)

    def execute(self, context):
        get_active_iUsdzScene().usdzActiveTriggerName = self.triggers
        
        return {'FINISHED'}

        
class ActionEnumOperator(Operator):
    bl_label = ''
    bl_idname = 'object.action_enum_operator'
    bl_description = 'Select a action'
    def get_actions(self, context):
        return [(action.name, f'{action.actionType}-{action.name}', action.name) for action in get_active_interaction().actions]# if get_active_interaction() is not None else [("--", "--", "add a trigger")]
    actions : EnumProperty(name="Actions", items=get_actions)

    def execute(self, context):
        get_active_iUsdzScene().usdzActiveActionName = self.actions
        
        return {'FINISHED'}


class EditAffectedObjectsButton(Operator):
    bl_idname = "object.edit_affected_objects"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Edit affected objects'

    element_type: StringProperty("element type", default="element")

    def execute(self, context):
        set_object_selection_status(self.element_type)
        element = get_active_element_by_type(self.element_type)
        if element is None:
            set_object_selection_status(None)
            return {'CANCELLED'}
        
        set_tmp_selected_objects(bpy.context.selected_objects)
        set_tmp_active_object(bpy.context.active_object)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = None

        element.select_objects()
        return {'FINISHED'}
    

class SelectObjectsOperator(Operator):
    bl_idname = "object.select_objects"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Select objects'


    def execute(self, context):
        affected_element = get_object_selection_status()
        element = get_active_element_by_type(affected_element)
        if element is None:
            set_object_selection_status(None)
            return {'CANCELLED'}
        
        element.update_objects(bpy.context.selected_objects)
        bpy.ops.object.select_all(action='DESELECT')
        set_object_selection_status(None)
        for obj in get_tmp_selected_objects():
            obj.select_set(True)
        bpy.context.view_layer.objects.active = get_tmp_active_object()
        
        return {'FINISHED'}
    
    
class CancelSelectObjectsOperator(Operator):
    bl_idname = "object.cancel_select_objects"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Cancel'

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        set_object_selection_status(None)
        for obj in get_tmp_selected_objects():
            obj.select_set(True)
        bpy.context.view_layer.objects.active = get_tmp_active_object()
        return {'FINISHED'}

class ExportActiveIUsdzSceneOperator(Operator):
    bl_idname = "object.export_active_iusdz_scene"
    bl_label = "Export"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Export the active IUsdz Scene'

    def execute(self, context):
        # export usdz model
        set_tmp_selected_objects(bpy.context.selected_objects)
        set_tmp_active_object(bpy.context.active_object)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = None

        render_settings = {}
        get_active_iUsdzScene().select_objects()
        for obj in bpy.context.selected_objects:
            render_settings[obj.name] = {
                "hide": obj.hide_get(),
                "hide_render": obj.hide_render,
            }
            obj.hide_set(False)
            obj.hide_render = False
        
        dir = '\\'.join(os.path.dirname(__file__).split('\\')[:-2])
        bpy.ops.wm.usd_export(filepath=f"{dir}\\tmp_iusdz_model.usdz", selected_objects_only=True)

        for obj in bpy.context.selected_objects:
            obj.hide_set(render_settings[obj.name]["hide"])
            obj.hide_render = render_settings[obj.name]["hide_render"]
        bpy.ops.object.select_all(action='DESELECT')
        for obj in get_tmp_selected_objects():
            obj.select_set(True)
        bpy.context.view_layer.objects.active = get_tmp_active_object()

        # save json file with interaction props
        json_data = {}
        json_data["interactions"] = []
        for interaction in get_active_iUsdzScene().interactions:
            json_data["interactions"].append({
                "name": interaction.name,
                "triggers": [{
                    "name": trigger.name,
                    "type": trigger.triggerType,
                    "affected_objects": [object.object_ref.name for object in trigger.affectedObjects],
                    } for trigger in interaction.triggers],
                "actions": [{
                    "name": action.name,
                    "type": action.actionType,
                    "affected_objects": [object.object_ref.name for object in action.affectedObjects],
                    } for action in interaction.actions],
            })
        with open(f"{dir}\\tmp_iusdz_model_interactions.json", "w") as file:
            file.write(dumps(json_data))
        return {'FINISHED'}
    
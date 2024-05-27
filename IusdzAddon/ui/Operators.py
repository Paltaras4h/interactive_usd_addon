import bpy
from IusdzAddon.ui.StaticFuncs import addTrigger, addInteraction, get_active_interaction, get_active_trigger, addAction, addIUsdzScene, removeIUsdzScene, get_active_iUsdzScene, get_object_iUsdzScenes
from IusdzAddon.ui.StaticVars import trigger_types, action_types, is_active_obj_selected
from bpy.props import EnumProperty, StringProperty
from bpy.types import Operator

object_selection_status = False


class AddElementButton(Operator):
    bl_idname = "object.add_element_button"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    element_name: StringProperty("element name", default="element")
    bl_description = f'Add a new element'
    input_field: StringProperty(f"Element name")


    def invoke(self, context, event):
        if (self.element_name == "iusdzscene"):
            self.input_field = f"IUScene{len(bpy.context.scene.allIUsdzScenes)}"
        elif (self.element_name == "interaction"):
            self.input_field = f"Inter{len(get_active_iUsdzScene().interactions)}"
        elif (self.element_name == "trigger"):
            self.input_field = f"Trigger{len(get_active_interaction().triggers)}"
        elif (self.element_name == "action"):
            self.input_field = f"Action{len(get_active_interaction().actions)}"
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        try:
            if (self.element_name == "iusdzscene"):
                scene = addIUsdzScene(self.input_field, bpy.context.selected_objects)
                context.scene.activeIUsdzSceneName = scene.name
            elif (self.element_name == "interaction"):
                interaction = addInteraction(self.input_field)
                get_active_iUsdzScene().usdzActiveInteractionName = interaction.name
            elif (self.element_name == "trigger"):
                trigger = addTrigger(self.input_field, self.triggerType)
                get_active_iUsdzScene().usdzActiveTriggerName = trigger.name
            elif (self.element_name == "action"):
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

class IUsdzScenesEnumOperator(Operator):
    bl_label = ''
    bl_idname = 'object.iusdzscenes_enum_operator'
    bl_description = 'Select an IUsdz Scene'
    def get_iUsdzScenes(self, context):
        if len(bpy.context.selected_objects)==0:
            if context.scene.activeIUsdzSceneName == "":
                context.scene.activeIUsdzSceneName = bpy.context.scene.allIUsdzScenes[0].name
            bpy.context.area.tag_redraw()
            return [(iUsdzScene.name, iUsdzScene.name, iUsdzScene.name) for iUsdzScene in bpy.context.scene.allIUsdzScenes if iUsdzScene is not None]
        if is_active_obj_selected():
            result = [(iUsdzScene.name, iUsdzScene.name, iUsdzScene.name) for iUsdzScene in get_object_iUsdzScenes(bpy.context.active_object) if iUsdzScene is not None]
            context.scene.activeIUsdzSceneName = "" if len(result)==0 else result[0][0]
            bpy.context.area.tag_redraw()
            return result
    iUsdzScenes : EnumProperty(name="IUsdzScenes", items=get_iUsdzScenes)

    def execute(self, context):
        context.scene.activeIUsdzSceneName = self.iUsdzScenes
        bpy.context.area.tag_redraw()
        
        return {'FINISHED'}


class AddIUsdzSceneButton(Operator):
    bl_idname = "object.add_iusdzscene_button"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Add a new IUsdz Scene with selected objects'
    input_field: StringProperty("IUsdz Scene Name")


    def invoke(self, context, event):
        self.input_field = f"IUScene{len(bpy.context.scene.allIUsdzScenes)}"
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        try:
            scene = addIUsdzScene(self.input_field, bpy.context.selected_objects)
            context.scene.activeIUsdzSceneName = scene.name
            # update the panel
            bpy.context.area.tag_redraw()
        except ValueError as e:
            bpy.context.window_manager.popup_menu(lambda self, context: self.layout.label(text=str(e)), title="Error", icon='ERROR')
        
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        # input field for IUsdzScene name
        layout.prop(self, "input_field", text="Name")

class RemoveIUsdzSceneButton(Operator):
    bl_idname = "object.remove_iusdzscene_button"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Remove active IUsdz Scene'
    input_field: StringProperty("IUsdz Scene Name")


    def invoke(self, context, event):
        self.input_field = f"IUScene{len(bpy.context.scene.allIUsdzScenes)}"
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        try:
            removeIUsdzScene(get_active_iUsdzScene())
            # update the panel
            bpy.context.area.tag_redraw()
        except ValueError as e:
            bpy.context.window_manager.popup_menu(lambda self, context: self.layout.label(text=str(e)), title="Error", icon='ERROR')
        
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        # input field for IUsdzScene name
        layout.prop(self, "input_field", text="Name")
        

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


class AddInteractionButton(Operator):
    bl_idname = "object.add_interaction_button"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Add a new interaction'
    input_field: StringProperty("Interaction Name")


    def invoke(self, context, event):
        self.input_field = f"Inter{len(get_active_iUsdzScene().interactions)}"
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        try:
            interaction = addInteraction(self.input_field)
            get_active_iUsdzScene().usdzActiveInteractionName = interaction.name
            # update the panel
            bpy.context.area.tag_redraw()
        except ValueError as e:
            bpy.context.window_manager.popup_menu(lambda self, context: self.layout.label(text=str(e)), title="Error", icon='ERROR')
        
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        # input field for interaction name
        layout.prop(self, "input_field", text="Name")
        

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


class AddTriggerButton(Operator):
    bl_idname = "object.add_trigger_button"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Add a new trigger'
    input_field: StringProperty("Trigger Name")
    triggerType: EnumProperty(name="Trigger Type", items=trigger_types)


    def invoke(self, context, event):
        self.input_field = f"Trigger{len(get_active_interaction().triggers)}"
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        try:
            trigger = addTrigger(self.input_field, self.triggerType)
            get_active_iUsdzScene().usdzActiveTriggerName = trigger.name
            # update the panel
            bpy.context.area.tag_redraw()
        except ValueError as e:
            bpy.context.window_manager.popup_menu(lambda self, context: self.layout.label(text=str(e)), title="Error", icon='ERROR')
        
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        # input field for Trigger name
        layout.prop(self, "input_field", text="Name")
        row = layout.row()
        row.label(text="Trigger Type")
        row.prop_menu_enum(self, property="triggerType", text=self.triggerType)

        
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


class AddActionButton(Operator):
    bl_idname = "object.add_action_button"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Add a new action'
    input_field: StringProperty("Action Name")
    actionType: EnumProperty(name="Action Type", items=action_types)


    def invoke(self, context, event):
        self.input_field = f"Action{len(get_active_interaction().actions)}"
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        try:
            action = addAction(self.input_field, self.actionType)
            get_active_iUsdzScene().usdzActiveActionName = action.name
            # update the panel
            bpy.context.area.tag_redraw()
        except ValueError as e:
            bpy.context.window_manager.popup_menu(lambda self, context: self.layout.label(text=str(e)), title="Error", icon='ERROR')
        
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        # input field for Action name
        layout.prop(self, "input_field", text="Name")
        row = layout.row()
        row.label(text="Action Type")
        row.prop_menu_enum(self, property="actionType", text=self.actionType)

class EditTriggeredObjectsButton(Operator):
    bl_idname = "object.edit_triggered_objects"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Edit triggered objects'

    def execute(self, context):
        object_selection_status = True
        bpy.context.scene.TmpObjectName = bpy.context.active_object.name
        return {'FINISHED'}
    
class SelectTriggeredObjectsOperator(Operator):
    bl_idname = "object.select_triggered_objects"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Select triggered objects'

    def execute(self, context):
        if object_selection_status:
            for obj in bpy.context.selected_objects:
                print(obj)
        return {'FINISHED'}
    

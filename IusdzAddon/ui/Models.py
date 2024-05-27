import bpy
from bpy.props import EnumProperty
from IusdzAddon.ui.StaticVars import trigger_types, action_types

class Trigger(bpy.types.PropertyGroup):
    affectedObjects = []
    def get_affected_objects_names_property(self, context):
        return [(object.name, object.name, object.name) for object in self.affectedObjects]
    affectedObjectsNames: bpy.props.EnumProperty(name="affectedObjectsNames", items=get_affected_objects_names_property)
    triggerType: EnumProperty(name="Trigger Type", items=trigger_types)
    
    def set_affected_objects(self, context):
        self.affectedObjects = [object for object in bpy.context.selected_objects]
    
    
class Action(bpy.types.PropertyGroup):
    affectedObjects = []
    def get_affected_objects_names_property(self, context):
        return [(object.name, object.name, object.name) for object in self.affectedObjects]
    affectedObjectsNames: bpy.props.EnumProperty(name="affectedObjectsNames", items=get_affected_objects_names_property)
    actionType: EnumProperty(name="Action Type", items=[('hide', 'Hide', 'Hide'), ('show', 'Show', 'Show')])
    duration: bpy.props.FloatProperty(name="Duration", default=0.0) # todo

  
class Interaction(bpy.types.PropertyGroup):
    iUsdzScene: bpy.props.PointerProperty(type=bpy.types.PropertyGroup)
    triggers: bpy.props.CollectionProperty(type=Trigger)
    actions: bpy.props.CollectionProperty(type=Action)
    
    def __init__(self, iUsdzScene):
        self.iUsdzScene = iUsdzScene


class IUsdzScene(bpy.types.PropertyGroup):
    interactions: bpy.props.CollectionProperty(type=Interaction)
    usdzActiveInteractionName: bpy.props.StringProperty(name="Active Interaction Name")
    usdzActiveTriggerName: bpy.props.StringProperty(name="Active Trigger Name")
    usdzActiveActionName: bpy.props.StringProperty(name="Active Action Name")
    
    objects = []

    def get_objects(self):
        return self.objects.copy()
    
    def add_object(self, object):
        self.objects.append(object)
        object.objectIUsdzScenesNames.add().name = self.name

    def add_all_objects(self, objects):
        self.objects.extend(objects)
        for object in objects:
            object.objectIUsdzScenesNames.add().name = self.name
    
    def clear_objects(self):
        for object in self.objects:
            object.objectIUsdzScenesNames.remove(self.name)
        self.objects.clear()

    def update_objects(self, source_objects):
        for object in self.objects.copy():
            if object not in source_objects:
                self.remove_object(object)
        
        objects_to_add = [object for object in source_objects if object not in self.objects]
        self.add_all_objects(objects_to_add)

    def remove_object(self, object):
        object.objectIUsdzScenesNames.remove(self.name)
        self.objects.remove(self)

    
    def select_objects(self):
        if len(self.objects) == 0:
            return
        
        bpy.context.view_layer.objects.active = self.objects[0]
        for object in self.objects:
            object.select_set(True)


class IUsdzSceneReference(bpy.types.PropertyGroup):
    empty = None
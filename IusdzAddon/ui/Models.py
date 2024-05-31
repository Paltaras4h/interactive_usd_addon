import bpy
from bpy.props import EnumProperty
from IusdzAddon.ui.StaticVars import trigger_types

class ObjectPointerProperty(bpy.types.PropertyGroup):
    object_ref: bpy.props.PointerProperty(type=bpy.types.Object)

class Trigger(bpy.types.PropertyGroup):
    affectedObjects: bpy.props.CollectionProperty(type=ObjectPointerProperty)
    def get_affected_objects_names_property(self, context):
        return [(object.name, object.name, object.name) for object in self.affectedObjects]
    affectedObjectsNames: bpy.props.EnumProperty(name="affectedObjectsNames", items=get_affected_objects_names_property)
    triggerType: EnumProperty(name="Trigger Type", items=trigger_types)

    def require_affection(self):
        return self.triggerType == 'click'
    
    def get_affected_objects(self):
        return list({object.object_ref for object in self.affectedObjects})
    
    def add_affected_object(self, object):
        self.affectedObjects.add().object_ref = object
        object.objectTriggerNames.add().name = self.name
        
    def remove_affected_object_by_ref(self, object):
        if object not in self.get_affected_objects():
            return
        object.objectTriggerNames.remove(object.objectTriggerNames.find(self.name))
        obj_index = [i for i, obj in enumerate(self.affectedObjects) if obj.object_ref == object][0]
        self.affectedObjects.remove(obj_index)

    def remove_affected_object_by_prop(self, object):
        if object not in self.get_affected_objects():
            return
        object.object_ref.objectTriggerNames.remove(object.objectTriggerNames.find(self.name))
        self.affectedObjects.remove(self.affectedObjects.find(object))
# --------------------------------------------------------------------------------------------
    def add_all_objects(self, objects):
        for object in objects:
            self.add_affected_object(object)

    def update_objects(self, source_objects):
        existing_objects = self.get_affected_objects()
        for object_ref in existing_objects:
            if object_ref not in source_objects:
                self.remove_affected_object_by_ref(object_ref)
        objects_to_add = [object for object in source_objects if object not in existing_objects]
        self.add_all_objects(objects_to_add)
    

    def clear_objects(self):
        for object in self.get_affected_objects():
            object.objectTriggerNames.remove(object.objectTriggerNames.find(self.name))
        self.affectedObjects.clear()

    def select_objects(self):
        if len(self.affectedObjects) == 0:
            return
        bpy.context.view_layer.objects.active = self.get_affected_objects()[0]
        for object in self.get_affected_objects():
            object.select_set(True)
# --------------------------------------------------------------------------------------------
    def cascade_delete(self):
        for object in self.get_affected_objects():
            object.objectTriggerNames.remove(object.objectTriggerNames.find(self.name))
        self.affectedObjects.clear()
    
class Action(bpy.types.PropertyGroup):
    affectedObjects: bpy.props.CollectionProperty(type=ObjectPointerProperty)
    def get_affected_objects_names_property(self, context):
        return [(object.name, object.name, object.name) for object in self.affectedObjects]
    affectedObjectsNames: bpy.props.EnumProperty(name="affectedObjectsNames", items=get_affected_objects_names_property)
    actionType: EnumProperty(name="Action Type", items=[('hide', 'Hide', 'Hide'), ('show', 'Show', 'Show')])
    duration: bpy.props.FloatProperty(name="Duration", default=0.0, min=0.0, max=100.0)

    def get_affected_objects(self):
        return list({object.object_ref for object in self.affectedObjects})
    
    def add_affected_object(self, object):
        self.affectedObjects.add().object_ref = object
        object.objectActionsNames.add().name = self.name

    def remove_affected_object_by_ref(self, object):
        if object not in self.get_affected_objects():
            return
        object.objectActionsNames.remove(object.objectActionsNames.find(self.name))
        obj_index = [i for i, obj in enumerate(self.affectedObjects) if obj.object_ref == object][0]
        self.affectedObjects.remove(obj_index)

    def remove_affected_object_by_prop(self, object):
        if object not in self.get_affected_objects():
            return
        object.object_ref.objectActionsNames.remove(object.objectActionsNames.find(self.name))
        self.affectedObjects.remove(self.affectedObjects.find(object))
# --------------------------------------------------------------------------------------------
    def add_all_objects(self, objects):
        for object in objects:
            self.add_affected_object(object)

    def update_objects(self, source_objects):
        existing_objects = self.get_affected_objects()
        for object_ref in existing_objects:
            if object_ref not in source_objects:
                self.remove_affected_object_by_ref(object_ref)
        objects_to_add = [object for object in source_objects if object not in existing_objects]
        self.add_all_objects(objects_to_add)

    def clear_objects(self):
        for object in self.get_affected_objects():
            object.objectActionsNames.remove(object.objectActionsNames.find(self.name))
        self.affectedObjects.clear()

    def select_objects(self):
        if len(self.affectedObjects) == 0:
            return
        bpy.context.view_layer.objects.active = self.get_affected_objects()[0]
        for object in self.get_affected_objects():
            object.select_set(True)
# --------------------------------------------------------------------------------------------
    def cascade_delete(self):
        for object in self.get_affected_objects():
            object.objectActionsNames.remove(object.objectActionsNames.find(self.name))
        self.affectedObjects.clear()
                
  
class Interaction(bpy.types.PropertyGroup):
    iUsdzSceneName: bpy.props.StringProperty(name="IUsdzScene Name")
    triggers: bpy.props.CollectionProperty(type=Trigger)
    actions: bpy.props.CollectionProperty(type=Action)

    def cascade_delete(self):
        for trigger in self.triggers:
            trigger.cascade_delete()
        for action in self.actions:
            action.cascade_delete()


class IUsdzScene(bpy.types.PropertyGroup):
    interactions: bpy.props.CollectionProperty(type=Interaction)
    usdzActiveInteractionName: bpy.props.StringProperty(name="Active Interaction Name")
    usdzActiveTriggerName: bpy.props.StringProperty(name="Active Trigger Name")
    usdzActiveActionName: bpy.props.StringProperty(name="Active Action Name")
    
    objects: bpy.props.CollectionProperty(type=ObjectPointerProperty)

    def icludes_removed_objects(self):
        return any([object.object_ref not in bpy.context.scene.objects.values() for object in self.objects])
    
    def get_objects(self):
        return list({object.object_ref for object in self.objects})
    
    def add_object(self, object):
        self.objects.add().object_ref = object
        object.objectIUsdzScenesNames.add().name = self.name

    def remove_object_by_ref(self, object):
        object.objectIUsdzScenesNames.remove(object.objectIUsdzScenesNames.find(self.name))
        obj_index = [i for i, obj in enumerate(self.objects) if obj.object_ref == object][0]
        self.objects.remove(obj_index)
        for interaction in self.interactions:
            for trigger in interaction.triggers:
                if trigger.require_affection():
                    trigger.remove_affected_object_by_ref(object)
            for action in interaction.actions:
                action.remove_affected_object_by_ref(object)

    def remove_object_by_prop(self, object):
        object.object_ref.objectIUsdzScenesNames.remove(object.object_ref.objectIUsdzScenesNames.find(self.name))
        self.objects.remove(self.objects.find(object))
        for interaction in self.interactions:
            interaction.cascade_delete()
# --------------------------------------------------------------------------------------------

    def add_all_objects(self, objects):
        for object in objects:
            self.add_object(object)

    def update_objects(self, source_objects):
        existing_objects = self.get_objects()
        for object_ref in existing_objects:
            if object_ref not in source_objects:
                self.remove_object_by_ref(object_ref)
        objects_to_add = [object for object in source_objects if object not in existing_objects]
        self.add_all_objects(objects_to_add)

    def clear_objects(self):
        for object in self.get_objects():
            object.objectIUsdzScenesNames.remove(object.objectIUsdzScenesNames.find(self.name))
        self.objects.clear()

    def select_objects(self):
        if len(self.objects) == 0:
            return
        bpy.context.view_layer.objects.active = self.get_objects()[0]
        for object in self.get_objects():
            object.select_set(True)


class NameReference(bpy.types.PropertyGroup):
    empty = None  


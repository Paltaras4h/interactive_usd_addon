import bpy
from IusdzAddon.ui.StaticVars import is_active_obj_selected

# static funcs
def addTrigger(name, triggerType):
    if name in [trigger.name for trigger in get_active_interaction().triggers]:# if get_active_interaction() is not None else [("--", "--", "add a trigger")]:
        # show window with error
        raise ValueError(f"Name {name} already exists")
    trigger = get_active_interaction().triggers.add()
    trigger.name = name
    trigger.triggerType = triggerType
    return trigger

def removeTrigger(trigger):
    get_active_interaction().triggers.remove(get_active_interaction().triggers.find(trigger.name))
    get_active_iUsdzScene().usdzActiveTriggerName = get_active_interaction().triggers[0].name if len(get_active_interaction().triggers) != 0 else ""

def addAction(name, actionType):
    if name in [action.name for action in get_active_interaction().actions]:# if get_active_interaction() is not None else [("--", "--", "add a trigger")]:
        # show window with error
        raise ValueError(f"Name {name} already exists")
    action = get_active_interaction().actions.add()
    action.name = name
    action.actionType = actionType
    return action

def removeAction(action):
    get_active_interaction().actions.remove(get_active_interaction().actions.find(action.name))
    get_active_iUsdzScene().usdzActiveActionName = get_active_interaction().actions[0].name if len(get_active_interaction().actions) != 0 else ""

def addInteraction(name):
    if name in [interaction.name for interaction in get_active_iUsdzScene().interactions]:
        # show window with error
        raise ValueError(f"Name {name} already exists")
    interaction = get_active_iUsdzScene().interactions.add()
    interaction.name = name
    return interaction

def removeInteraction(interaction):
    get_active_iUsdzScene().interactions.remove(get_active_iUsdzScene().interactions.find(interaction.name))
    get_active_iUsdzScene().usdzActiveInteractionName = get_active_iUsdzScene().interactions[0].name if len(get_active_iUsdzScene().interactions) != 0 else ""
    get_active_iUsdzScene().usdzActiveTriggerName = get_active_interaction().triggers[0].name if len(get_active_interaction().triggers) != 0 else ""
    get_active_iUsdzScene().usdzActiveActionName = get_active_interaction().actions[0].name if len(get_active_interaction().actions) != 0 else ""

def addIUsdzScene(name, objects):
    if name in [scene.name for scene in bpy.context.scene.allIUsdzScenes]:
        # show window with error
        raise ValueError(f"Name {name} already exists")
        
    scene = bpy.context.scene.allIUsdzScenes.add()
    scene.name = name

    if len(objects) != 0:
        scene.update_objects(objects)

    return scene

def removeIUsdzScene(iUsdzScene):
    bpy.context.scene.allIUsdzScenes.remove(bpy.context.scene.allIUsdzScenes.find(iUsdzScene.name))
    bpy.context.scene.activeIUsdzSceneName = bpy.context.scene.allIUsdzScenes[0].name if len(bpy.context.scene.allIUsdzScenes) != 0 else ""
    bpy.context.active_object.objectIUsdzScenesNames.remove(bpy.context.active_object.objectIUsdzScenesNames.find(iUsdzScene.name))



def get_interaction_by_name(name):
    try:
        return get_active_iUsdzScene().interactions[name]
    except KeyError:
        return None
    
def get_active_interaction():
    return get_interaction_by_name(get_active_iUsdzScene().usdzActiveInteractionName)

def get_trigger_by_name(name):
    try:
        return get_active_interaction().triggers[name]
    except KeyError:
        return None

def get_active_trigger():
    return get_trigger_by_name(get_active_iUsdzScene().usdzActiveTriggerName)

def get_action_by_name(name):
    try:
        return get_active_interaction().actions[name]
    except KeyError:
        return None

def get_active_action():
    return get_action_by_name(get_active_iUsdzScene().usdzActiveActionName)

def get_iUsdzScene_by_name(name):
    try:
        return bpy.context.scene.allIUsdzScenes[name]
    except KeyError:
        return None

def get_active_iUsdzScene():
    active_iUsdzScene = None
    if len(bpy.context.selected_objects)==0:
        if len(bpy.context.scene.allIUsdzScenes)>0:
            active_iUsdzScene = get_iUsdzScene_by_name(bpy.context.scene.activeIUsdzSceneName) if bpy.context.scene.activeIUsdzSceneName != "" else bpy.context.scene.allIUsdzScenes[0]
        else:
            active_iUsdzScene = None
    if is_active_obj_selected():
        obj_iUsdzScenes = get_object_iUsdzScenes(bpy.context.active_object)
        if len(obj_iUsdzScenes)>0:
            active_iUsdzScene = obj_iUsdzScenes[0]
        else:
            active_iUsdzScene = None
    return active_iUsdzScene

def get_iUsdzScene_by_name(name):
    try:
        return bpy.context.scene.allIUsdzScenes[name]
    except KeyError:
        return None
    
def get_object_iUsdzScenes(object):
    iUsdzScenes = []
    for iUsdzScene_ref in object.objectIUsdzScenesNames:
        if get_iUsdzScene_by_name(iUsdzScene_ref.name) is not None:
            iUsdzScenes.append(get_iUsdzScene_by_name(iUsdzScene_ref.name))
    return iUsdzScenes
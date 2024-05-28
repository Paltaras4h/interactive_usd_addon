import bpy
from IusdzAddon.ui.StaticVars import is_active_obj_selected, get_object_selection_status
from IusdzAddon.ui.Exceptions import ElementNotCreated

# static funcs
def addTrigger(name, triggerType):
    if name in [trigger.name for trigger in get_active_interaction().triggers]:
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
    if name in [action.name for action in get_active_interaction().actions]:
        # show window with error
        raise ValueError(f"Name {name} already exists")
    action = get_active_interaction().actions.add()
    action.name = name
    action.actionType = actionType
    return action

def removeAction(action):
    action.clear_objects()
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
    if len(get_active_iUsdzScene().interactions) != 0:
        get_active_iUsdzScene().usdzActiveInteractionName = get_active_iUsdzScene().interactions[0].name
        get_active_iUsdzScene().usdzActiveTriggerName = get_active_interaction().triggers[0].name if len(get_active_interaction().triggers) != 0 else ""
        get_active_iUsdzScene().usdzActiveActionName = get_active_interaction().actions[0].name if len(get_active_interaction().actions) != 0 else ""
    else: 
        get_active_iUsdzScene().usdzActiveInteractionName = ""

def addIUsdzScene(name, objects):
    if name in [scene.name for scene in bpy.context.scene.allIUsdzScenes]:
        # show window with error
        raise ValueError(f"Name {name} already exists")
        
    scene = bpy.context.scene.allIUsdzScenes.add()
    scene.name = name

    if len(objects) != 0:
        scene.add_all_objects(objects)

    return scene

def removeIUsdzScene(iUsdzScene):
    iUsdzScene.clear_objects()
    bpy.context.scene.allIUsdzScenes.remove(bpy.context.scene.allIUsdzScenes.find(iUsdzScene.name))
    bpy.context.scene.activeIUsdzSceneName = bpy.context.scene.allIUsdzScenes[0].name if len(bpy.context.scene.allIUsdzScenes) != 0 else ""



def get_interaction_by_name(name):
    try:
        return get_active_iUsdzScene().interactions[name]
    except KeyError:
        raise ElementNotCreated("interaction")
    
def get_active_interaction():
    try:
        return get_interaction_by_name(get_active_iUsdzScene().usdzActiveInteractionName)
    except ElementNotCreated as e:
        raise e

def get_trigger_by_name(name):
    try:
        return get_active_interaction().triggers[name]
    except KeyError:
        raise ElementNotCreated("trigger")

def get_active_trigger():
    try:
        return get_trigger_by_name(get_active_iUsdzScene().usdzActiveTriggerName)
    except ElementNotCreated as e:
        raise e

def get_action_by_name(name):
    try:
        return get_active_interaction().actions[name]
    except KeyError:
        raise ElementNotCreated("action")

def get_active_action():
    try:
        return get_action_by_name(get_active_iUsdzScene().usdzActiveActionName)
    except ElementNotCreated as e:
        raise e

def get_iUsdzScene_by_name(name):
    try:
        return bpy.context.scene.allIUsdzScenes[name]
    except KeyError:
        return None

def get_active_iUsdzScene():
    if get_object_selection_status() is not None:
        return get_iUsdzScene_by_name(bpy.context.scene.activeIUsdzSceneName)
    active_iUsdzScene = None
    if len(bpy.context.selected_objects)==0:
        if len(bpy.context.scene.allIUsdzScenes)>0:
            if bpy.context.scene.activeIUsdzSceneName != "":
                active_iUsdzScene = get_iUsdzScene_by_name(bpy.context.scene.activeIUsdzSceneName)
            else:
                active_iUsdzScene = bpy.context.scene.allIUsdzScenes[0]
                #bpy.context.scene.activeIUsdzSceneName = active_iUsdzScene.name
        else:
            active_iUsdzScene = None
    if is_active_obj_selected():
        obj_iUsdzScenes = get_object_iUsdzScenes(bpy.context.active_object)
        if len(obj_iUsdzScenes)>0:
            active_iUsdzScene = obj_iUsdzScenes[0]
        else:
            active_iUsdzScene = None
            
    return active_iUsdzScene
    
def get_object_iUsdzScenes(object):
    iUsdzScenes = []
    for iUsdzScene_ref in object.objectIUsdzScenesNames:
        scene = get_iUsdzScene_by_name(iUsdzScene_ref.name)
        if scene is not None:
            iUsdzScenes.append(scene)
    return iUsdzScenes


def get_active_element_by_type(element_type):
    if element_type == "iusdzscene":
        return get_active_iUsdzScene()
    elif element_type == "interaction":
        return get_active_interaction()
    elif element_type == "trigger":
        return get_active_trigger()
    elif element_type == "action":
        return get_active_action()
    return None
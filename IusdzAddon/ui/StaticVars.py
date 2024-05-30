import bpy

trigger_types = [
    ('click','Click','Triggers after clicking on selected object'),
    ('on_load', 'On load', 'Triggers right after loading the USDZ scene'),
]
action_types = [
    ('hide', 'Hide', 'Hide the selected object'),
    ('show', 'Show', 'Show the selected object'),
]


tmp_selected_objects = []
tmp_active_object = None

def get_tmp_selected_objects():
    return tmp_selected_objects

def set_tmp_selected_objects(objects):
    global tmp_selected_objects
    tmp_selected_objects = objects

def get_tmp_active_object():
    return tmp_active_object

def set_tmp_active_object(object):
    global tmp_active_object
    tmp_active_object = object


object_selection_status = None

def get_object_selection_status():
    return object_selection_status
def set_object_selection_status(status: str):
    '''status: "iusdzscene", "trigger", "action", None'''
    global object_selection_status
    object_selection_status = status


def is_active_obj_selected():
    return bpy.context.active_object is not None and bpy.context.active_object.select_get() == True


is_simulating_iusdz_scene = False
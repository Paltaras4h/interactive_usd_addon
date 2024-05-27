import bpy

trigger_types = [
    ('click','Click','Triggers after clicking on selected object'),
    ('on_load', 'On load', 'Triggers right after loading the USDZ scene'),
]
action_types = [
    ('hide', 'Hide', 'Hide the selected object'),
    ('show', 'Show', 'Show the selected object'),
]

def is_active_obj_selected():
    return bpy.context.active_object is not None and bpy.context.active_object.select_get() == True
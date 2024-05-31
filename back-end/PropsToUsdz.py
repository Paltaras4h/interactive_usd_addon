from pxr import Usd, UsdGeom, Sdf
import os
import json
import zipfile

cast_names={
    'click': 'TapGesture',
    'on_load': 'SceneTransition'
}

def extract_usdz(usdz_path, extract_dir):
    with zipfile.ZipFile(usdz_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"Extracted {usdz_path} to {extract_dir}")

def create_usdz(modified_usd, assets_dir, output_usdz):
    with zipfile.ZipFile(output_usdz, 'w') as zip_ref:
        zip_ref.write(modified_usd, os.path.basename(modified_usd))
        for folder_name, subfolders, filenames in os.walk(assets_dir):
            for filename in filenames:
                file_path = os.path.join(folder_name, filename)
                arcname = os.path.relpath(file_path, assets_dir)
                # don't save the usd file in the assets
                if arcname.endswith('.usda') or arcname.endswith('.usdc'):
                    continue
                zip_ref.write(file_path, arcname)
    print(f"Created {output_usdz} from {modified_usd} and assets in {assets_dir}")



def find_xform_path(stage, name):
    """
    Find the full path of an Xform object by its name in a USD stage.
    
    Args:
        stage (Usd.Stage): The USD stage to search.
        name (str): The name of the Xform object to find.
    
    Returns:
        str or None: The full path of the Xform object if found, or None if not found.
    """
    # Traverse the stage hierarchy
    for prim in stage.Traverse():
        if prim.IsA(UsdGeom.Xform) and prim.GetName() == name.replace(' ', '_').replace('.', '_'):
            return prim.GetPath()
    return None

def props_to_usdz(usdz_model_path, props):
    extract_usdz(usdz_model_path, './tmp_usdz_extract')
    usda = Usd.Stage.Open(usdz_model_path)
    # add interaction to usda root
    # Define a new scope
    main_scope = UsdGeom.Scope.Define(usda, f'{usda.GetDefaultPrim().GetPath()}/Behaviors')

    for interaction_data in props['interactions']:
        # add Preliminary_Behavior
        interaction = usda.DefinePrim(f'{main_scope.GetPath()}/{interaction_data["name"]}')
        interaction.SetTypeName('Preliminary_Behavior')
        interaction.CreateAttribute('exclusive', Sdf.ValueTypeNames.Bool).Set(False)
        # add rel list of actions
        interaction.CreateRelationship("actions").SetTargets([f'{interaction.GetPath()}/ActionRoot'])
        interaction.CreateRelationship("triggers").SetTargets([f'{interaction.GetPath()}/{trigger_data["name"]}' for trigger_data in interaction_data['triggers']])
        # add a uniform bool exclusive attribute
        for trigger_data in interaction_data['triggers']:
            # add Preliminary_Trigger
            trigger = usda.DefinePrim(f'{interaction.GetPath()}/{trigger_data["name"]}')
            trigger.SetTypeName('Preliminary_Trigger')
            # add token info:id
            trigger.CreateAttribute('info:id', Sdf.ValueTypeNames.Token).Set(cast_names[trigger_data['type']])
            # add rel list of objects
            if trigger_data['type'] == 'on_load':
                trigger.CreateAttribute('type', Sdf.ValueTypeNames.Token).Set("enter")
            else:
                objects_paths = [find_xform_path(usda, obj) for obj in trigger_data['affected_objects'] if find_xform_path(usda, obj) is not None] # can catch objects that are not in the model
                print(objects_paths)
                trigger.CreateRelationship("affectedObjects").SetTargets(objects_paths)

        # create action root
        action_root = usda.DefinePrim(f'{interaction.GetPath()}/ActionRoot')
        action_root.SetTypeName('Preliminary_Action')
        # add rel list of actions
        action_root.CreateRelationship("actions").SetTargets([f'{action_root.GetPath()}/{action_data["name"]}' for action_data in interaction_data['actions']])
        # add token info:id
        action_root.CreateAttribute('info:id', Sdf.ValueTypeNames.Token).Set("Group")
        action_root.CreateAttribute('loops', Sdf.ValueTypeNames.Bool).Set(False)
        action_root.CreateAttribute('performCount', Sdf.ValueTypeNames.Int).Set(1)
        action_root.CreateAttribute('type', Sdf.ValueTypeNames.Token).Set("parallel") # can be serial or parallel

        for action_data in interaction_data['actions']:
            # add Preliminary_Action
            action = usda.DefinePrim(f'{action_root.GetPath()}/{action_data["name"]}')
            action.SetTypeName('Preliminary_Action')
            # add rel list of objects
            objects_paths = [find_xform_path(usda, obj) for obj in action_data['affected_objects'] if find_xform_path(usda, obj) is not None]
            action.CreateRelationship("affectedObjects").SetTargets(objects_paths)
            if action_data['type'] == 'hide' or action_data['type'] == 'show':
                action.CreateAttribute('duration', Sdf.ValueTypeNames.Double).Set(action_data['duration'])
                action.CreateAttribute('easeType', Sdf.ValueTypeNames.Token).Set("inout")
                action.CreateAttribute('info:id', Sdf.ValueTypeNames.Token).Set("Visibility")
                action.CreateAttribute('motionType', Sdf.ValueTypeNames.Token).Set("pop")
                action.CreateAttribute('moveDistance', Sdf.ValueTypeNames.Double).Set(0.0)
                action.CreateAttribute('style', Sdf.ValueTypeNames.Token).Set("basic")
                action.CreateAttribute('type', Sdf.ValueTypeNames.Token).Set(action_data['type'])


    usda.GetRootLayer().Export('./back-end/model.usdc')
    print(usda.GetRootLayer().ExportToString())
    # convert usda to usdz
    create_usdz('./back-end/model.usdc', './tmp_usdz_extract', './back-end/model.usdz')
    

if __name__ == '__main__':
    # props_json = {
    #     "interactions": [
    #         {
    #             "name": "interaction1",
    #             "triggers": [
    #                 {
    #                     "name": "trigger1",
    #                     "type": "click",
    #                     "affected_objects": ["Cube_002", "Cube_001"]
    #                 }
    #             ],
    #             "actions": [
    #                 {
    #                     "name": "action1",
    #                     "type": "hide",
#                         "duration": 0.33,
    #                     "affected_objects": ["Cube_002", "Cube_001"]
    #                 }
    #             ]
    #         }
    #     ]
    # }
    props_json = None
    with open('./tmp_iusdz_model_interactions.json', 'r') as f:
        props_json = json.load(f)
    #usdz_model = None
    # with open('./IusdzAddon/tmp_iusdz_model.usdz', 'r') as f:
    #     usdz_model = f.read()
    #if usdz_model is None:
    #    raise ValueError("Model not found")
    
    #usda_model = None
    # run command to convert the model to usda:
    #os.system("usdcat -o back-end/model.usda back-end/model.usdz")
    #usda_model_path = './back-end/model.usdz'

    # model = Usd.Stage.Open(usdz_model)
    
    # model.ExportToString()
    # print(model)

    # with open('props.json', 'r') as f:
    #     props_json = f.read()
    props_to_usdz('./tmp_iusdz_model.usdz', props_json)

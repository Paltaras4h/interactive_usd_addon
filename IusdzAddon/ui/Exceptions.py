import bpy

class ElementNotCreated(Exception):
    def __init__(self, element_type):
        self.element_type = element_type
        self.message = f"Element of type '{element_type}' not created"
        super().__init__(self.message)
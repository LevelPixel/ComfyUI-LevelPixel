class FloatSlider:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "number":("FLOAT", {
                        "default": 0, 
                        "min": 0.0001,
                        "max": 1.0000,
                        "step": 0.0001, 
                        "display": "slider"
                    }),
                },
        }
    
    RETURN_TYPES = ("FLOAT",) 
    RETURN_NAMES = ('FLOAT',)
    FUNCTION = "run"

    CATEGORY = "LevelPixel/IO"

    INPUT_IS_LIST = False
    OUTPUT_IS_LIST = (False,)

    def run(self, number):
        if number < 0.0001:
            number = 0.0001
        elif number > 1.0000:
            number = 1.0000
        return (number,)
    
NODE_CLASS_MAPPINGS = {
    "SimpleFloatSlider|LP": FloatSlider,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleFloatSlider|LP": "Simple Float Slider [LP]",
}
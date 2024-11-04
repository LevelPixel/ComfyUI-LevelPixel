class FloatSlider:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "number":("FLOAT", {
                        "default": 0, 
                        "min": 0.000000,
                        "max": 1.000000,
                        "step": 0.000001, 
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
        if number < 0.000000:
            number = 0.000000
        elif number > 1.000000:
            number = 1.000000
        return (number,)
    
NODE_CLASS_MAPPINGS = {
    "SimpleFloatSlider|LP": FloatSlider,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleFloatSlider|LP": "Simple Float Slider [LP]",
}
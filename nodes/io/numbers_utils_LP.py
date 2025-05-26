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
    
class TenthsFloatSlider:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "number":("FLOAT", {
                        "default": 0, 
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.1, 
                        "display": "slider"
                    }),
                },
        }
    
    RETURN_TYPES = ("FLOAT",) 
    RETURN_NAMES = ('FLOAT',)
    FUNCTION = "tenthsFloatSlider"

    CATEGORY = "LevelPixel/IO"

    INPUT_IS_LIST = False
    OUTPUT_IS_LIST = (False,)

    def tenthsFloatSlider(self, number):
        if number < 0.0:
            number = 0.0
        elif number > 1.0:
            number = 1.0
        return (number,)

class HundredthsFloatSlider:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "number":("FLOAT", {
                        "default": 0, 
                        "min": 0.00,
                        "max": 1.00,
                        "step": 0.01, 
                        "display": "slider"
                    }),
                },
        }
    
    RETURN_TYPES = ("FLOAT",) 
    RETURN_NAMES = ('FLOAT',)
    FUNCTION = "hundredthsFloatSlider"

    CATEGORY = "LevelPixel/IO"

    INPUT_IS_LIST = False
    OUTPUT_IS_LIST = (False,)

    def hundredthsFloatSlider(self, number):
        if number < 0.00:
            number = 0.00
        elif number > 1.00:
            number = 1.00
        return (number,)
    
class Seed:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})}}

    RETURN_TYPES = ("INT",  )
    RETURN_NAMES = ("seed INT", )
    FUNCTION = "seedint"
    OUTPUT_NODE = True
    CATEGORY = "LevelPixel/IO"

    @staticmethod
    def seedint(seed):
        return (seed,)
    
NODE_CLASS_MAPPINGS = {
    "SimpleFloatSlider|LP": FloatSlider,
    "TenthsSimpleFloatSlider|LP": TenthsFloatSlider,
    "HundredthsSimpleFloatSlider|LP": HundredthsFloatSlider,
    "Seed|LP": Seed,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleFloatSlider|LP": "Simple Float Slider [LP]",
    "TenthsSimpleFloatSlider|LP": "Simple Float Slider - Tenths Step [LP]",
    "HundredthsSimpleFloatSlider|LP": "Simple Float Slider - Hundredths Step [LP]",
    "Seed|LP": "Seed [LP]",
}
import time

class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

any = AnyType("*")

class Delay:    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input": (any, {"defaultInput": True}),
                "delay_seconds": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "step": 0.1
                }),
            },
        }

    RETURN_TYPES = (any,)
    RETURN_NAMES = ("output",)
    FUNCTION = "add_delay"
    CATEGORY = "LevelPixel/Unloaders"
    
    def add_delay(self, input, delay_seconds):
        delay_text = f"{delay_seconds:.1f} second{'s' if delay_seconds != 1 else ''}"
        print(f"[Delay Node] Starting delay of {delay_text}")
        time.sleep(delay_seconds)
        print(f"[Delay Node] Delay of {delay_text} completed")
        return (input,)

NODE_CLASS_MAPPINGS = {
    "Delay|LP": Delay,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Delay|LP": "Delay [LP]",
}


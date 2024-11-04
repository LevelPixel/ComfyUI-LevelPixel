import os
import json

tag_category = json.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"tag_category.json")))

def category_for_tags(tags):
    tags = [tag.strip() for tag in tags.replace(".", ",").replace("\n", ",").split(",")]
    tags2 = [tag.replace(" ", "_").lower() for tag in tags]

    result = []
    for i, tag2 in enumerate(tags2):
        if tag2 in tag_category:
            category_list = tag_category.get(tag2, [])
            for category in category_list:
                if category not in result:
                    result.append(category)
                    break

    return ", ".join(result)

class TagCategoryFilter:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", {"default": ""}),
                "include_categories": ("STRING", {"default": ""}),
                "exclude_categories": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag_category"

    CATEGORY = "LevelPixel/Tags"

    OUTPUT_NODE = True

    def tag_category(self, tags,  include_categories="", exclude_categories=""):
        targets = []
        exclude_targets = []

        if not include_categories:
            print("categories - ", category_for_tags(tags))
            include_categories = category_for_tags(tags)

        include_categories = include_categories.strip()
        if include_categories:
            targets += [category.strip() for category in include_categories.replace("\n",",").split(",")]

        if exclude_categories:
            exclude_targets = [category.strip() for category in exclude_categories.replace("\n",",").split(",")]
            targets = [target for target in targets if target not in exclude_targets]
        
        print("targets", targets)

        tags = [tag.strip() for tag in tags.replace(".", ",").replace("\n", ",").split(",")]
        tags2 = [tag.replace(" ", "_").lower() for tag in tags]

        result = []
        for i, tag2 in enumerate(tags2):
            if tag2 in tag_category:
                category_list = tag_category.get(tag2, [])

                for category in category_list:
                    if category in exclude_targets:
                        break
                else:
                    for category in category_list:
                        if '*' in include_categories or ( category in targets and tags[i] not in result ):
                            result.append(tags[i])
                            break

        return (", ".join(result),)
    
class TagCategoryKeeper:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", {"default": ""}),
                "include_categories": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag_keeper"

    CATEGORY = "LevelPixel/Tags"

    OUTPUT_NODE = True

    def tag_keeper(self, tags,  include_categories=""):

        targets = []

        include_categories = include_categories.strip()
        if include_categories:
            targets += [category.strip() for category in include_categories.replace("\n",",").split(",")]
        
        print("targets", targets)

        tags = [tag.strip() for tag in tags.replace(".", ",").replace("\n", ",").split(",")]
        tags2 = [tag.replace(" ", "_").lower() for tag in tags]

        result = []
        for i, tag2 in enumerate(tags2):
            if tag2 in tag_category:
                category_list = tag_category.get(tag2, [])
                for category in category_list:
                    if '*' in include_categories or ( category in targets and tags[i] not in result ):
                        result.append(tags[i])
                        break

        return (", ".join(result),)
    
class TagCategoryRemover:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", {"default": ""}),
                "exclude_categories": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag_remover"

    CATEGORY = "LevelPixel/Tags"

    OUTPUT_NODE = True

    def tag_remover(self, tags, exclude_categories=""):

        targets = []
        exclude_targets = []

        if exclude_categories:
            exclude_targets = [category.strip() for category in exclude_categories.replace("\n",",").split(",")]
            targets = [target for target in targets if target not in exclude_targets]
        
        print("targets", targets)

        tags = [tag.strip() for tag in tags.replace(".", ",").replace("\n", ",").split(",")]
        tags2 = [tag.replace(" ", "_").lower() for tag in tags]

        result = []
        for i, tag2 in enumerate(tags2):
            if tag2 in tag_category:
                category_list = tag_category.get(tag2, [])

                for category in category_list:
                    if category in exclude_targets:
                        break
                    else:
                        if tags[i] not in result:
                            result.append(tags[i])
                        break

        return (", ".join(result),)

class TagSwitcher:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_tags": ("STRING", {"default": ""}),
                "default_image": ("IMAGE", {"default": ""}),
                "tags1": ("STRING", {"default": ""}),
                "image1": ("IMAGE", {"default": ""}),
                "any1": ("BOOLEAN", {"default": True}),
            },
            "optional": {   
                "tags2": ("STRING", {"default": ""}),
                "image2": ("IMAGE", {"default": ""}),
                "any2": ("BOOLEAN", {"default": True}),
                "tags3": ("STRING", {"default": ""}),
                "image3": ("IMAGE", {"default": ""}),
                "any3": ("BOOLEAN", {"default": True}),
                "tags4": ("STRING", {"default": ""}),
                "image4": ("IMAGE", {"default": ""}),
                "any4": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    FUNCTION = "tag_switcher"

    CATEGORY = "LevelPixel/Tags"

    OUTPUT_NODE = True

    def _tag_split(self, tags: str) -> list:
        return [tag.strip().replace("_", " ").lower().strip() for tag in tags.replace(".",",").replace("\n",",").split(",")]

    def tag_switcher(self, input_tags="", default_image=None, tags1="", image1=None, any1=True, tags2="", image2=None, any2=True, tags3="", image3=None, any3=True, tags4="", image4=None, any4=True):
        input_tags = self._tag_split(input_tags)

        target_tags = []
        tags1 = set(self._tag_split(tags1))
        target_tags.append((tags1, image1, any1))

        tags2 = set(self._tag_split(tags2))
        target_tags.append((tags2, image2, any2))

        tags3 = set(self._tag_split(tags3))
        target_tags.append((tags3, image3, any3))

        tags4 = set(self._tag_split(tags4))
        target_tags.append((tags4, image4, any4))

        for tags, image, any_flag in target_tags:
            if any_flag:
                if any(tag in tags for tag in input_tags):
                    return (image,)
            else:
                if all(tag in input_tags for tag in tags):
                    return (image,)

        return (default_image,)


class TagMerger:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags1": ("STRING", {"default": ""}),
                "tags2": ("STRING", {"default": ""}),
                "under_score": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag_merger"

    CATEGORY = "LevelPixel/Tags"

    OUTPUT_NODE = True

    def tag_merger(self, tags1:str, tags2:str, under_score=True):
        tags1 = [tag.strip().replace(" ", "_").lower() for tag in tags1.replace(".",",").replace("\n",",").split(",")]
        tags2 = [tag.strip().replace(" ", "_").lower() for tag in tags2.replace(".",",").replace("\n",",").split(",")]

        tags = tags1 + list(set(tags2) - set(tags1))

        tags = [tag for tag in tags if tag]

        if not under_score:
            tags = [tag.replace("_", " ") for tag in tags]

        return (", ".join(tags),)


class TagRemover:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", {"default": ""}),
                "exclude_tags": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag_remover"

    CATEGORY = "LevelPixel/Tags"

    OUTPUT_NODE = True

    def tag_remover(self, tags:str, exclude_tags:str=""):
        tags = [tag.strip() for tag in tags.replace("\n",",").split(",")]
        tags2 = [tag.replace(" ", "_").lower().strip() for tag in tags]

        exclude_tags = [tag.strip() for tag in exclude_tags.replace("\n",",").split(",")]
        exclude_tags2 = [tag.replace(" ", "_").lower().strip() for tag in exclude_tags]

        result = []
        for i, tag2 in enumerate(tags2):
            if tag2 not in exclude_tags2:
                result.append(tags[i])
        
        return (", ".join(result),)


class TagReplace:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", {"default": ""}),
                "replace_tags": ("STRING", {"default": ""}),
                "match": ("FLOAT", {"default": 0.3}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag_replace"

    CATEGORY = "LevelPixel/Tags"

    OUTPUT_NODE = True

    def _get_categories(self, tag: str) -> set:
        return set(tag_category.get(tag, []))

    def _category_match_percentage(self, categories1: set, categories2: set) -> float:
        if not categories1 or not categories2:
            return 0
        intersection = categories1.intersection(categories2)
        union = categories1.union(categories2)
        return len(intersection) / len(union)

    def tag_replace(self, tags:str, replace_tags:str="", match:float=0.3):
        tags = [tag.strip() for tag in tags.replace("\n",",").split(",")]
        tags_normalized = [tag.replace(" ", "_").lower().strip() for tag in tags]

        replace_tags = [tag.strip() for tag in replace_tags.replace("\n",",").split(",")]
        replace_tags_normalized = [tag.replace(" ", "_").lower().strip() for tag in replace_tags]
        replace_tags_used = {tag:False for tag in replace_tags_normalized}

        result = []
        for i, tag in enumerate(tags_normalized):
            tag_categories = self._get_categories(tag)
            best_match_tag = None
            best_match_tag_id = None
            best_match_percentage = 0

            for k, replace_tag in enumerate(replace_tags_normalized):
                replace_categories = self._get_categories(replace_tag)
                match_percentage = self._category_match_percentage(tag_categories, replace_categories)

                if match_percentage and match_percentage > best_match_percentage:
                    best_match_percentage = match_percentage
                    best_match_tag = replace_tag
                    replace_tags_used[replace_tag] = True
                    best_match_tag_id = k

            
            if best_match_tag and best_match_percentage >= match:
                result.append(replace_tags[best_match_tag_id])
            else:
                result.append(tags[i])

        extra_tags = [replace_tag for replace_tag, used in replace_tags_used.items() if not used]
        result.extend(extra_tags)
        
        return (", ".join(result),)
    
class TagCategory:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag_category_info"

    CATEGORY = "LevelPixel/Tags"

    OUTPUT_NODE = True

    def tag_category_info(self, tags):
        tags = [tag.strip() for tag in tags.replace(".", ",").replace("\n", ",").split(",")]
        tags2 = [tag.replace(" ", "_").lower() for tag in tags]

        result = []
        for i, tag2 in enumerate(tags2):
            if tag2 in tag_category:
                category_list = tag_category.get(tag2, [])
                for category in category_list:
                    if category not in result:
                        result.append(category)
                        break

        return (", ".join(result),)

NODE_CLASS_MAPPINGS = {
    "TagCategory|LP": TagCategory,
    "TagCategoryFilter|LP": TagCategoryFilter,
    "TagCategoryKeeper|LP": TagCategoryKeeper,
    "TagCategoryRemover|LP": TagCategoryRemover,
    "TagSwitcher|LP": TagSwitcher,
    "TagMerger|LP": TagMerger,
    "TagReplace|LP": TagReplace,
    "TagRemover|LP": TagRemover,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TagCategory|LP": "Tag Category [LP]",
    "TagCategoryFilter|LP": "Tag Category Filter [LP]",
    "TagCategoryKeeper|LP": "Tag Category Keeper [LP]",
    "TagCategoryRemover|LP": "Tag Category Remover [LP]",
    "TagSwitcher|LP": "Tag Switcher [LP]",
    "TagMerger|LP": "Tag Merger [LP]",
    "TagReplace|LP": "Tag Replace [LP]",
    "TagRemover|LP": "Tag Remover [LP]"
}

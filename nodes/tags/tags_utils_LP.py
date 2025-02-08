import os
import json
import string
import re

tag_category = json.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"tag_category.json")))
banned_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),"banned_tags.txt")

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
    
def parse_tags(text):
    return [tag.strip() for tag in text.split(",") if tag.strip() != ""]

def update_scores(scores, text, base, bonus_first, bonus_4_10, include_new=True):
    tags = parse_tags(text)
    for i, tag in enumerate(tags):
        if i < 3:
            points = base + bonus_first
        elif i < 10:
            points = base + bonus_4_10
        else:
            points = base

        if len(tag.split()) == 1:
            points += 1

        if tag in scores:
            scores[tag] += points
        else:
            if include_new:
                scores[tag] = points

class ResortingTags:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "priority_texts": ("LIST", {"forceInput": True}),
                "inclusive_texts": ("LIST", {"forceInput": True}),
                "auxiliary_texts": ("LIST", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("tags TEXT", "tags_with_rating TEXT",)

    FUNCTION = "resorting_tags"

    CATEGORY = "LevelPixel/Tags"

    def resorting_tags(self, priority_texts, inclusive_texts, auxiliary_texts):
        scores = {}
        for text in priority_texts:
            update_scores(scores, text, base=3, bonus_first=2, bonus_4_10=1, include_new=True)

        for text in inclusive_texts:
            update_scores(scores, text, base=2, bonus_first=2, bonus_4_10=1, include_new=True)

        for text in auxiliary_texts:
            update_scores(scores, text, base=1, bonus_first=1, bonus_4_10=0, include_new=False)

        sorted_tags = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        result = ", ".join(tag for tag, _ in sorted_tags)
        rating_text = ", ".join(f"{tag}:{points}" for tag, points in sorted_tags)

        print("Result tags:")
        print(result)
        print("\nRating result tags:")
        print(rating_text)

        return (result, rating_text,)

class RemoveDuplicateTags:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "forceInput": True})
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("tags TEXT",)

    FUNCTION = "remove_duplicate_tags"

    CATEGORY = "LevelPixel/Tags"
    
    def remove_duplicate_tags(self, text):
        tags = text.split(',')
        seen = set()
        unique_tags = []
        
        for tag in tags:
            tag_clean = tag.strip()
            if tag_clean and tag_clean not in seen:
                seen.add(tag_clean)
                unique_tags.append(tag_clean)
        
        result = ", ".join(unique_tags) + ","

        return (result,)

def is_english_core(core: str) -> bool:
    for ch in core:
        if ch.isalpha() and ch not in string.ascii_letters:
            return False
    return True

class KeepOnlyEnglishTags:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "forceInput": True})
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("tags TEXT",)

    FUNCTION = "keep_only_english_tags"

    CATEGORY = "LevelPixel/Tags"
    
    def keep_only_english_tags(self, text):
        tags = [tag.strip() for tag in text.split(',') if tag.strip()]
        
        filtered_tags = [tag for tag in tags if is_english_core(tag)]

        result = ', '.join(filtered_tags)
        if text.strip()[-1] == ',':
            result += ','

        return (result,)
    
class RemoveBannedTagsFromTags:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "forceInput": True})
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("tags TEXT",)

    FUNCTION = "remove_banned_tags_from_tags"

    CATEGORY = "LevelPixel/Tags"
    
    def remove_banned_tags_from_tags(self, text):
        with open(banned_file, "r", encoding="utf-8") as f:
            banned_tags = {line.strip().lower() for line in f if line.strip()}

        text_lower = text.lower()
        tokens = text_lower.split(',')
        wrapper_chars = '\"\'“”‘’()[]{}<>«»'

        kept_tokens = []
        for token in tokens:
            token_for_check = token.strip()
            while token_for_check and token_for_check[0] in wrapper_chars:
                token_for_check = token_for_check[1:]
            while token_for_check and token_for_check[-1] in wrapper_chars:
                token_for_check = token_for_check[:-1]

            if token_for_check in banned_tags:
                continue
            else:
                kept_tokens.append(token)

        result = ",".join(kept_tokens)

        return (result,)
    
class RemoveBannedTagsFromText:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "forceInput": True})
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("tags TEXT",)

    FUNCTION = "remove_banned_tags_from_text"

    CATEGORY = "LevelPixel/Tags"
    
    def remove_banned_tags_from_text(self, text):
        with open(banned_file, "r", encoding="utf-8") as f:
            banned_tags = [line.strip() for line in f if line.strip()]

        encl_chars = r'\"\'‘’“”«»\(\)\[\]\{\}<>'

        for tag in banned_tags:
            pattern = re.compile(
                r'(?<!\w)[' + re.escape(encl_chars) + r']*' + 
                re.escape(tag.lower()) +
                r'[' + re.escape(encl_chars) + r']*(?!\w)',
                re.IGNORECASE
            )
            text = pattern.sub("", text)
        
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s+([,.;?!])', r'\1', text)
        result = text.strip()

        return (result,)


NODE_CLASS_MAPPINGS = {
    "TagCategory|LP": TagCategory,
    "TagCategoryFilter|LP": TagCategoryFilter,
    "TagCategoryKeeper|LP": TagCategoryKeeper,
    "TagCategoryRemover|LP": TagCategoryRemover,
    "TagSwitcher|LP": TagSwitcher,
    "TagMerger|LP": TagMerger,
    "TagReplace|LP": TagReplace,
    "TagRemover|LP": TagRemover,
    "ResortingTags|LP": ResortingTags,
    "RemoveDuplicateTags|LP": RemoveDuplicateTags,
    "KeepOnlyEnglishTags|LP": KeepOnlyEnglishTags,
    "RemoveBannedTagsFromTags|LP": RemoveBannedTagsFromTags,
    "RemoveBannedTagsFromText|LP": RemoveBannedTagsFromText,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TagCategory|LP": "Tag Category [LP]",
    "TagCategoryFilter|LP": "Tag Category Filter [LP]",
    "TagCategoryKeeper|LP": "Tag Category Keeper [LP]",
    "TagCategoryRemover|LP": "Tag Category Remover [LP]",
    "TagSwitcher|LP": "Tag Switcher [LP]",
    "TagMerger|LP": "Tag Merger [LP]",
    "TagReplace|LP": "Tag Replace [LP]",
    "TagRemover|LP": "Tag Remover [LP]",
    "ResortingTags|LP": "Resorting Tags [LP]",
    "RemoveDuplicateTags|LP": "Remove Duplicate Tags [LP]",
    "KeepOnlyEnglishTags|LP": "Keep Only English Tags [LP]",
    "RemoveBannedTagsFromTags|LP": "Remove Banned Tags From Tags [LP]",
    "RemoveBannedTagsFromText|LP": "Remove Banned Tags From Text [LP]",
}

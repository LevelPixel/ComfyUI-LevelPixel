import { app } from "../../../scripts/app.js";

// Some fragments of this code are from https://github.com/LucianoCirino/efficiency-nodes-comfyui

function inpaintCropStitchHandler(node) {
    if (node.comfyClass == "InpaintCrop|LP") {
        toggleWidget(node, findWidgetByName(node, "target_size"));
        toggleWidget(node, findWidgetByName(node, "aspect_ratio_limit"));
        toggleWidget(node, findWidgetByName(node, "force_width"));
        toggleWidget(node, findWidgetByName(node, "force_height"));
        if (findWidgetByName(node, "mode").value == "none") {
            toggleWidget(node, findWidgetByName(node, "target_size"), false);
            toggleWidget(node, findWidgetByName(node, "aspect_ratio_limit"), false);
            toggleWidget(node, findWidgetByName(node, "force_width"), false);
            toggleWidget(node, findWidgetByName(node, "force_height"), false);
        }
        else if (findWidgetByName(node, "mode").value == "input size parameters") {
            toggleWidget(node, findWidgetByName(node, "target_size"), false);
            toggleWidget(node, findWidgetByName(node, "aspect_ratio_limit"), false);
            toggleWidget(node, findWidgetByName(node, "force_width"), false);
            toggleWidget(node, findWidgetByName(node, "force_height"), false);
        }
        else if (findWidgetByName(node, "mode").value == "aspect size") {
            toggleWidget(node, findWidgetByName(node, "target_size"), true);
            toggleWidget(node, findWidgetByName(node, "aspect_ratio_limit"), true);
            toggleWidget(node, findWidgetByName(node, "force_width"), false);
            toggleWidget(node, findWidgetByName(node, "force_height"), false);
        }
        else if (findWidgetByName(node, "mode").value == "forced size") {
            toggleWidget(node, findWidgetByName(node, "target_size"), false);
            toggleWidget(node, findWidgetByName(node, "aspect_ratio_limit"), false);
            toggleWidget(node, findWidgetByName(node, "force_width"), true);
            toggleWidget(node, findWidgetByName(node, "force_height"), true);
        }
    }
    return;
}

function resizeImageAndMasksHandler(node) {
    if (node.comfyClass == "ResizeImageAndMasks|LP") {
        toggleWidget(node, findWidgetByName(node, "preresize_min_width"));
        toggleWidget(node, findWidgetByName(node, "preresize_min_height"));
        toggleWidget(node, findWidgetByName(node, "preresize_max_width"));
        toggleWidget(node, findWidgetByName(node, "preresize_max_height"));
        if (findWidgetByName(node, "preresize_mode").value == "ensure minimum resolution") {
            toggleWidget(node, findWidgetByName(node, "preresize_min_width"), true);
            toggleWidget(node, findWidgetByName(node, "preresize_min_height"), true);
            toggleWidget(node, findWidgetByName(node, "preresize_max_width"), false);
            toggleWidget(node, findWidgetByName(node, "preresize_max_height"), false);
        }
        else if (findWidgetByName(node, "preresize_mode").value == "ensure minimum and maximum resolution") {
            toggleWidget(node, findWidgetByName(node, "preresize_min_width"), true);
            toggleWidget(node, findWidgetByName(node, "preresize_min_height"), true);
            toggleWidget(node, findWidgetByName(node, "preresize_max_width"), true);
            toggleWidget(node, findWidgetByName(node, "preresize_max_height"), true);
        }
        else if (findWidgetByName(node, "preresize_mode").value == "ensure maximum resolution") {
            toggleWidget(node, findWidgetByName(node, "preresize_min_width"), false);
            toggleWidget(node, findWidgetByName(node, "preresize_min_height"), false);
            toggleWidget(node, findWidgetByName(node, "preresize_max_width"), true);
            toggleWidget(node, findWidgetByName(node, "preresize_max_height"), true);
        }
    }
    return;
}

const findWidgetByName = (node, name) => {
    return node.widgets ? node.widgets.find((w) => w.name === name) : null;
};

function toggleWidget(node, widget, show = false, suffix = "") {
    if (!widget) return;
    widget.disabled = !show
    widget.linkedWidgets?.forEach(w => toggleWidget(node, w, ":" + widget.name, show));
}   

app.registerExtension({
    name: "levelpixel.showcontrol",
    nodeCreated(node) {
        if (!node.comfyClass.startsWith("Inpaint") && !node.comfyClass.startsWith("ResizeImageAndMasks")) {
            return;
        }

        inpaintCropStitchHandler(node);
        resizeImageAndMasksHandler(node);
        for (const w of node.widgets || []) {
            let widgetValue = w.value;
            let originalDescriptor = Object.getOwnPropertyDescriptor(w, 'value') || 
                Object.getOwnPropertyDescriptor(Object.getPrototypeOf(w), 'value');
            if (!originalDescriptor) {
                originalDescriptor = Object.getOwnPropertyDescriptor(w.constructor.prototype, 'value');
            }

            Object.defineProperty(w, 'value', {
                get() {
                    let valueToReturn = originalDescriptor && originalDescriptor.get
                        ? originalDescriptor.get.call(w)
                        : widgetValue;

                    return valueToReturn;
                },
                set(newVal) {
                    if (originalDescriptor && originalDescriptor.set) {
                        originalDescriptor.set.call(w, newVal);
                    } else { 
                        widgetValue = newVal;
                    }

                    inpaintCropStitchHandler(node);
                    resizeImageAndMasksHandler(node);
                }
            });
        }
    }
});

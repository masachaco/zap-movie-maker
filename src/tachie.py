import psd_tools

target_layers = []

def show_visible_layer_list(kaisou, layer,route):
    if layer.is_group():
        for k, child in enumerate(layer):
            show_visible_layer_list(kaisou+1, child,route+"/"+child.name)
    else:
        if layer.is_visible():
            print(route)


def show_layer_list(kaisou, layer,route):
    if layer.is_group():
        # print("".join(([" "]*kaisou)), layer.name, layer.kind)
        for k, child in enumerate(layer):
            show_layer_list(kaisou+1, child,route+"/"+child.name)
    else:
        print(route)

def set_visibility(kaisou, layer,route):
    if layer.is_group():
        # print("".join(([" "]*kaisou)), layer.name, layer.kind)
        for k, child in enumerate(layer):
            set_visibility(kaisou+1, child,route+"/"+child.name)
    else:
        if route in target_layers:
            layer.visible = True
        else:
            layer.visible = False

def export(psd):
    for k, layer in enumerate(psd):
        set_visibility(0, layer,layer.name)
    psd.composite(force=True).save('./sample.png')

def show_layers(psd):
    for k, layer in enumerate(psd):
        show_layer_list(0, layer,layer.name)

def show_visible_layers(psd):
    for k, layer in enumerate(psd):
        show_visible_layer_list(0, layer,layer.name)

def main():
    global target_layers
    target_layers = [

    ]
    psd = psd_tools.PSDImage.open('')
    export(psd)
    # show_layers(psd)
    # show_visible_layers(psd)

main()
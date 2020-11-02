import PySimpleGUI as sg
import struct
from Model import Sh2Model
from Field import FieldType
from SimpleMaterial import SimpleMaterial

tooltips = [' Pointer to the next material (Relative start of this material) \n',
            ' Reserved, zero in all .mdl files ',
            ' Number of elements in first u16 array, array purpose unknown ',
            ' Pointer to first array of u16s, always 128 (Relative start of this material) ',
            ' Number of elements in second u16 array ',
            ' Pointer to second array of u16s (Relative start of this material) ',
            ' Number of elements in third u16 array, always 1 ',
            ' Pointer to third array of u16s (Relative start of this material) ',
            ' Pointer to array of 4 u8s containing values for ADDRESSU, ADDRESSV, MAGFILTER and MINFILTER sampler states ',
            ' Determines which of the diffuse/ambient/specular color arrays are passed to vertex/pixel shaders \n\n'
            ' 1 = No lighting (fullbright), ignores diffuse, ambient and specular color \n'
            ' 2 = Matte, respects diffuse and ambient color, no specular highlight \n'
            ' 3 = Seems the same as 2, but always paired with non-zero specular color, unk_diffuse_float and unk_ambient_float \n'
            ' 4 = Glossy, respects diffuse, ambient and specular colors \n'
            ' Any other value = Defaults to type 2/3 behavior ',
            ' Used to identify pieces of the model so their visibility can be toggled \n'
            ' e.g. Swapping James\'s hand pose when using different weapons \n\n'
            ' 0 = Always visible ',
            ' 0 = CULLMODE set to D3DCULL_NONE, TEXTUREFACTOR Alpha set to 33 \n'
            ' 1 = CULLMODE set to D3DCULL_CW, TEXTUREFACTOR Alpha set to 25 ',
            ' Purpose unknown, affects diffuse color somehow, always 0 or positive (vs float register 43[3]) ',
            ' Purpose unknown, affects ambient color somehow, always 0 or negative (vs float register 44[3]) ',
            ' Controls the size of the specular highlight, larger value = smaller highlight (Distance from light source?) \n'
            ' Only used when material_type = 4 ',
            ' Reserved, zero in all .mdl files, generated value placed here at run-time ',
            ' Reserved, zero in all .mdl files ',
            ' Controls diffuse color (X,R,G,B) \n Range = [0.0 - 1.0] ',
            ' Controls diffuse color (R,G,B) \n Range = [0.0 - 1.0] ', ' ', ' ',
            ' Controls ambient color (X,R,G,B) \n Range = [0.0 - 1.0] ',
            ' Controls ambient color (R,G,B) \n Range = [0.0 - 1.0] ', ' ', ' ',
            ' Controls color of specular highlights (X,R,G,B) \n Range = [0.0 - 128.0] ',
            ' Controls color of specular highlights (R,G,B) \n Range = [0.0 - 128.0] ', ' ', ' ',
            ' Reserved, zero in all .mdl files ',
            ' Index into some array of u16s (An index buffer?) ',
            ' Number of indices to use (A buffer with length this*2 is malloc\'d at runtime) ',
            ' Reserved, zero in all .mdl files ',
            #' First array of u16s, purpose unknown ',
            #' Second array of u16s, purpose unknown ',
            #' Third array of u16s, always length 1 in retail .mdls, purpose unknown ',
            ' Texture-address mode for the u coordinate \n\n'
            ' 1 = D3DTADDRESS_WRAP \n'
            ' 2 = D3DTADDRESS_MIRROR \n'
            ' 3 = D3DTADDRESS_CLAMP \n'
            ' 4 = D3DTADDRESS_BORDER \n'
            ' 5 = D3DTADDRESS_MIRRORONCE ',
            ' Texture-address mode for the v coordinate \n\n'
            ' 1 = D3DTADDRESS_WRAP \n'
            ' 2 = D3DTADDRESS_MIRROR \n'
            ' 3 = D3DTADDRESS_CLAMP \n'
            ' 4 = D3DTADDRESS_BORDER \n'
            ' 5 = D3DTADDRESS_MIRRORONCE ',
            ' Texture filtering mode used for magnification \n\n'
            ' 0 = D3DTEXF_NONE \n'
            ' 1 = D3DTEXF_POINT \n'
            ' 2 = D3DTEXF_LINEAR \n'
            ' 3 = D3DTEXF_ANISOTROPIC \n'
            ' 4 = D3DTEXF_PYRAMIDALQUAD \n'
            ' 5 = D3DTEXF_GAUSSIANQUAD \n'
            ' 6 = D3DTEXF_CONVOLUTIONMONO ',
            ' Texture filtering mode used for minification \n\n'
            ' 0 = D3DTEXF_NONE \n'
            ' 1 = D3DTEXF_POINT \n'
            ' 2 = D3DTEXF_LINEAR \n'
            ' 3 = D3DTEXF_ANISOTROPIC \n'
            ' 4 = D3DTEXF_PYRAMIDALQUAD \n'
            ' 5 = D3DTEXF_GAUSSIANQUAD \n'
            ' 6 = D3DTEXF_CONVOLUTIONMONO ']


def open_model(filename):
    if filename == '' or filename is None:
        return None, None, None

    with open(filename, 'rb') as f:
        file_data = f.read()

        f.seek(0)
        model = Sh2Model(f)

    ptr_table = model.child_at(0)
    material_list_og = ptr_table.get_children()

    # Convert to SimpleMaterials for easier display
    material_list = []
    for mat in material_list_og:
        material_list.append(SimpleMaterial(mat))

    return filename, material_list, file_data


def create_layout(full=True):
    menu_def = [['File', ['Open...', 'Save', 'Save As...', 'Exit']],
                ['Advanced', ['Toggle Hidden Fields']]]

    mat_combo = []
    for i in range(len(materials)):
        mat_combo.append(f'{i} - [File Offset: 0x{materials[i].at(0).offset:X}]')

    entry_keys.clear()
    if full:
        for i in range(37):
            entry_keys.append(f'-ENTRY{i}-')
    else:
        for i in range(37):
            if i in {9, 10, 11, 12, 13, 14, 18, 19, 20, 22, 23, 24, 26, 27, 28, 33, 34, 35, 36}:
                entry_keys.append(f'-ENTRY{i}-')
            else:
                entry_keys.append(None)

    combo = sg.Combo(mat_combo, mat_combo[current_mat], change_submits=True, readonly=True, key='-MATSELECT-',
                     size=(25, 1))

    layout = [[sg.Menu(menu_def)],
              [sg.Text('Current Material: '), combo, sg.Text('* Hover over field names for explanatory tooltip')],
              [sg.HorizontalSeparator(pad=(0, 8))]]

    if full:
        layout = full_layout(layout)
    else:
        layout = small_layout(layout)

    return layout


def full_layout(layout):
    for i in range(len(entry_keys)):

        # Skip entries not used in layout
        if entry_keys[i] is None:
            continue

        # Skip *_color fields displayed on 1 line
        if i in {18, 19, 20, 22, 23, 24, 26, 27, 28}:
            continue

        # Lock pointer fields to avoid making files unreadable
        locked = False
        if i in {0, 2, 3, 4, 5, 6, 7, 8}:
            locked = True

        current_field = materials[current_mat].at(i)
        layout.append([sg.Text(current_field.name, size=(18, 1), justification='r', tooltip=tooltips[i]),
                        sg.Input(current_field.value, size=(20, 1), key=entry_keys[i], enable_events=True,
                                    metadata=current_field, readonly=locked)])

        # Special case for *_color fields, display on single line
        if i in {17, 21, 25}:
            current_field = materials[current_mat].at(i + 1)
            layout[-1].append(sg.Input(str(current_field.value), size=(20, 1), key=entry_keys[i + 1], enable_events=True, metadata=current_field))

            current_field = materials[current_mat].at(i + 2)
            layout[-1].append(sg.Input(str(current_field.value), size=(20, 1), key=entry_keys[i + 2], enable_events=True, metadata=current_field))

            current_field = materials[current_mat].at(i + 3)
            layout[-1].append(sg.Input(str(current_field.value), size=(20, 1), key=entry_keys[i + 3], enable_events=True, metadata=current_field))

    return layout


def small_layout(layout):
    for i in range(len(entry_keys)):

        # Skip entries not used in layout
        if entry_keys[i] is None:
            continue

        # Skip *_color fields displayed on 1 line
        if i in {19, 20, 23, 24, 27, 28}:
            continue

        current_field = materials[current_mat].at(i)
        layout.append([sg.Text(current_field.name, size=(18, 1), justification='r', tooltip=tooltips[i]),
                        sg.Input(current_field.value, size=(20, 1), key=entry_keys[i], enable_events=True,
                                    metadata=current_field)])

        # Special case for *_color fields, display on single line
        if i in {18, 22, 26}:
            current_field = materials[current_mat].at(i + 1)
            layout[-1].append(sg.Input(str(current_field.value), size=(20, 1), key=entry_keys[i + 1], enable_events=True, metadata=current_field))

            current_field = materials[current_mat].at(i + 2)
            layout[-1].append(sg.Input(str(current_field.value), size=(20, 1), key=entry_keys[i + 2], enable_events=True, metadata=current_field))

    return layout


def validate(type, value):
    if type in {FieldType.u8, FieldType.u16, FieldType.u32}:
        try:
            int(value)
            return True
        except ValueError:
            return False
    elif type == FieldType.f32:
        try:
            float(value)
            return True
        except ValueError:
            return False
    else:
        return False


def validate_ex(input):
    if validate(input.metadata.type, input.Get()):
        if input.Get() != str(input.metadata.value):
            input.Update(background_color='lightgreen')
        else:
            input.Update(background_color='white')
    else:
        input.Update(background_color='red')


def save(file_data, file_name):
    for index, value in enumerate(entry_keys):

        if value is None:
            continue

        field = window[entry_keys[index]].metadata
        val = window[entry_keys[index]].Get()

        if not validate(field.type, val):
            sg.popup('Material could not be saved, invalid fields!')
            return False

        # Skip writing value to file if string representations match
        if val == str(field.value):
            continue

        if field.type == FieldType.u8:
            file_data = file_data[:field.offset] + struct.pack('<B', int(val)) + file_data[field.offset+1:]
        elif field.type == FieldType.u16:
            file_data = file_data[:field.offset] + struct.pack('<H', int(val)) + file_data[field.offset+2:]
        elif field.type == FieldType.u32:
            file_data = file_data[:field.offset] + struct.pack('<I', int(val)) + file_data[field.offset+4:]
        elif field.type == FieldType.f32:
            file_data = file_data[:field.offset] + struct.pack('<f', float(val)) + file_data[field.offset+4:]

    with open(file_name, 'wb') as f:
        f.write(file_data)

    return True


sg.theme('SystemDefaultForReal')

current_mat = 0
entry_keys = []
full = False

filename = sg.popup_get_file('file to open', file_types=(('SH2 Model files', '*.mdl'),), no_window=True)
name, materials, file_data = open_model(filename)
layout = create_layout(full)

window = sg.Window(f'Sh2 Model Material Editor ({name})', layout, finalize=True)
window.TKroot.focus_force()

while True:
    event, values = window.read()
    if event == 'Exit' or event == sg.WIN_CLOSED:
        break

    if event in entry_keys:
        validate_ex(window[event])

    if event == 'Toggle Hidden Fields':
        full = not full

        window.close()
        layout = create_layout(full)
        window = sg.Window(f'Sh2 Model Material Editor ({name})', layout, finalize=True)
        window.TKroot.focus_force()

    if event == '-MATSELECT-':
        current_mat = int(values['-MATSELECT-'].split(' ', 1)[0])

        for index, key in enumerate(entry_keys):
            if key is None:
                continue

            window[key].metadata = materials[current_mat].at(index)
            window[key].Update(materials[current_mat].at(index).value)
            window[key].Update(background_color='white')

    elif event == 'Open...':
        filename = sg.popup_get_file('file to open', file_types=(('SH2 Model files', '*.mdl'),), no_window=True)
        name, materials_out, file_data = open_model(filename)

        if name is not None and materials is not None:
            current_mat = 0
            materials = materials_out

            window.close()
            layout = create_layout(full)
            window = sg.Window(f'Sh2 Model Material Editor ({name})', layout, finalize=True)
            window.TKroot.focus_force()

    elif event == 'Save':
        if save(file_data, name):
            name, materials, file_data = open_model(name)

            window.close()
            layout = create_layout(full)
            window = sg.Window(f'Sh2 Model Material Editor ({name})', layout, finalize=True)
            window.TKroot.focus_force()

            sg.popup('File saved!')

    elif event == 'Save As...':
        save_name = sg.popup_get_file('Choose file', file_types=(('SH2 Model files', '*.mdl'),), no_window=True, save_as=True)
        if save_name != '':
            if save(file_data, save_name):
                name, materials, file_data = open_model(save_name)

                window.close()
                layout = create_layout(full)
                window = sg.Window(f'Sh2 Model Material Editor ({name})', layout, finalize=True)
                window.TKroot.focus_force()

                sg.popup('File saved!')

window.close()

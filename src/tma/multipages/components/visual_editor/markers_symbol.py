from plotly.validators.scatter.marker import SymbolValidator


def extract_symbol_info():
    raw_symbols = SymbolValidator().values
    namestems = []
    namevariants = []
    symbols = []

    for i in range(0, len(raw_symbols), 3):
        name = raw_symbols[i + 2]
        symbols.append(raw_symbols[i])
        namestems.append(name.replace("-open", "").replace("-dot", ""))
        namevariants.append(name[len(namestems[-1]):])

    return namestems, namevariants, symbols


def get_markers_names():
    namestems, namevariants, symbols = extract_symbol_info()

    name_style_dict = {}
    for stem, variant in zip(namestems, namevariants):
        if stem not in name_style_dict:
            name_style_dict[stem] = set()
        name_style_dict[stem].add(variant)

    result_names = [name for name, styles in name_style_dict.items() if len(styles) == 4]

    return result_names


def get_markers_style():
    _, namevariants, _ = extract_symbol_info()

    unique_numbers = [variant if variant else '-basic' for variant in namevariants]

    return unique_numbers

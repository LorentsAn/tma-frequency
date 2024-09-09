from enum import Enum


class Parameter(Enum):
    TEMP = 'TEMP'
    TSUSC = 'TSUSC'
    CSUSC = 'CSUSC'
    MSUSC = 'MSUSC'
    NSUSC = 'NSUSC'
    BSUSC = 'BSUSC'
    BULKS = 'BULKS'
    FERRT = 'FERRT'
    FERRB = 'FERRB'
    MASSS = 'MASSS'
    TIME0_EC = 'TIME0-EC-2020'
    TIME0_EF = 'TIME0-EF-2020'
    EMPTY = 'EMPTY'

    @staticmethod
    def get_parameter(column):
        try:
            return getattr(Parameter, column, '')
        except AttributeError:
            return ''

    @staticmethod
    def get_units(column):
        units_mapping = {
            Parameter.TEMP: 'T[°C]',
            Parameter.TSUSC: 'Kt [E-6]',
            Parameter.CSUSC: 'Kt [E-6]',
            Parameter.MSUSC: 'Km [E-8]',
            Parameter.MASSS: 'Km [E-8]',
            Parameter.NSUSC: 'Kn [E-9]',
            Parameter.BSUSC: 'Kb [E-6]',
            Parameter.BULKS: 'Kb [E-6]',
            Parameter.FERRT: '',
            Parameter.FERRB: '',
            Parameter.TIME0_EC: '',
            Parameter.TIME0_EF: '',
            Parameter.EMPTY: '',
        }
        parameter = Parameter.get_parameter(column)
        return units_mapping.get(parameter, '')

from tma.core.service.exceptions.invalid_filename_error import InvalidFilenameError
from tma.core.service.measurement.analysis.data_calculation import DataCalculation
from tma.core.service.measurement.models.furnance_source import ConstantFurnaceValue, FileFurnaceValue
from tma.core.service.sample.model.specimen_item import SpecimenItem
from tma.core.service.sample.model.specimen_item_calculator import SpecimenItemCalculator


class DataCorrection:
    @staticmethod
    def correct_by_constant(specimen_item: SpecimenItem, constant):
        specimen_item.measurement.value.correct_by_constant(constant)
        specimen_item.empty_furnace_source.set(ConstantFurnaceValue(constant))
        specimen_item.df.set(SpecimenItemCalculator.create_dataframe_for_all_columns(specimen_item))

    @staticmethod
    def correct_by_file(specimen_item: SpecimenItem, correction_item: SpecimenItem):
        if correction_item.measurement.value.get_measurement_type() != specimen_item.measurement.value.get_measurement_type():
            raise InvalidFilenameError('Mismatched data types for subtraction.')
        data_calc = DataCalculation()
        data_calc.set_interpolation_strategy(correction_item.interpolate_method.value)
        specimen_item.measurement.value.correct_by_file(correction_item.measurement.value.measurement, data_calc)
        specimen_item.empty_furnace_source.set(FileFurnaceValue(correction_item.filename.value))
        specimen_item.df.set(SpecimenItemCalculator.create_dataframe_for_all_columns(specimen_item))

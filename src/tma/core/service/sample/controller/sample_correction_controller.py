from typing import Optional, Callable, List

from tma.core.service.exceptions.invalid_filename_error import InvalidFilenameError
from tma.core.service.exceptions.parameter_error import ParameterError
from tma.core.service.sample.controller.repository_controllers.measured_data_controller import \
    MeasuredDataRepositoryController
from tma.core.service.sample.controller.sample_controller import SampleController
from tma.core.service.sample.model.specimen_item import SpecimenItem


class SampleCorrectionController:
    def __init__(self, sample_controller: 'SampleController'):
        self.sample_controller = sample_controller
        self.sample = sample_controller.sample

    def correct_by_constant(self, constant: float, correct_all_files: bool = False) -> Optional[str]:
        files_to_correct = self._get_files_to_correct(correct_all_files)
        errors = []

        for filename in files_to_correct:
            specimen_item = self.sample.value.get_specimen_item_by_filename(filename)
            error = self._process_correction_by_constant(specimen_item, constant)
            if error:
                errors.append(f'Error with file {filename}: {error}')

        return '\n'.join(errors) if errors else None

    def _process_correction_by_constant(self, file: SpecimenItem, constant: float) -> Optional[str]:
        measured_data_repository_controller = MeasuredDataRepositoryController()

        try:
            file.correct_by_constant(constant)
            measured_data_repository_controller.update_measured_data(
                self.sample.value,
                file.filename.value,
                file.measurement.value.get_measured_data()
            )
            return None
        except Exception as e:
            return str(e)

    def correct_by_file(self, correction_file: str, correct_all_files: bool = False) -> Optional[str]:
        source_file = self.sample.value.get_specimen_item_by_filename(correction_file)
        if source_file is None:
            return f'File {correction_file} not found.'

        def measurement_type_filter(item):
            return item.measurement.value.get_measurement_type() == source_file.measurement.value.get_measurement_type()

        files_to_correct = self._get_files_to_correct(correct_all_files, measurement_type_filter)
        errors = []

        for filename in files_to_correct:
            current_specimen_item = self.sample.value.get_specimen_item_by_filename(filename)
            if current_specimen_item is None:
                errors.append(f'File {filename} not found.')
                continue

            error = self._process_correction_by_file(current_specimen_item, source_file)
            if error:
                errors.append(f'Error with file {filename}: {error}')

        return '\n'.join(errors) if errors else None

    def _process_correction_by_file(self, filename_to_correct: SpecimenItem, correction_file: SpecimenItem) -> Optional[
        str]:
        measured_data_repository_controller = MeasuredDataRepositoryController()
        try:
            filename_to_correct.correct_by_file(correction_file)
            measured_data_repository_controller.update_measured_data(
                self.sample.value,
                filename_to_correct.filename.value,
                filename_to_correct.measurement.value.get_measured_data()
            )
            return None
        except InvalidFilenameError as e:
            return str(e)
        except Exception as e:
            return str(e)

    def calculate_bulk(self, method, calculate_for_all_files=False, **config) -> Optional[str]:
        def measurement_type_filter(item):
            return (item.measurement.value.get_measurement_type() ==
                    self.sample_controller.get_selected_specimen_item().measurement.value.get_measurement_type())

        files_to_correct = self._get_files_to_correct(calculate_for_all_files, measurement_type_filter)
        errors = []

        for filename in files_to_correct:
            current_specimen_item = self.sample.value.get_specimen_item_by_filename(filename)
            if current_specimen_item is None:
                errors.append(f'File {filename} not found.')
                continue

            error = self._process_bulk_calculation(current_specimen_item, method, **config)
            if error:
                errors.append(f'Error with file {filename}: {error}')

        return '\n'.join(errors) if errors else None

    def _process_bulk_calculation(self, file: SpecimenItem, method, **config) -> Optional[str]:
        measured_data_repository_controller = MeasuredDataRepositoryController()

        if not file.is_empty_furnace_or_cryostat_file():
            # try:
            file.calculate_bulk(method, **config)
            measured_data_repository_controller.update_measured_data(
                self.sample.value,
                file.filename.value,
                file.measurement.value.get_measured_data()
            )
            return None
        # except ParameterError as e:
        #     return str(e.reason)
        # except Exception as e:
        #     return str(e)

    def calculate_mass(self, mass, calculate_for_all_files=False) -> Optional[str]:
        def measurement_type_filter(item):
            return (item.measurement.value.get_measurement_type() ==
                    self.sample_controller.get_selected_specimen_item().measurement.value.get_measurement_type())

        files_to_correct = self._get_files_to_correct(calculate_for_all_files, measurement_type_filter)
        errors = []

        for filename in files_to_correct:
            current_specimen_item = self.sample.value.get_specimen_item_by_filename(filename)
            if current_specimen_item is None:
                errors.append(f'File {filename} not found.')
                continue

            error = self._process_mass_calculation(current_specimen_item, mass)
            if error:
                errors.append(f'Error with file {filename}: {error}')

        return '\n'.join(errors) if errors else None

    def _process_mass_calculation(self, file: SpecimenItem, mass) -> Optional[str]:
        measured_data_repository_controller = MeasuredDataRepositoryController()

        if not file.is_empty_furnace_or_cryostat_file():
            try:
                file.calculate_mass(mass)
                measured_data_repository_controller.update_measured_data(
                    self.sample.value,
                    file.filename.value,
                    file.measurement.value.get_measured_data()
                )
                return None
            except ParameterError as e:
                return str(e.reason)
            except Exception as e:
                return str(e)

    def _get_files_to_correct(self, correct_all_files: bool, additional_filter: Optional[Callable] = None) -> List[str]:
        if correct_all_files:
            return self.sample_controller.get_filenames_list(include_empty_source=False,
                                                             additional_filter=additional_filter)
        else:
            return [self.sample_controller.get_selected_specimen_item().filename.value]

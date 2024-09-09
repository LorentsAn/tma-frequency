import os
import time
import unittest
from scipy import stats
import numpy as np

from tma.core.data.parser.model.parameter import Parameter
from tma.core.service.measurement.analysis.data_calculation import DataCalculation
from tma.core.service.measurement.model.measurement_factory import MeasurementFactory
from tma.core.service.measurement.model.measurement_manager import MeasurementManager


class TestSubtractionByFile(unittest.TestCase):
    uncorrected_measurements: list[MeasurementManager] = []
    answer_measurements: list[MeasurementManager] = []

    correction_files = [
        '2021-syntetic-epsilon-iron-III/uncorrected/AP1190-EC-220111.clw',
        '2021-syntetic-epsilon-iron-III/uncorrected/AP1190-EF-220111.cur'
    ]
    correction_cur_measurement: MeasurementManager = None
    correction_clw_measurement: MeasurementManager = None

    def setUp(self):
        test_directory = '/Users/a.lorenz/tma-freq/tests/analysis/correction/check-tables/2021-syntetic-epsilon-iron-III/time_test'
        uncorrected_files = [os.path.join(test_directory, file) for file in os.listdir(test_directory) if
                             file.endswith('.clw')]
        self.uncorrected_measurements = self._process_files(uncorrected_files)
        # self.answer_measurements = self._process_files(corrected_files, 'check-tables/')
        self._load_correction_files('check-tables/')

    def _process_files(self, files, directory=None):
        measurement_managers = []
        for index, filename in enumerate(files):
            file_path = filename if directory is None else os.path.abspath(os.path.join(directory, filename))
            with open(file_path, 'rb') as file:
                file_extension = filename.split('.')[-1]
                file_content = file.read()
                measurement_managers.append(MeasurementFactory.extract_values(index, file_extension, {'data': file_content}))
        return measurement_managers

    def _load_correction_files(self, directory):
        for index, filename in enumerate(self.correction_files):
            file_path = os.path.abspath(os.path.join(directory, filename))
            with open(file_path, 'rb') as file:
                file_extension = filename.split('.')[-1]
                file_content = file.read()
                measurement_manager = MeasurementFactory.extract_values(index, file_extension, {'data': file_content})
                if measurement_manager.get_measurement_type() == 'clw':
                    self.correction_clw_measurement = measurement_manager
                else:
                    self.correction_cur_measurement = measurement_manager

    def _perform_statistical_tests(self, data_1, data_2):
        statistic, shapiro_test_1_pvalue = stats.shapiro(data_1)
        statistic, shapiro_test_2_pvalue = stats.shapiro(data_2)

        if (shapiro_test_1_pvalue > 0.05) and (shapiro_test_2_pvalue > 0.05):
            statistic, levene_test_pvalue = stats.levene(data_1, data_2)
            t_test = stats.ttest_ind(data_1, data_2, equal_var=(levene_test_pvalue > 0.05))
            return t_test
        else:
            ks_test = stats.ks_2samp(data_1, data_2)
            return ks_test

    def _assert_measurements_equal(self, measurement: MeasurementManager, answer_measurement: MeasurementManager, params, comparison_keys=None):
        print()
        for param in params:
            for curve, answer_curve in zip(measurement.get_curves(param.value), answer_measurement.get_curves(param.value)):
                data_1 = np.array(curve.values)
                data_2 = np.array(answer_curve.values)
                test_result = self._perform_statistical_tests(data_1, data_2)
                print(test_result.pvalue)
                self.assertGreater(test_result.pvalue, 0.05)
        print()

    def _truncate_measurement(self, measurement: MeasurementManager, target_length: int):
        for param in [Parameter.TEMP, Parameter.TSUSC, Parameter.CSUSC]:
            if measurement.measurement.has_heating_curve[param.value]:
                measurement.measurement.heating_curve[param.value].values = measurement.measurement.heating_curve[param.value].values[:target_length]
            if measurement.measurement.has_cooling_curve[param.value]:
                measurement.measurement.cooling_curve[param.value].values = measurement.measurement.cooling_curve[param.value].values[:target_length]

    def _truncate_measurements(self, measurement_managers: [MeasurementManager], target_length: int):
        for measurement in measurement_managers:
            self._truncate_measurement(measurement, target_length)

    def test_correct_by_file_with_less_length(self):
        data_calc = DataCalculation()
        data_calc.set_interpolation_strategy('Linear Interpolation')

        start_time = time.time()
        correction_file = self.correction_clw_measurement
        for measurement in self.uncorrected_measurements:
            measurement.correct_by_file(correction_file.measurement, data_calc)
        duration = time.time() - start_time
        print(f"Correction time: {duration:.4f} seconds")

        self.assertTrue(True)

    def test_correct_by_file_with_greater_length(self):
        self._truncate_measurements(self.uncorrected_measurements, len(self.uncorrected_measurements[0].measurement.heating_curve[Parameter.TEMP.value].values) // 2)

        data_calc = DataCalculation()
        data_calc.set_interpolation_strategy('Linear Interpolation')

        correction_file = self.correction_clw_measurement
        start_time = time.time()
        for measurement_manager in self.uncorrected_measurements:
            measurement_manager.correct_by_file(correction_file.measurement, data_calc)
        duration = time.time() - start_time
        print(f"Correction time: {duration:.4f} seconds")


    def test_correct_by_file_with_equal_length(self):
        target_length = 100  # Пример одинаковой длины
        self._truncate_measurements(self.answer_measurements, target_length)
        self._truncate_measurements(self.uncorrected_measurements, target_length)
        self._truncate_measurement(self.correction_cur_measurement, target_length)
        self._truncate_measurement(self.correction_clw_measurement, target_length)

        data_calc = DataCalculation()
        data_calc.set_interpolation_strategy('Linear Interpolation')

        start_time = time.time()
        correction_file = self.correction_clw_measurement
        for measurement in self.uncorrected_measurements:
            measurement.correct_by_file(correction_file.measurement, data_calc)
        duration = time.time() - start_time
        print(f"Correction time: {duration:.4f} seconds")
        self.assertTrue(True)


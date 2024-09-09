import os
import unittest
import numpy as np
from scipy import stats

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
        test_directory = 'check-tables/'
        uncorrected_files = [
            '2021-syntetic-epsilon-iron-III/uncorrected/#4_L1-.218.clw',
            '2021-syntetic-epsilon-iron-III/uncorrected/#4_L2-.218.clw',
            '2021-syntetic-epsilon-iron-III/uncorrected/#4_O1-.218.cur',
        ]

        corrected_files = [
            '2021-syntetic-epsilon-iron-III/subtraction_file/corrected/#4_L1-.218.clw',
            '2021-syntetic-epsilon-iron-III/subtraction_file/corrected/#4_L2-.218.clw',
            '2021-syntetic-epsilon-iron-III/subtraction_file/corrected/#4_O1-.218.cur',
        ]

        self.uncorrected_measurements = self._process_files(uncorrected_files, test_directory)
        self.answer_measurements = self._process_files(corrected_files, test_directory)
        self._load_correction_files(test_directory)

    def _process_files(self, files, directory):
        measurement_managers = []
        for index, filename in enumerate(files):
            file_path = os.path.abspath(os.path.join(directory, filename))
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

        if shapiro_test_1_pvalue > 0.05 and shapiro_test_2_pvalue > 0.05:
            statistic, levene_test_pvalue = stats.levene(data_1, data_2)
            t_test = stats.ttest_ind(data_1, data_2, equal_var=(levene_test_pvalue > 0.05))
            return t_test
        else:
            ks_test = stats.ks_2samp(data_1, data_2)
            return ks_test

    def _assert_measurements_equal(self, measurement: MeasurementManager, answer_measurement: MeasurementManager, params, comparison_keys=None):
        for param in params:
            for curve, answer_curve in zip(measurement.get_curves(param.value), answer_measurement.get_curves(param.value)):
                data_1 = np.array(curve.values)
                data_2 = np.array(answer_curve.values)
                test_result = self._perform_statistical_tests(data_1, data_2)
                self.assertGreater(test_result.pvalue, 0.05)
                # self.assertListEqual(answer_curve.values, curve.values)

    def _truncate_measurement(self, measurement: MeasurementManager):

        for param in [Parameter.TEMP, Parameter.TSUSC, Parameter.CSUSC]:
            measured_data_len = measurement.measurement.get_curve_length(param.value)
            curves = measurement.get_curves(param.value)
            if measurement.measurement.has_heating_curve[param.value]:
                measurement.measurement.heating_curve[param.value].values = curves[0].values[:measured_data_len // 2]
            if measurement.measurement.has_cooling_curve[param.value]:
                measurement.measurement.cooling_curve[param.value].values = curves[1].values[:measured_data_len // 2]

    def _truncate_measurements(self, measurement_managers: [MeasurementManager]):
        for measurement in measurement_managers:
            self._truncate_measurement(measurement)

    def test_correct_by_file_with_less_length(self):
        data_calc = DataCalculation()
        data_calc.set_interpolation_strategy('Linear Interpolation')

        for measurement in self.uncorrected_measurements:
            correction_file = self.correction_clw_measurement if measurement.get_measurement_type() == 'clw' else self.correction_cur_measurement
            measurement.correct_by_file(correction_file.measurement, data_calc)
            answer_measurement = self.answer_measurements[measurement.get_measurement_id()]

            if measurement.get_measurement_type() == 'clw':
                self._assert_measurements_equal(measurement, answer_measurement, [Parameter.CSUSC])
            else:
                self._assert_measurements_equal(measurement, answer_measurement, [Parameter.TSUSC, Parameter.CSUSC],
                                                ['increasing', 'decreasing'])

    def test_correct_by_file_with_greater_length(self):
        self._truncate_measurements(self.answer_measurements)
        self._truncate_measurements(self.uncorrected_measurements)

        data_calc = DataCalculation()
        data_calc.set_interpolation_strategy('Lagrange Interpolation')

        for measurement_manager in self.uncorrected_measurements:
            correction_file = self.correction_clw_measurement if measurement_manager.get_measurement_type() == 'clw' else self.correction_cur_measurement
            measurement_manager.correct_by_file(correction_file.measurement, data_calc)
            answer_measurement = self.answer_measurements[measurement_manager.get_measurement_id()]

            if measurement_manager.get_measurement_type() == 'clw':
                self._assert_measurements_equal(measurement_manager, answer_measurement, [Parameter.CSUSC])
            else:
                self._assert_measurements_equal(measurement_manager, answer_measurement, [Parameter.CSUSC])

    def test_correct_by_file_with_equal_length(self):
        self._truncate_measurements(self.answer_measurements)
        self._truncate_measurements(self.uncorrected_measurements)
        self._truncate_measurement(self.correction_cur_measurement)
        self._truncate_measurement(self.correction_clw_measurement)

        data_calc = DataCalculation()
        data_calc.set_interpolation_strategy('Spline Interpolation')

        for measurement in self.uncorrected_measurements:
            correction_file = self.correction_clw_measurement if measurement.get_measurement_type() == 'clw' else self.correction_cur_measurement
            measurement.correct_by_file(correction_file.measurement, data_calc)
            answer_measurement = self.answer_measurements[measurement.get_measurement_id()]

            if measurement.get_measurement_type() == 'clw':
                self._assert_measurements_equal(measurement, answer_measurement, [Parameter.CSUSC])
            else:
                self._assert_measurements_equal(measurement, answer_measurement, [Parameter.CSUSC])

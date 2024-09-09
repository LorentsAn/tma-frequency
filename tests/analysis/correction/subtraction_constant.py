import os
import unittest
import numpy as np
from scipy import stats

from tma.core.data.parser.model.parameter import Parameter
from tma.core.service.measurement.model.measurement_factory import MeasurementFactory
from tma.core.service.measurement.model.measurement_manager import MeasurementManager


class TestSubtractionConstant(unittest.TestCase):
    uncorrected_measurements: list[MeasurementManager] = []
    answer_measurements: list[MeasurementManager] = []

    correction_cur_constant: int = -190
    correction_clw_measurement: int = -110

    def setUp(self):
        test_directory = 'check-tables/'

        uncorrected_files = [
            '2021-syntetic-epsilon-iron-III/uncorrected/#4_L1-.218.clw',
            '2021-syntetic-epsilon-iron-III/uncorrected/#4_L2-.218.clw',
            '2021-syntetic-epsilon-iron-III/uncorrected/#4_O1-.218.cur'
        ]

        corrected_files = [
            '2021-syntetic-epsilon-iron-III/subtraction_constant/corrected/#4_L1-.218.clw',
            '2021-syntetic-epsilon-iron-III/subtraction_constant/corrected/#4_L2-.218.clw',
            '2021-syntetic-epsilon-iron-III/subtraction_constant/corrected/#4_O1-.218.cur'
        ]

        self.uncorrected_measurements = self._process_files(uncorrected_files, test_directory)
        self.answer_measurements = self._process_files(corrected_files, test_directory)

    def _process_files(self, files, directory):
        measurements = []
        for index, filename in enumerate(files):
            file_path = os.path.abspath(os.path.join(directory, filename))
            with open(file_path, 'rb') as file:
                file_extension = filename.split('.')[-1]
                file_content = file.read()
                measurements.append(MeasurementFactory.extract_values(index, file_extension, {'data': file_content}))
        return measurements

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
            for curve, answer_curve in zip(measurement.get_curves(param), answer_measurement.get_curves(param)):
                data_1 = np.array(curve.values)
                data_2 = np.array(answer_curve.values)
                test_result = self._perform_statistical_tests(data_1, data_2)
                print(test_result.pvalue)
                self.assertGreater(test_result.pvalue, 0.05)
                self.assertListEqual(answer_curve.values, curve.values)


    def test_correct_by_constant_with_less_length(self):
        for measurement_manager in self.uncorrected_measurements:
            correction_constant = self.correction_clw_measurement \
                if measurement_manager.get_measurement_type() == 'clw' else self.correction_cur_constant
            measurement_manager.correct_by_constant(correction_constant)
            answer_measurement = self.answer_measurements[measurement_manager.get_measurement_id()]

            if measurement_manager.get_measurement_type() == 'clw':
                self._assert_measurements_equal(measurement_manager, answer_measurement, [Parameter.CSUSC.value])
            else:
                self._assert_measurements_equal(measurement_manager, answer_measurement, [Parameter.TSUSC.value, Parameter.CSUSC.value],
                                                ['increasing', 'decreasing'])

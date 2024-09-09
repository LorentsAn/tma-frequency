import unittest
import os
import numpy as np
from scipy import stats


from tma.core.data.parser.model.parameter import Parameter
from tma.core.service.measurement.analysis.data_calculation import DataCalculation
from tma.core.service.measurement.model.measurement import Measurement
from tma.core.service.measurement.model.measurement_factory import MeasurementFactory
from tma.core.service.measurement.model.measurement_manager import MeasurementManager


class TestBulkCalculation(unittest.TestCase):
    uncorrected_measurements: list[MeasurementManager] = []
    corrected_measurements_sets_by_mass: dict[float, list[Measurement]] = {}
    mass_constants = [5.5, 7.1]
    density = [1.2, 1.5]
    volume = [6.7, 2.5]

    def setUp(self):
        test_directory = 'check-tables/'

        uncorrected_files = [
            '2021-syntetic-epsilon-iron-III/uncorrected/#4_L1-.218.clw',
            '2021-syntetic-epsilon-iron-III/uncorrected/#4_L2-.218.clw',
            '2021-syntetic-epsilon-iron-III/uncorrected/#4_O1-.218.cur'
        ]

        corrected_files_sets_by_mass = {
            5.5: [
                '2021-syntetic-epsilon-iron-III/bulk-mass-5-5/#4_L1-.218.clw',
                '2021-syntetic-epsilon-iron-III/bulk-mass-5-5/#4_L2-.218.clw',
                '2021-syntetic-epsilon-iron-III/bulk-mass-5-5/#4_O1-.218.cur'
            ],
            7.1: [
                '2021-syntetic-epsilon-iron-III/bulk-mass-7-1/#4_L1-.218.clw',
                '2021-syntetic-epsilon-iron-III/bulk-mass-7-1/#4_L2-.218.clw',
                '2021-syntetic-epsilon-iron-III/bulk-mass-7-1/#4_O1-.218.cur'
            ]
        }

        corrected_files_sets_by_volume = {
            6.7: [
                '2021-syntetic-epsilon-iron-III/bulk-volume-6-7/#4_L1-.218.clw',
                '2021-syntetic-epsilon-iron-III/bulk-volume-6-7/#4_L2-.218.clw',
                '2021-syntetic-epsilon-iron-III/bulk-volume-6-7/#4_O1-.218.cur'
            ],
            2.5: [
                '2021-syntetic-epsilon-iron-III/bulk-volume-2-5/#4_L1-.218.clw',
                '2021-syntetic-epsilon-iron-III/bulk-volume-2-5/#4_L2-.218.clw',
                '2021-syntetic-epsilon-iron-III/bulk-volume-2-5/#4_O1-.218.cur'
            ],
        }

        # Load uncorrected measurements
        self.uncorrected_measurements = self._process_files(uncorrected_files, test_directory)

        # Load corrected measurements for each mass constant
        self.corrected_measurements_sets_by_mass = {
            mass_constant: self._process_files(corrected_files, test_directory)
            for mass_constant, corrected_files in corrected_files_sets_by_mass.items()
        }

        # Load corrected measurements for each volume constant
        self.corrected_measurements_sets_by_volume = {
            volume_constant: self._process_files(corrected_files, test_directory)
            for volume_constant, corrected_files in corrected_files_sets_by_volume.items()
        }

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

    def _assert_measurements_equal(self, measurement, answer_measurement, params, comparison_keys=None):
        if comparison_keys is None:
            comparison_keys = ['values']
        print()
        for param in params:
            for key in comparison_keys:
                data_1 = np.array(answer_measurement.get_measured_data()[Parameter.BULKS.value][key])
                data_2 = np.array(measurement.get_measured_data()[param.value][key])
                test_result = self._perform_statistical_tests(data_1, data_2)
                print(test_result.pvalue)
                self.assertGreater(test_result.pvalue, 0.05)
        print()

    def _process_files(self, files, directory):
        measurements = []
        for index, filename in enumerate(files):
            file_path = os.path.abspath(os.path.join(directory, filename))
            with open(file_path, 'rb') as file:
                file_extension = filename.split('.')[-1]
                file_content = file.read()
                measurements.append(MeasurementFactory.extract_values(index, file_extension, {'data': file_content}))
        return measurements


    def test_calculate_mass_susceptibility(self):
        for mass_constant, answer_measurements in self.corrected_measurements_sets_by_mass.items():
            data_calc = DataCalculation()
            density = self.density[self.mass_constants.index(mass_constant)]
            data_calc.set_bulk_calculation_strategy('mass', mass=mass_constant, density=density)

            for measurement in self.uncorrected_measurements:
                measurement.calculate_bulk(data_calc)
                answer_measurement = answer_measurements[measurement.get_measurement_id()]

                if measurement.get_measurement_type() == 'clw':
                    self._assert_measurements_equal(measurement, answer_measurement, [Parameter.BSUSC])
                else:
                    self._assert_measurements_equal(measurement, answer_measurement, [Parameter.BSUSC], ['increasing', 'decreasing'])

    def test_calculate_volume_susceptibility(self):
        for volume, answer_measurements in self.corrected_measurements_sets_by_volume.items():
            data_calc = DataCalculation()
            data_calc.set_bulk_calculation_strategy('volume', volume=volume)

            for measurement in self.uncorrected_measurements:
                measurement.calculate_bulk(data_calc)
                answer_measurement = answer_measurements[measurement.get_measurement_id()]

                if measurement.get_measurement_type() == 'clw':
                    self._assert_measurements_equal(measurement, answer_measurement, [Parameter.BSUSC])
                else:
                    self._assert_measurements_equal(measurement, answer_measurement, [Parameter.BSUSC], ['increasing', 'decreasing'])

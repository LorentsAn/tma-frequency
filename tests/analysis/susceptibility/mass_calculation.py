import unittest
import os
import numpy as np

from tma.core.data.parser.model.parameter import Parameter
from tma.core.service.measurement.analysis.data_calculation import DataCalculation
from tma.core.service.measurement.analysis.mass_calculation import MassCalculation
from tma.core.service.measurement.model.measurement import Measurement
from tma.core.service.measurement.model.measurement_factory import MeasurementFactory
from tma.core.service.measurement.model.measurement_manager import MeasurementManager


class TestSubtractionConstant(unittest.TestCase):
    uncorrected_measurements: list[MeasurementManager] = []
    corrected_measurements_sets: dict[float, list[MeasurementManager]] = {}
    mass_constants = [5.5, 7.1]

    def setUp(self):
        test_directory = 'check-tables/'

        uncorrected_files = [
            '2021-syntetic-epsilon-iron-III/uncorrected/#4_L1-.218.clw',
            '2021-syntetic-epsilon-iron-III/uncorrected/#4_L2-.218.clw',
            '2021-syntetic-epsilon-iron-III/uncorrected/#4_O1-.218.cur'
        ]

        corrected_files_sets = {
            5.5: [
                '2021-syntetic-epsilon-iron-III/mass-5-5/#4_L1-.218.clw',
                '2021-syntetic-epsilon-iron-III/mass-5-5/#4_L2-.218.clw',
                '2021-syntetic-epsilon-iron-III/mass-5-5/#4_O1-.218.cur'
            ],
            7.1: [
                '2021-syntetic-epsilon-iron-III/mass-7-1/#4_L1-.218.clw',
                '2021-syntetic-epsilon-iron-III/mass-7-1/#4_L2-.218.clw',
                '2021-syntetic-epsilon-iron-III/mass-7-1/#4_O1-.218.cur'
            ]
        }

        # Load uncorrected measurements
        self.uncorrected_measurements = self._process_files(uncorrected_files, test_directory)

        # Load corrected measurements for each mass constant
        self.corrected_measurements_sets = {
            mass_constant: self._process_files(corrected_files, test_directory)
            for mass_constant, corrected_files in corrected_files_sets.items()
        }

    def _process_files(self, files, directory):
        measurements = []
        for index, filename in enumerate(files):
            file_path = os.path.abspath(os.path.join(directory, filename))
            with open(file_path, 'rb') as file:
                file_extension = filename.split('.')[-1]
                file_content = file.read()
                measurements.append(MeasurementFactory.extract_values(index, file_extension, {'data': file_content}))
        return measurements

    def _assert_measurements_equal(self, measurement, answer_measurement, params, comparison_keys=None):
        if comparison_keys is None:
            comparison_keys = ['values']
        for param in params:
            for key in comparison_keys:
                self.assertListEqual(
                    answer_measurement.measured_data[Parameter.MASSS.value][key].tolist(),
                    measurement.measured_data[param.value][key].tolist()
                )

    def test_calculate_mass_susceptibility(self):
        for mass_constant, answer_measurements in self.corrected_measurements_sets.items():
            data_calc = DataCalculation()
            data_calc.set_mass_calculation_strategy(MassCalculation, mass=mass_constant)

            for measurement in self.uncorrected_measurements:
                measurement.calculate_mass(data_calc)
                answer_measurement = answer_measurements[measurement.measurement_id]

                if measurement.measurement_type == 'clw':
                    self._assert_measurements_equal(measurement, answer_measurement, [Parameter.MSUSC])
                else:
                    self._assert_measurements_equal(measurement, answer_measurement, [Parameter.MSUSC], ['increasing', 'decreasing'])

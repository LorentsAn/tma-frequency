import unittest
from unittest.mock import MagicMock
import json
import numpy as np

from tma.core.service.services.measured_data_service import MeasuredDataService


class TestMeasuredDataService(unittest.TestCase):
    def setUp(self):
        self.mock_repository = MagicMock()
        self.service = MeasuredDataService(self.mock_repository)

    def test_get_measured_data_by_specimen_item_id(self):
        specimen_item_id = 1
        self.service.get_measured_data_by_specimen_item_id(specimen_item_id)
        self.mock_repository.get_measured_data.assert_called_once_with(specimen_item_id=specimen_item_id)

    def test_get_data_by_specimen_item_id_column_name(self):
        specimen_item_id = 1
        column_name = "test_column"
        mock_data = MagicMock()
        self.mock_repository.get_measured_data.return_value.first.return_value = mock_data

        result = self.service.get_data_by_specimen_item_id_column_name(specimen_item_id, column_name)

        self.mock_repository.get_measured_data.assert_called_once_with(specimen_item_id=specimen_item_id,
                                                                       column_name=column_name)
        self.assertEqual(result, mock_data)

    def test_get_data_by_measurement_id(self):
        measurement_id = 1
        mock_data = [MagicMock(data=json.dumps({'key': [1, 2, 3]}), column_name='test_column')]
        self.mock_repository.get_measured_data.return_value = mock_data

        result = self.service.get_data_by_measurement_id(measurement_id)

        self.mock_repository.get_measured_data.assert_called_once_with(measurement_id=measurement_id)
        self.assertIn('test_column', result)
        self.assertTrue(np.array_equal(result['test_column']['key'], np.array([1, 2, 3])))

    def test_add_measured_data(self):
        measurement_id = 1
        specimen_item_id = 1
        column_name = "test_column"
        data = {'key': [1, 2, 3]}

        self.service.add_measured_data(measurement_id, specimen_item_id, column_name, data)

        self.mock_repository.create_measured_data.assert_called_once_with(
            measurement_id, specimen_item_id, column_name, data
        )

    def test_add_measured_data_by_model(self):
        measurement_id = 1
        specimen_item_id = 1
        measured_data = {'test_column': {'key': np.array([1, 2, 3])}}

        self.service.add_measured_data_by_model(measurement_id, specimen_item_id, measured_data)

        expected_data = json.dumps({'key': [1, 2, 3]})
        self.mock_repository.create_measured_data.assert_called_once_with(
            measurement_id, specimen_item_id, 'test_column', expected_data
        )

    def test_update_measured_data_details(self):
        measurement_data_id = 1
        data = {'key': np.array([1, 2, 3])}

        self.service.update_measured_data_details(measurement_data_id, data=data)

        expected_data = json.dumps({'key': [1, 2, 3]})
        self.mock_repository.update_measured_data.assert_called_once_with(
            measurement_data_id, data=expected_data
        )

    def test_remove_measured_data_by_measurement_id(self):
        measurement_id = 1

        self.service.remove_measured_data_by_measurement_id(measurement_id)

        self.mock_repository.delete_measured_data_by_measurement_id.assert_called_once_with(measurement_id)

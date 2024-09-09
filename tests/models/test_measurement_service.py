import unittest
from unittest.mock import MagicMock
import json
from tma.core.model.repository.measurement_repository import MeasurementRepository
from tma.core.service.measurement.model.measurement import Measurement
from tma.core.service.services.measurement_service import MeasurementService


class TestMeasurementService(unittest.TestCase):
    def setUp(self):
        self.mock_repository = MagicMock(spec=MeasurementRepository)
        self.service = MeasurementService(self.mock_repository)

    def test_get_measurement(self):
        measurement_id = 1
        mock_measurement = MagicMock()
        self.mock_repository.get_measurement_by_id.return_value = mock_measurement

        result = self.service.get_measurement(measurement_id)

        self.mock_repository.get_measurement_by_id.assert_called_once_with(measurement_id)
        self.assertEqual(result, mock_measurement)

    def test_get_measurement_by_specimen_item_id(self):
        specimen_item_id = 1
        mock_measurement = MagicMock()
        self.mock_repository.get_measurement_by_specimen_item_id.return_value = mock_measurement

        result = self.service.get_measurement_by_specimen_item_id(specimen_item_id)

        self.mock_repository.get_measurement_by_specimen_item_id.assert_called_once_with(specimen_item_id)
        self.assertEqual(result, mock_measurement)

    def test_add_measurement(self):
        specimen_item_id = 1
        measurement_type = 2
        columns = {"col1": "value1"}
        mock_measurement = MagicMock()
        self.mock_repository.create_measurement.return_value = mock_measurement

        result = self.service.add_measurement(specimen_item_id, measurement_type, columns)

        self.mock_repository.create_measurement.assert_called_once_with(specimen_item_id, measurement_type, columns)
        self.assertEqual(result, mock_measurement)

    def test_add_measurement_by_model(self):
        specimen_item_id = 1
        measurement_type = 2
        columns = {"col1": "value1"}
        measurement = Measurement(specimen_item_id=specimen_item_id, measurement_type=measurement_type, columns=columns)
        mock_measurement = MagicMock()
        self.mock_repository.create_measurement.return_value = mock_measurement

        result = self.service.add_measurement_by_model(specimen_item_id, measurement)

        self.mock_repository.create_measurement.assert_called_once_with(specimen_item_id, measurement_type, json.dumps(columns))
        self.assertEqual(result, mock_measurement)

    def test_update_measurement_details(self):
        measurement_id = 1
        update_fields = {"field1": "new_value"}
        mock_measurement = MagicMock()
        self.mock_repository.update_measurement.return_value = mock_measurement

        result = self.service.update_measurement_details(measurement_id, **update_fields)

        self.mock_repository.update_measurement.assert_called_once_with(measurement_id, **update_fields)
        self.assertEqual(result, mock_measurement)

    def test_remove_measurement(self):
        measurement_id = 1

        self.service.remove_measurement(measurement_id)

        self.mock_repository.delete_measurement.assert_called_once_with(measurement_id)


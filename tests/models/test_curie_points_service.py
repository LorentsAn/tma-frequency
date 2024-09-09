import unittest
from unittest.mock import MagicMock
from typing import List
from tma.core.model.repository.curie_point_repository import CuriePointRepository
from tma.core.service.services.curie_point_service import CuriePointService


class TestCuriePointService(unittest.TestCase):
    def setUp(self):
        self.mock_repository = MagicMock(spec=CuriePointRepository)

    def test_get_curie_points_by_specimen_item_id(self):
        specimen_item_id = 1
        mock_points = [MagicMock()]
        self.mock_repository.get_curie_point.return_value = mock_points

        result = self.service.get_curie_points_by_specimen_item_id(specimen_item_id)

        self.mock_repository.get_curie_point.assert_called_once_with(specimen_item_id=specimen_item_id)
        self.assertEqual(result, mock_points)

    def test_get_curie_points_models_by_specimen_item_id(self):
        specimen_item_id = 1
        mock_point = MagicMock(
            curie_point_id=1,
            id_plot_selected=2,
            column_name="test_column",
            temperature_value=100.0,
            magnetization_value=0.5
        )
        self.mock_repository.get_curie_point.return_value = [mock_point]

        result = self.service.get_curie_points_models_by_specimen_item_id(specimen_item_id)

        self.mock_repository.get_curie_point.assert_called_once_with(specimen_item_id=specimen_item_id)
        expected_result = [
            CuriePoint(
                id_curie_point=1,
                id_plot_select=2,
                column_name="test_column",
                temperature_value=100.0,
                magnetization_value=0.5
            )
        ]
        self.assertEqual(result, expected_result)

    def test_add_curie_point(self):
        specimen_item_id = 1
        column_name = "test_column"
        id_plot_select = 2
        temperature_value = 100.0
        magnetization_value = 0.5
        mock_curie_point = MagicMock()

        self.mock_repository.add_curie_point.return_value = mock_curie_point

        result = self.service.add_curie_point(
            specimen_item_id, column_name, id_plot_select, temperature_value, magnetization_value
        )

        self.mock_repository.add_curie_point.assert_called_once_with(
            specimen_item_id=specimen_item_id,
            column_name=column_name,
            id_plot_selected=id_plot_select,
            temperature_value=temperature_value,
            magnetization_value=magnetization_value,
        )
        self.assertEqual(result, mock_curie_point)

    def test_delete_curie_point(self):
        curie_point_id = 1

        self.service.delete_curie_point(curie_point_id)

        self.mock_repository.delete_curie_point.assert_called_once_with(curie_point_id)


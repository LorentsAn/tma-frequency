import numpy as np
import pandas as pd
from pandas import DataFrame

from tma.core.service.sample.model.specimen_item import SpecimenItem


class SpecimenItemCalculator:
    @staticmethod
    def align_and_sum(arr1, arr2):
        return np.concatenate((arr1, arr2)) if len(arr1) > len(arr2) else np.concatenate((arr2, arr1))

    @staticmethod
    def getDF(file_item: SpecimenItem, x_column: str, y_column: str) -> DataFrame:
        df_x = file_item.measurement.value.create_dataframe_by_column(x_column)
        df_y = file_item.measurement.value.create_dataframe_by_column(y_column)
        return pd.concat([df_x, df_y], axis=1)

    @staticmethod
    def create_dataframe_for_all_columns(specimen_item: SpecimenItem) -> DataFrame:
        df_result = DataFrame()
        for column in specimen_item.measurement.value.get_measurement_columns():
            df = specimen_item.measurement.value.create_dataframe_by_column(column)
            df_result = pd.concat([df_result, df], axis=1)
        return df_result

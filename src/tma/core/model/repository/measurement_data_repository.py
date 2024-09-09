from sqlalchemy.orm import Session

from tma.core.model.models.measurement_data import MeasuredData


class MeasuredDataRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_measured_data(self, **filters):
        """
        Retrieves measured data records based on variable filtering criteria.

        Args:
            **filters: Arbitrary keyword arguments for filtering data.

        Returns:
            The query result based on the applied filters.
        """
        query = self.session.query(MeasuredData)
        for attr, value in filters.items():
            # Dynamically build the query based on provided filters
            query = query.filter(getattr(MeasuredData, attr) == value)
        return query

    def create_measured_data(self, measurement_id: int, specimen_item_id: int, column_name: str, data):
        new_data = MeasuredData(
            measurement_id=measurement_id,
            specimen_item_id=specimen_item_id,
            column_name=column_name,
            data=data
        )
        self.session.add(new_data)
        self.session.commit()
        return new_data

    def update_measured_data(self, measurement_data_id: int, **kwargs):
        data_record = self.session.query(MeasuredData).filter(
            MeasuredData.measurement_data_id == measurement_data_id).first()
        if data_record:
            for key, value in kwargs.items():
                setattr(data_record, key, value)
            self.session.commit()
            return data_record
        return None

    def delete_measured_data_by_measurement_id(self, measurement_id: int):
        data_records = self.session.query(MeasuredData).filter(MeasuredData.measurement_id == measurement_id)
        for data_record in data_records:
            if data_record:
                self.session.delete(data_record)
        self.session.commit()
        return True

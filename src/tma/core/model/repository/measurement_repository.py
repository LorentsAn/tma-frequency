from tma.core.model.models.measurement import Measurement
from sqlalchemy.orm import Session


class MeasurementRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_measurement_by_id(self, measurement_id: int):
        return self.session.query(Measurement).filter(Measurement.measurement_id == measurement_id).first()

    def get_measurement_by_specimen_item_id(self, specimen_item_id: int):
        return self.session.query(Measurement).filter(Measurement.specimen_item_id == specimen_item_id).first()

    def create_measurement(self, specimen_item_id: int, measurement_type: int, columns):
        new_measurement = Measurement(
            specimen_item_id=specimen_item_id,
            measurement_type=measurement_type,
            columns=columns
        )
        self.session.add(new_measurement)
        self.session.commit()
        return new_measurement

    def update_measurement(self, measurement_id: int, **kwargs):
        measurement = self.session.query(Measurement).filter(Measurement.measurement_id == measurement_id).first()
        if measurement:
            for key, value in kwargs.items():
                setattr(measurement, key, value)
            self.session.commit()
            return measurement
        return None

    def delete_measurement(self, measurement_id: int):
        measurement = self.session.query(Measurement).filter(Measurement.measurement_id == measurement_id).first()
        if measurement:
            self.session.delete(measurement)
            self.session.commit()
            return True
        return False

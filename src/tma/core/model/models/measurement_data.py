from sqlalchemy import Column, Integer, ForeignKey, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from tma.core.database import Base


class MeasuredData(Base):
    __tablename__ = 'measured_data'

    measurement_data_id = Column(Integer, primary_key=True)
    measurement_id = Column(Integer, nullable=False)
    specimen_item_id = Column(Integer, nullable=False)
    column_name = Column(String(255), nullable=False)
    data = Column(JSON)

    # Relationship to Measurement
    # measurement = relationship("Measurement", back_populates="measured_data")

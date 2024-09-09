from sqlalchemy import Column, Integer, ForeignKey, JSON, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from tma.core.database import Base


class Measurement(Base):
    __tablename__ = 'measurements'

    measurement_id = Column(Integer, primary_key=True)
    specimen_item_id = Column(Integer, nullable=False)
    measurement_type = Column(String(255), nullable=False)
    columns = Column(JSON)

    # specimen_item = relationship("SpecimenItem", back_populates="measurements")

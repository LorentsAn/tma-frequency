from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base

from tma.core.database import Base


class CuriePoint(Base):
    __tablename__ = 'curie_points'

    curie_point_id = Column(Integer, primary_key=True)
    specimen_item_id = Column(Integer, nullable=False)
    column_name = Column(String(255), nullable=False)
    id_plot_selected = Column(Integer, nullable=False, default=0)
    temperature_value = Column(Float, nullable=False, default=0.0)
    magnetization_value = Column(Float, nullable=False, default=0.0)

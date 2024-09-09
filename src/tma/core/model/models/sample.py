from sqlalchemy import Column, Integer, String

from tma.core.database import Base


class Sample(Base):
    __tablename__ = 'samples'

    sample_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    x_column = Column(String(255), nullable=False, default='')
    y_column = Column(String(255), nullable=False, default='')
    selected_file_index = Column(Integer, nullable=False, default=0)
    name = Column(String(255), default='')

    # user = relationship("User", back_populates="samples")

from sqlalchemy import Column, Integer, String, Boolean, UniqueConstraint

from tma.core.database import Base


class SpecimenItem(Base):
    __tablename__ = 'specimenitems'

    specimen_item_id = Column(Integer, primary_key=True)
    sample_id = Column(Integer, nullable=False)
    filename = Column(String(255))
    uploaded = Column(Boolean, default=True)
    file_extension = Column(String(255))
    is_empty_source = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint('sample_id', 'filename', name='unique_sample_id_filename'),
    )

    # Relationship to Sample
    # sample = relationship("Sample", back_populates="specimen_items")

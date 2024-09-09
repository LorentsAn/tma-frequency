from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from tma.core.model.models.specimen_item import SpecimenItem


class SpecimenItemRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, specimen_item_id: int):
        return self.session.query(SpecimenItem).filter(SpecimenItem.specimen_item_id == specimen_item_id).first()

    def get_items_by_sample_id(self, sample_id: int):
        return self.session.query(SpecimenItem).filter(SpecimenItem.sample_id == sample_id)

    def get_first_by_sample_id(self, sample_id: int):
        return self.session.query(SpecimenItem).filter(SpecimenItem.sample_id == sample_id).first()

    def get_by_sample_id_and_filename(self, sample_id: int, filename: str):
        return self.session.query(SpecimenItem).filter(
            SpecimenItem.sample_id == sample_id,
            SpecimenItem.filename == filename
        ).first()

    def create_specimen_item(self, sample_id: int, filename: str, file_extension: str, is_empty_source: bool):
        try:
            new_item = SpecimenItem(
                sample_id=sample_id,
                filename=filename,
                file_extension=file_extension,
                is_empty_source=is_empty_source
            )
            self.session.add(new_item)
            self.session.commit()
            return new_item
        except IntegrityError:
            self.session.rollback()
            return None

    def update_specimen_item(self, specimen_item_id: int, **kwargs):
        item = self.session.query(SpecimenItem).filter(SpecimenItem.specimen_item_id == specimen_item_id).first()
        if item:
            for key, value in kwargs.items():
                setattr(item, key, value)
            self.session.commit()
            return item
        return None

    def delete_specimen_item_by_sample_id(self, sample_id: int):
        items = self.session.query(SpecimenItem).filter(SpecimenItem.sample_id == sample_id)
        for item in items:
            if item:
                self.session.delete(item)
        self.session.commit()
        return True

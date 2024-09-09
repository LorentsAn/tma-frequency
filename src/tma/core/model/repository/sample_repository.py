from sqlalchemy.orm import Session

from tma.core.model.models.sample import Sample


class SampleRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_sample_by_id(self, sample_id: int):
        return self.session.query(Sample).filter(Sample.sample_id == sample_id).first()

    def get_sample_by_user_id(self, user_id: int):
        return self.session.query(Sample).filter(Sample.user_id == user_id).first()

    def create_sample(self, user_id: int, x_column: int, y_column: int, selected_file_index: int, name: str):
        new_sample = Sample(
            user_id=user_id,
            x_column=x_column,
            y_column=y_column,
            selected_file_index=selected_file_index,
            name=name
        )
        self.session.add(new_sample)
        self.session.commit()
        return new_sample

    def update_sample(self, sample_id: int, **kwargs):
        sample = self.session.query(Sample).filter(Sample.sample_id == sample_id).first()
        if sample:
            for key, value in kwargs.items():
                setattr(sample, key, value)
            self.session.commit()
            return sample
        return None

    def delete_sample(self, sample_id: int):
        sample = self.session.query(Sample).filter(Sample.sample_id == sample_id).first()
        if sample:
            self.session.delete(sample)
            self.session.commit()
            return True
        return False

from sqlalchemy.orm import Session

from tma.core.model.models.curie_point import CuriePoint


class CuriePointRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_curie_point(
        self,
        specimen_item_id: int,
        column_name: str,
        id_plot_selected: int,
        temperature_value: float,
        magnetization_value: float
    ):
        """
        Adds a new CuriePoint record to the database.
        """
        curie_point_model = CuriePoint(
            specimen_item_id=specimen_item_id,
            column_name=column_name,
            id_plot_selected=id_plot_selected,
            temperature_value=temperature_value,
            magnetization_value=magnetization_value,
        )
        self.session.add(curie_point_model)
        self.session.commit()
        return curie_point_model

    def get_curie_point(self, **filters):
        """
        Retrieves measured data records based on variable filtering criteria.

        Args:
            **filters: Arbitrary keyword arguments for filtering data.

        Returns:
            The query result based on the applied filters.
        """
        query = self.session.query(CuriePoint)
        for attr, value in filters.items():
            query = query.filter(getattr(CuriePoint, attr) == value)
        return query

    def get_all_curie_points(self):
        """
        Retrieves all CuriePoint records from the database.
        """
        return self.session.query(CuriePoint).all()

    def update_curie_point(self, curie_point_id, **kwargs):
        """
        Updates specific fields of a CuriePoint record.
        """
        self.session.query(CuriePoint).filter(CuriePoint.curie_point_id == curie_point_id).update(kwargs)
        self.session.commit()

    def delete_curie_point(self, curie_point_id):
        """
        Deletes a CuriePoint record from the database.
        """
        curie_point = self.get_curie_point(curie_point_id=curie_point_id).first()
        if curie_point:
            self.session.delete(curie_point)
            self.session.commit()

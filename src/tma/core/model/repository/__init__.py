from tma.core.database import SessionLocal
from tma.core.model.repository.curie_point_repository import CuriePointRepository
from tma.core.model.repository.measurement_data_repository import MeasuredDataRepository
from tma.core.model.repository.measurement_repository import MeasurementRepository
from tma.core.model.repository.sample_repository import SampleRepository
from tma.core.model.repository.specimen_item_repository import SpecimenItemRepository
from tma.core.model.repository.user_repository import UserRepository

db = SessionLocal()

user_repo = UserRepository(session=db)
sample_repo = SampleRepository(session=db)
specimen_item_repo = SpecimenItemRepository(session=db)
measurement_repo = MeasurementRepository(session=db)
measured_data_repo = MeasuredDataRepository(session=db)
curie_point_repo = CuriePointRepository(session=db)

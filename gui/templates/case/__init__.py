from .case_animation import CaseAnimationMixin
from .case_items import CaseItemsMixin
from .case_ui import CaseUIMixin
from .case_storage import CaseStorageMixin


class CaseMixin(CaseAnimationMixin, CaseItemsMixin, CaseUIMixin, CaseStorageMixin):
    pass
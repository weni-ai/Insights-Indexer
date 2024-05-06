from abc import ABC
from typing import Any


class BaseRetrieveStorage(ABC):
    def get_by_pk(self, identifier: Any): ...


class BaseInsertStorage(ABC):
    def insert(self, new_obj: object): ...


class GenericStorage(BaseRetrieveStorage, BaseInsertStorage, ABC): ...

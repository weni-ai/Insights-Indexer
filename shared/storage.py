from abc import ABC
from typing import Any


class BaseRetrieveStorage(ABC):
    def get_by_pk(identifier: Any): ...


class BaseInsertStorage(ABC):
    def insert(new_obj: object): ...


class GenericStorage(BaseRetrieveStorage, BaseInsertStorage, ABC): ...

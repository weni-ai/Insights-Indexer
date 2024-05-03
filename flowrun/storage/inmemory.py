from shared.storage import BaseRetrieveStorage


class FlowRunInMemory(BaseRetrieveStorage):
    def __init__(self) -> None:
        self._storage = {}
        super().__init__()

    def get_by_pk(self, identifier: str):
        try:
            return self._storage.get(identifier)
        except AttributeError:
            return None

    def insert(self, new_obj: dict) -> bool:
        try:
            self._storage[new_obj.get("uuid")] = new_obj
            return True
        except AttributeError:
            return False

from typing import Callable


class ObjectETLProcessor:
    def __init__(
        self, object_transformer: Callable, storage_from: object, storage_to: object
    ) -> None:
        self.object_transformer = object_transformer
        self.storage_from = storage_from
        self.storage_to = storage_to

    def execute(self, object_identifier: str):
        # validate is already create in the To Storage
        try:
            to_obj = self.storage_to.get_by_pk(object_identifier)
            if to_obj is not None:
                return True
        except AttributeError as err:
            print("[-] Elasticsearch Get error: ", type(err), err)

        # [E]xtract the obj instance from the From Storage
        from_obj = self.storage_from.get_by_pk(object_identifier)
        if from_obj is None:
            return False

        # [T]ransform the object to be saved in the new storage
        transformed_obj = self.object_transformer(from_obj)

        # [L]oad the treated object into the new storage
        new_obj = self.storage_to.insert(transformed_obj)

        return bool(new_obj)  # if None will return False else True

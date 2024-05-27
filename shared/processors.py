import time
import settings

from typing import Callable
from datetime import datetime, timedelta


class BulkObjectETLProcessor:
    def __init__(
        self,
        object_transformer: Callable,
        storage_from: object,
        storage_to: object,
        storage_org: object,
    ) -> None:
        self.object_transformer = object_transformer
        self.storage_from = storage_from
        self.storage_to = storage_to
        self.storage_org = storage_org

    def execute(self):
        orgs = self.storage_org.list_active()
        for org in orgs:
            org_id = org.get("id")

            # Get last indexed timestamp document on the storage_to
            last_indexed_at = self.storage_to.get_last_indexed_timestamp(org_id)

            # [E]xtract the obj list from the From Storage, filtered by the last indexed timestamp
            from_obj_list = self.storage_from.list_by_timestamp_and_org(
                modified_on=last_indexed_at, org_id=org_id
            )
            if len(from_obj_list) == 0:  # if there's no objects on the list
                time.sleep(settings.EMPTY_ORG_SLEEP)
                continue

            transformed_objects = []
            start = datetime.now()

            for obj in from_obj_list:
                # [T]ransform the object into the new format to be saved in the storage_to
                transformed_obj = self.object_transformer(obj)
                transformed_objects += transformed_obj
                if start < datetime.now() - timedelta(
                    minutes=settings.BATCH_PROCESSING_TIME_LIMIT
                ):  # no single org should take more than X time
                    break

            # [L]oad the treated object list into the new storage
            is_inserted: bool = self.storage_to.bulk_insert(transformed_objects)
            time.sleep(settings.EMPTY_ORG_SLEEP)

        return is_inserted

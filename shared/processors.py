import time
import logging
import settings
from typing import Callable
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

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
        start_time = datetime.now()  # Tempo de início do processo completo

        orgs = (
            settings.ALLOWED_ORGS
            if settings.ALLOWED_ORGS != []
            else self.storage_org.list_active()
        )
        
        for org in orgs:
            logger.info(f"Extraction for org {org}")
            org_id = org if type(org) is int else org.get("id")
            org_start_time = datetime.now()  # Tempo de início do processo por organização

            # Get last indexed timestamp document on the storage_to
            last_indexed_at = self.storage_to.get_last_indexed_timestamp(org_id)
            logger.info(f"last_indexed_at for org {org}, its:{last_indexed_at}")

            # [E]xtract the obj list from the From Storage, filtered by the last indexed timestamp
            extract_start_time = datetime.now()
            from_obj_list = self.storage_from.list_by_timestamp_and_org(
                modified_on=last_indexed_at, org_id=org_id
            )
            extract_elapsed_time = datetime.now() - extract_start_time
            logger.info(f"Extraction for org {org_id} took {extract_elapsed_time.total_seconds():.4f} seconds")

            if len(from_obj_list) == 0:  # if there's no objects on the list
                time.sleep(settings.EMPTY_ORG_SLEEP)
                continue

            transformed_objects = []
            transform_start_time = datetime.now()

            logger.info(f"first object to be indexed {from_obj_list[0]}")

            for obj in from_obj_list:
                # [T]ransform the object into the new format to be saved in the storage_to
                transformed_obj = self.object_transformer(obj)
                transformed_objects += transformed_obj

                if transform_start_time < datetime.now() - timedelta(
                    minutes=settings.BATCH_PROCESSING_TIME_LIMIT
                ):  # no single org should take more than X time
                    break

            transform_elapsed_time = datetime.now() - transform_start_time
            logger.info(f"Transformation for org {org_id} took {transform_elapsed_time.total_seconds():.4f} seconds")

            # [L]oad the treated object list into the new storage
            load_start_time = datetime.now()
            self.storage_to.bulk_insert(transformed_objects)
            load_elapsed_time = datetime.now() - load_start_time
            logger.info(f"Load for org {org_id} took {load_elapsed_time.total_seconds():.4f} seconds")

            org_elapsed_time = datetime.now() - org_start_time
            logger.info(f"Processing for org {org_id} took {org_elapsed_time.total_seconds():.4f} seconds")

            time.sleep(settings.EMPTY_ORG_SLEEP)

        total_elapsed_time = datetime.now() - start_time
        logger.info(f"Total ETL process took {total_elapsed_time.total_seconds():.4f} seconds")

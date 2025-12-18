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

    def _process_org(self, org_id: int) -> None:
        org_start_time = time.time()
        last_indexed_at, last_indexed_uuid = self.storage_to.get_last_indexed_timestamp(org_id)

        extract_start_time = time.time()
        from_obj_list = self.storage_from.list_by_timestamp_and_org(
            modified_on=last_indexed_at, org_id=org_id
        )

        extract_elapsed_time = time.time() - extract_start_time
        logger.info(f"Extraction for org {org_id} took {extract_elapsed_time:.4f} seconds")

        if from_obj_list:
            last_uuid = from_obj_list[-1]["uuid"]
            if last_uuid == last_indexed_uuid:
                from_obj_list = self.storage_from.list_by_timestamp_and_org(
                    modified_on=last_indexed_at, 
                    org_id=org_id, 
                    last_id=last_uuid
                )

        if not from_obj_list:
            time.sleep(settings.EMPTY_ORG_SLEEP)
            return

        transformed_objects = []
        transform_start_time = datetime.now()

        for obj in from_obj_list:
            transformed_obj = self.object_transformer(obj)
            transformed_objects += transformed_obj

            if transform_start_time < datetime.now() - timedelta(
                minutes=settings.BATCH_PROCESSING_TIME_LIMIT
            ):
                break

        transform_elapsed_time = time.time() - transform_start_time
        logger.info(f"Transformation for org {org_id} took {transform_elapsed_time:.4f} seconds")

        load_start_time = time.time()
        self.storage_to.bulk_insert(transformed_objects)
        load_elapsed_time = time.time() - load_start_time
        logger.info(f"Load for org {org_id} took {load_elapsed_time:.4f} seconds")

        org_elapsed_time = time.time() - org_start_time
        logger.info(f"Processing for org {org_id} took {org_elapsed_time:.4f} seconds")

        time.sleep(settings.EMPTY_ORG_SLEEP)

    def execute(self):
        start_time = time.time()
        orgs = (
            settings.ALLOWED_ORGS
            if settings.ALLOWED_ORGS != []
            else self.storage_org.list_active()
        )
        
        for org in orgs:
            org_id = org if type(org) is int else org.get("id")
            self._process_org(org_id)

        total_elapsed_time = time.time() - start_time
        logger.info(f"Total ETL process took {total_elapsed_time:.4f} seconds")

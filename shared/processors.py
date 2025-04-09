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
        start_time = time.time()  # Tempo de início do processo completo

        projects = (
            settings.ALLOWED_PROJECTS
            if settings.ALLOWED_PROJECTS != []
            else self.storage_org.list_active()
        )
        
        for project in projects:
            project_uuid = project
            project_start_time = time.time()  # Tempo de início do processo por organização

            # Get last indexed timestamp document on the storage_to
            last_indexed_at = self.storage_to.get_last_indexed_timestamp(project_uuid)

            # [E]xtract the obj list from the From Storage, filtered by the last indexed timestamp
            extract_start_time = time.time()
            from_obj_list = self.storage_from.list_by_timestamp_and_project(
                modified_on=last_indexed_at, project_uuid=project_uuid
            )
            extract_elapsed_time = time.time() - extract_start_time
            logger.info(f"Extraction for project {project_uuid} took {extract_elapsed_time:.4f} seconds")

            if len(from_obj_list) == 0:  # if there's no objects on the list
                time.sleep(settings.EMPTY_ORG_SLEEP)
                continue

            transformed_objects = []
            transform_start_time = datetime.now()


            for obj in from_obj_list:
                # [T]ransform the object into the new format to be saved in the storage_to
                transformed_obj = self.object_transformer(obj)
                transformed_objects += transformed_obj

                if transform_start_time < datetime.now() - timedelta(
                    minutes=settings.BATCH_PROCESSING_TIME_LIMIT
                ):  # no single org should take more than X time
                    break

            transform_elapsed_time = time.time() - transform_start_time
            logger.info(f"Transformation for org {org_id} took {transform_elapsed_time:.4f} seconds")

            # [L]oad the treated object list into the new storage
            load_start_time = time.time()
            self.storage_to.bulk_insert(transformed_objects)
            load_elapsed_time = time.time() - load_start_time
            logger.info(f"Load for org {project_uuid} took {load_elapsed_time:.4f} seconds")

            org_elapsed_time = time.time() - project_start_time
            logger.info(f"Processing for org {project_uuid} took {org_elapsed_time:.4f} seconds")

            time.sleep(settings.EMPTY_ORG_SLEEP)

        total_elapsed_time = time.time() - start_time
        logger.info(f"Total ETL process took {total_elapsed_time:.4f} seconds")

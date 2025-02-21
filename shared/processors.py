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
        start_time = time.time()  # Full process start time

        orgs = (
            settings.ALLOWED_ORGS
            if settings.ALLOWED_ORGS != []
            else self.storage_org.list_active()
        )
        
        for org in orgs:
            org_id = org if type(org) is int else org.get("id")
            org_start_time = time.time()  # Process start time by organization

            # Get the last indexed timestamp
            last_indexed_at, last_indexed_id = self.storage_to.get_last_indexed_timestamp(org_id)

            max_retries = 8
            for attempt in range(max_retries):
                extract_start_time = time.time()

                # First search WITHOUT filtering by ID
                from_obj_list = self.storage_from.list_by_timestamp_and_org(
                    modified_on=last_indexed_at, org_id=org_id
                )

                extract_elapsed_time = time.time() - extract_start_time
                logger.info(
                    f"Extraction attempt {attempt+1}/{max_retries} for org {org_id} took {extract_elapsed_time:.4f} seconds"
                )

                # If you found objects, check if the last ID matches the one in Elasticsearch
                if from_obj_list:


                    # looop 
                    last_modified_on = from_obj_list[-1]["modified_on"]  # Get the last returned ID
                    last_id_flows = from_obj_list[-1]["id"]
                    # If the last ID is equal to `last_indexed_id`, redo the search now passing `last_id`
                    
                    # Loop
                    if last_indexed_at == last_modified_on:
                        from_obj_list = self.storage_from.list_by_timestamp_and_org(
                            modified_on=last_indexed_at, org_id=org_id, last_id=last_id_flows
                        )
                    

                        if(from_obj_list[-1]["modified_on"] == last_indexed_at)
                            
                            # loop pra ele bater novamente no flows

                    else:
                        break
                else:
                    break      

            if not from_obj_list:
                time.sleep(settings.EMPTY_ORG_SLEEP)
                continue

            # Further processing
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
            logger.info(f"Load for org {org_id} took {load_elapsed_time:.4f} seconds")

            org_elapsed_time = time.time() - org_start_time
            logger.info(f"Processing for org {org_id} took {org_elapsed_time:.4f} seconds")

            time.sleep(settings.EMPTY_ORG_SLEEP)

        total_elapsed_time = time.time() - start_time
        logger.info(f"Total ETL process took {total_elapsed_time:.4f} seconds")

import settings
from shared.storage import BaseRetrieveStorage
from db.postgres.connection import get_cursor


if settings.FLOWRUN_USE_ORG:
    get_flowrun_by_uuid_sql = "SELECT fr.id, fr.uuid, fr.status, fr.org_id, fr.created_on, fr.modified_on, fr.exited_on, fr.responded, fr.results, fr.delete_reason, fr.exit_type, c.uuid AS contact_uuid, c.name AS contact_name, cu.identity AS contact_urn, f.uuid AS flow_uuid, f.name AS flow_name, o.proj_uuid AS project_uuid FROM flows_flowrun fr INNER JOIN contacts_contact c ON fr.contact_id = c.id INNER JOIN contacts_contacturn cu ON cu.id =(SELECT id from contacts_contacturn WHERE contact_id = c.id FETCH FIRST 1 ROWS ONLY) INNER JOIN flows_flow f ON fr.flow_id = f.id INNER JOIN orgs_org o ON fr.org_id = o.id WHERE fr.uuid = (%s);"
else:
    get_flowrun_by_uuid_sql = "SELECT fr.id, fr.uuid, fr.status, fr.org_id, fr.created_on, fr.modified_on, fr.exited_on, fr.responded, fr.results, fr.delete_reason, fr.exit_type, c.uuid AS contact_uuid, c.name AS contact_name, cu.identity AS contact_urn, f.uuid AS flow_uuid, f.name AS flow_name, proj.project_uuid AS project_uuid FROM flows_flowrun fr INNER JOIN contacts_contact c ON fr.contact_id = c.id INNER JOIN contacts_contacturn cu ON cu.id =( SELECT id from contacts_contacturn WHERE contact_id = c.id FETCH FIRST 1 ROWS ONLY) INNER JOIN flows_flow f ON fr.flow_id = f.id INNER JOIN internal_project proj ON fr.org_id = proj.org_ptr_id WHERE fr.uuid =(%s);"

list_flowrun_by_org_id_and_modified_on_sql = "SELECT fr.id, fr.uuid, fr.org_id, fr.status, fr.created_on, fr.modified_on, fr.exited_on, fr.responded, fr.results, fr.delete_reason, fr.exit_type, c.uuid AS contact_uuid, c.name AS contact_name, cu.identity AS contact_urn, f.uuid AS flow_uuid, f.name AS flow_name, o.proj_uuid AS project_uuid FROM flows_flowrun fr INNER JOIN contacts_contact c ON fr.contact_id = c.id LEFT JOIN contacts_contacturn cu ON cu.id =( SELECT id from contacts_contacturn WHERE contact_id = c.id FETCH FIRST 1 ROWS ONLY) INNER JOIN flows_flow f ON fr.flow_id = f.id INNER JOIN orgs_org o ON fr.org_id = o.id WHERE fr.exited_on IS NOT null AND fr.org_id =(%s) AND fr.modified_on > (%s) ORDER BY fr.modified_on ASC, id ASC FETCH FIRST (%s) ROWS ONLY;"


class FlowRunPostgreSQL(BaseRetrieveStorage):
    def get_by_pk(self, identifier: str) -> dict:
        with get_cursor() as cur:
            flowrun_query = cur.execute(
                get_flowrun_by_uuid_sql,
                (identifier,),
            ).fetchone()
            return flowrun_query

    def list_by_timestamp_and_org(
        self, modified_on: str, org_id: int, limit: int = settings.FLOW_RUN_BATCH_LIMIT
    ) -> list[dict]:
        with get_cursor() as cur:
            flowrun_query = cur.execute(
                list_flowrun_by_org_id_and_modified_on_sql,
                (org_id, modified_on, limit),
            ).fetchall()
            return flowrun_query


get_active_orgs = "SELECT id FROM orgs_org WHERE is_active = TRUE "
org_query_attrs = []

if settings.ALLOWED_PROJECTS:
    placeholders = ", ".join(["%s"] * len(settings.ALLOWED_PROJECTS))
    get_active_orgs += f"AND proj_uuid IN ({placeholders}) "
    org_query_attrs += settings.ALLOWED_PROJECTS


# Commented to be used in the next version V5
# if settings.IS_LAST_ORG_BATCH:
#     get_active_orgs += "AND id > (%s)"
#     org_query_attrs.append(settings.ORG_RANGE_FROM)

get_active_orgs += "order by id;"  # FETCH FIRST (%s) ROWS ONLY;"


class OrgPostgreSQL(BaseRetrieveStorage):
    def list_active(self) -> list[dict]:
        with get_cursor() as cur:
            flowrun_query = cur.execute(
                get_active_orgs,
                org_query_attrs,
                # settings.ORGS_BATCH_SIZE,
            ).fetchall()
            return flowrun_query

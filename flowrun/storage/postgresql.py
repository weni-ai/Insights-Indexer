import settings
from shared.storage import BaseRetrieveStorage
from db.postgres.connection import get_cursor


if settings.FLOWRUN_USE_ORG:
    get_flowrun_by_uuid_sql = "SELECT fr.id, fr.uuid, fr.status, fr.created_on, fr.exited_on, fr.responded, fr.results, fr.delete_reason, fr.exit_type, c.uuid AS contact_uuid, c.name AS contact_name, cu.identity AS contact_urn, f.uuid AS flow_uuid, f.name AS flow_name, o.proj_uuid AS project_uuid FROM flows_flowrun fr INNER JOIN contacts_contact c ON fr.contact_id = c.id INNER JOIN contacts_contacturn cu ON cu.id =(SELECT id from contacts_contacturn WHERE contact_id = c.id FETCH FIRST 1 ROWS ONLY) INNER JOIN flows_flow f ON fr.flow_id = f.id INNER JOIN orgs_org o ON fr.org_id = o.id WHERE fr.uuid = (%s);"
else:
    get_flowrun_by_uuid_sql = "SELECT fr.id, fr.uuid, fr.status, fr.created_on, fr.exited_on, fr.responded, fr.results, fr.delete_reason, fr.exit_type, c.uuid AS contact_uuid, c.name AS contact_name, cu.identity AS contact_urn, f.uuid AS flow_uuid, f.name AS flow_name, proj.project_uuid AS project_uuid FROM flows_flowrun fr INNER JOIN contacts_contact c ON fr.contact_id = c.id INNER JOIN contacts_contacturn cu ON cu.id =( SELECT id from contacts_contacturn WHERE contact_id = c.id FETCH FIRST 1 ROWS ONLY) INNER JOIN flows_flow f ON fr.flow_id = f.id INNER JOIN internal_project proj ON fr.org_id = proj.org_ptr_id WHERE fr.uuid =(%s);"


class FlowRunPostgreSQL(BaseRetrieveStorage):
    def get_by_pk(self, identifier: str) -> dict:
        with get_cursor() as cur:
            flowrun_query = cur.execute(
                get_flowrun_by_uuid_sql,
                (identifier,),
            ).fetchone()
            return flowrun_query

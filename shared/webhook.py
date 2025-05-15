import settings
import logging
from flask import Flask, request, jsonify
from cache.project_cache import ProjectUUIDCache
import threading

logger = logging.getLogger(__name__)
app = Flask(__name__)

@app.route('/webhook/project/update', methods=['POST'])
def project_update_webhook():
    """
    Webhook to receive notifications when projects are released
    
    Expects a JSON with:
    {
        "project_uuid": "UUID of the released project"
    }
    """
    data = request.json
    
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400
    
    project_uuid = data.get('project_uuid')
    
    if not project_uuid:
        return jsonify({
            "status": "error", 
            "message": "Missing required field: project_uuid"
        }), 400
    
    logger.info("Received project update notification for project_uuid={}".format(project_uuid))
    
    threading.Thread(
        target=update_project_cache,
        args=(project_uuid,),
        daemon=True
    ).start()
    
    return jsonify({
        "status": "success",
        "message": "Project {} will be included in the next indexing cycle".format(project_uuid)
    })

def update_project_cache(project_uuid):
    """
    Updates the project cache to include the released project
    """
    try:
        logger.info("Updating project cache for project_uuid={}".format(project_uuid))
        
        cache = ProjectUUIDCache.get_instance()
        
        cache.refresh()
        
        projects = cache.get_projects_uuids()
        if projects and project_uuid in [p if isinstance(p, str) else p.get("uuid") for p in projects]:
            logger.info("Project {} successfully added to cache".format(project_uuid))
        else:
            logger.warning("Project {} might not be in the cache yet. Will be included in next refresh.".format(project_uuid))
        
    except Exception as e:
        logger.error("Error updating project cache for project_uuid={}: {}".format(project_uuid, str(e)))

def run_webhook_server():
    """Starts the Flask server for the webhook"""
    app.run(
        host=settings.WEBHOOK_HOST if hasattr(settings, 'WEBHOOK_HOST') else '0.0.0.0',
        port=settings.WEBHOOK_PORT if hasattr(settings, 'WEBHOOK_PORT') else 5000,
        debug=settings.DEBUG if hasattr(settings, 'DEBUG') else False
    )

if __name__ == "__main__":
    run_webhook_server()
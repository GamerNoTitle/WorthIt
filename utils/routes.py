from flask import blueprints, send_from_directory

ADMIN_ROUTES = blueprints.Blueprint("admin_routes", __name__)
ADMIN_API_ROUTES = blueprints.Blueprint("admin_api_routes", __name__)
PUBLIC_ROUTES = blueprints.Blueprint("user_routes", __name__)
PUBLIC_API_ROUTES = blueprints.Blueprint("user_api_routes", __name__)

PUBLIC_ROUTES.add_url_rule("/", "index", lambda: send_from_directory("templates", "index.html"))

@PUBLIC_ROUTES.route("/static/<path:filename>")
def static_files(filename):
    """
    提供静态文件服务，允许访问 static 目录下的静态资源。
    """
    return send_from_directory("static", filename)


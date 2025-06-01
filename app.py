from flask import Flask, send_from_directory
from utils.routes import ADMIN_ROUTES, ADMIN_API_ROUTES, PUBLIC_ROUTES, PUBLIC_API_ROUTES

app = Flask(__name__)
# 注册蓝图
app.register_blueprint(ADMIN_ROUTES, url_prefix="/admin")
app.register_blueprint(ADMIN_API_ROUTES, url_prefix="/admin/api")
app.register_blueprint(PUBLIC_ROUTES, url_prefix="/")
app.register_blueprint(PUBLIC_API_ROUTES, url_prefix="/api/public")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
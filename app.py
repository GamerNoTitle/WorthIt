from flask import Flask, send_from_directory
from utils.routes import ADMIN_API_ROUTES, PUBLIC_ROUTES, PUBLIC_API_ROUTES
import os
from utils.database import NotionItemTrackerClient
from utils.tools import load_config

# 初始化 Notion 客户端
notion_client = NotionItemTrackerClient(
    os.environ.get("NOTION_TOKEN", load_config().get("token")),
    os.environ.get("NOTION_DATABASE_ID", load_config().get("dbid"))
)

app = Flask(__name__)

app.config['ENABLE_PUBLIC_VIEW'] = True if str(os.environ.get("ENABLE_PUBLIC_VIEW", load_config().get("public"))).lower() not in ['false', '0'] else False
app.config['SECRET_KEY'] = os.urandom(64).hex()

# 注册蓝图
app.register_blueprint(ADMIN_API_ROUTES, url_prefix="/admin/api")
app.register_blueprint(PUBLIC_ROUTES, url_prefix="/")
app.register_blueprint(PUBLIC_API_ROUTES, url_prefix="/api/public")

if __name__ == "__main__":
    app.client = notion_client
    resp = app.client.update_item(
        page_id="2056dedb-b716-8055-ad48-d7c4ab5a18e7",
        updates={
            "物品名称": "测试测试测试",
            "入役日期": "2025-05-30",
            "购买价格": 1145.14,
            "附加价值": 1919.81,
            "退役日期": "2025-06-02",
            "备注": "测试备注",
        }
    )
    print(resp)
    app.run(host="127.0.0.1", port=5000, debug=True)
from flask import Flask, send_from_directory
from utils.routes import ADMIN_API_ROUTES, PUBLIC_ROUTES, PUBLIC_API_ROUTES
import os
from utils.database import NotionItemTrackerClient
from utils.tools import load_config
import json

# 检查配置是否正确
if (
    os.environ.get("NOTION_TOKEN") is None
    or os.environ.get("NOTION_DATABASE_ID") is None
    or os.environ.get("WORTHIT_USERNAME") is None
    or os.environ.get("WORTHIT_PASSWORD") is None
):
    try:
        with open("config.json") as f:
            config = json.loads(f.read())
            if (
                (config.get("token") is None and os.environ.get("NOTION_TOKEN") is None)
                or (
                    config.get("dbid") is None
                    and os.environ.get("NOTION_DATABASE_ID") is None
                )
                or (
                    config.get("credentials", {}).get("username") == ""
                    and os.environ.get("WORTHIT_USERNAME") is None
                )
                or (
                    config.get("credentials", {}).get("password") == ""
                    and os.environ.get("WORTHIT_PASSWORD") is None
                )
            ):
                print("CRITICAL: 请先配置好程序需要的环境变量/配置后再运行本程序！")
    except FileNotFoundError:
        print(
            "CRITICAL: 你并没有在环境变量中配置必要的配置，且没有使用配置文件进行配置，请先对程序进行配置后再运行！"
        )
        os._exit(1)
    except Exception as e:
        print(f"CRITICAL: 程序在检查配置的时候遇到了未预料的错误：{e}")
        os._exit(1)

# 初始化 Notion 客户端
notion_client = NotionItemTrackerClient(
    os.environ.get("NOTION_TOKEN", load_config().get("token")),
    os.environ.get("NOTION_DATABASE_ID", load_config().get("dbid")),
)

app = Flask(__name__)

app.config["ENABLE_PUBLIC_VIEW"] = (
    True
    if str(os.environ.get("ENABLE_PUBLIC_VIEW", load_config().get("public"))).lower()
    not in ["false", "0"]
    else False
)
app.config["SECRET_KEY"] = os.urandom(64).hex() if not os.environ.get("SECRET_KEY") else os.environ.get("SECRET_KEY")   # 使用 os 做云函数兼容性处理
app.config["WORTHIT_USERNAME"] = (
    os.environ.get("WORTHIT_USERNAME")
    if not os.environ.get("WORTHIT_USERNAME") is None
    else load_config().get("credentials", {}).get("username")
)
app.config["WORTHIT_PASSWORD"] = (
    os.environ.get("WORTHIT_PASSWORD")
    if not os.environ.get("WORTHIT_PASSWORD") is None
    else load_config().get("credentials", {}).get("password")
)

# 注册蓝图
app.register_blueprint(ADMIN_API_ROUTES, url_prefix="/api/admin")
app.register_blueprint(PUBLIC_ROUTES, url_prefix="/")
app.register_blueprint(PUBLIC_API_ROUTES, url_prefix="/api/public")

if __name__ == "__main__":
    app.client = notion_client
    print(app.config)
    app.run(host="127.0.0.1", port=5000, debug=True)

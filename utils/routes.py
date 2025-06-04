from flask import blueprints, send_from_directory, current_app, request, jsonify
from utils.database import NotionItemTrackerClient
from jwt import decode, encode, ExpiredSignatureError, InvalidTokenError
from utils.security import verify_password
import os
import json

ADMIN_API_ROUTES = blueprints.Blueprint("admin_api_routes", __name__)
PUBLIC_ROUTES = blueprints.Blueprint("user_routes", __name__)
PUBLIC_API_ROUTES = blueprints.Blueprint("user_api_routes", __name__)

PUBLIC_ROUTES.add_url_rule(
    "/", "index", lambda: send_from_directory("templates", "index.html")
)


@ADMIN_API_ROUTES.before_request
def check_admin_access(is_request: bool = True):
    cookie = request.cookies
    token = cookie.get("token")
    if not token:
        if is_request:
            return jsonify({"success": False, "message": "Unauthorized access"}), 401
        else:
            return False

    # 云函数兼容性处理
    try:
        secret_key = current_app.config["SECRET_KEY"]
    except AttributeError:
        secret_key = os.environ.get("SECRET_KEY", "")

    if not secret_key:
        if is_request:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Server configuration error: missing secret key.",
                    }
                ),
                500,
            )
        else:
            return False

    try:
        payload = decode(
            token,
            secret_key,  # 使用获取到的secret_key
            algorithms=["HS256"],
        )
        if not is_request:
            return True
    except ExpiredSignatureError:
        if is_request:
            response = jsonify({"success": False, "message": "Token expired"})
            response.delete_cookie("token")
            return response, 401
        else:
            return False
    except InvalidTokenError:
        if is_request:
            response = jsonify({"success": False, "message": "Invalid token"})
            response.delete_cookie("token")
            return response, 401
        else:
            return False
    except Exception as e:
        if is_request:
            response = jsonify(
                {"success": False, "message": f"Error decoding token: {str(e)}"}
            )
            response.delete_cookie("token")
            return (
                response,
                500,
            )
        else:
            return False


@PUBLIC_ROUTES.route("/static/<path:filename>")
def static_files(filename):
    """
    提供静态文件服务，允许访问 static 目录下的静态资源。
    """
    return send_from_directory("static", filename)


@PUBLIC_API_ROUTES.route("/health")
def health_check():
    """
    健康检查接口，返回服务状态。
    """
    return {"status": "ok"}, 200


@PUBLIC_API_ROUTES.route("/items", methods=["GET"])
def get_items():
    """
    获取网站所有者的所有好物的接口
    """
    # 云函数兼容性处理：获取 NotionItemTrackerClient 实例
    try:
        client: NotionItemTrackerClient = current_app.client
    except AttributeError:
        client = NotionItemTrackerClient(
            os.environ.get("NOTION_TOKEN", ""), os.environ.get("NOTION_DATABASE_ID", "")
        )

    # 云函数兼容性处理：获取 ENABLE_PUBLIC_VIEW 配置
    enable_public_view = False
    try:
        enable_public_view = current_app.config["ENABLE_PUBLIC_VIEW"]
    except AttributeError:
        enable_public_view = (
            True
            if str(os.environ.get("ENABLE_PUBLIC_VIEW", "true")).lower()
            not in ["false", "0"]
            else False
        )

    if not enable_public_view:
        if not check_admin_access(is_request=False):
            return {
                "success": False,
                "message": "本好物页面未公开展示，你需要登录来进行查看！",
            }, 403
        items = client.read_items(include_formula_and_rollup=True)
        return {"success": True, "items": items, "message": "success"}, 200
    else:
        items = client.read_items(include_formula_and_rollup=True)
        return {"success": True, "items": items, "message": "success"}, 200


@PUBLIC_API_ROUTES.route("/login", methods=["POST"])
def login():
    """
    登录 API
    """
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return (
            jsonify(
                {"success": False, "message": "Username and password are required"}
            ),
            400,
        )

    # 云函数兼容性处理：获取 WORTHIT_USERNAME, WORTHIT_PASSWORD, SECRET_KEY
    app_username = None
    app_password_hash = None
    secret_key = None
    try:
        app_username = current_app.config["WORTHIT_USERNAME"]
        app_password_hash = current_app.config["WORTHIT_PASSWORD"]
        secret_key = current_app.config["SECRET_KEY"]
    except AttributeError:
        app_username = os.environ.get("WORTHIT_USERNAME")
        app_password_hash = os.environ.get("WORTHIT_PASSWORD")
        secret_key = os.environ.get("SECRET_KEY", "")

    if not app_username or not app_password_hash or not secret_key:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Server configuration error: missing credentials or secret key.",
                }
            ),
            500,
        )

    if username == app_username:
        if verify_password(password, app_password_hash):
            try:
                token = encode(
                    {"username": username},
                    secret_key,  # 使用获取到的secret_key
                    algorithm="HS256",
                )
                response = jsonify({"success": True, "message": "Login successful"})
                response.set_cookie("token", token, httponly=True, secure=True)
                return response
            except Exception as e:
                # 记录编码token的错误
                current_app.logger.error(f"Error encoding token: {e}")
                return (
                    jsonify({"success": False, "message": "Failed to create token"}),
                    500,
                )
        else:
            return (
                jsonify({"success": False, "message": "Invalid credentials"}),
                401,
            )
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401


@PUBLIC_API_ROUTES.route("/logout", methods=["POST"])
def logout():
    """
    注销 API
    """
    response = jsonify({"success": True, "message": "Logout successful"})
    response.delete_cookie("token")
    return response


@ADMIN_API_ROUTES.route("/health", methods=["GET"])
def admin_health_check():
    """
    检查用户是否登录
    """
    if not check_admin_access(is_request=False):
        return jsonify({"success": False, "message": "Unauthorized access"}), 401
    return jsonify({"success": True, "message": "Admin API is healthy"}), 200


@ADMIN_API_ROUTES.route("/items/<item_id>", methods=["GET"])
def get_item(item_id: str):
    """
    获取指定 ID 的物品数据
    """
    # 云函数兼容性处理：获取 NotionItemTrackerClient 实例
    try:
        client: NotionItemTrackerClient = current_app.client
    except AttributeError:
        client = NotionItemTrackerClient(
            os.environ.get("NOTION_TOKEN", ""), os.environ.get("NOTION_DATABASE_ID", "")
        )
    item = None  # 初始化为None
    try:
        items = client.read_items(include_formula_and_rollup=True)
        for i in items:  # 使用 i 避免与外部 item 变量混淆
            if i.get("id") == item_id:
                item = i
                break
    except Exception as e:
        return jsonify(
            {
                "success": False,
                "message": "Failed to retrieve item. Please refer to the log for details.",
                "error": str(e),
            }
        )
    if item:
        return (
            jsonify(
                {
                    "success": True,
                    "item": item,
                    "message": "Item retrieved successfully",
                }
            ),
            200,
        )
    else:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Item not found",
                    "error": "Item not found",
                }
            ),
            404,
        )


@ADMIN_API_ROUTES.route("/items", methods=["POST"])
def create_item():
    """
    创建一个新的物品数据
    """
    # 云函数兼容性处理：获取 NotionItemTrackerClient 实例
    try:
        client: NotionItemTrackerClient = current_app.client
    except AttributeError:
        client = NotionItemTrackerClient(
            os.environ.get("NOTION_TOKEN", ""), os.environ.get("NOTION_DATABASE_ID", "")
        )
    data = request.json
    name = data.get("properties", {}).get("name")
    entry_date = data.get("properties", {}).get("entry_date")
    purchase_price = data.get("properties", {}).get("purchase_price")
    additional_value = data.get("properties", {}).get("additional_value")
    retirement_date = data.get("properties", {}).get("retirement_date")
    remark = data.get("properties", {}).get("remark")
    # 检查必填字段
    if not name or not purchase_price:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Name and purchase price are required fields.",
                }
            ),
            400,
        )
    try:
        result = client.add_item(
            item_name=name,
            entry_date=entry_date,
            purchase_price=purchase_price,
            additional_value=additional_value
            if (additional_value is not None or additional_value == 0)
            else None,
            retirement_date=retirement_date if retirement_date is not None else None,
            remark=remark if remark is not None else None,
        )
    except Exception as e:
        return jsonify(
            {
                "success": False,
                "message": "Failed to create item. Please refer to the log for details.",
                "error": str(e),
            }
        )
    if result:
        print(result)  # 建议使用 current_app.logger.info(result)
        if result.get("object") == "page" and result.get("id"):
            return jsonify(
                {
                    "success": True,
                    "message": "Item created successfully.",
                }
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Failed to create item. Please refer to the log for details.",
                        "error": result,
                    }
                ),
                500,
            )
    else:
        return jsonify(
            {
                "success": False,
                "message": "Failed to create item. Please refer to the log for details.",
            },
            500,
        )


@ADMIN_API_ROUTES.route("/items/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    """
    删除指定 ID 的物品数据
    """
    # 云函数兼容性处理：获取 NotionItemTrackerClient 实例
    try:
        client: NotionItemTrackerClient = current_app.client
    except AttributeError:
        client = NotionItemTrackerClient(
            os.environ.get("NOTION_TOKEN", ""), os.environ.get("NOTION_DATABASE_ID", "")
        )
    try:
        result = client.delete_item(item_id)
    except Exception as e:
        return jsonify(
            {
                "success": False,
                "message": "Failed to delete item. Please refer to the log for details.",
                "error": str(e),
            }
        )
    if result:
        if result.get("object") == "page" and result.get("id"):
            return jsonify(
                {
                    "success": True,
                    "message": "Item deleted successfully.",
                }
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Failed to delete item. Please refer to the log for details.",
                        "error": result,
                    }
                ),
                500,
            )
    else:
        return jsonify(
            {
                "success": False,
                "message": "Failed to delete item. Please refer to the log for details.",
            }
        )


@ADMIN_API_ROUTES.route("/items/<item_id>", methods=["PATCH"])
def modify_item(item_id: str):
    """
    修改特定物品数据
    """
    # 云函数兼容性处理：获取 NotionItemTrackerClient 实例
    try:
        client: NotionItemTrackerClient = current_app.client
    except AttributeError:
        client = NotionItemTrackerClient(
            os.environ.get("NOTION_TOKEN", ""), os.environ.get("NOTION_DATABASE_ID", "")
        )
    data = request.json
    name = data.get("name")
    entry_date = data.get("entry_date")
    purchase_price = data.get("purchase_price")
    additional_value = data.get("additional_value")
    retirement_date = data.get("retirement_date")
    remark = data.get("remark")

    updates = {}
    if name is not None:
        updates["物品名称"] = name
    if entry_date is not None:
        updates["入役日期"] = entry_date
    if purchase_price is not None:
        updates["购买价格"] = float(purchase_price)
    if additional_value is not None:
        updates["附加价值"] = float(additional_value)
    if retirement_date is not None:
        updates["退役日期"] = retirement_date
    if remark is not None:
        updates["备注"] = remark

    try:
        result = client.update_item(page_id=item_id, updates=updates)
    except Exception as e:
        return jsonify(
            {
                "success": False,
                "message": "Failed to update item. Please refer to the log for details.",
                "error": str(e),
            }
        )

    if result:
        if result.get("object") == "page" and result.get("id"):
            return jsonify(
                {
                    "success": True,
                    "message": "Item updated successfully.",
                }
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Failed to update item. Please refer to the log for details.",
                        "error": result,
                    }
                ),
                500,
            )
    else:
        return jsonify(
            {
                "success": False,
                "message": "Failed to update item. Please refer to the log for details.",
            }
        )
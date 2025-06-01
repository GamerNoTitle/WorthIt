from flask import blueprints, send_from_directory, current_app, request, jsonify
from utils.database import NotionItemTrackerClient

ADMIN_API_ROUTES = blueprints.Blueprint("admin_api_routes", __name__)
PUBLIC_ROUTES = blueprints.Blueprint("user_routes", __name__)
PUBLIC_API_ROUTES = blueprints.Blueprint("user_api_routes", __name__)

PUBLIC_ROUTES.add_url_rule(
    "/", "index", lambda: send_from_directory("templates", "index.html")
)


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
    client: NotionItemTrackerClient = current_app.client
    items = client.read_items(include_formula_and_rollup=True)
    return {"items": items}, 200


@ADMIN_API_ROUTES.route("/items", methods=["POST"])
def create_item():
    """
    创建一个新的物品数据
    """
    client: NotionItemTrackerClient = current_app.client
    data = request.json
    name = data.get("name")
    entry_date = data.get("entry_date")
    purchase_price = data.get("purchase_price")
    additional_value = data.get("additional_value")
    retirement_date = data.get("retirement_date")
    remark = data.get("remark")
    try:
        result = client.add_item(
            item_name=name,
            entry_date=entry_date,
            purchase_price=purchase_price,
            additional_value=additional_value if additional_value is not None else None,
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
            }
        )


@ADMIN_API_ROUTES.route("/items/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    """
    删除指定 ID 的物品数据
    """
    client: NotionItemTrackerClient = current_app.client
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
    client: NotionItemTrackerClient = current_app.client
    data = request.json
    name = data.get("name")
    entry_date = data.get("entry_date")
    purchase_price = data.get("purchase_price")
    additional_value = data.get("additional_value")
    retirement_date = data.get("retirement_date")
    remark = data.get("remark")
    updates = {}
    if not name is None:
        updates["物品名称"] = name
    if not entry_date is None:
        updates["入役日期"] = entry_date
    if not purchase_price is None:
        updates["购买价格"] = float(purchase_price)
    if not additional_value is None:
        updates["附加价值"] = float(additional_value)
    if not retirement_date is None:
        updates["退役日期"] = retirement_date
    if not remark is None:
        updates["备注"] = remark
    result = client.update_item(
        page_id=item_id,
        updates=updates
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
import os
import sys
from notion_client import Client
from notion_client.errors import APIResponseError

# Notion API 令牌的环境变量名
NOTION_TOKEN_ENV_VAR = "NOTION_TOKEN"

def get_notion_client():
    """
    尝试从环境变量中获取 Notion API 令牌并初始化 Notion 客户端。
    """
    token = os.getenv(NOTION_TOKEN_ENV_VAR)

    if not token:
        print(f"错误: 请将您的 Notion 集成令牌设置为环境变量 '{NOTION_TOKEN_ENV_VAR}'。")
        print("您可以在这里创建和获取令牌: https://www.notion.so/my-integrations")
        print("示例 (在 Bash/Zsh 中): export NOTION_TOKEN='secret_YOUR_TOKEN_HERE'")
        print("示例 (在 PowerShell 中): $env:NOTION_TOKEN='secret_YOUR_TOKEN_HERE'")
        sys.exit(1)

    try:
        client = Client(auth=token)
        print("Notion 客户端初始化成功！")
        return client
    except APIResponseError as e:
        print(f"初始化 Notion 客户端时发生 API 错误: {e}")
        print("请检查您的 Notion 令牌是否正确且有效。")
        sys.exit(1)
    except Exception as e:
        print(f"初始化 Notion 客户端时发生未知错误: {e}")
        sys.exit(1)

def get_user_databases(client):
    """
    列出用户集成有权访问的所有 Notion 数据库。
    """
    print("\n正在搜索您有权访问的数据库...")
    try:
        # 使用 search API 查找所有 object 类型为 "database" 的项
        response = client.search(
            filter={"property": "object", "value": "database"}
        )
        databases = response.get("results", [])

        if not databases:
            print("未找到任何数据库，或您的集成当前无法访问任何数据库。")
            print("请确保您已将 Notion 数据库或页面分享给您的集成。")
            print("分享方式: 在 Notion 中打开数据库 -> 点击 'Share' -> 'Invite' -> 搜索您的集成名称 -> 选择并赋予 'Can view' 权限。")
            return []
        
        return databases
    except APIResponseError as e:
        print(f"搜索数据库时发生 API 错误: {e}")
        if "Unauthorized" in str(e):
            print("请确保您的 Notion 令牌正确且具有搜索权限。")
        return []
    except Exception as e:
        print(f"搜索数据库时发生未知错误: {e}")
        return []

def select_database(databases):
    """
    让用户从列表中选择一个数据库。
    """
    if not databases:
        return None

    print("\n可用的数据库:")
    for i, db in enumerate(databases):
        # 数据库的标题通常是 rich_text 数组，我们需要提取 plain_text
        title_rich_text = db.get("title", [{"plain_text": "Untitled"}])
        title = "".join([t.get("plain_text", "") for t in title_rich_text])
        print(f"{i + 1}. {title} (ID: {db['id']})")

    while True:
        try:
            choice = int(input(f"请输入您想读取的数据库的序号 (1-{len(databases)}): "))
            if 1 <= choice <= len(databases):
                return databases[choice - 1]
            else:
                print("无效的选择。请输入列表中的数字。")
        except ValueError:
            print("无效的输入。请输入一个数字。")

def _get_property_value(property_data):
    """
    根据 Notion 属性类型提取并格式化其值。
    Notion API 返回的属性值结构复杂，需要根据类型解析。
    """
    prop_type = property_data.get("type")

    # === 关键改动：添加对 'string' 类型的直接处理 ===
    if prop_type == "string":
        return property_data["string"]
    # ===============================================
    elif prop_type == "title":
        return "".join([rt.get("plain_text", "") for rt in property_data["title"]])
    elif prop_type == "rich_text":
        return "".join([rt.get("plain_text", "") for rt in property_data["rich_text"]])
    elif prop_type == "number":
        return property_data["number"]
    elif prop_type == "checkbox":
        return "✅" if property_data["checkbox"] else "❌"
    elif prop_type == "select":
        return property_data["select"].get("name") if property_data["select"] else None
    elif prop_type == "multi_select":
        return ", ".join([s.get("name") for s in property_data["multi_select"]])
    elif prop_type == "date":
        date_obj = property_data["date"]
        if date_obj:
            start = date_obj.get("start")
            end = date_obj.get("end")
            if start and end:
                return f"{start} - {end}"
            elif start:
                return start
        return None
    elif prop_type == "url":
        return property_data["url"]
    elif prop_type == "email":
        return property_data["email"]
    elif prop_type == "phone_number":
        return property_data["phone_number"]
    elif prop_type == "files":
        return ", ".join([f.get("name") for f in property_data["files"]])
    elif prop_type == "relation":
        # 关系属性只返回关联页面的ID，如果需要标题，需要额外查询
        return f"关系: {[r.get('id') for r in property_data['relation']]}"
    elif prop_type == "people":
        # 人员属性返回用户ID和名称
        return ", ".join([p.get("name") for p in property_data["people"]])
    elif prop_type == "formula":
        # 公式属性的结果类型不定，需要进一步解析
        formula_result = property_data["formula"]
        formula_type = formula_result.get("type") # e.g., "number", "string", "boolean", "date"
        
        # 递归调用 _get_property_value 以解析公式的实际结果。
        # 结构为 { "type": 公式输出类型, 公式输出类型: 实际值 }
        # 例如，如果公式输出字符串，则 `formula_result` 中包含 {"type": "string", "string": "一些文本"}。
        # 我们将此子结构传递给 _get_property_value，它将正确处理。
        return _get_property_value({formula_type: formula_result.get(formula_type), "type": formula_type})
    elif prop_type == "rollup":
        # Rollup 属性结果复杂，可能是一个数组或其他类型
        rollup_result = property_data["rollup"]
        if rollup_result.get("type") == "array":
            processed_items = []
            for item in rollup_result.get("array"):
                # Rollup 数组中的每个项目本身可能是一个完整的 Notion 属性结构
                if isinstance(item, dict) and "type" in item:
                    processed_items.append(_get_property_value(item))
                else:
                    processed_items.append(str(item)) # 如果不是标准属性结构，则直接转为字符串
            return ", ".join(map(str, processed_items))
        # 对于其他简单类型的 rollup 结果 (例如，来自公式的 "number", "date", "boolean", "string")
        elif rollup_result.get("type") in ["number", "date", "boolean", "string"]:
            return _get_property_value({"type": rollup_result["type"], rollup_result["type"]: rollup_result.get(rollup_result["type"])})
        
        # 捕获未知或未处理的 rollup 类型
        return f"[rollup类型: {rollup_result.get('type', '未知')}]"

    elif prop_type == "created_time":
        return property_data["created_time"]
    elif prop_type == "last_edited_time":
        return property_data["last_edited_time"]
    elif prop_type == "created_by":
        return property_data["created_by"].get("name")
    elif prop_type == "last_edited_by":
        return property_data["last_edited_by"].get("name")
    # 添加更多您需要的属性类型
    else:
        return f"[不支持的类型: {prop_type}]"


def read_database_content(client, database_id):
    """
    读取指定数据库中的所有页面内容。
    """
    print(f"\n正在读取数据库内容 (ID: {database_id})...")
    try:
        response = client.databases.query(database_id=database_id)
        pages = response.get("results", [])

        if not pages:
            print("该数据库中没有页面。")
            return

        print(f"找到 {len(pages)} 个页面:")
        for page in pages:
            print("-" * 40) # 分隔符

            # 尝试找到页面的主要标题 (通常是 'title' 类型的属性)
            page_title = "无标题页面"
            for prop_name, prop_data in page.get("properties", {}).items():
                if prop_data.get("type") == "title":
                    page_title = _get_property_value(prop_data)
                    break # 找到标题后退出循环

            print(f"页面标题: {page_title}")
            print(f"页面ID: {page['id']}")

            # 遍历并打印所有其他属性
            for prop_name, prop_data in page.get("properties", {}).items():
                if prop_data.get("type") == "title":
                    continue # 标题已经打印过了，跳过

                value = _get_property_value(prop_data)
                # 过滤掉空值或None，除非你希望显示它们
                if value is not None and value != "" and value != []:
                    print(f"  {prop_name}: {value}")
        print("-" * 40)

    except APIResponseError as e:
        print(f"读取数据库内容时发生 API 错误: {e}")
        if "Unauthorized" in str(e) or "Not found" in str(e):
            print("请确保您的 Notion 令牌对该数据库有 'Can view' 权限。")
        elif "Validation error" in str(e):
            print("数据库结构或查询参数可能存在问题。")
        return
    except Exception as e:
        print(f"读取数据库内容时发生未知错误: {e}")
        return

def main():
    """
    主程序入口。
    """
    client = get_notion_client()
    if not client:
        return

    databases = get_user_databases(client)
    if not databases:
        return

    selected_db = select_database(databases)
    if not selected_db:
        print("未选择数据库，程序退出。")
        return

    read_database_content(client, selected_db["id"])

    print("\n程序执行完毕。")

if __name__ == "__main__":
    main()
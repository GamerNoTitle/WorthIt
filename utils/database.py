import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from notion_client import Client
from notion_client.errors import APIResponseError

class NotionItemTrackerClient:
    """
    一个用于与 Notion '记物' 数据库交互的客户端。
    封装了初始化、数据库发现以及物品的增删查改 (CRUD) 功能。
    """
    def __init__(self, notion_token: str):
        """
        初始化 Notion 客户端。
        :param notion_token: Notion API 集成令牌。
        :raises ValueError: 如果 notion_token 为空。
        :raises notion_client.errors.APIResponseError: 如果 Notion API 令牌无效或发生其他 API 错误。
        :raises Exception: 其他未知错误。
        """
        if not notion_token:
            raise ValueError(
                "Notion API 令牌不能为空。请从 https://www.notion.so/my-integrations 获取并设置。"
            )
        try:
            self.client = Client(auth=notion_token)
            # 尝试做一次小查询来验证令牌的有效性
            # self.client.users.list() # 这是一个轻量级的验证方法
            print("NotionItemTrackerClient: Notion 客户端初始化成功。")
        except APIResponseError as e:
            raise APIResponseError(
                f"初始化 Notion 客户端时发生 API 错误: {e}. 请检查您的 Notion 令牌是否正确且有效。"
            ) from e
        except Exception as e:
            raise Exception(f"初始化 Notion 客户端时发生未知错误: {e}") from e

    def _get_property_value(self, property_data: Dict[str, Any]) -> Any:
        """
        根据 Notion 属性类型提取并格式化其值。
        Notion API 返回的属性值结构复杂，需要根据类型解析。
        """
        prop_type = property_data.get("type")

        if prop_type == "string":
            return property_data["string"]
        elif prop_type == "title":
            return "".join([rt.get("plain_text", "") for rt in property_data["title"]])
        elif prop_type == "rich_text":
            return "".join([rt.get("plain_text", "") for rt in property_data["rich_text"]])
        elif prop_type == "number":
            return property_data["number"]
        elif prop_type == "checkbox":
            return property_data["checkbox"] # 返回 True/False
        elif prop_type == "select":
            return property_data["select"].get("name") if property_data["select"] else None
        elif prop_type == "multi_select":
            return [s.get("name") for s in property_data["multi_select"]]
        elif prop_type == "date":
            date_obj = property_data["date"]
            if date_obj:
                start = date_obj.get("start")
                end = date_obj.get("end")
                if start and end:
                    return {"start": start, "end": end}
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
            return [f.get("name") for f in property_data["files"]]
        elif prop_type == "relation":
            return [r.get("id") for r in property_data["relation"]]
        elif prop_type == "people":
            return [p.get("name") for p in property_data["people"]]
        elif prop_type == "formula":
            formula_result = property_data["formula"]
            formula_type = formula_result.get("type")
            if formula_type and formula_result.get(formula_type) is not None:
                 return self._get_property_value({formula_type: formula_result.get(formula_type), "type": formula_type})
            return None
        elif prop_type == "rollup":
            rollup_result = property_data["rollup"]
            if rollup_result.get("type") == "array":
                processed_items = []
                for item in rollup_result.get("array"):
                    if isinstance(item, dict) and "type" in item:
                        processed_items.append(self._get_property_value(item))
                    else:
                        processed_items.append(str(item)) 
                return processed_items
            elif rollup_result.get("type") in ["number", "date", "boolean", "string"]:
                return self._get_property_value({"type": rollup_result["type"], rollup_result["type"]: rollup_result.get(rollup_result["type"])})
            return None # Handle other complex rollup types as None or raise error
        elif prop_type == "created_time":
            return property_data["created_time"]
        elif prop_type == "last_edited_time":
            return property_data["last_edited_time"]
        elif prop_type == "created_by":
            return property_data["created_by"].get("name")
        elif prop_type == "last_edited_by":
            return property_data["last_edited_by"].get("name")
        else:
            return None # 暂时不支持的类型返回 None

    def _format_property_for_notion(self, value: Any, prop_type: str) -> Optional[Dict[str, Any]]:
        """
        根据 Notion 属性类型和值，将其格式化为 Notion API 期望的字典结构。
        用于创建和更新页面。
        对于数字和日期类型，None 表示清空该属性。
        """
        if prop_type == "title":
            if value is None or str(value).strip() == "":
                return None # Title cannot be empty
            return {"title": [{"text": {"content": str(value)}}]}
        elif prop_type == "rich_text":
            if value is None or str(value).strip() == "":
                return {"rich_text": []} # Clear rich text
            return {"rich_text": [{"text": {"content": str(value)}}]}
        elif prop_type == "number":
            if value is None or str(value).strip() == "":
                return {"number": None} # Clear number property
            try:
                return {"number": float(value)}
            except ValueError:
                raise ValueError(f"值 '{value}' 无法转换为数字，无法设置 {prop_type} 属性。")
        elif prop_type == "date":
            if value is None or str(value).strip() == "":
                return {"date": None} # Clear date property
            try:
                # 校验日期格式
                datetime.strptime(str(value), "%Y-%m-%d")
                return {"date": {"start": str(value), "end": None}}
            except ValueError:
                raise ValueError(f"日期 '{value}' 格式不正确，请使用 YYYY-MM-DD 格式。")
        # 添加更多您需要在写入时处理的属性类型
        # 例如：
        # elif prop_type == "checkbox":
        #     return {"checkbox": bool(value)}
        # elif prop_type == "select":
        #     if value is None or str(value).strip() == "":
        #         return {"select": None}
        #     return {"select": {"name": str(value)}}
        else:
            raise ValueError(f"不支持将 '{prop_type}' 类型的属性写入或未实现其格式化逻辑。")

    def get_databases(self) -> List[Dict[str, Any]]:
        """
        列出用户集成有权访问的所有 Notion 数据库。
        :return: 数据库列表，每个元素包含 'id' 和 'title'。
        :raises notion_client.errors.APIResponseError: 搜索数据库时发生 API 错误。
        :raises Exception: 其他未知错误。
        """
        print("NotionItemTrackerClient: 正在搜索数据库...")
        try:
            response = self.client.search(
                filter={"property": "object", "value": "database"}
            )
            databases = response.get("results", [])
            
            result_list = []
            for db in databases:
                title_rich_text = db.get("title", [{"plain_text": "Untitled"}])
                title = "".join([t.get("plain_text", "") for t in title_rich_text])
                result_list.append({"id": db["id"], "title": title})
            
            return result_list
        except APIResponseError as e:
            raise APIResponseError(f"搜索数据库时发生 API 错误: {e}") from e
        except Exception as e:
            raise Exception(f"搜索数据库时发生未知错误: {e}") from e

    def read_items(self, database_id: str, include_formula_and_rollup: bool = False) -> List[Dict[str, Any]]:
        """
        读取指定数据库中的所有页面内容。
        :param database_id: 要读取的 Notion 数据库ID。
        :param include_formula_and_rollup: 是否包含公式和 Rollup 等只读属性。
        :return: 物品（页面）列表，每个物品是一个字典，包含其属性名和对应的Python值。
        :raises notion_client.errors.APIResponseError: 读取数据库时发生 API 错误。
        :raises Exception: 其他未知错误。
        """
        print(f"NotionItemTrackerClient: 正在读取数据库内容 (ID: {database_id})...")
        try:
            response = self.client.databases.query(database_id=database_id)
            pages = response.get("results", [])

            processed_items = []
            for page in pages:
                item_data = {"id": page["id"], "archived": page["archived"], "properties": {}}
                
                for prop_name, prop_data in page.get("properties", {}).items():
                    # 跳过公式和Rollup属性，除非显式要求显示
                    if not include_formula_and_rollup and prop_data.get("type") in ["formula", "rollup", "created_time", "last_edited_time", "created_by", "last_edited_by"]:
                        continue

                    value = self._get_property_value(prop_data)
                    # 过滤掉 None 值，除非你希望在返回数据中明确显示它们
                    if value is not None:
                        item_data["properties"][prop_name] = value
                processed_items.append(item_data)
            return processed_items

        except APIResponseError as e:
            raise APIResponseError(f"读取数据库内容时发生 API 错误: {e}") from e
        except Exception as e:
            raise Exception(f"读取数据库内容时发生未知错误: {e}") from e

    def add_item(self, database_id: str, item_name: str, entry_date: str, purchase_price: float, additional_value: Optional[float] = None, retirement_date: Optional[str] = None) -> Dict[str, Any]:
        """
        向指定的 Notion 数据库添加一个新的物品条目。
        :param database_id: 目标数据库ID。
        :param item_name: 物品名称。
        :param entry_date: 入役日期 (YYYY-MM-DD)。
        :param purchase_price: 购买价格。
        :param additional_value: 附加价值 (可选)。
        :param retirement_date: 退役日期 (可选，YYYY-MM-DD)。
        :return: Notion API 返回的创建页面的原始响应数据。
        :raises ValueError: 如果输入数据格式不正确。
        :raises notion_client.errors.APIResponseError: 添加物品时发生 API 错误。
        :raises Exception: 其他未知错误。
        """
        print(f"NotionItemTrackerClient: 正在添加物品 '{item_name}' 到数据库 (ID: {database_id})...")
        
        properties = {
            "物品名称": self._format_property_for_notion(item_name, "title"),
            "入役日期": self._format_property_for_notion(entry_date, "date"),
            "购买价格": self._format_property_for_notion(purchase_price, "number"),
        }
        
        if additional_value is not None:
            properties["附加价值"] = self._format_property_for_notion(additional_value, "number")
        
        if retirement_date:
            properties["退役日期"] = self._format_property_for_notion(retirement_date, "date")
        # 如果 retirement_date 为 None，则不传递该属性，让 Notion 公式自行处理

        try:
            response = self.client.pages.create(
                parent={"database_id": database_id},
                properties=properties
            )
            return response
        except APIResponseError as e:
            raise APIResponseError(f"添加物品时发生 API 错误: {e}") from e
        except Exception as e:
            raise Exception(f"添加物品时发生未知错误: {e}") from e

    def update_item(self, page_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        修改指定 Notion 页面（物品条目）的属性。
        :param page_id: 要修改的物品的页面ID。
        :param updates: 包含要更新的属性名和新值的字典，例如:
                        {"物品名称": "新笔记本", "购买价格": 1200.0, "退役日期": "2024-03-15"}
                        若要清空数字或日期属性，请传入 None，例如 {"附加价值": None, "退役日期": None}
        :return: Notion API 返回的更新页面的原始响应数据。
        :raises ValueError: 如果输入数据格式不正确或属性名无效。
        :raises notion_client.errors.APIResponseError: 修改物品时发生 API 错误。
        :raises Exception: 其他未知错误。
        """
        print(f"NotionItemTrackerClient: 正在更新物品 (ID: {page_id})...")
        
        properties_to_update = {}
        for prop_name, new_value in updates.items():
            # 这里需要一个映射来确定属性的 Notion 类型
            # 实际项目中，你可以先查询数据库的 schema 来获取这些类型
            # 为简化示例，我们手动映射常用字段的类型
            if prop_name == "物品名称":
                prop_type = "title"
            elif prop_name == "入役日期" or prop_name == "退役日期":
                prop_type = "date"
            elif prop_name == "购买价格" or prop_name == "附加价值":
                prop_type = "number"
            elif prop_name == "备注" or prop_name == "描述": # 示例，如果你的数据库有这些字段
                prop_type = "rich_text"
            else:
                raise ValueError(f"属性 '{prop_name}' 不支持更新或未映射其 Notion 类型。")

            formatted_value = self._format_property_for_notion(new_value, prop_type)
            if formatted_value is not None:
                properties_to_update[prop_name] = formatted_value
            elif formatted_value is None and prop_type == "title":
                 raise ValueError("物品名称不能为空。") # 标题不能清空

        if not properties_to_update:
            raise ValueError("没有有效的属性被提供以进行更新。")

        try:
            response = self.client.pages.update(
                page_id=page_id,
                properties=properties_to_update
            )
            return response
        except APIResponseError as e:
            raise APIResponseError(f"修改物品时发生 API 错误: {e}") from e
        except Exception as e:
            raise Exception(f"修改物品时发生未知错误: {e}") from e

    def delete_item(self, page_id: str) -> Dict[str, Any]:
        """
        删除（归档）指定 Notion 页面（物品条目）。
        Notion API 中的“删除”是归档，而不是永久删除。
        :param page_id: 要删除的物品的页面ID。
        :return: Notion API 返回的归档页面的原始响应数据。
        :raises notion_client.errors.APIResponseError: 删除物品时发生 API 错误。
        :raises Exception: 其他未知错误。
        """
        print(f"NotionItemTrackerClient: 正在归档物品 (ID: {page_id})...")
        try:
            response = self.client.pages.update(
                page_id=page_id,
                archived=True
            )
            return response
        except APIResponseError as e:
            raise APIResponseError(f"删除物品时发生 API 错误: {e}") from e
        except Exception as e:
            raise Exception(f"删除物品时发生未知错误: {e}") from e

# --- 示例 Flask 应用中如何调用此客户端 ---
# 以下代码仅为演示如何在 Flask (或其他程序) 中使用 NotionItemTrackerClient
# 实际的 Flask 应用会有路由、HTML 模板等。

if __name__ == "__main__":
    NOTION_TOKEN = "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"

    if not NOTION_TOKEN:
        print("错误: 请将您的 Notion 集成令牌设置为环境变量 'NOTION_TOKEN'。")
        print("您可以在这里创建和获取令牌: https://www.notion.so/my-integrations")
        print("示例 (在 Bash/Zsh 中): export NOTION_TOKEN='secret_YOUR_TOKEN_HERE'")
        exit(1)

    try:
        # 1. 实例化客户端
        tracker_client = NotionItemTrackerClient(NOTION_TOKEN)

        # 2. 获取所有可用数据库，让用户选择
        all_databases = tracker_client.get_databases()
        if not all_databases:
            print("未找到任何可用数据库。请确保您的集成已获得数据库访问权限。")
            exit(0)

        print("\n--- 可用的 Notion 数据库 ---")
        for i, db in enumerate(all_databases):
            print(f"{i+1}. {db['title']} (ID: {db['id']})")
        
        selected_db_index = -1
        while True:
            try:
                choice = int(input(f"请输入您想操作的数据库的序号 (1-{len(all_databases)}): "))
                if 1 <= choice <= len(all_databases):
                    selected_db_index = choice - 1
                    break
                else:
                    print("无效的选择。请输入列表中的数字。")
            except ValueError:
                print("无效的输入。请输入一个数字。")
        
        selected_database_id = all_databases[selected_db_index]['id']
        selected_database_title = all_databases[selected_db_index]['title']
        print(f"\n已选择数据库: {selected_database_title} (ID: {selected_database_id})")

        while True:
            print("\n--- 请选择操作 ---")
            print("1. 查看所有物品 (Read)")
            print("2. 添加新物品 (Create)")
            print("3. 修改现有物品 (Update)")
            print("4. 删除物品 (Delete/Archive)")
            print("5. 退出程序")

            operation_choice = input("请输入您的选择 (1-5): ").strip()

            if operation_choice == '1':
                print("\n--- 查看所有物品 ---")
                items = tracker_client.read_items(selected_database_id, include_formula_and_rollup=True)
                with open('items.txt', 'w', encoding='utf-8') as f:
                    f.write(json.dumps(items))
                if items:
                    for i, item in enumerate(items):
                        print(f"\n--- 物品 {i+1} (ID: {item['id']}) ---")
                        for prop_name, prop_value in item['properties'].items():
                            print(f"  {prop_name}: {prop_value}")
                else:
                    print("该数据库中没有物品。")

            elif operation_choice == '2':
                print("\n--- 添加新物品 ---")
                item_name = input("请输入物品名称: ").strip()
                if not item_name:
                    print("物品名称不能为空，操作取消。")
                    continue
                
                entry_date = input("请输入入役日期 (YYYY-MM-DD): ").strip()
                try:
                    datetime.strptime(entry_date, "%Y-%m-%d")
                except ValueError:
                    print("入役日期格式不正确，操作取消。")
                    continue

                try:
                    purchase_price = float(input("请输入购买价格: ").strip())
                except ValueError:
                    print("购买价格必须是数字，操作取消。")
                    continue
                
                additional_value_input = input("请输入附加价值 (可选，无则回车): ").strip()
                additional_value = float(additional_value_input) if additional_value_input else None

                retirement_date_input = input("请输入退役日期 (可选，YYYY-MM-DD，无则回车): ").strip()
                retirement_date = retirement_date_input if retirement_date_input else None
                if retirement_date:
                    try:
                        datetime.strptime(retirement_date, "%Y-%m-%d")
                    except ValueError:
                        print("退役日期格式不正确，将忽略退役日期。")
                        retirement_date = None

                try:
                    new_item_response = tracker_client.add_item(
                        selected_database_id,
                        item_name,
                        entry_date,
                        purchase_price,
                        additional_value,
                        retirement_date
                    )
                    print(f"物品 '{item_name}' 添加成功！新页面ID: {new_item_response['id']}")
                    # print("原始响应数据:", new_item_response) # 可用于调试
                except Exception as e:
                    print(f"添加物品失败: {e}")

            elif operation_choice == '3':
                print("\n--- 修改现有物品 ---")
                # 先显示所有物品，方便用户选择ID
                items_for_update = tracker_client.read_items(selected_database_id)
                if not items_for_update:
                    print("数据库中没有物品可供修改。")
                    continue
                
                print("\n现有物品列表:")
                for item in items_for_update:
                    # 尝试从properties中获取物品名称，默认为"Untitled"
                    item_name_display = item['properties'].get('物品名称', 'Untitled')
                    print(f"  ID: {item['id']} | 名称: {item_name_display}")

                page_id = input("请输入要修改的物品的页面ID: ").strip()
                if not page_id:
                    print("页面ID不能为空，操作取消。")
                    continue

                updates = {}
                print("您可以修改以下属性: 物品名称, 入役日期, 购买价格, 附加价值, 退役日期")
                print("若要清空数字/日期属性，请输入 'NONE'")

                while True:
                    prop_name = input("请输入要修改的属性名称 (或输入 '完成' 结束修改): ").strip()
                    if prop_name == "完成":
                        break
                    if prop_name not in ["物品名称", "入役日期", "购买价格", "附加价值", "退役日期"]:
                        print("不支持的属性名称，请检查拼写。")
                        continue
                    
                    new_value_input = input(f"请输入 '{prop_name}' 的新值: ").strip()
                    new_value = None if new_value_input.upper() == "NONE" else new_value_input

                    # 根据属性名进行类型转换
                    if prop_name == "购买价格" or prop_name == "附加价值":
                        try:
                            updates[prop_name] = float(new_value) if new_value is not None else None
                        except ValueError:
                            print("值必须是数字。")
                            continue
                    elif prop_name in ["入役日期", "退役日期"]:
                        if new_value is not None:
                            try:
                                datetime.strptime(new_value, "%Y-%m-%d")
                                updates[prop_name] = new_value
                            except ValueError:
                                print("日期格式不正确。请使用 YYYY-MM-DD。")
                                continue
                        else:
                            updates[prop_name] = None
                    else: # 物品名称
                        updates[prop_name] = new_value

                if not updates:
                    print("未输入任何要修改的属性，操作取消。")
                    continue

                try:
                    updated_item_response = tracker_client.update_item(page_id, updates)
                    print(f"物品 '{page_id}' 修改成功！")
                    # print("原始响应数据:", updated_item_response) # 可用于调试
                except Exception as e:
                    print(f"修改物品失败: {e}")

            elif operation_choice == '4':
                print("\n--- 删除物品 ---")
                # 先显示所有物品，方便用户选择ID
                items_for_delete = tracker_client.read_items(selected_database_id)
                if not items_for_delete:
                    print("数据库中没有物品可供删除。")
                    continue
                
                print("\n现有物品列表:")
                for item in items_for_delete:
                    item_name_display = item['properties'].get('物品名称', 'Untitled')
                    print(f"  ID: {item['id']} | 名称: {item_name_display}")

                page_id_to_delete = input("请输入要删除的物品的页面ID: ").strip()
                if not page_id_to_delete:
                    print("页面ID不能为空，操作取消。")
                    continue
                
                confirm = input(f"确定要删除 (归档) 页面ID为 '{page_id_to_delete}' 的物品吗？(y/N): ").strip().lower()
                if confirm != 'y':
                    print("操作取消。")
                    continue

                try:
                    deleted_item_response = tracker_client.delete_item(page_id_to_delete)
                    print(f"物品 '{page_id_to_delete}' 已成功归档 (删除)。")
                    # print("原始响应数据:", deleted_item_response) # 可用于调试
                except Exception as e:
                    print(f"删除物品失败: {e}")

            elif operation_choice == '5':
                print("退出程序。")
                break
            else:
                print("无效的选择，请重新输入。")

    except ValueError as ve:
        print(f"配置错误: {ve}")
    except APIResponseError as api_e:
        print(f"Notion API 错误: {api_e}")
    except Exception as general_e:
        print(f"发生未预期错误: {general_e}")
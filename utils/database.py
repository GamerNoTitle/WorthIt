import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import re  # 导入 re 模块
import warnings

from notion_client import Client
from notion_client.errors import APIResponseError
from utils.models import *


class NotionItemTrackerClient:
    """
    一个用于与 Notion '记物' 数据库交互的客户端。
    封装了初始化、数据库发现以及物品的增删查改 (CRUD) 功能。
    """

    def __init__(self, notion_token: str, raw_database_id_input: str):
        """
        初始化 Notion 客户端。
        :param notion_token: Notion API 集成令牌。
        :param raw_database_id_input: 用户传入的 Notion 数据库 ID，可以带或不带连字符。
        :raises ValueError: 如果 notion_token 或 raw_database_id_input 为空，或指定的数据库 ID 未找到。
        :raises notion_client.errors.APIResponseError: 如果 Notion API 令牌无效或发生其他 API 错误。
        :raises Exception: 其他未知错误。
        """
        if not notion_token:
            raise ValueError(
                "Notion API 令牌不能为空。请从 https://www.notion.so/my-integrations 获取并设置。"
            )
        if not raw_database_id_input:
            raise ValueError("Notion 数据库 ID 不能为空。请确保您已正确设置数据库 ID。")

        self.client = Client(auth=notion_token)
        print("NotionItemTrackerClient: Notion 客户端初始化成功。")

        # 尝试解析并存储正确的、带连字符的数据库 ID
        self.database_id: Optional[str] = None
        try:
            all_databases = self.get_databases()  # 使用 self 来调用类内方法

            found_db_title = "未知"
            # 移除用户输入 ID 中的所有连字符，方便比较
            normalized_user_id = raw_database_id_input.replace("-", "")

            for i, db in enumerate(all_databases):
                # 移除 Notion API 返回的 ID 中的所有连字符
                normalized_notion_id = db["id"].replace("-", "")

                if normalized_notion_id == normalized_user_id:
                    self.database_id = db[
                        "id"
                    ]  # 存储 Notion API 返回的原始 ID (带连字符)
                    found_db_title = db["title"]
                    break

            if self.database_id:
                print(
                    f"NotionItemTrackerClient: 指定的数据库 ID '{raw_database_id_input}' 已成功匹配到数据库 '{found_db_title}' (ID: {self.database_id})。"
                )
            else:
                raise ValueError(
                    f"指定的数据库 ID '{raw_database_id_input}' 未找到或不在您的 Notion 集成权限范围内。"
                )
        except APIResponseError as e:
            raise APIResponseError(
                f"初始化 Notion 客户端时发生 API 错误: {e}. 请检查您的 Notion 令牌是否正确且有效。"
            ) from e
        except Exception as e:
            raise Exception(f"初始化 Notion 客户端时发生未知错误: {e}") from e
        print(
            f"NotionItemTrackerClient: 客户端已初始化，实际使用的数据库 ID: {self.database_id}"
        )

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
            return "".join(
                [rt.get("plain_text", "") for rt in property_data["rich_text"]]
            )
        elif prop_type == "number":
            return property_data["number"]
        elif prop_type == "checkbox":
            return property_data["checkbox"]  # 返回 True/False
        elif prop_type == "select":
            return (
                property_data["select"].get("name") if property_data["select"] else None
            )
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
                # 递归调用以处理公式结果
                return self._get_property_value(
                    {
                        formula_type: formula_result.get(formula_type),
                        "type": formula_type,
                    }
                )
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
                # 递归调用以处理 rollup 的单个结果
                return self._get_property_value(
                    {
                        "type": rollup_result["type"],
                        rollup_result["type"]: rollup_result.get(rollup_result["type"]),
                    }
                )
            return None  # Handle other complex rollup types as None or raise error
        elif prop_type == "created_time":
            return property_data["created_time"]
        elif prop_type == "last_edited_time":
            return property_data["last_edited_time"]
        elif prop_type == "created_by":
            return property_data["created_by"].get("name")
        elif prop_type == "last_edited_by":
            return property_data["last_edited_by"].get("name")
        else:
            return None  # 暂时不支持的类型返回 None

    def _format_property_for_notion(
        self, value: Any, prop_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        根据 Notion 属性类型和值，将其格式化为 Notion API 期望的字典结构。
        用于创建和更新页面。
        对于数字和日期类型，None 表示清空该属性。
        """
        if prop_type == "title":
            if value is None or str(value).strip() == "":
                return None  # Title cannot be empty
            return {"title": [{"text": {"content": str(value)}}]}
        elif prop_type == "rich_text":
            if value is None or str(value).strip() == "":
                return {"rich_text": []}  # Clear rich text
            return {"rich_text": [{"text": {"content": str(value)}}]}
        elif prop_type == "number":
            if value is None or str(value).strip() == "":
                return {"number": None}  # Clear number property
            try:
                return {"number": float(value)}
            except ValueError:
                raise ValueError(
                    f"值 '{value}' 无法转换为数字，无法设置 {prop_type} 属性。"
                )
        elif prop_type == "date":
            if value is None or str(value).strip() == "":
                return {"date": None}  # Clear date property
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
            raise ValueError(
                f"不支持将 '{prop_type}' 类型的属性写入或未实现其格式化逻辑。"
            )

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

    def read_items(
        self, include_formula_and_rollup: bool = False
    ) -> List[Dict[str, Any]]:
        """
        读取指定数据库中的所有页面内容。
        :param include_formula_and_rollup: 是否包含公式和 Rollup 等只读属性。
        :return: 物品（页面）列表，每个物品是一个字典，包含其属性名和对应的Python值。
        :raises RuntimeError: 如果数据库 ID 未设置。
        :raises notion_client.errors.APIResponseError: 读取数据库时发生 API 错误。
        :raises Exception: 其他未知错误。
        """
        if not self.database_id:
            raise RuntimeError("Notion 数据库 ID 未在客户端初始化时正确设置。")

        print(
            f"NotionItemTrackerClient: 正在读取数据库内容 (ID: {self.database_id})..."
        )
        try:
            response = self.client.databases.query(database_id=self.database_id)
            pages = response.get("results", [])

            processed_items = []
            for page in pages:
                item_data = {
                    "id": page["id"],
                    "archived": page["archived"],
                    "properties": {},
                }

                for prop_name, prop_data in page.get("properties", {}).items():
                    # 跳过公式和Rollup属性，除非显式要求显示
                    if not include_formula_and_rollup and prop_data.get("type") in [
                        "formula",
                        "rollup",
                        "created_time",
                        "last_edited_time",
                        "created_by",
                        "last_edited_by",
                    ]:
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

    def add_item(
        self,
        item_name: str,
        entry_date: str,
        purchase_price: float,
        additional_value: Optional[float] = None,
        retirement_date: Optional[str] = None,
        remark: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        向指定的 Notion 数据库添加一个新的物品条目。
        :param item_name: 物品名称。
        :param entry_date: 入役日期 (YYYY-MM-DD)。
        :param purchase_price: 购买价格。
        :param additional_value: 附加价值 (可选)。
        :param retirement_date: 退役日期 (可选，YYYY-MM-DD)。
        :return: Notion API 返回的创建页面的原始响应数据。
        :raises RuntimeError: 如果数据库 ID 未设置。
        :raises ValueError: 如果输入数据格式不正确。
        :raises notion_client.errors.APIResponseError: 添加物品时发生 API 错误。
        :raises Exception: 其他未知错误。
        """
        if not self.database_id:
            raise RuntimeError("Notion 数据库 ID 未在客户端初始化时正确设置。")

        print(
            f"NotionItemTrackerClient: 正在添加物品 '{item_name}' 到数据库 (ID: {self.database_id})..."
        )

        properties = {
            "物品名称": self._format_property_for_notion(item_name, "title"),
            "入役日期": self._format_property_for_notion(entry_date, "date"),
            "购买价格": self._format_property_for_notion(purchase_price, "number"),
        }

        if additional_value is not None:
            properties["附加价值"] = self._format_property_for_notion(
                additional_value, "number"
            )

        if retirement_date:  # 只有当 retirement_date 非空字符串时才设置
            properties["退役日期"] = self._format_property_for_notion(
                retirement_date, "date"
            )

        if remark is not None:
            properties["备注"] = self._format_property_for_notion(remark, "rich_text")

        try:
            response = self.client.pages.create(
                parent={"database_id": self.database_id}, properties=properties
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
            elif prop_name == "备注":
                prop_type = "rich_text"
            else:
                raise ValueError(
                    f"属性 '{prop_name}' 不支持更新或未映射其 Notion 类型。"
                )

            formatted_value = self._format_property_for_notion(new_value, prop_type)
            if formatted_value is not None:
                properties_to_update[prop_name] = formatted_value
            elif formatted_value is None and prop_type == "title":
                raise ValueError("物品名称不能为空。")  # 标题不能清空

        if not properties_to_update:
            raise ValueError("没有有效的属性被提供以进行更新。")

        try:
            response = self.client.pages.update(
                page_id=page_id, properties=properties_to_update
            )
            return response
        except APIResponseError as e:
            raise APIResponseError(f"修改物品时发生 API 错误: {e}") from e
        except Exception as e:
            raise Exception(f"修改物品时发生未知错误: {e}") from e

    def delete_item(self, page_id: str) -> Dict[str, Any]:
        """
        删除（归档）指定 Notion 页面（物品条目）。
        Notion API 中的 “删除” 是归档，而不是永久删除。
        :param page_id: 要删除的物品的页面ID。
        :return: Notion API 返回的归档页面的原始响应数据。
        :raises notion_client.errors.APIResponseError: 删除物品时发生 API 错误。
        :raises Exception: 其他未知错误。
        """
        print(f"NotionItemTrackerClient: 正在归档物品 (ID: {page_id})...")
        try:
            response = self.client.pages.update(page_id=page_id, archived=True)
            return response
        except Exception as e:
            raise Exception(f"删除物品时发生未知错误: {e}") from e


# 示例使用
if __name__ == "__main__":
    NOTION_API_TOKEN = (
        ""
    )
    # 假设用户传入的是不带连字符的ID
    USER_PROVIDED_DB_ID = ""

    try:
        # 实例化客户端，传入用户可能不带连字符的ID
        tracker_client = NotionItemTrackerClient(NOTION_API_TOKEN, USER_PROVIDED_DB_ID)

        # 客户端初始化后，会自动将正确的带连字符的数据库ID存储在 self.database_id 中
        print(f"\n客户端已初始化，实际使用的数据库 ID: {tracker_client.database_id}")

        # 现在可以调用不带 database_id 参数的方法
        all_items_raw = tracker_client.read_items()
        print(
            f"\n从数据库 '{tracker_client.database_id}' 读取到 {len(all_items_raw)} 条原始物品数据。"
        )

        # 可以用 Pydantic 模型来验证和解析这些原始数据
        from models import Item  # 导入 Pydantic 模型

        parsed_items = []
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            for item_data in all_items_raw:
                try:
                    item = Item.model_validate(item_data)
                    parsed_items.append(item)
                except Exception as e:
                    print(f"Pydantic 验证失败：{e} for item {item_data.get('id')}")

            if w:
                print("\n--- Pydantic 解析过程中捕获到以下警告 ---")
                for warning_message in w:
                    print(f"Warning: {warning_message.message}")

        if parsed_items:
            print("\n--- 使用 Pydantic 模型解析后的数据示例 (第一条) ---")
            first_item = parsed_items[0]
            print(f"物品名称: {first_item.properties.item_name}")
            print(f"购买价格: {first_item.properties.purchase_price}")
            print(f"入役日期: {first_item.properties.service_start_date}")
            print(f"退役日期: {first_item.properties.service_end_date}")
            print(f"日均价格: {first_item.properties.daily_price}")
            print(f"服役天数: {first_item.properties.service_days}")
            print(f"附加价值: {first_item.properties.additional_value}")
            print(f"备注: {first_item.properties.note}")
            print(f"ID: {first_item.id}")
            print(f"Archived: {first_item.archived}")
        else:
            print("\n没有物品被成功解析。")

    except (ValueError, APIResponseError, Exception) as e:
        print(f"程序运行出错: {e}")

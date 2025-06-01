import re
import warnings
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator


# 定义 Pydantic 模型
# 这是一个嵌套模型，用于解析 'properties' 字典内的字段
class ItemProperties(BaseModel):
    """
    物品的属性模型，对应 Notion 数据库中的 'properties' 字段。
    """

    item_name: str = Field(alias="物品名称", description="物品的名称，必须填写")
    purchase_price: float = Field(
        alias="购买价格", description="物品的购买价格，必须填写"
    )

    service_start_date: Optional[date] = Field(
        default=None, alias="入役日期", description="物品开始服役的日期"
    )
    service_end_date: date = Field(
        default_factory=date.today,
        alias="退役日期",
        description="物品退役的日期，默认为今天",
    )

    daily_price: Optional[float] = Field(
        default=None, alias="日均价格", description="物品的日均价格，格式为 'X 元'"
    )
    service_days: Optional[int] = Field(
        default=None, alias="服役天数", description="物品的服役天数，格式为 'X 天'"
    )
    note: Optional[str] = Field(default=None, alias="备注", description="备注信息")
    additional_value: Optional[float] = Field(
        default=None,
        alias="附加价值",
        description="额外增加的价值或维修费用，应为纯数字",
    )

    @field_validator("service_start_date", mode="before")
    @classmethod
    def warn_if_service_start_date_missing(cls, v):
        """
        在解析 '入役日期' 之前进行处理。
        如果输入为 None 或空字符串，则发出警告并返回 None。
        """
        if v is None or v == "":
            warnings.warn(
                "入役日期 (service_start_date) 未填写，此字段为空。", UserWarning
            )
            return None
        return v

    @field_validator("service_end_date", mode="before")
    @classmethod
    def set_default_service_end_date(cls, v):
        """
        在解析 '退役日期' 之前进行处理。
        如果输入为 None 或空字符串，则返回当前的日期。
        """
        if v is None or v == "":
            return date.today()
        return v

    @field_validator("daily_price", mode="before")
    @classmethod
    def parse_daily_price_string(cls, v):
        """
        解析 '日均价格' 字符串，提取数值部分。
        例如 "1.88 元" -> 1.88
        """
        if v is None or v == "":
            return None
        if isinstance(v, (int, float)):  # 如果已经是数值类型，直接返回
            return float(v)
        if isinstance(v, str):
            match = re.search(r"(\d+(\.\d+)?)\s*元", v)
            if match:
                return float(match.group(1))
        warnings.warn(
            f"无法解析日均价格 '{v}'，预期格式如 'X 元'，设为 None。", UserWarning
        )
        return None

    @field_validator("service_days", mode="before")
    @classmethod
    def parse_service_days_string(cls, v):
        """
        解析 '服役天数' 字符串，提取数值部分。
        例如 "1331 天" -> 1331
        """
        if v is None or v == "":
            return None
        if isinstance(v, int):  # 如果已经是整数类型，直接返回
            return v
        if isinstance(v, str):
            match = re.search(r"(\d+)\s*天", v)
            if match:
                return int(match.group(1))
        warnings.warn(
            f"无法解析服役天数 '{v}'，预期格式如 'X 天'，设为 None。", UserWarning
        )
        return None

    @field_validator("additional_value", mode="before")
    @classmethod
    def parse_additional_value(cls, v):
        """
        处理 '附加价值'。根据用户说明，这应该是一个纯数字。
        如果为 None 或空字符串，则返回 None。
        否则，尝试将其转换为浮点数。
        """
        if v is None or v == "":
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            # 这种情况通常不应该发生，因为用户说它会是一个数字。
            # 如果发生，意味着数据源的 '附加价值' 字段格式不符合预期。
            warnings.warn(
                f"无法解析附加价值 '{v}' 为数字，此字段设为 None。请检查数据源中 '附加价值' 字段的格式。",
                UserWarning,
            )
            return None


# 顶级模型，对应每个 JSON 条目
class Item(BaseModel):
    """
    单个物品的顶级模型，对应 Notion 数据库中的一个条目。
    """

    id: UUID = Field(description="物品的唯一标识符")
    archived: bool = Field(description="物品是否已归档")
    properties: ItemProperties = Field(description="物品的属性详情")


# --- 测试和使用 ---
if __name__ == "__main__":
    # 示例数据（保持不变，因为它在 '附加价值' 字段中本身就是数字）
    json_data = [
        {
            "id": "2046dedb-b716-8148-8942-efb45cca9a33",
            "archived": False,
            "properties": {
                "日均价格": "1.88 元",
                "备注": "",
                "退役日期": "2025-01-31",
                "服役天数": "1331 天",
                "入役日期": "2021-06-10",
                "购买价格": 2499,
                "物品名称": "红米 K40",
            },
        },
        {
            "id": "2046dedb-b716-816b-9b27-fa0c483c9049",
            "archived": False,
            "properties": {
                "日均价格": "1.05 元",
                "备注": "",
                "服役天数": "74 天",
                "入役日期": "2025-03-18",
                "购买价格": 78,
                "物品名称": "小米触屏音响 LX04",
            },
        },
        {
            "id": "2046dedb-b716-8194-b89c-e8bbd6340257",
            "archived": False,
            "properties": {
                "日均价格": "3.03 元",
                "备注": "",
                "服役天数": "264 天",
                "入役日期": "2024-09-09",
                "购买价格": 798.95,
                "物品名称": "AOC 24G4 显示器",
            },
        },
        {
            "id": "2046dedb-b716-81a2-819c-c797beeb55c0",
            "archived": False,
            "properties": {
                "附加价值": 3732,
                "日均价格": "10.03 元",
                "备注": "维修花费 3732 元",
                "服役天数": "1369 天",
                "入役日期": "2021-08-31",
                "购买价格": 9999,
                "物品名称": "DELL 游匣 G15",
            },
        },
        {
            "id": "2046dedb-b716-81c4-9d31-c6f44490c7e1",
            "archived": False,
            "properties": {
                "附加价值": 300,
                "日均价格": "3.14 元",
                "备注": "换电池及维修花费 300 元",
                "服役天数": "986 天",
                "入役日期": "2022-09-18",
                "购买价格": 2800,
                "物品名称": "Microsoft Surface 5",
            },
        },
        {
            "id": "2046dedb-b716-81db-937c-c6f44c2804ce",
            "archived": False,
            "properties": {
                "日均价格": "0.88 元",
                "备注": "",
                "退役日期": "2025-05-29",
                "服役天数": "910 天",
                "入役日期": "2022-12-01",
                "购买价格": 800,
                "物品名称": "OPPO Watch 2 46mm",
            },
        },
        {
            "id": "2046dedb-b716-8123-a908-cc3243ae26cc",
            "archived": False,
            "properties": {
                "日均价格": "3.43 元",
                "备注": "",
                "服役天数": "46 天",
                "入役日期": "2025-04-15",
                "购买价格": 158,
                "物品名称": "小米屏幕挂灯 1S",
            },
        },
        {
            "id": "2046dedb-b716-814b-919f-dc50cd023e2e",
            "archived": False,
            "properties": {
                "日均价格": "0.18 元",
                "备注": "",
                "服役天数": "870 天",
                "入役日期": "2023-01-12",
                "购买价格": 160,
                "物品名称": "水月雨 Nekocake 黑猫饼",
            },
        },
        {
            "id": "2046dedb-b716-8181-8674-efdd6731d103",
            "archived": False,
            "properties": {
                "日均价格": "25.83 元",
                "备注": "",
                "服役天数": "120 天",
                "入役日期": "2025-01-31",
                "购买价格": 3099,
                "物品名称": "一加 ACE5",
            },
        },
        {
            "id": "2046dedb-b716-81c7-8242-de3f4c89e45c",
            "archived": False,
            "properties": {
                "日均价格": "529 元",
                "备注": "比赛奖品",
                "服役天数": "2 天",
                "入役日期": "2025-05-29",
                "购买价格": 1058,
                "物品名称": "华为 GT4 41mm",
            },
        },
    ]

    parsed_items: List[Item] = []
    print("开始解析数据...")

    # 为了捕获警告，暂时设置警告过滤器
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")  # 确保所有警告都被捕获

        for i, item_data in enumerate(json_data):
            try:
                # 使用 model_validate 来从字典创建模型实例
                item = Item.model_validate(item_data)
                parsed_items.append(item)
                # print(f"成功解析第 {i+1} 条：{item.properties.item_name}")
            except ValidationError as e:
                print(f"解析第 {i+1} 条数据时发生验证错误: {e}")
            except Exception as e:
                print(f"解析第 {i+1} 条数据时发生未知错误: {e}")

        # 打印所有捕获到的警告
        if w:
            print("\n--- 解析过程中捕获到以下警告 ---")
            for warning_message in w:
                print(f"Warning: {warning_message.message}")
        else:
            print("\n--- 未捕获到任何警告 ---")

    print("\n--- 解析结果示例 (前三条数据) ---")
    for i, item in enumerate(parsed_items[:3]):
        print(f"\n物品 {i+1}: {item.properties.item_name}")
        print(f"  ID: {item.id}")
        print(f"  已归档: {item.archived}")
        print(f"  购买价格: {item.properties.purchase_price} 元")
        print(f"  入役日期: {item.properties.service_start_date}")
        print(f"  退役日期: {item.properties.service_end_date} (若为空白则为当前日期)")
        print(f"  日均价格: {item.properties.daily_price} 元")
        print(f"  服役天数: {item.properties.service_days} 天")
        print(f"  备注: {item.properties.note if item.properties.note else '无'}")
        print(
            f"  附加价值: {item.properties.additional_value if item.properties.additional_value else '无'}"
        )

    # 验证特定条目，例如“小米触屏音响 LX04”的退役日期是否为今天
    xiaomi_speaker = next(
        (
            item
            for item in parsed_items
            if item.properties.item_name == "小米触屏音响 LX04"
        ),
        None,
    )
    if xiaomi_speaker:
        print(f"\n--- 验证 '小米触屏音响 LX04' 的退役日期 ---")
        print(f"  物品名称: {xiaomi_speaker.properties.item_name}")
        print(f"  退役日期: {xiaomi_speaker.properties.service_end_date}")
        print(f"  当前日期: {date.today()}")
        if xiaomi_speaker.properties.service_end_date == date.today():
            print("  ✅ '小米触屏音响 LX04' 的退役日期成功默认为当前日期。")
        else:
            print("  ❌ '小米触屏音响 LX04' 的退役日期未成功默认为当前日期。")

    # 验证一个附加价值为数字的条目 (DELL 游匣 G15)
    dell_g15 = next(
        (item for item in parsed_items if item.properties.item_name == "DELL 游匣 G15"),
        None,
    )
    if dell_g15:
        print(f"\n--- 验证 'DELL 游匣 G15' 的附加价值 ---")
        print(f"  物品名称: {dell_g15.properties.item_name}")
        print(f"  附加价值: {dell_g15.properties.additional_value}")
        if dell_g15.properties.additional_value == 3732.0:
            print("  ✅ 'DELL 游匣 G15' 的附加价值解析正确。")
        else:
            print("  ❌ 'DELL 游匣 G15' 的附加价值解析不正确。")

    # 制造一个入役日期缺失的条目来测试警告
    print("\n--- 测试 '入役日期' 缺失的警告 ---")
    test_item_missing_start_date = {
        "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
        "archived": False,
        "properties": {
            "物品名称": "测试物品 (无入役日期)",
            "购买价格": 100.0,
            # "入役日期": "2024-01-01", # 故意注释掉，使其缺失
            "备注": "这个物品没有入役日期",
            "日均价格": "5.0 元",
        },
    }
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            missing_date_item = Item.model_validate(test_item_missing_start_date)
            print(f"  解析成功: {missing_date_item.properties.item_name}")
            print(f"  入役日期: {missing_date_item.properties.service_start_date}")
        except ValidationError as e:
            print(f"  解析失败: {e}")
        if w:
            print("  捕获到警告:")
            for warn_message in w:
                print(f"    {warn_message.message}")
        else:
            print("  未捕获到警告。")

    # 制造一个 '附加价值' 非数字的条目来测试警告 (尽管用户说不会发生)
    print("\n--- 测试 '附加价值' 非数字的警告 (模拟异常数据) ---")
    test_item_bad_additional_value = {
        "id": "f5e4d3c2-b1a0-9876-5432-10fedcba9876",
        "archived": False,
        "properties": {
            "物品名称": "测试物品 (附加价值非数字)",
            "购买价格": 200.0,
            "入役日期": "2024-06-01",
            "附加价值": "这是维修费用",  # 故意传入非数字字符串
            "备注": "附加价值字段有问题",
        },
    }
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            bad_value_item = Item.model_validate(test_item_bad_additional_value)
            print(f"  解析成功: {bad_value_item.properties.item_name}")
            print(f"  附加价值: {bad_value_item.properties.additional_value}")
        except ValidationError as e:
            print(f"  解析失败: {e}")
        if w:
            print("  捕获到警告:")
            for warn_message in w:
                print(f"    {warn_message.message}")
        else:
            print("  未捕获到警告。")

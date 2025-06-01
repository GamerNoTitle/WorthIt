import re
import warnings
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator


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

"""Shop and economy system models."""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CurrencyType(str, Enum):
    """Currency type."""
    STARS = "stars"               # 星星（游戏内货币）
    REAL_MONEY = "real_money"     # 真实货币


class ProductCategory(str, Enum):
    """Product category."""
    SCRIPT = "script"             # 剧本
    THEME = "theme"               # 界面主题/皮肤
    CHAT_SKIN = "chat_skin"       # 聊天窗口皮肤
    PROFILE_SKIN = "profile_skin" # 个人主页皮肤
    AVATAR_FRAME = "avatar_frame" # 头像框
    GIFT = "gift"                 # 虚拟礼物
    MEMBERSHIP = "membership"     # 会员


class ProductStatus(str, Enum):
    """Product status."""
    ACTIVE = "active"             # 上架
    INACTIVE = "inactive"         # 下架
    LIMITED = "limited"           # 限定
    SEASONAL = "seasonal"         # 季节限定


class Product(BaseModel):
    """Shop product."""
    product_id: str
    name: str
    description: str
    category: ProductCategory
    icon: Optional[str] = None    # 图标URL
    preview_images: List[str] = Field(default_factory=list)  # 预览图

    # 定价
    price_stars: int              # 星星价格
    original_price: Optional[int] = None  # 原价（用于折扣）

    # 限定信息
    status: ProductStatus = ProductStatus.ACTIVE
    limited_start: Optional[datetime] = None  # 限定开始时间
    limited_end: Optional[datetime] = None      # 限定结束时间

    # 解锁条件
    unlock_condition: Optional[Dict[str, Any]] = None  # 解锁条件

    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class OrderStatus(str, Enum):
    """Order status."""
    PENDING = "pending"           # 待支付
    PAID = "paid"                 # 已支付
    COMPLETED = "completed"       # 已完成
    REFUNDED = "refunded"         # 已退款
    CANCELLED = "cancelled"       # 已取消


class OrderType(str, Enum):
    """Order type."""
    PURCHASE = "purchase"         # 购买
    RECHARGE = "recharge"         # 充值
    GIFT = "gift"                 # 赠送
    REWARD = "reward"             # 奖励


class Order(BaseModel):
    """Purchase order."""
    order_id: str
    order_type: OrderType
    player_id: str
    product_id: Optional[str] = None  # 商品ID（充值时为None）
    product_name: Optional[str] = None

    # 金额
    amount: int                   # 金额（星星数或分）
    currency: CurrencyType

    # 状态
    status: OrderStatus = OrderStatus.PENDING
    paid_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # 关联信息
    recipient_id: Optional[str] = None  # 礼物接收者
    gift_message: Optional[str] = None   # 礼物留言

    # 第三方支付信息
    payment_provider: Optional[str] = None  # 支付渠道
    payment_transaction_id: Optional[str] = None  # 交易号

    created_at: datetime = Field(default_factory=lambda: datetime.now())


class PlayerWallet(BaseModel):
    """Player wallet."""
    player_id: str
    stars: int = 0                # 星星余额
    total_recharged: int = 0    # 累计充值（分）
    total_spent: int = 0        # 累计消费（星星）
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class RechargeTier(BaseModel):
    """Recharge tier configuration."""
    tier_id: str
    amount_cny: int             # 人民币金额（元）
    stars_given: int            # 获得星星数
    bonus_stars: int = 0        # 赠送星星数
    is_promotion: bool = False  # 是否促销


class GiftRecord(BaseModel):
    """Gift sending record."""
    gift_id: str
    sender_id: str
    recipient_id: str
    product_id: str
    product_name: str
    message: Optional[str] = None
    sent_at: datetime = Field(default_factory=lambda: datetime.now())


class CartItem(BaseModel):
    """Shopping cart item."""
    product_id: str
    quantity: int = 1
    added_at: datetime = Field(default_factory=lambda: datetime.now())


class ShoppingCart(BaseModel):
    """Player shopping cart."""
    player_id: str
    items: List[CartItem] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


class PurchaseRequest(BaseModel):
    """Purchase request."""
    player_id: str
    product_id: str
    use_stars: bool = True      # 使用星星支付


class GiftRequest(BaseModel):
    """Gift request."""
    sender_id: str
    recipient_id: str
    product_id: str
    message: Optional[str] = None


class RechargeRequest(BaseModel):
    """Recharge request."""
    player_id: str
    tier_id: str
    payment_method: str         # 支付方式


class WalletTransaction(BaseModel):
    """Wallet transaction record."""
    transaction_id: str
    player_id: str
    transaction_type: str       # 收入/支出类型
    amount: int                 # 变动金额
    balance_after: int          # 变动后余额
    description: str
    related_order_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())

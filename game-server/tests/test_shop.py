"""Shop and economy system tests."""
import pytest
from datetime import datetime, timedelta

from src.services.shop_service import ShopService
from src.models.shop import (
    Product, RechargeRequest, PurchaseRequest, GiftRequest,
    ProductCategory, ProductStatus, OrderType, OrderStatus
)


@pytest.fixture
def shop_service():
    """Create a fresh shop service for tests."""
    service = ShopService()
    # Clear any existing data
    service._products.clear()
    service._orders.clear()
    service._wallets.clear()
    service._gift_records.clear()
    service._carts.clear()
    service._transactions.clear()
    return service


@pytest.fixture
def sample_product():
    """Sample product for testing."""
    return Product(
        product_id="prod_001",
        name="暗夜主题",
        description="深色主题皮肤",
        category=ProductCategory.THEME,
        price_stars=60,
        status=ProductStatus.ACTIVE
    )


class TestProduct:
    """Test product management."""

    @pytest.mark.asyncio
    async def test_create_product(self, shop_service, sample_product):
        """Test creating product."""
        product = await shop_service.create_product(sample_product)

        assert product.product_id == "prod_001"
        assert product.name == "暗夜主题"
        assert product.price_stars == 60

    @pytest.mark.asyncio
    async def test_get_product(self, shop_service, sample_product):
        """Test getting product."""
        await shop_service.create_product(sample_product)

        product = await shop_service.get_product("prod_001")
        assert product is not None
        assert product.name == "暗夜主题"

    @pytest.mark.asyncio
    async def test_get_product_not_found(self, shop_service):
        """Test getting non-existent product."""
        product = await shop_service.get_product("non_existent")
        assert product is None

    @pytest.mark.asyncio
    async def test_get_products_by_category(self, shop_service):
        """Test getting products filtered by category."""
        products = [
            Product(product_id="p1", name="主题1", description="desc", category=ProductCategory.THEME, price_stars=60),
            Product(product_id="p2", name="头像框1", description="desc", category=ProductCategory.AVATAR_FRAME, price_stars=30),
            Product(product_id="p3", name="主题2", description="desc", category=ProductCategory.THEME, price_stars=80),
        ]
        for p in products:
            await shop_service.create_product(p)

        theme_products = await shop_service.get_products(category=ProductCategory.THEME)
        assert len(theme_products) == 2
        assert all(p.category == ProductCategory.THEME for p in theme_products)

    @pytest.mark.asyncio
    async def test_update_product(self, shop_service, sample_product):
        """Test updating product."""
        await shop_service.create_product(sample_product)

        updated = await shop_service.update_product("prod_001", {"price_stars": 50, "name": "暗夜主题升级版"})

        assert updated.price_stars == 50
        assert updated.name == "暗夜主题升级版"

    @pytest.mark.asyncio
    async def test_delete_product(self, shop_service, sample_product):
        """Test deleting product."""
        await shop_service.create_product(sample_product)

        success = await shop_service.delete_product("prod_001")
        assert success is True

        product = await shop_service.get_product("prod_001")
        assert product is None


class TestRecharge:
    """Test recharge functionality."""

    @pytest.mark.asyncio
    async def test_recharge(self, shop_service):
        """Test recharge."""
        request = RechargeRequest(
            player_id="player_001",
            tier_id="tier_6",
            payment_method="alipay"
        )

        result = await shop_service.recharge(request)

        assert result["success"] is True
        assert result["stars_added"] == 60  # 6元 = 60星
        assert result["stars_balance"] == 60

        # Verify wallet updated
        wallet = await shop_service.get_wallet("player_001")
        assert wallet.stars == 60
        assert wallet.total_recharged == 600  # 6元 = 600分

    @pytest.mark.asyncio
    async def test_recharge_with_bonus(self, shop_service):
        """Test recharge with bonus."""
        request = RechargeRequest(
            player_id="player_001",
            tier_id="tier_30",
            payment_method="wechat"
        )

        result = await shop_service.recharge(request)

        assert result["stars_added"] == 310  # 300 + 10 bonus
        assert result["stars_balance"] == 310

    @pytest.mark.asyncio
    async def test_recharge_invalid_tier(self, shop_service):
        """Test recharge with invalid tier."""
        request = RechargeRequest(
            player_id="player_001",
            tier_id="invalid_tier",
            payment_method="alipay"
        )

        with pytest.raises(ValueError, match="Recharge tier.*not found"):
            await shop_service.recharge(request)

    @pytest.mark.asyncio
    async def test_get_recharge_tiers(self, shop_service):
        """Test getting recharge tiers."""
        tiers = await shop_service.get_recharge_tiers()

        assert len(tiers) == 6
        tier_prices = [t.amount_cny for t in tiers]
        assert 6 in tier_prices
        assert 648 in tier_prices


class TestPurchase:
    """Test purchase functionality."""

    @pytest.mark.asyncio
    async def test_purchase_success(self, shop_service, sample_product):
        """Test successful purchase."""
        # Setup: recharge first
        await shop_service.recharge(RechargeRequest(
            player_id="player_001",
            tier_id="tier_6",
            payment_method="alipay"
        ))

        # Create product
        await shop_service.create_product(sample_product)

        # Purchase
        request = PurchaseRequest(
            player_id="player_001",
            product_id="prod_001",
            use_stars=True
        )

        result = await shop_service.purchase(request)

        assert result["success"] is True
        assert result["product"].product_id == "prod_001"
        assert result["stars_balance"] == 0  # 60 - 60 = 0

    @pytest.mark.asyncio
    async def test_purchase_insufficient_stars(self, shop_service, sample_product):
        """Test purchase with insufficient stars."""
        await shop_service.create_product(sample_product)

        request = PurchaseRequest(
            player_id="player_001",
            product_id="prod_001"
        )

        with pytest.raises(ValueError, match="Insufficient stars"):
            await shop_service.purchase(request)

    @pytest.mark.asyncio
    async def test_purchase_product_not_found(self, shop_service):
        """Test purchase non-existent product."""
        request = PurchaseRequest(
            player_id="player_001",
            product_id="non_existent"
        )

        with pytest.raises(ValueError, match="Product.*not found"):
            await shop_service.purchase(request)


class TestGift:
    """Test gift functionality."""

    @pytest.mark.asyncio
    async def test_send_gift(self, shop_service):
        """Test sending gift."""
        # Setup: recharge sender
        await shop_service.recharge(RechargeRequest(
            player_id="sender_001",
            tier_id="tier_30",
            payment_method="alipay"
        ))

        # Create gift product
        gift_product = Product(
            product_id="gift_001",
            name="鲜花",
            description="一束鲜花",
            category=ProductCategory.GIFT,
            price_stars=50
        )
        await shop_service.create_product(gift_product)

        # Send gift
        request = GiftRequest(
            sender_id="sender_001",
            recipient_id="recipient_001",
            product_id="gift_001",
            message="谢谢你的帮助！"
        )

        result = await shop_service.send_gift(request)

        assert result["success"] is True
        assert "gift_id" in result
        assert "order_id" in result

        # Verify sender balance
        wallet = await shop_service.get_wallet("sender_001")
        assert wallet.stars == 310 - 50  # 310 - 50 = 260

    @pytest.mark.asyncio
    async def test_send_gift_insufficient_stars(self, shop_service):
        """Test gift with insufficient stars."""
        gift_product = Product(
            product_id="gift_001",
            name="鲜花",
            description="一束鲜花",
            category=ProductCategory.GIFT,
            price_stars=50
        )
        await shop_service.create_product(gift_product)

        request = GiftRequest(
            sender_id="sender_001",
            recipient_id="recipient_001",
            product_id="gift_001"
        )

        with pytest.raises(ValueError, match="Insufficient stars"):
            await shop_service.send_gift(request)


class TestShoppingCart:
    """Test shopping cart functionality."""

    @pytest.mark.asyncio
    async def test_add_to_cart(self, shop_service, sample_product):
        """Test adding item to cart."""
        await shop_service.create_product(sample_product)

        cart = await shop_service.add_to_cart("player_001", "prod_001", 2)

        assert len(cart.items) == 1
        assert cart.items[0].product_id == "prod_001"
        assert cart.items[0].quantity == 2

    @pytest.mark.asyncio
    async def test_remove_from_cart(self, shop_service, sample_product):
        """Test removing item from cart."""
        await shop_service.create_product(sample_product)
        await shop_service.add_to_cart("player_001", "prod_001")

        cart = await shop_service.remove_from_cart("player_001", "prod_001")

        assert len(cart.items) == 0

    @pytest.mark.asyncio
    async def test_clear_cart(self, shop_service, sample_product):
        """Test clearing cart."""
        await shop_service.create_product(sample_product)
        await shop_service.add_to_cart("player_001", "prod_001")

        cart = await shop_service.clear_cart("player_001")

        assert len(cart.items) == 0

    @pytest.mark.asyncio
    async def test_checkout_cart(self, shop_service, sample_product):
        """Test checkout cart."""
        # Setup: recharge
        await shop_service.recharge(RechargeRequest(
            player_id="player_001",
            tier_id="tier_6",
            payment_method="alipay"
        ))

        # Create product and add to cart
        await shop_service.create_product(sample_product)
        await shop_service.add_to_cart("player_001", "prod_001")

        # Checkout
        result = await shop_service.checkout_cart("player_001")

        assert result["success"] is True
        assert result["total_cost"] == 60
        assert result["stars_balance"] == 0

    @pytest.mark.asyncio
    async def test_checkout_empty_cart(self, shop_service):
        """Test checkout with empty cart."""
        with pytest.raises(ValueError, match="Cart is empty"):
            await shop_service.checkout_cart("player_001")


class TestOrders:
    """Test order management."""

    @pytest.mark.asyncio
    async def test_get_orders(self, shop_service, sample_product):
        """Test getting player orders."""
        # Create order
        await shop_service.recharge(RechargeRequest(
            player_id="player_001",
            tier_id="tier_6",
            payment_method="alipay"
        ))

        await shop_service.create_product(sample_product)
        await shop_service.purchase(PurchaseRequest(
            player_id="player_001",
            product_id="prod_001"
        ))

        orders = await shop_service.get_orders("player_001")

        assert len(orders) == 2  # 1 recharge + 1 purchase

    @pytest.mark.asyncio
    async def test_get_orders_by_type(self, shop_service):
        """Test getting orders filtered by type."""
        await shop_service.recharge(RechargeRequest(
            player_id="player_001",
            tier_id="tier_6",
            payment_method="alipay"
        ))

        recharge_orders = await shop_service.get_orders("player_001", OrderType.RECHARGE)

        assert len(recharge_orders) == 1
        assert all(o.order_type == OrderType.RECHARGE for o in recharge_orders)


class TestRefund:
    """Test refund functionality."""

    @pytest.mark.asyncio
    async def test_process_refund(self, shop_service, sample_product):
        """Test processing refund."""
        # Setup: recharge and purchase
        await shop_service.recharge(RechargeRequest(
            player_id="player_001",
            tier_id="tier_6",
            payment_method="alipay"
        ))
        await shop_service.create_product(sample_product)
        purchase_result = await shop_service.purchase(PurchaseRequest(
            player_id="player_001",
            product_id="prod_001"
        ))

        order_id = purchase_result["order_id"]

        # Refund
        result = await shop_service.process_refund(order_id)

        assert result["success"] is True
        assert result["refund_amount"] == 60
        assert result["stars_balance"] == 60

        # Verify order status
        order = shop_service._orders[order_id]
        assert order.status == OrderStatus.REFUNDED

    @pytest.mark.asyncio
    async def test_refund_already_refunded(self, shop_service, sample_product):
        """Test refund already refunded order."""
        await shop_service.recharge(RechargeRequest(
            player_id="player_001",
            tier_id="tier_6",
            payment_method="alipay"
        ))
        await shop_service.create_product(sample_product)
        purchase_result = await shop_service.purchase(PurchaseRequest(
            player_id="player_001",
            product_id="prod_001"
        ))

        order_id = purchase_result["order_id"]
        await shop_service.process_refund(order_id)

        with pytest.raises(ValueError, match="Order already refunded"):
            await shop_service.process_refund(order_id)


class TestWallet:
    """Test wallet functionality."""

    @pytest.mark.asyncio
    async def test_get_wallet_new_player(self, shop_service):
        """Test getting wallet for new player."""
        wallet = await shop_service.get_wallet("new_player")

        assert wallet.player_id == "new_player"
        assert wallet.stars == 0
        assert wallet.total_recharged == 0

    @pytest.mark.asyncio
    async def test_get_transactions(self, shop_service):
        """Test getting transaction history."""
        # Create some transactions
        await shop_service.recharge(RechargeRequest(
            player_id="player_001",
            tier_id="tier_6",
            payment_method="alipay"
        ))

        transactions = await shop_service.get_transactions("player_001")

        assert len(transactions) >= 1
        assert transactions[0].transaction_type == "recharge"
        assert transactions[0].amount == 60

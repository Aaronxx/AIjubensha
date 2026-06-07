"""Shop and economy service."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4

from ..models.shop import (
    Product, Order, PlayerWallet, RechargeTier, GiftRecord,
    ShoppingCart, CartItem, PurchaseRequest, GiftRequest, RechargeRequest,
    WalletTransaction, ProductStatus, OrderStatus, OrderType,
    ProductCategory
)


class ShopService:
    """Manages shop and economy system."""

    def __init__(self):
        # In-memory stores
        self._products: dict[str, Product] = {}
        self._orders: dict[str, Order] = {}
        self._wallets: dict[str, PlayerWallet] = {}
        self._recharge_tiers: dict[str, RechargeTier] = {}
        self._gift_records: dict[str, GiftRecord] = {}
        self._carts: dict[str, ShoppingCart] = {}
        self._transactions: dict[str, WalletTransaction] = {}

        # Initialize default recharge tiers
        self._init_recharge_tiers()

    def _init_recharge_tiers(self):
        """Initialize default recharge tiers."""
        tiers = [
            RechargeTier(tier_id="tier_6", amount_cny=6, stars_given=60),
            RechargeTier(tier_id="tier_30", amount_cny=30, stars_given=300, bonus_stars=10),
            RechargeTier(tier_id="tier_68", amount_cny=68, stars_given=680, bonus_stars=30),
            RechargeTier(tier_id="tier_128", amount_cny=128, stars_given=1280, bonus_stars=80),
            RechargeTier(tier_id="tier_328", amount_cny=328, stars_given=3280, bonus_stars=280),
            RechargeTier(tier_id="tier_648", amount_cny=648, stars_given=6480, bonus_stars=680),
        ]
        for tier in tiers:
            self._recharge_tiers[tier.tier_id] = tier

    async def create_product(self, product: Product) -> Product:
        """Create a new product."""
        self._products[product.product_id] = product
        return product

    async def get_product(self, product_id: str) -> Optional[Product]:
        """Get product by ID."""
        return self._products.get(product_id)

    async def get_products(
        self,
        category: Optional[ProductCategory] = None,
        status: Optional[ProductStatus] = None
    ) -> List[Product]:
        """Get products with filters."""
        products = list(self._products.values())

        if category:
            products = [p for p in products if p.category == category]
        if status:
            products = [p for p in products if p.status == status]

        # Check limited availability
        now = datetime.now()
        active_products = []
        for p in products:
            if p.status == ProductStatus.LIMITED:
                if p.limited_start and p.limited_end:
                    if p.limited_start <= now <= p.limited_end:
                        active_products.append(p)
            else:
                active_products.append(p)

        return active_products

    async def update_product(
        self,
        product_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Product]:
        """Update product."""
        product = self._products.get(product_id)
        if not product:
            return None

        for key, value in updates.items():
            if hasattr(product, key):
                setattr(product, key, value)

        product.updated_at = datetime.now()
        return product

    async def delete_product(self, product_id: str) -> bool:
        """Delete product."""
        if product_id in self._products:
            del self._products[product_id]
            return True
        return False

    async def get_wallet(self, player_id: str) -> PlayerWallet:
        """Get or create player wallet."""
        if player_id not in self._wallets:
            self._wallets[player_id] = PlayerWallet(player_id=player_id)
        return self._wallets[player_id]

    async def recharge(self, request: RechargeRequest) -> Dict[str, Any]:
        """Process recharge request."""
        tier = self._recharge_tiers.get(request.tier_id)
        if not tier:
            raise ValueError(f"Recharge tier {request.tier_id} not found")

        # Create order
        total_stars = tier.stars_given + tier.bonus_stars
        order = Order(
            order_id=str(uuid4()),
            order_type=OrderType.RECHARGE,
            player_id=request.player_id,
            amount=tier.amount_cny * 100,  # Convert to cents
            currency="real_money",
            status=OrderStatus.PENDING,
            payment_provider=request.payment_method
        )
        self._orders[order.order_id] = order

        # Simulate payment completion (in real app, wait for payment callback)
        order.status = OrderStatus.PAID
        order.paid_at = datetime.now()

        # Update wallet
        wallet = await self.get_wallet(request.player_id)
        wallet.stars += total_stars
        wallet.total_recharged += tier.amount_cny * 100
        wallet.updated_at = datetime.now()

        # Complete order
        order.status = OrderStatus.COMPLETED
        order.completed_at = datetime.now()

        # Record transaction
        await self._add_transaction(
            player_id=request.player_id,
            transaction_type="recharge",
            amount=total_stars,
            balance_after=wallet.stars,
            description=f"充值 {tier.amount_cny}元",
            order_id=order.order_id
        )

        return {
            "success": True,
            "order_id": order.order_id,
            "stars_added": total_stars,
            "stars_balance": wallet.stars
        }

    async def purchase(self, request: PurchaseRequest) -> Dict[str, Any]:
        """Process purchase request."""
        product = await self.get_product(request.product_id)
        if not product:
            raise ValueError(f"Product {request.product_id} not found")

        if product.status not in [ProductStatus.ACTIVE, ProductStatus.LIMITED, ProductStatus.SEASONAL]:
            raise ValueError("Product not available")

        # Check unlock conditions
        if product.unlock_condition:
            # TODO: Check if player meets unlock conditions
            pass

        wallet = await self.get_wallet(request.player_id)
        if wallet.stars < product.price_stars:
            raise ValueError("Insufficient stars")

        # Create order
        order = Order(
            order_id=str(uuid4()),
            order_type=OrderType.PURCHASE,
            player_id=request.player_id,
            product_id=product.product_id,
            product_name=product.name,
            amount=product.price_stars,
            currency="stars",
            status=OrderStatus.PENDING
        )
        self._orders[order.order_id] = order

        # Deduct stars
        wallet.stars -= product.price_stars
        wallet.total_spent += product.price_stars
        wallet.updated_at = datetime.now()

        # Complete order
        order.status = OrderStatus.COMPLETED
        order.completed_at = datetime.now()

        # Record transaction
        await self._add_transaction(
            player_id=request.player_id,
            transaction_type="purchase",
            amount=-product.price_stars,
            balance_after=wallet.stars,
            description=f"购买 {product.name}",
            order_id=order.order_id
        )

        return {
            "success": True,
            "order_id": order.order_id,
            "product": product,
            "stars_balance": wallet.stars
        }

    async def send_gift(self, request: GiftRequest) -> Dict[str, Any]:
        """Send gift to another player."""
        product = await self.get_product(request.product_id)
        if not product or product.category != ProductCategory.GIFT:
            raise ValueError("Gift product not found")

        # Check sender balance
        sender_wallet = await self.get_wallet(request.sender_id)
        if sender_wallet.stars < product.price_stars:
            raise ValueError("Insufficient stars")

        # Deduct stars from sender
        sender_wallet.stars -= product.price_stars
        sender_wallet.total_spent += product.price_stars
        sender_wallet.updated_at = datetime.now()

        # Create gift order for sender
        order = Order(
            order_id=str(uuid4()),
            order_type=OrderType.GIFT,
            player_id=request.sender_id,
            product_id=product.product_id,
            product_name=product.name,
            amount=product.price_stars,
            currency="stars",
            recipient_id=request.recipient_id,
            gift_message=request.message,
            status=OrderStatus.COMPLETED,
            completed_at=datetime.now()
        )
        self._orders[order.order_id] = order

        # Record gift
        gift = GiftRecord(
            gift_id=str(uuid4()),
            sender_id=request.sender_id,
            recipient_id=request.recipient_id,
            product_id=product.product_id,
            product_name=product.name,
            message=request.message
        )
        self._gift_records[gift.gift_id] = gift

        # Record transaction
        await self._add_transaction(
            player_id=request.sender_id,
            transaction_type="gift_sent",
            amount=-product.price_stars,
            balance_after=sender_wallet.stars,
            description=f"赠送 {product.name} 给 {request.recipient_id}",
            order_id=order.order_id
        )

        return {
            "success": True,
            "gift_id": gift.gift_id,
            "order_id": order.order_id
        }

    async def _add_transaction(
        self,
        player_id: str,
        transaction_type: str,
        amount: int,
        balance_after: int,
        description: str,
        order_id: Optional[str] = None
    ):
        """Add wallet transaction."""
        transaction = WalletTransaction(
            transaction_id=str(uuid4()),
            player_id=player_id,
            transaction_type=transaction_type,
            amount=amount,
            balance_after=balance_after,
            description=description,
            related_order_id=order_id
        )
        self._transactions[transaction.transaction_id] = transaction

    async def get_orders(
        self,
        player_id: str,
        order_type: Optional[OrderType] = None
    ) -> List[Order]:
        """Get player orders."""
        orders = [
            o for o in self._orders.values()
            if o.player_id == player_id
        ]
        if order_type:
            orders = [o for o in orders if o.order_type == order_type]
        orders.sort(key=lambda x: x.created_at, reverse=True)
        return orders

    async def get_transactions(
        self,
        player_id: str,
        limit: int = 50
    ) -> List[WalletTransaction]:
        """Get player transaction history."""
        transactions = [
            t for t in self._transactions.values()
            if t.player_id == player_id
        ]
        transactions.sort(key=lambda x: x.created_at, reverse=True)
        return transactions[:limit]

    async def get_recharge_tiers(self) -> List[RechargeTier]:
        """Get all recharge tiers."""
        return list(self._recharge_tiers.values())

    async def get_cart(self, player_id: str) -> ShoppingCart:
        """Get player shopping cart."""
        if player_id not in self._carts:
            self._carts[player_id] = ShoppingCart(player_id=player_id)
        return self._carts[player_id]

    async def add_to_cart(
        self,
        player_id: str,
        product_id: str,
        quantity: int = 1
    ) -> ShoppingCart:
        """Add item to cart."""
        cart = await self.get_cart(player_id)

        # Check if product exists
        product = await self.get_product(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        # Check if already in cart
        existing = next((item for item in cart.items if item.product_id == product_id), None)
        if existing:
            existing.quantity += quantity
        else:
            cart.items.append(CartItem(product_id=product_id, quantity=quantity))

        cart.updated_at = datetime.now()
        return cart

    async def remove_from_cart(
        self,
        player_id: str,
        product_id: str
    ) -> ShoppingCart:
        """Remove item from cart."""
        cart = await self.get_cart(player_id)
        cart.items = [item for item in cart.items if item.product_id != product_id]
        cart.updated_at = datetime.now()
        return cart

    async def clear_cart(self, player_id: str) -> ShoppingCart:
        """Clear shopping cart."""
        cart = await self.get_cart(player_id)
        cart.items.clear()
        cart.updated_at = datetime.now()
        return cart

    async def checkout_cart(self, player_id: str) -> Dict[str, Any]:
        """Checkout shopping cart."""
        cart = await self.get_cart(player_id)

        if not cart.items:
            raise ValueError("Cart is empty")

        # Calculate total
        total_cost = 0
        products = []
        for item in cart.items:
            product = await self.get_product(item.product_id)
            if product:
                total_cost += product.price_stars * item.quantity
                products.append(product)

        wallet = await self.get_wallet(player_id)
        if wallet.stars < total_cost:
            raise ValueError("Insufficient stars")

        # Process purchases
        order_ids = []
        for item in cart.items:
            for _ in range(item.quantity):
                result = await self.purchase(PurchaseRequest(
                    player_id=player_id,
                    product_id=item.product_id
                ))
                order_ids.append(result["order_id"])

        # Clear cart
        await self.clear_cart(player_id)

        return {
            "success": True,
            "order_ids": order_ids,
            "total_cost": total_cost,
            "stars_balance": wallet.stars
        }

    async def process_refund(self, order_id: str) -> Dict[str, Any]:
        """Process refund for an order."""
        order = self._orders.get(order_id)
        if not order:
            raise ValueError("Order not found")

        if order.status == OrderStatus.REFUNDED:
            raise ValueError("Order already refunded")

        if order.status != OrderStatus.COMPLETED:
            raise ValueError("Only completed orders can be refunded")

        # Restore stars
        wallet = await self.get_wallet(order.player_id)
        wallet.stars += order.amount
        wallet.updated_at = datetime.now()

        # Update order status
        order.status = OrderStatus.REFUNDED

        # Record transaction
        await self._add_transaction(
            player_id=order.player_id,
            transaction_type="refund",
            amount=order.amount,
            balance_after=wallet.stars,
            description=f"退款 {order.product_name or '充值'}",
            order_id=order.order_id
        )

        return {
            "success": True,
            "order_id": order_id,
            "refund_amount": order.amount,
            "stars_balance": wallet.stars
        }


# Singleton instance
shop_service = ShopService()

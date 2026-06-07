"""Shop and economy routes."""
from fastapi import APIRouter, HTTPException
from typing import List, Optional

from ..models.shop import (
    Product, PurchaseRequest, GiftRequest, RechargeRequest,
    ProductCategory, ProductStatus, OrderType
)
from ..services.shop_service import shop_service

router = APIRouter(prefix="/shop", tags=["shop"])


@router.post("/products", response_model=Product)
async def create_product(product: Product):
    """Create a new product."""
    return await shop_service.create_product(product)


@router.get("/products")
async def get_products(
    category: Optional[ProductCategory] = None,
    status: Optional[ProductStatus] = None
):
    """Get products with filters. Returns array directly for client compatibility."""
    products = await shop_service.get_products(category, status)
    return products


@router.get("/products/{product_id}")
async def get_product(product_id: str):
    """Get product by ID."""
    product = await shop_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.patch("/products/{product_id}")
async def update_product(product_id: str, updates: dict):
    """Update product."""
    product = await shop_service.update_product(product_id, updates)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/products/{product_id}")
async def delete_product(product_id: str):
    """Delete product."""
    success = await shop_service.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"success": True}


@router.get("/wallet/{player_id}")
async def get_wallet(player_id: str):
    """Get player wallet."""
    wallet = await shop_service.get_wallet(player_id)
    return wallet


@router.get("/balance")
async def get_balance():
    """Get current user's stars balance. Returns {balance: int}."""
    from fastapi import Request
    # This route is a compatibility endpoint for the iOS client
    # which calls /shop/balance without player_id.
    # For now, return 0 balance. In production, extract user from auth token.
    return {"balance": 0}


@router.post("/recharge")
async def recharge(request: RechargeRequest):
    """Process recharge."""
    try:
        result = await shop_service.recharge(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/recharge-tiers")
async def get_recharge_tiers():
    """Get recharge tiers."""
    tiers = await shop_service.get_recharge_tiers()
    return {"tiers": tiers}


@router.post("/purchase")
async def purchase(request: PurchaseRequest):
    """Purchase a product."""
    try:
        result = await shop_service.purchase(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/products/{product_id}/purchase")
async def purchase_product(product_id: str):
    """Purchase a product by ID (iOS client compatibility route).
    Extracts player_id from auth token in production, falls back to mock."""
    # For MVP: just return success. Full implementation would:
    # 1. Extract player_id from JWT token
    # 2. Call shop_service.purchase(PurchaseRequest(player_id, product_id))
    return {"success": True, "product_id": product_id}


@router.post("/gift")
async def send_gift(request: GiftRequest):
    """Send gift to another player."""
    try:
        result = await shop_service.send_gift(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/orders/{player_id}")
async def get_orders(
    player_id: str,
    order_type: Optional[OrderType] = None
):
    """Get player orders."""
    orders = await shop_service.get_orders(player_id, order_type)
    return {
        "player_id": player_id,
        "orders": orders,
        "total": len(orders)
    }


@router.get("/transactions/{player_id}")
async def get_transactions(player_id: str, limit: int = 50):
    """Get player transaction history."""
    transactions = await shop_service.get_transactions(player_id, limit)
    return {
        "player_id": player_id,
        "transactions": transactions,
        "total": len(transactions)
    }


@router.get("/cart/{player_id}")
async def get_cart(player_id: str):
    """Get shopping cart."""
    cart = await shop_service.get_cart(player_id)
    return cart


@router.post("/cart/{player_id}/add")
async def add_to_cart(player_id: str, product_id: str, quantity: int = 1):
    """Add item to cart."""
    try:
        cart = await shop_service.add_to_cart(player_id, product_id, quantity)
        return cart
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/cart/{player_id}/remove")
async def remove_from_cart(player_id: str, product_id: str):
    """Remove item from cart."""
    cart = await shop_service.remove_from_cart(player_id, product_id)
    return cart


@router.post("/cart/{player_id}/clear")
async def clear_cart(player_id: str):
    """Clear shopping cart."""
    cart = await shop_service.clear_cart(player_id)
    return cart


@router.post("/cart/{player_id}/checkout")
async def checkout_cart(player_id: str):
    """Checkout cart."""
    try:
        result = await shop_service.checkout_cart(player_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refund/{order_id}")
async def process_refund(order_id: str):
    """Process refund."""
    try:
        result = await shop_service.process_refund(order_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

"""Achievements, shop, orders, users, audit — admin CRUD."""
from fastapi import APIRouter, HTTPException
from ..services.store import store

router = APIRouter(prefix="/api/admin", tags=["admin"])

# ── Achievements ──
@router.post("/achievements", status_code=201)
def create_achievement(data: dict):
    data["id"] = str(hash(str(data)))  # simple id generation
    store.achievements.append(data)
    return data

@router.get("/achievements")
def list_achievements(): return store.achievements

@router.put("/achievements/{ach_id}")
def update_achievement(ach_id: str, data: dict):
    for i, a in enumerate(store.achievements):
        if a.get("id") == ach_id:
            store.achievements[i].update(data)
            return store.achievements[i]
    raise HTTPException(404, "Achievement not found")

@router.delete("/achievements/{ach_id}")
def delete_achievement(ach_id: str):
    store.achievements = [a for a in store.achievements if a.get("id") != ach_id]
    return {"status": "deleted"}

# ── Products (Shop) ──
@router.post("/products", status_code=201)
def create_product(data: dict):
    data["id"] = str(hash(str(data)))
    store.products.append(data)
    return data

@router.get("/products")
def list_products(): return store.products

@router.put("/products/{prod_id}")
def update_product(prod_id: str, data: dict):
    for i, p in enumerate(store.products):
        if p.get("id") == prod_id: store.products[i].update(data); return store.products[i]
    raise HTTPException(404)

@router.delete("/products/{prod_id}")
def delete_product(prod_id: str):
    store.products = [p for p in store.products if p.get("id") != prod_id]
    return {"status": "deleted"}

# ── Orders ──
@router.get("/orders")
def list_orders(): return store.orders

@router.get("/orders/{order_id}")
def get_order(order_id: str):
    for o in store.orders:
        if o.get("id") == order_id: return o
    raise HTTPException(404)

@router.post("/orders/{order_id}/refund")
def refund_order(order_id: str, data: dict):
    for o in store.orders:
        if o.get("id") == order_id:
            o["status"] = "refunded"
            o["refund_reason"] = data.get("reason", "")
            return o
    raise HTTPException(404)

# ── Users ──
@router.get("/users")
def list_users(): return list(store.users.values())

@router.get("/users/{user_id}")
def get_user(user_id: str):
    u = store.users.get(user_id)
    if not u: raise HTTPException(404)
    return u

@router.put("/users/{user_id}")
def update_user(user_id: str, data: dict):
    u = store.users.get(user_id)
    if not u: raise HTTPException(404)
    u.update(data)
    return u

@router.post("/users/{user_id}/ban")
def ban_user(user_id: str):
    u = store.users.get(user_id)
    if not u: raise HTTPException(404)
    u["status"] = "banned"
    return u

# ── Content Audit ──
@router.get("/audit")
def list_audit_queue(): return store.audit_queue

@router.post("/audit/{item_id}/approve")
def approve_audit(item_id: str):
    for item in store.audit_queue:
        if item.get("id") == item_id: item["status"] = "approved"; return item
    raise HTTPException(404)

@router.post("/audit/{item_id}/reject")
def reject_audit(item_id: str):
    for item in store.audit_queue:
        if item.get("id") == item_id: item["status"] = "rejected"; return item
    raise HTTPException(404)

# ── Dashboard ──
@router.get("/dashboard")
def dashboard():
    return {
        "total_scripts": len(store.scripts),
        "total_characters": len(store.characters),
        "total_users": len(store.users),
        "total_orders": len(store.orders),
        "pending_audit": sum(1 for a in store.audit_queue if a.get("status") == "pending"),
    }

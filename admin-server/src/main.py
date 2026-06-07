"""Admin backend app entry."""
from fastapi import FastAPI
from .routes.characters import router as char_router
from .routes.scripts import router as script_router
from .routes.admin_modules import router as admin_router

app = FastAPI(title="AI推理叙事游戏 — 后台管理系统", version="0.1.0")

app.include_router(char_router)
app.include_router(script_router)
app.include_router(admin_router)

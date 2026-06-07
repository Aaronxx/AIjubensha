"""FastAPI app entry point."""
from fastapi import FastAPI
from .routes.auth import router as auth_router
from .routes.scripts import router as scripts_router
from .routes.rooms import router as rooms_router
from .routes.characters import router as characters_router
from .routes.dialogue import router as dialogue_router
from .routes.game import router as game_router
from .routes.investigation import router as investigation_router
from .routes.voting import router as voting_router
from .routes.settlement import router as settlement_router
from .routes.shop import router as shop_router
from .routes.ws import router as ws_router

app = FastAPI(title="AI推理叙事游戏 — 后端服务", version="0.1.0")

app.include_router(auth_router, prefix="/api", tags=["authentication"])
app.include_router(scripts_router, prefix="/api", tags=["scripts"])
app.include_router(rooms_router, prefix="/api", tags=["rooms"])
app.include_router(characters_router, prefix="/api", tags=["characters"])
app.include_router(dialogue_router, prefix="/api", tags=["dialogue"])
app.include_router(game_router, prefix="/api", tags=["game"])
app.include_router(investigation_router, prefix="/api", tags=["investigation"])
app.include_router(voting_router, prefix="/api", tags=["voting"])
app.include_router(settlement_router, prefix="/api", tags=["settlement"])
app.include_router(shop_router, prefix="/api", tags=["shop"])
app.include_router(ws_router)

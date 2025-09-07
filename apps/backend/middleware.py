"""Middleware enforcing asset visibility policies."""

from datetime import datetime
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .database import SessionLocal
from .services.models import Asset, AssetVisibility


class AssetAccessMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path.startswith("/assets/"):
            segments = path.strip("/").split("/")
            if len(segments) >= 2 and segments[1].isdigit():
                asset_id = int(segments[1])
                db = SessionLocal()
                try:
                    asset = db.query(Asset).filter(Asset.id == asset_id).first()
                    whitelist = [w.account_email for w in asset.whitelist_entries] if asset else []
                finally:
                    db.close()
                if not asset:
                    return JSONResponse({"detail": "Asset not found"}, status_code=404)
                if asset.expires_at and asset.expires_at < datetime.utcnow():
                    return JSONResponse({"detail": "Asset expired"}, status_code=403)
                if asset.visibility == AssetVisibility.public:
                    pass
                elif asset.visibility == AssetVisibility.gated:
                    token = request.headers.get("X-Asset-Token")
                    if not token or token != asset.nda_group:
                        return JSONResponse({"detail": "Valid passcode required"}, status_code=403)
                elif asset.visibility == AssetVisibility.private:
                    user = request.headers.get("X-User")
                    if not user:
                        return JSONResponse({"detail": "Authentication required"}, status_code=401)
                    if user not in whitelist:
                        return JSONResponse({"detail": "User not authorized"}, status_code=403)
        response = await call_next(request)
        return response

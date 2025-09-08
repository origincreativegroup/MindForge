"""Middleware enforcing asset visibility policies."""


from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


from .services.models import Asset, AssetVisibility


class AssetAccessMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path.startswith("/assets/"):
            segments = path.strip("/").split("/")
            if len(segments) >= 2 and segments[1].isdigit():
                asset_id = int(segments[1])

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

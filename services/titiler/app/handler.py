from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from titiler.core.factory import TilerFactory
from titiler.extensions import cogValidateExtension
from mangum import Mangum

app = FastAPI(title="TiTiler (Lambda)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番は絞ってください
    allow_methods=["*"],
    allow_headers=["*"],
)

# /cog/* に COG エンドポイント
cog = TilerFactory(
    router_prefix="/cog",
    extensions=[cogValidateExtension()],
)
app.include_router(cog.router, tags=["COG"])

@app.get("/")
def root():
    return {"message": "Welcome to TiTiler on Lambda"}

# Lambda エントリポイント
handler = Mangum(app)

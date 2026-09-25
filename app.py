from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers.traducao import router as router_traducao

app = FastAPI(title="Tradutor de Documentos")

app.include_router(router_traducao)

# Serve os arquivos estÃ¡ticos (css, js)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def home():
    return FileResponse("static/index.html")





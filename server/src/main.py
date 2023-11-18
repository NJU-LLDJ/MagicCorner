from fastapi import FastAPI

from api import api

app = FastAPI()
app.include_router(api, prefix="/api", tags=["api"])


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn
    from server import Server

    with open("server/config/server.json") as file:
        server = Server.model_validate_json(file.read())
    uvicorn.run("main:app", host=server.host, port=server.port, reload=True)

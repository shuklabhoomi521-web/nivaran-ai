from fastapi import FastAPI

app = FastAPI(title="Nivaran")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

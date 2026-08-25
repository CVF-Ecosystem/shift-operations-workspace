from fastapi import FastAPI

from integration_edge.health import EdgeReadiness
from integration_edge.webhook.router import router

app = FastAPI(title="Shift Operations Integration Edge", version="0.1.0")
app.include_router(router)


@app.get("/health")
def health():
    readiness=getattr(app.state,"readiness",EdgeReadiness(False,False,False,False,False,False))
    return {"service":"integration-edge",**readiness.public()}

import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
time_limit = 180


@app.get("/")
def read_root():
    return {"message": "Hello World"}


class Metric(BaseModel):
    cpu_percentage: float
    ram_used: float
    ram_total: float
    disk_percentage: int


metric_data: Metric | None = None
call_time: float | None = None


@app.post("/metrics")
def exec_metric(metric: Metric):
    global metric_data, call_time
    metric_data = metric
    call_time = time.monotonic()
    return metric


@app.get("/metrics", response_model=Metric)
def read_metric():
    if metric_data is None:
        raise HTTPException(status_code=404, detail="Metric not found")
    return metric_data


@app.get("/lastcall")
def read_last_call():
    if call_time is None:
        return {"status": "no_data"}
    last_call = round(time.monotonic() - call_time)
    if last_call > time_limit:
        return {"status": "stale"}
    else:
        return {"status": "ok"}

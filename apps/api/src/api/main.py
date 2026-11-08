from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello World"}


class Metric(BaseModel):
    cpu_percentage: float
    ram_used: float
    ram_total: float
    disk_percentage: int

metric_data = None

@app.post("/metrics")
def exec_metric(metric: Metric):
    global metric_data
    metric_data = metric
    return metric

@app.get("/metrics")
def read_metric():
    if metric_data is None:
        raise HTTPException(status_code=404, detail="Metric not found")
    else:
        return metric_data
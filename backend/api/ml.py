"""
GreenLedger - ML API Router
"""

from fastapi import APIRouter
from schemas.models import TelemetryInput, PredictionResponse
from services.ml.inference import ml_engine

router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])


@router.post("/predict", response_model=PredictionResponse)
def predict_power(telemetry: TelemetryInput):
    """Executes XGBoost inference to estimate hardware power consumption."""
    result = ml_engine.predict_power(telemetry.model_dump())
    return result


@router.get("/diagnostics")
def get_diagnostics():
    """Returns model performance metrics (R², MAE, RMSE) and training schema."""
    return ml_engine.get_model_diagnostics()

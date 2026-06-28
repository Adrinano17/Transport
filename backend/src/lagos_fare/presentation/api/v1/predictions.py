from fastapi import APIRouter, Depends

from lagos_fare.application.dto.trip_request_dto import TripRequestDTO
from lagos_fare.application.use_cases.predict_fare import PredictFareUseCase
from lagos_fare.dependencies import get_predict_fare_use_case

router = APIRouter()


@router.post("", response_model=dict, summary="Predict transportation fare")
async def predict_fare(
    body: TripRequestDTO,
    use_case: PredictFareUseCase = Depends(get_predict_fare_use_case),
) -> dict:
    result = await use_case.execute(body)
    return result.model_dump(mode="json")

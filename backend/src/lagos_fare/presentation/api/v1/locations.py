"""Lagos location presets for frontend."""

from fastapi import APIRouter

from lagos_fare.domain.data.lagos_locations import LAGOS_LOCATIONS, LAGOS_ROUTE_PRESETS

router = APIRouter()


@router.get("")
async def list_lagos_locations() -> dict:
    locations = {
        key: {
            "name": loc.name,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "area": loc.area,
        }
        for key, loc in LAGOS_LOCATIONS.items()
    }
    presets = []
    for p in LAGOS_ROUTE_PRESETS:
        pickup = LAGOS_LOCATIONS[p["pickup"]]
        dropoff = LAGOS_LOCATIONS[p["dropoff"]]
        presets.append({
            "id": p["id"],
            "label": p["label"],
            "pickup": {"name": pickup.name, "latitude": pickup.latitude, "longitude": pickup.longitude},
            "dropoff": {"name": dropoff.name, "latitude": dropoff.latitude, "longitude": dropoff.longitude},
        })
    return {"locations": locations, "presets": presets}

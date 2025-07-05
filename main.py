from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncpg
import os

app = FastAPI()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/rout"
)

class RouteRequest(BaseModel):
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float

async def get_nearest_node(conn, lon: float, lat: float) -> int:
    query = """
    SELECT id
    FROM unique_nodes1
    ORDER BY geom <-> ST_SetSRID(ST_MakePoint($1, $2), 4326)
    LIMIT 1;
    """
    result = await conn.fetchrow(query, lon, lat)
    if result:
        return result["id"]
    raise HTTPException(status_code=404, detail="No nearest node found.")

async def calculate_route(conn, source: int, target: int):
    SPEED_KMH = 50  # سرعة افتراضية بالكيلومتر/ساعة
    SPEED_MPS = SPEED_KMH * 1000 / 3600  # متر/ثانية

    query = """
    SELECT r.seq, r.node, r.edge, r.cost, roads1.name, ST_AsGeoJSON(roads1.geom) as geom
    FROM pgr_dijkstra(
        $$
        SELECT id, source, target,
               ST_Length(geom::geography) AS cost,
               ST_Length(geom::geography) AS reverse_cost
        FROM roads1
        $$::text,
        $1::integer, $2::integer,
        directed := true
    ) AS r
    JOIN roads1 ON r.edge = roads1.id
    WHERE r.edge <> -1
    ORDER BY r.seq;
    """
    rows = await conn.fetch(query, source, target)
    if not rows:
        raise HTTPException(status_code=404, detail="Route not found. Please check direction and coordinates.")

    geojson_features = []
    total_distance = 0
    total_duration_seconds = 0

    for row in rows:
        distance = row["cost"]
        total_distance += distance

        duration_seconds = distance / SPEED_MPS
        total_duration_seconds += duration_seconds

        duration_min = int(duration_seconds // 60)
        duration_sec = int(duration_seconds % 60)

        geojson_features.append({
            "type": "Feature",
            "geometry": eval(row["geom"]),
            "properties": {
                "seq": row["seq"],
                "node": row["node"],
                "edge": row["edge"],
                "cost_meters": round(distance, 2),
                "street_name": row["name"],
                "duration": f"{duration_min} min {duration_sec} sec"
            }
        })

    total_min = int(total_duration_seconds // 60)
    total_sec = int(total_duration_seconds % 60)

    return {
        "type": "FeatureCollection",
        "features": geojson_features,
        "summary": {
            "total_distance_meters": round(total_distance, 2),
            "total_duration": f"{total_min} min {total_sec} sec"
        }
    }

@app.post("/route")
async def get_route(data: RouteRequest):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        start_node = await get_nearest_node(conn, data.start_lon, data.start_lat)
        end_node = await get_nearest_node(conn, data.end_lon, data.end_lat)
        route = await calculate_route(conn, start_node, end_node)
        return route
    finally:
        await conn.close()

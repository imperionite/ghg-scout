import os
from fastapi import APIRouter, Depends, HTTPException, Request, Query, status
from fastapi.concurrency import run_in_threadpool
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from fastapi.responses import JSONResponse
from typing import List, Optional
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from bson.objectid import ObjectId
from bson.regex import Regex


from huggingface_hub import InferenceClient

from routes.auth import get_current_user
from models.schemas import GHGSubmission
from core.db import db

router = APIRouter()

HF_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
hf_client = InferenceClient(model=HF_MODEL, token=HF_API_TOKEN)

@router.post("/submit")
async def submit(submission: GHGSubmission, current_user=Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    latest = await db.ghg_submissions.find_one(
        {"user_id": current_user["_id"], "sector": submission.sector},
        sort=[("created_at", -1)]
    )
    waiting_period = 7 * 24 * 60 * 60  # 7 days in seconds

    if latest:
        last_time = latest["created_at"]
        elapsed = (now.replace(tzinfo=None) - last_time).total_seconds()
        if elapsed < waiting_period:
            next_allowed = last_time + timedelta(seconds=waiting_period)
            next_allowed_str = next_allowed.strftime("%Y-%m-%d %H:%M:%S UTC")
            raise HTTPException(
                status_code=403,
                detail=(
                    f"You can only submit once every 7 days for the {submission.sector} sector. "
                    f"Your next allowed submission will be on: {next_allowed_str}."
                )
            )

    # Philippine-specific and IPCC Tier 1 emission factors
    ef = {
        "electricity": 0.709,
        "lpg": 2.983,
        "kerosene": 2.391,
        "firewood": 0.015,
        "diesel": 2.68,
        "gasoline": 2.32,
        "coal": 2.42,
        "cng": 2.0,
        "others": 2.0
    }
    doc = submission.model_dump()
    co2e = 0.0

    if submission.sector == "energy":
        co2e += doc.get("electricity_consumed_kwh", 0) * ef["electricity"]
        co2e += doc.get("lpg_used_kg", 0) * ef["lpg"]
        co2e += doc.get("kerosene_used_liters", 0) * ef["kerosene"]
        co2e += doc.get("firewood_used_kg", 0) * ef["firewood"]
        co2e += doc.get("diesel_used_liters", 0) * ef["diesel"]
        co2e += doc.get("gasoline_used_liters", 0) * ef["gasoline"]
        co2e += doc.get("coal_used_kg", 0) * ef["coal"]

    elif submission.sector == "transport":
        vehicles = doc.get("number_of_vehicles", 0)
        distance = doc.get("distance_travelled_daily_km", 0)
        freq = doc.get("travel_frequency_per_week", 0)
        trips = doc.get("trips_per_day", 0)
        fuel_type = doc.get("fuel_type", "diesel").lower()
        fuel_ef = ef.get(fuel_type, 2.0)
        co2e = vehicles * distance * freq * trips * fuel_ef

    elif submission.sector == "waste":
        waste = doc.get("waste_generated_kg_per_month", 0)
        organic = doc.get("organic_fraction_percent", 0)
        method = doc.get("waste_disposal_method", "landfill")
        methane_capture = doc.get("methane_capture", False)
        waste_ef = {
            "landfill": 1.8,
            "open_dumping": 2.0,
            "composting": 0.2,
            "recycling": 0.0,
            "incineration": 2.0,
            "others": 1.0
        }
        base_ef = waste_ef.get(method, 1.0)
        if methane_capture and method == "landfill":
            base_ef *= 0.5  # 50% reduction for methane capture
        co2e = waste * (organic / 100.0) * base_ef

    elif submission.sector == "agriculture":
        co2e = (
            doc.get("number_of_cattle", 0) * 912.5 +
            doc.get("number_of_carabao", 0) * 730 +
            doc.get("number_of_goats", 0) * 182.5 +
            doc.get("number_of_pigs", 0) * 401.5 +
            doc.get("number_of_chickens", 0) * 7.3 +
            doc.get("fertilizer_applied_kg", 0) * 5.5
        )
        if doc.get("rice_paddy_area_hectares", 0) > 0:
            water_mgmt = doc.get("rice_water_management", "continuous_flooding")
            rice_ef = {
                "continuous_flooding": 1200,
                "intermittent_flooding": 800,
                "dry_cultivation": 100
            }
            co2e += doc["rice_paddy_area_hectares"] * rice_ef.get(water_mgmt, 1200)

    elif submission.sector == "ippu":
        co2e = (
            doc.get("cement_produced_tonnes", 0) * 800 +
            doc.get("lime_produced_tonnes", 0) * 900 +
            doc.get("steel_produced_tonnes", 0) * 1800 +
            doc.get("refrigerant_consumed_kg", 0) * 1430 +
            doc.get("solvent_used_liters", 0) * 2.0 +
            doc.get("other_process_emissions_CO2e_tonnes", 0) * 1000
        )

    doc.update({
        "user_id": current_user["_id"],
        "created_at": now,
        "updated_at": now,
        "estimated_co2e_kg": round(co2e, 2)
    })
    result = await db.ghg_submissions.insert_one(doc)
    await FastAPICache.clear() # invalidate all cache
    return {
        "message": f"GHG data submitted for {submission.sector} sector successfully",
        "id": str(result.inserted_id),
        "estimated_co2e_kg": round(co2e, 2)
    }

@router.get("/community-summary")
@cache(expire=300)  # 5 minutes
async def get_community_summary():
    pipeline = [
        {"$lookup": {"from": "users", "localField": "user_id", "foreignField": "_id", "as": "user_info"}},
        {"$unwind": "$user_info"},
        {"$group": {"_id": {"region": "$user_info.region", "city": "$user_info.city"},
                    "total_emissions": {"$sum": "$estimated_co2e_kg"}, "count": {"$sum": 1}}},
        {"$sort": {"_id.region": 1, "_id.city": 1}}
    ]
    result = await db.ghg_submissions.aggregate(pipeline).to_list(length=None)
    return [{"region": r["_id"].get("region"), "city": r["_id"].get("city"), "total_emissions": round(r["total_emissions"], 2), "count": r["count"]} for r in result]

@router.get("/timeseries")
@cache(expire=600)
async def get_timeseries_summary(regions: Optional[str] = Query(default=None)):
    match_stage = {}
    if regions:
        region_list = regions.split(',')
        match_stage = {"user_info.region": {"$in": region_list}}

    pipeline = [
        {"$lookup": {"from": "users", "localField": "user_id", "foreignField": "_id", "as": "user_info"}},
        {"$unwind": "$user_info"},
    ]
    if match_stage:
        pipeline.append({"$match": match_stage})
    pipeline += [
        {"$group": {
            "_id": {"date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}},
            "total_emissions": {"$sum": "$estimated_co2e_kg"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id.date": 1}}
    ]
    result = await db.ghg_submissions.aggregate(pipeline).to_list(length=None)
    return {
        "labels": [r["_id"]["date"] for r in result],
        "datasets": [{
            "label": "Total CO2e per Day (kg)",
            "data": [round(r["total_emissions"], 2) for r in result],
            "backgroundColor": "rgba(75,192,192,0.4)",
            "borderColor": "rgba(75,192,192,1)",
            "borderWidth": 1,
            "fill": True
        }]
    }

# Chart: Compare average emissions per community type
# Usage: Identify which community types are most polluting on average
@router.get("/aggregated-by-type")
@cache(expire=300)
async def aggregated_by_type(regions: Optional[str] = Query(default=None)):
    match_stage = {}
    if regions:
        region_list = regions.split(',')
        match_stage = {"user_info.region": {"$in": region_list}}

    pipeline = [
        {"$lookup": {"from": "users", "localField": "user_id", "foreignField": "_id", "as": "user_info"}},
        {"$unwind": "$user_info"},
    ]
    if match_stage:
        pipeline.append({"$match": match_stage})
    pipeline += [
        {"$group": {
            "_id": "$user_info.community_type",
            "total_emissions": {"$sum": "$estimated_co2e_kg"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    result = await db.ghg_submissions.aggregate(pipeline).to_list(None)
    return [{"community_type": r["_id"], "total_emissions": round(r["total_emissions"], 2), "count": r["count"]} for r in result]

# Returns: Emissions over time grouped by region
# Chart: Stacked or grouped line chart per region
@router.get("/regional-trend-summary")
@cache(expire=900)
async def regional_trend_summary(regions: List[str] = Query(default=None)):
    match_stage = {}
    if regions:
        # Modify the match to use regex for partial matches
        match_stage["user_info.region"] = {"$in": [Regex(f".*{region}.*", "i") for region in regions]}

    pipeline = [
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "_id",
            "as": "user_info"
        }},
        {"$unwind": "$user_info"},
        *([{"$match": match_stage}] if match_stage else []),
        {"$group": {
            "_id": {
                "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "region": "$user_info.region"
            },
            "total_emissions": {"$sum": "$estimated_co2e_kg"}
        }},
        {"$sort": {"_id.date": 1}}
    ]

    result = await db.ghg_submissions.aggregate(pipeline).to_list(None)

    from collections import defaultdict
    grouped = defaultdict(lambda: {"labels": [], "data": []})
    for r in result:
        date = r["_id"]["date"]
        region = r["_id"]["region"]
        grouped[region]["labels"].append(date)
        grouped[region]["data"].append(round(r["total_emissions"], 2))

    return grouped


# Returns: Time-series GHG data per sector for a given user
# Chart: Sectoral trend lines (weekly or monthly) for a specific community
@router.get("/user-trend/{user_id}")
async def user_trend(user_id: str):
    try:
        uid = ObjectId(user_id)
    except:
        raise HTTPException(400, "Invalid ID")

    pipeline = [
        {"$match": {"user_id": uid}},
        {"$group": {
            "_id": {
                "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "sector": "$sector"
            },
            "emissions": {"$sum": "$estimated_co2e_kg"}
        }},
        {"$sort": {"_id.date": 1}}
    ]
    data = await db.ghg_submissions.aggregate(pipeline).to_list(None)
    
    from collections import defaultdict
    output = defaultdict(lambda: {"labels": [], "data": []})
    for r in data:
        sector = r["_id"]["sector"]
        date = r["_id"]["date"]
        output[sector]["labels"].append(date)
        output[sector]["data"].append(round(r["emissions"], 2))
    
    return output

# Sectoral Emissions by Region or City
# Purpose: See which sectors dominate emissions in each region or city.
@router.get("/sectoral-by-region")
@cache(expire=300)
async def sectoral_by_region(regions: Optional[str] = Query(default=None)):
    match_stage = {}
    if regions:
        region_list = regions.split(',')
        match_stage = {"user.region": {"$in": region_list}}

    pipeline = [
        {"$lookup": {"from": "users", "localField": "user_id", "foreignField": "_id", "as": "user"}},
        {"$unwind": "$user"},
    ]
    if match_stage:
        pipeline.append({"$match": match_stage})
    pipeline += [
        {"$group": {
            "_id": {
                "region": "$user.region",
                "sector": "$sector"
            },
            "total_emissions": {"$sum": "$estimated_co2e_kg"}
        }},
        {"$sort": {"_id.region": 1, "_id.sector": 1}}
    ]
    result = await db.ghg_submissions.aggregate(pipeline).to_list(None)

    from collections import defaultdict
    data = defaultdict(lambda: {"labels": [], "data": []})
    for r in result:
        region = r["_id"]["region"]
        sector = r["_id"]["sector"]
        data[region]["labels"].append(sector)
        data[region]["data"].append(round(r["total_emissions"], 2))
    return data

#  Sectoral Trend Over Time (National)
# Purpose: Analyze which sectors are increasing or decreasing over time
@router.get("/sectoral-trend")
@cache(expire=900)
async def sectoral_trend():
    pipeline = [
        {"$group": {
            "_id": {
                "sector": "$sector",
                "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}
            },
            "total_emissions": {"$sum": "$estimated_co2e_kg"}
        }},
        {"$sort": {"_id.date": 1}}
    ]
    result = await db.ghg_submissions.aggregate(pipeline).to_list(None)

    from collections import defaultdict
    grouped = defaultdict(lambda: {"labels": [], "data": []})
    for r in result:
        sector = r["_id"]["sector"]
        grouped[sector]["labels"].append(r["_id"]["date"])
        grouped[sector]["data"].append(round(r["total_emissions"], 2))

    return grouped

# Sectoral Composition by Community Type
# Purpose: Identify what emissions sectors dominate for schools, barangays, LGUs, etc.
@router.get("/sectoral-by-community-type")
@cache(expire=300)
async def sectoral_by_community_type(regions: Optional[str] = Query(default=None)):
    match_stage = {}
    if regions:
        region_list = regions.split(',')
        match_stage = {"user.region": {"$in": region_list}}

    pipeline = [
        {"$lookup": {"from": "users", "localField": "user_id", "foreignField": "_id", "as": "user"}},
        {"$unwind": "$user"},
    ]
    if match_stage:
        pipeline.append({"$match": match_stage})
    pipeline += [
        {"$group": {
            "_id": {
                "community_type": "$user.community_type",
                "sector": "$sector"
            },
            "total_emissions": {"$sum": "$estimated_co2e_kg"}
        }},
        {"$sort": {"_id.community_type": 1, "_id.sector": 1}}
    ]
    result = await db.ghg_submissions.aggregate(pipeline).to_list(None)

    from collections import defaultdict
    grouped = defaultdict(lambda: {"labels": [], "data": []})
    for r in result:
        comm_type = r["_id"]["community_type"]
        sector = r["_id"]["sector"]
        grouped[comm_type]["labels"].append(sector)
        grouped[comm_type]["data"].append(round(r["total_emissions"], 2))
    return grouped


# Sector Contribution Ranking (Top Contributors Globally per Sector)
# Purpose: Who are the top GHG emitters in each sector?
@router.get("/top-by-sector")
@cache(expire=600)
async def top_by_sector(limit: int = 5, regions: Optional[str] = Query(default=None)):
    match_stage = {}
    if regions:
        region_list = regions.split(',')
        match_stage = {"user.region": {"$in": region_list}}

    pipeline = [
        {"$group": {
            "_id": {
                "user_id": "$user_id",
                "sector": "$sector"
            },
            "total_emissions": {"$sum": "$estimated_co2e_kg"}
        }},
        {"$sort": {"_id.sector": 1, "total_emissions": -1}}
    ]
    sector_user_emissions = await db.ghg_submissions.aggregate(pipeline).to_list(None)

    from collections import defaultdict
    grouped = defaultdict(list)
    for record in sector_user_emissions:
        sector = record["_id"]["sector"]
        grouped[sector].append(record)

    top_by_sector = {sector: records[:limit] for sector, records in grouped.items()}
    user_ids = [r["_id"]["user_id"] for records in top_by_sector.values() for r in records]
    users = await db.users.find({"_id": {"$in": user_ids}}).to_list(None)
    user_map = {u["_id"]: u for u in users}

    response = {}
    for sector, records in top_by_sector.items():
        filtered = []
        for rec in records:
            uid = rec["_id"]["user_id"]
            user = user_map.get(uid)
            if user and (not regions or user.get("region") in region_list):
                filtered.append({
                    "user_id": str(uid),
                    "community_name": user.get("community_name"),
                    "region": user.get("region"),
                    "city": user.get("city"),
                    "total_emissions": round(rec["total_emissions"], 2)
                })
        response[sector] = filtered
    return response

@router.get("/top-emitters")
@cache(expire=1800)
async def get_top_emitters(limit: int = 5):
    pipeline = [
        {"$group": {"_id": "$user_id", "total_emissions": {"$sum": "$estimated_co2e_kg"}}}
    ]
    all_users = await db.ghg_submissions.aggregate(pipeline).to_list(None)
    all_users_sorted = sorted(all_users, key=lambda x: x["total_emissions"], reverse=True)

    total_count = len(all_users_sorted)
    user_ranks = {
        str(doc["_id"]): round((i + 1) / total_count * 100, 2)
        for i, doc in enumerate(all_users_sorted)
    }

    top = all_users_sorted[:limit]
    user_ids = [doc["_id"] for doc in top]
    users = await db.users.find({"_id": {"$in": user_ids}}).to_list(None)
    user_map = {user["_id"]: user for user in users}

    return [
        {
            "user_id": str(uid),
            "username": user_map[uid]["username"],
            "community_name": user_map[uid].get("community_name"),
            "region": user_map[uid].get("region"),
            "city": user_map[uid].get("city"),
            "total_emissions": round(doc["total_emissions"], 2),
            "global_percentile_rank": user_ranks[str(uid)]
        }
        for doc in top if (uid := doc["_id"]) in user_map
    ]

@router.get("/lowest-emitters")
@cache(expire=1800)
async def get_lowest_emitters(limit: int = 5):
    pipeline = [
        {"$group": {"_id": "$user_id", "total_emissions": {"$sum": "$estimated_co2e_kg"}}}
    ]
    all_users = await db.ghg_submissions.aggregate(pipeline).to_list(None)
    all_users_sorted = sorted(all_users, key=lambda x: x["total_emissions"])

    total_count = len(all_users_sorted)
    user_ranks = {
        str(doc["_id"]): round((i + 1) / total_count * 100, 2)
        for i, doc in enumerate(all_users_sorted)
    }

    bottom = all_users_sorted[:limit]
    user_ids = [doc["_id"] for doc in bottom]
    users = await db.users.find({"_id": {"$in": user_ids}}).to_list(None)
    user_map = {user["_id"]: user for user in users}

    return [
        {
            "user_id": str(uid),
            "username": user_map[uid]["username"],
            "community_name": user_map[uid].get("community_name"),
            "region": user_map[uid].get("region"),
            "city": user_map[uid].get("city"),
            "total_emissions": round(doc["total_emissions"], 2),
            "global_percentile_rank": user_ranks[str(uid)]
        }
        for doc in bottom if (uid := doc["_id"]) in user_map
    ]
# -------------------------------- USER SPECIFIC ------------------------------ #

@router.get("/user-summary/{user_id}")
async def get_user_summary(user_id: str):
    try:
        object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    pipeline = [
        {"$match": {"user_id": object_id}},
        {"$group": {
            "_id": "$sector",
            "total_emissions": {"$sum": "$estimated_co2e_kg"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    result = await db.ghg_submissions.aggregate(pipeline).to_list(length=None)

    return {
        "user_id": user_id,
        "labels": [r["_id"] for r in result],
        "datasets": [{
            "label": "User CO2e per Sector (kg)",
            "data": [round(r["total_emissions"], 2) for r in result],
            "backgroundColor": ["#36A2EB", "#FF6384", "#FFCE56", "#4BC0C0"]
        }]
    }

@router.get("/compare-user-to-average/{user_id}")
async def compare_user_to_average(user_id: str):
    try:
        object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    # Get all sector-level totals for user
    user_data = await db.ghg_submissions.aggregate([
        {"$match": {"user_id": object_id}},
        {"$group": {"_id": "$sector", "user_total": {"$sum": "$estimated_co2e_kg"}}}
    ]).to_list(None)

    # Get national stats and percentile distribution
    national_data = await db.ghg_submissions.aggregate([
        {"$group": {
            "_id": {"sector": "$sector", "user_id": "$user_id"},
            "user_sector_total": {"$sum": "$estimated_co2e_kg"}
        }},
        {"$group": {
            "_id": "$_id.sector",
            "user_totals": {"$push": "$user_sector_total"},
            "avg_total": {"$avg": "$user_sector_total"},
            "count": {"$sum": 1}
        }}
    ]).to_list(None)

    # Combine sector-level comparison
    comparison = []
    for sector_stat in national_data:
        sector = sector_stat["_id"]
        user_total = next((u["user_total"] for u in user_data if u["_id"] == sector), 0.0)
        user_totals = sector_stat["user_totals"]
        avg_total = sector_stat["avg_total"]

        # Percentile rank computation
        below = len([v for v in user_totals if v < user_total])
        percentile = round((below / len(user_totals)) * 100, 2)

        comparison.append({
            "sector": sector,
            "user_total": round(user_total, 2),
            "national_avg": round(avg_total, 2),
            "difference": round(user_total - avg_total, 2),
            "percentile_rank": percentile,
            "entries": sector_stat["count"]
        })

    return comparison


# Helper function to generate a natural description
def generate_description(community_type, community_name, city, region, labels, data):
    total_emissions = sum(data)
    sector_details = ", ".join(
        [f"{d} kg from {l}" for d, l in zip(data, labels)]
    )
    description = (
        f"The {community_type.lower()} '{community_name}' located in {city}, {region}, "
        f"has reported a total annual greenhouse gas emission of approximately "
        f"{round(total_emissions, 2)} kg CO2e. The emissions come from various sectors including "
        f"{sector_details}. "
        f"These are the locally relevant ways this {community_type.lower()} can reduce its emissions, "
        f"including practical carbon offset strategies suitable for their communities."
    )
    return description


@router.get("/my-summary-interpret")
async def my_summary_interpret(request: Request, current_user=Depends(get_current_user)):
    user_id = current_user["_id"]

    # Rate limiting: check if user requested within the last 7 days
    one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent_request = await db.llm_requests.find_one({
        "user_id": user_id,
        "endpoint": "my-summary-interpret",
        "requested_at": {"$gte": one_week_ago}
    })
    if recent_request:
        # Return 429 Too Many Requests with a message
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "You can only request this summary once per week. Please try again later."
            }
        )

    # User context
    community_type = current_user.get("community_type", "community")
    community_name = current_user.get("community_name", "your community")
    region = current_user.get("region", "the Philippines")
    city = current_user.get("city", "")

    # Aggregate user GHG data by sector
    pipeline = [
        {"$match": {"user_id": user_id}},
        {"$group": {
            "_id": "$sector",
            "total_emissions": {"$sum": "$estimated_co2e_kg"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    result = await db.ghg_submissions.aggregate(pipeline).to_list(length=None)
    if not result:
        raise HTTPException(status_code=404, detail="No GHG data found for your account.")

    labels = [r["_id"] for r in result]
    data = [round(r["total_emissions"], 2) for r in result]

    # Construct the prompt with the carbon offset bullet request
    prompt = (
        f"You are a sustainability expert in the Philippines. "
        f"A {community_type.lower()} named {community_name} located in {city}, {region}, "
        f"has reported these annual greenhouse gas emissions: "
        f"{'; '.join([f'{d} kg from {l}' for d, l in zip(data, labels)])}. "
        f"Give 2 locally relevant ways this {community_type.lower()} can reduce its emissions, "
        f"and 1 practical carbon offset strategy suitable for Philippine communities. "
        f"List them clearly using bullet points."
    )

    # Natural description
    description = generate_description(community_type, community_name, city, region, labels, data)

    # Call the Hugging Face chat completion in a threadpool (async-safe)
    def call_llm():
        return hf_client.chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful sustainability expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=400
        ).choices[0].message["content"].strip()

    try:
        ai_output = await run_in_threadpool(call_llm)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM failed to generate interpretation: {str(e)}")

    # Log the request for rate limiting
    await db.llm_requests.insert_one({
        "user_id": user_id,
        "endpoint": "my-summary-interpret",
        "requested_at": datetime.now(timezone.utc)
    })

    return {
        "summary_text": prompt,
        "description": description,
        "ai_interpretation": ai_output,
        "raw_data": {
            "labels": labels,
            "data": data
        }
    }

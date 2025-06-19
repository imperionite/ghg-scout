import asyncio
import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta, timezone
from random import randint, uniform, choice, random
from bson import ObjectId
from faker import Faker
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB URI and client setup
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.ghg_scout

faker = Faker()
COMMON_PASSWORD = "seed-password"

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    salt = bcrypt.gensalt()  # Generate a salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)  # Hash the password with the salt
    return hashed_password.decode('utf-8')  # Return the hashed password as a string

# Password for seeding
HASHED_PASSWORD = hash_password(COMMON_PASSWORD)


# Constants for regions, cities, community types, sectors, etc.
REGIONS_AND_CITIES = [
    ("National Capital Region (NCR)", ["Manila", "Quezon City", "Makati", "Pasig", "Taguig", "Caloocan"]),
    ("Cordillera Administrative Region (CAR)", ["Baguio City", "Tabuk City", "La Trinidad"]),
    ("Region I – Ilocos Region", ["Vigan City", "Laoag City", "San Fernando City"]),
    ("Region II – Cagayan Valley", ["Tuguegarao City", "Ilagan City", "Santiago City"]),
    ("Region III – Central Luzon", ["San Fernando City", "Angeles City", "Malolos City", "Olongapo City"]),
    ("Region IV-A – CALABARZON", ["Calamba City", "Batangas City", "Cavite City", "Santa Rosa City"]),
    ("Region IV-B – MIMAROPA", ["Puerto Princesa", "Calapan City", "Romblon"]),
    ("Region V – Bicol Region", ["Legazpi City", "Naga City", "Sorsogon City"]),
    ("Region VI – Western Visayas", ["Iloilo City", "Bacolod City", "Roxas City"]),
    ("Region VII – Central Visayas", ["Cebu City", "Lapu-Lapu City", "Tagbilaran City"]),
    ("Region VIII – Eastern Visayas", ["Tacloban City", "Ormoc City", "Borongan City"]),
    ("Region IX – Zamboanga Peninsula", ["Zamboanga City", "Pagadian City", "Dipolog City"]),
    ("Region X – Northern Mindanao", ["Cagayan de Oro City", "Iligan City", "Malaybalay City"]),
    ("Region XI – Davao Region", ["Davao City", "Tagum City", "Panabo City"]),
    ("Region XII – SOCCSKSARGEN", ["Koronadal City", "General Santos City", "Kidapawan City"]),
    ("Region XIII – Caraga", ["Butuan City", "Surigao City", "Bayugan City"]),
    ("Bangsamoro Autonomous Region in Muslim Mindanao (BARMM)", ["Cotabato City", "Marawi City", "Jolo"]),
]

COMMUNITY_TYPES = [
    "LGU",
    "Barangay",
    "School",
    "College/University"
]

SECTORS = ["energy", "transport", "waste", "agriculture", "ippu"]
WEEKS = 156  # Approx. 3 years

# Helper function to simulate optional values (20% chance of 0)
def maybe_zero(val, chance=0.2):
    return 0 if random() < chance else val

# Helper function to generate fake submissions per sector
def fake_submission(sector: str) -> dict:
    if sector == "energy":
        return {
            "sector": sector,
            "electricity_consumed_kwh": maybe_zero(round(uniform(50, 400), 2)),
            "lpg_used_kg": maybe_zero(round(uniform(0.5, 10), 2)),
            "kerosene_used_liters": maybe_zero(round(uniform(0, 5), 2)),
            "firewood_used_kg": maybe_zero(round(uniform(0, 15), 2)),
            "diesel_used_liters": maybe_zero(round(uniform(0, 20), 2)),
            "gasoline_used_liters": maybe_zero(round(uniform(0, 20), 2)),
            "coal_used_kg": maybe_zero(round(uniform(0, 30), 2)),
        }
    elif sector == "transport":
        return {
            "sector": sector,
            "vehicle_type": choice(["private_car", "motorcycle", "jeepney", "tricycle", "bus", "others"]),
            "fuel_type": choice(["gasoline", "diesel", "electric", "cng", "others"]),
            "number_of_vehicles": maybe_zero(randint(0, 10)),
            "distance_travelled_daily_km": maybe_zero(round(uniform(2, 50), 2)),
            "travel_frequency_per_week": maybe_zero(randint(0, 7)),
            "trips_per_day": maybe_zero(randint(0, 4)),
        }
    elif sector == "waste":
        return {
            "sector": sector,
            "waste_generated_kg_per_month": maybe_zero(round(uniform(10, 80), 2)),
            "organic_fraction_percent": maybe_zero(round(uniform(20, 70), 2)),
            "waste_disposal_method": choice(["landfill", "recycling", "composting", "incineration", "open_dumping", "others"]),
            "methane_capture": choice([True, False]),
        }
    elif sector == "agriculture":
        return {
            "sector": sector,
            "number_of_cattle": maybe_zero(randint(0, 10)),
            "number_of_carabao": maybe_zero(randint(0, 5)),
            "number_of_goats": maybe_zero(randint(0, 10)),
            "number_of_pigs": maybe_zero(randint(0, 8)),
            "number_of_chickens": maybe_zero(randint(0, 50)),
            "manure_management": choice(["dry_lot", "pasture", "lagoon", "composting", "none"]),
            "rice_paddy_area_hectares": maybe_zero(round(uniform(0, 3), 2)),
            "rice_water_management": choice(["continuous_flooding", "intermittent_flooding", "dry_cultivation"]),
            "fertilizer_type": choice(["synthetic", "organic", "none"]),
            "fertilizer_applied_kg": maybe_zero(round(uniform(0, 20), 2)),
        }
    elif sector == "ippu":
        return {
            "sector": sector,
            "cement_produced_tonnes": maybe_zero(round(uniform(0, 50), 2)),
            "lime_produced_tonnes": maybe_zero(round(uniform(0, 10), 2)),
            "steel_produced_tonnes": maybe_zero(round(uniform(0, 20), 2)),
            "refrigerant_consumed_kg": maybe_zero(round(uniform(0, 10), 2)),
            "solvent_used_liters": maybe_zero(round(uniform(0, 100), 2)),
            "other_process_emissions_CO2e_tonnes": maybe_zero(round(uniform(0, 5), 2)),
        }

def estimate_emissions(data: dict) -> float:
    sector = data.get("sector")
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

    co2e = 0.0

    if sector == "energy":
        co2e += data.get("electricity_consumed_kwh", 0) * ef["electricity"]
        co2e += data.get("lpg_used_kg", 0) * ef["lpg"]
        co2e += data.get("kerosene_used_liters", 0) * ef["kerosene"]
        co2e += data.get("firewood_used_kg", 0) * ef["firewood"]
        co2e += data.get("diesel_used_liters", 0) * ef["diesel"]
        co2e += data.get("gasoline_used_liters", 0) * ef["gasoline"]
        co2e += data.get("coal_used_kg", 0) * ef["coal"]

    elif sector == "transport":
        vehicles = data.get("number_of_vehicles", 0)
        distance = data.get("distance_travelled_daily_km", 0)
        freq = data.get("travel_frequency_per_week", 0)
        trips = data.get("trips_per_day", 0)
        fuel_type = data.get("fuel_type", "diesel").lower()
        fuel_ef = ef.get(fuel_type, 2.0)
        co2e = vehicles * distance * freq * trips * fuel_ef

    elif sector == "waste":
        waste = data.get("waste_generated_kg_per_month", 0)
        organic = data.get("organic_fraction_percent", 0)
        method = data.get("waste_disposal_method", "landfill")
        methane_capture = data.get("methane_capture", False)
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
            base_ef *= 0.5
        co2e = waste * (organic / 100.0) * base_ef

    elif sector == "agriculture":
        co2e = (
            data.get("number_of_cattle", 0) * 912.5 +
            data.get("number_of_carabao", 0) * 730 +
            data.get("number_of_goats", 0) * 182.5 +
            data.get("number_of_pigs", 0) * 401.5 +
            data.get("number_of_chickens", 0) * 7.3 +
            data.get("fertilizer_applied_kg", 0) * 5.5
        )
        if data.get("rice_paddy_area_hectares", 0) > 0:
            rice_ef = {
                "continuous_flooding": 1200,
                "intermittent_flooding": 800,
                "dry_cultivation": 100
            }
            water_mgmt = data.get("rice_water_management", "continuous_flooding")
            co2e += data["rice_paddy_area_hectares"] * rice_ef.get(water_mgmt, 1200)

    elif sector == "ippu":
        co2e = (
            data.get("cement_produced_tonnes", 0) * 800 +
            data.get("lime_produced_tonnes", 0) * 900 +
            data.get("steel_produced_tonnes", 0) * 1800 +
            data.get("refrigerant_consumed_kg", 0) * 1430 +
            data.get("solvent_used_liters", 0) * 2.0 +
            data.get("other_process_emissions_CO2e_tonnes", 0) * 1000
        )

    return round(co2e, 2)

async def seed_users(n=200):
    if await db.users.count_documents({}) > 0:
        print("Users already seeded. Skipping.")
        return []

    users = []
    used_communities = set()
    now = datetime.now(timezone.utc)

    regions_count = len(REGIONS_AND_CITIES)
    users_per_region = n // regions_count
    extra = n % regions_count

    user_id = 1
    for idx, (region, cities) in enumerate(REGIONS_AND_CITIES):
        count = users_per_region + (1 if idx < extra else 0)
        for _ in range(count):
            city = choice(cities)
            community_type = choice(COMMUNITY_TYPES)
            if community_type == "School":
                community = f"{faker.company()} School"
            elif community_type == "College/University":
                community = f"{faker.company()} University"
            else:
                community = f"{city} {community_type}"

            if community in used_communities:
                continue

            used_communities.add(community)
            user = {
                "username": f"user{user_id:03d}",
                "password": HASHED_PASSWORD,
                "community_type": community_type,
                "community_name": community,
                "region": region,
                "city": city,
                "created_at": now,
                "updated_at": now
            }
            result = await db.users.insert_one(user)
            users.append(result.inserted_id)
            user_id += 1

    print(f"Seeded {len(users)} users.")
    return users

async def seed_ghg_data_for_user(user_id: ObjectId, start_date: datetime, total_weeks: int):
    current_date = start_date
    for _ in range(total_weeks):
        if random() > 0.2:
            sector = choice(SECTORS)
            submission_data = fake_submission(sector)
            submission_data.update({
                "user_id": user_id,
                "created_at": current_date,
                "updated_at": current_date,
                "estimated_co2e_kg": estimate_emissions(submission_data)
            })
            await db.ghg_submissions.insert_one(submission_data)
        current_date += timedelta(weeks=1)

async def seed_ghg_data_for_all_users():
    users = await db.users.find().to_list(None)
    start_date = datetime(2022, 1, 1)
    for user in users:
        await seed_ghg_data_for_user(user["_id"], start_date, WEEKS)
    print("GHG Data Seeding Complete.")

async def main():
    await seed_users(200)
    await seed_ghg_data_for_all_users()

if __name__ == "__main__":
    asyncio.run(main())
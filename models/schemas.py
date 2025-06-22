from pydantic import BaseModel, Field
from typing import Optional, Literal, List


# --- Auth Models (unchanged) ---
class UserRegistration(BaseModel):
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=6)
    community_type: Optional[str] = None
    community_name: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    id: str
    username: str
    community_type: Optional[str]
    community_name: Optional[str]
    region: Optional[str]
    city: Optional[str]


class TokenResponse(BaseModel):
    token: str
    user: UserInfo


class UserUpdate(BaseModel):
    community_type: Optional[str] = None
    community_name: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None

    class Config:
        extra = "forbid"


# --- Sector Data Models ---

# Energy Sector
class GHGSubmissionEnergy(BaseModel):
    sector: Literal["energy"] = "energy"
    electricity_consumed_kwh: Optional[float] = Field(0.0, ge=0, description="Electricity consumed (kWh)")
    lpg_used_kg: Optional[float] = Field(0.0, ge=0, description="LPG used (kg)")
    kerosene_used_liters: Optional[float] = Field(0.0, ge=0, description="Kerosene used (liters)")
    firewood_used_kg: Optional[float] = Field(0.0, ge=0, description="Firewood used (kg)")
    diesel_used_liters: Optional[float] = Field(0.0, ge=0, description="Diesel used (liters)")
    gasoline_used_liters: Optional[float] = Field(0.0, ge=0, description="Gasoline used (liters)")
    coal_used_kg: Optional[float] = Field(0.0, ge=0, description="Coal used (kg)")


# Transport Sector
class GHGSubmissionTransport(BaseModel):
    sector: Literal["transport"] = "transport"
    vehicle_type: Optional[Literal[
        "private_car", "motorcycle", "jeepney", "tricycle", "bus", "others"
    ]] = None
    fuel_type: Optional[Literal[
        "gasoline", "diesel", "electric", "cng", "others"
    ]] = None
    number_of_vehicles: Optional[int] = Field(0, ge=0, description="Number of vehicles")
    distance_travelled_daily_km: Optional[float] = Field(0.0, ge=0, description="Distance travelled daily (km)")
    travel_frequency_per_week: Optional[int] = Field(0, ge=0, description="Travel frequency per week")
    trips_per_day: Optional[int] = Field(0, ge=0, description="Number of trips per day")


# Waste Sector
class GHGSubmissionWaste(BaseModel):
    sector: Literal["waste"] = "waste"
    waste_generated_kg_per_month: Optional[float] = Field(0.0, ge=0, description="Total waste generated (kg/month)")
    organic_fraction_percent: Optional[float] = Field(0.0, ge=0, le=100, description="Organic fraction of waste (%)")
    waste_disposal_method: Optional[Literal[
        "landfill", "open_dumping", "composting", "recycling", "incineration", "others"
    ]] = None
    methane_capture: Optional[bool] = False


# Agriculture Sector
class GHGSubmissionAgriculture(BaseModel):
    sector: Literal["agriculture"] = "agriculture"
    # Livestock counts
    number_of_cattle: Optional[int] = Field(0, ge=0, description="Number of cattle (beef/dairy)")
    number_of_carabao: Optional[int] = Field(0, ge=0, description="Number of carabao (water buffalo)")
    number_of_goats: Optional[int] = Field(0, ge=0, description="Number of goats")
    number_of_pigs: Optional[int] = Field(0, ge=0, description="Number of pigs")
    number_of_chickens: Optional[int] = Field(0, ge=0, description="Number of chickens")

    manure_management: Optional[Literal[
        "dry_lot", "pasture", "lagoon", "composting", "others", "none"
    ]] = None

    rice_paddy_area_hectares: Optional[float] = Field(0.0, ge=0, description="Area of rice paddies (hectares)")
    rice_water_management: Optional[Literal[
        "continuous_flooding", "intermittent_flooding", "dry_cultivation", "others"
    ]] = None

    fertilizer_type: Optional[Literal["synthetic", "organic", "none", "others"]] = "others"
    fertilizer_applied_kg: Optional[float] = Field(0.0, ge=0, description="Amount of fertilizer applied (kg)")


# IPPU Sector
class GHGSubmissionIPPU(BaseModel):
    sector: Literal["ippu"] = "ippu"
    cement_produced_tonnes: Optional[float] = Field(0.0, ge=0, description="Cement produced (tonnes)")
    lime_produced_tonnes: Optional[float] = Field(0.0, ge=0, description="Lime produced (tonnes)")
    steel_produced_tonnes: Optional[float] = Field(0.0, ge=0, description="Steel produced (tonnes)")
    refrigerant_consumed_kg: Optional[float] = Field(0.0, ge=0, description="Refrigerants consumed (kg)")
    solvent_used_liters: Optional[float] = Field(0.0, ge=0, description="Solvents used (liters)")
    other_process_emissions_CO2e_tonnes: Optional[float] = Field(0.0, ge=0, description="Other process emissions (CO2e tonnes)")


# Union of all sector submissions
GHGSubmission = Optional[
    GHGSubmissionEnergy
    | GHGSubmissionTransport
    | GHGSubmissionWaste
    | GHGSubmissionAgriculture
    | GHGSubmissionIPPU
]

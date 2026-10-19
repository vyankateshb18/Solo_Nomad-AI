"""Typed domain schemas and state representations for Solo Travel Intelligence Platform."""
from datetime import date
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator


class TravelStyle(str, Enum):
    CHEAPEST = "cheapest"
    BALANCED = "balanced"
    COMFORT_BUDGET = "comfort_budget"


class UserTravelRequest(BaseModel):
    """Validated input requirements from the solo traveller."""
    origin: str = Field(..., min_length=2, max_length=100, description="Source city or station")
    destination: str = Field(..., min_length=2, max_length=100, description="Target destination")
    duration_days: int = Field(default=3, ge=1, le=14, description="Trip duration in days")
    total_budget_inr: float = Field(..., gt=0, description="Total budget in Indian Rupees")
    travel_style: TravelStyle = Field(default=TravelStyle.BALANCED)
    interests: List[str] = Field(default_factory=list, description="Specific interests (e.g. food, hiking, heritage)")
    
    # Solo Traveler specific preferences
    allow_overnight_travel: bool = Field(default=True, description="Willingness to take overnight trains or buses to save accommodation costs")
    hostel_preference: bool = Field(default=True, description="Prefer social backpacker hostels")
    require_female_dorm: bool = Field(default=False, description="Prefer female-only dormitories where available")
    departure_date: Optional[date] = Field(default=None, description="Trip departure date if known")

    @field_validator("origin", "destination")
    @classmethod
    def clean_text_field(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Location string cannot be empty or whitespace only.")
        return cleaned

    @model_validator(mode="after")
    def validate_budget_feasibility(self) -> "UserTravelRequest":
        # Basic sanity check: Minimum realistic budget per day for solo travel in INR
        min_daily_budget = 300.0  # Absolute minimum survival baseline (INR)
        required_minimum = self.duration_days * min_daily_budget
        if self.total_budget_inr < required_minimum:
            raise ValueError(
                f"Budget of ₹{self.total_budget_inr:,.0f} is not feasible for a {self.duration_days}-day trip. "
                f"Minimum realistic baseline is ₹{required_minimum:,.0f} (₹{min_daily_budget:.0f}/day)."
            )
        return self


class TransportType(str, Enum):
    TRAIN = "train"
    BUS = "bus"
    FLIGHT = "flight"
    METRO_LOCAL = "metro_local"


class TransportOption(BaseModel):
    """Structured representation of a transit option."""
    mode: TransportType
    provider_or_operator: str
    identifier: Optional[str] = Field(default=None, description="Train number, Flight code, Bus route")
    departure_station: str
    arrival_station: str
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    duration_hours: Optional[float] = None
    fare_inr: float = Field(..., ge=0)
    indicative_only: bool = Field(default=True, description="True if fare is an estimate or indicative timetable")
    source_attribution: str = Field(default="Estimator", description="API feed, verified schedule or provider name")


class HostelOption(BaseModel):
    """Structured hostel recommendation."""
    name: str
    location_area: str
    price_per_night_inr: float = Field(..., ge=0)
    rating: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    review_count: Optional[int] = Field(default=None, ge=0)
    has_female_dorm: Optional[bool] = None
    social_atmosphere_note: Optional[str] = None
    source_url_or_note: Optional[str] = None


class TripBudgetBreakdown(BaseModel):
    """Deterministic budget calculation."""
    transport_total_inr: float = Field(default=0.0, ge=0)
    accommodation_total_inr: float = Field(default=0.0, ge=0)
    food_total_inr: float = Field(default=0.0, ge=0)
    attractions_and_activities_inr: float = Field(default=0.0, ge=0)
    local_transit_inr: float = Field(default=0.0, ge=0)
    contingency_buffer_inr: float = Field(default=0.0, ge=0)

    @property
    def grand_total_inr(self) -> float:
        return (
            self.transport_total_inr
            + self.accommodation_total_inr
            + self.food_total_inr
            + self.attractions_and_activities_inr
            + self.local_transit_inr
            + self.contingency_buffer_inr
        )


class SoloTravelState(BaseModel):
    """Complete shared state carried across workflow stages."""
    request: UserTravelRequest
    transport_candidates: List[TransportOption] = Field(default_factory=list)
    hostel_candidates: List[HostelOption] = Field(default_factory=list)
    budget_breakdown: Optional[TripBudgetBreakdown] = None
    itinerary_markdown: Optional[str] = None
    execution_warnings: List[str] = Field(default_factory=list)
    is_verified: bool = False
    human_approved: bool = False

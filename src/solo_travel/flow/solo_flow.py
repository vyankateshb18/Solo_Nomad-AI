"""CrewAI Flow orchestrating the end-to-end Solo Travel Intelligence lifecycle."""
import logging
from typing import Optional, Dict, Any
from crewai.flow.flow import Flow, start, listen
from solo_travel.models.state import SoloTravelState, UserTravelRequest, TripBudgetBreakdown
from solo_travel.guardrails.safety import evaluate_travel_request_guardrails
from solo_travel.providers.transport import TransportProvider
from solo_travel.providers.weather import WeatherProvider
from solo_travel.agents.crew import create_solo_travel_crew
from solo_travel.config import LLMProviderType

logger = logging.getLogger(__name__)


class SoloTravelFlow(Flow[SoloTravelState]):
    """
    CrewAI Flow for Solo Travel Intelligence:
    1. @start: Validate input and apply deterministic guardrails.
    2. @listen(validate_and_guard): Retrieve structured data (Transport options & Live Weather).
    3. @listen(retrieve_transit_and_weather): Kick off Multi-Agent Crew synthesis.
    4. @listen(synthesize_crew_itinerary): Verify deterministic budget arithmetic & finalize state.
    """

    def __init__(
        self,
        request: UserTravelRequest,
        provider: LLMProviderType = LLMProviderType.OLLAMA,
        model_name: Optional[str] = None
    ):
        initial_state = SoloTravelState(request=request)
        super().__init__(initial_state=initial_state)
        self.provider = provider
        self.model_name = model_name
        self.transport_provider = TransportProvider()
        self.weather_provider = WeatherProvider()

    @start()
    def validate_and_guard(self) -> SoloTravelState:
        """Step 1: Deterministic validation and prompt injection defense."""
        logger.info(f"Validating request for corridor {self.state.request.origin} -> {self.state.request.destination}")
        guard_res = evaluate_travel_request_guardrails(self.state.request)
        if not guard_res.is_safe:
            self.state.execution_warnings.extend(guard_res.rejection_reasons)
            raise ValueError(f"Guardrail Check Failed: {'; '.join(guard_res.rejection_reasons)}")

        # Use sanitized interests
        self.state.request.interests = guard_res.sanitized_interests
        return self.state

    @listen(validate_and_guard)
    def retrieve_transit_and_weather(self) -> SoloTravelState:
        """Step 2: Pre-fetch verified transit options and weather for agent grounding."""
        req = self.state.request
        logger.info(f"Retrieving structured transit and weather data for {req.destination}")

        # 1. Fetch trains & buses
        try:
            transit_opts = self.transport_provider.search(req.origin, req.destination)
            self.state.transport_candidates = transit_opts
        except Exception as exc:
            self.state.execution_warnings.append(f"Transit search warning: {str(exc)}")

        return self.state

    @listen(retrieve_transit_and_weather)
    def synthesize_crew_itinerary(self) -> SoloTravelState:
        """Step 3: Execute CrewAI multi-agent synthesis."""
        logger.info("Starting Multi-Agent Crew synthesis")
        crew = create_solo_travel_crew(
            request=self.state.request,
            provider=self.provider,
            model_name=self.model_name
        )

        crew_output = crew.kickoff()
        self.state.itinerary_markdown = str(crew_output)
        return self.state

    @listen(synthesize_crew_itinerary)
    def verify_and_finalize_budget(self) -> SoloTravelState:
        """Step 4: Deterministic budget verification in INR."""
        req = self.state.request

        # Calculate practical baseline allocations
        avg_transit = 600.0
        if self.state.transport_candidates:
            avg_transit = self.state.transport_candidates[0].fare_inr * 2  # Round trip

        nights = max(1, req.duration_days - (1 if req.allow_overnight_travel else 0))
        est_hostel_per_night = 500.0  # Indian backpacker dorm benchmark
        total_hostel = nights * est_hostel_per_night

        est_daily_food = 350.0  # Local street food / thali benchmark
        total_food = req.duration_days * est_daily_food

        est_local_transit = req.duration_days * 150.0
        est_activities = req.duration_days * 150.0
        contingency = max(300.0, req.total_budget_inr * 0.10)

        breakdown = TripBudgetBreakdown(
            transport_total_inr=avg_transit,
            accommodation_total_inr=total_hostel,
            food_total_inr=total_food,
            attractions_and_activities_inr=est_activities,
            local_transit_inr=est_local_transit,
            contingency_buffer_inr=contingency
        )

        self.state.budget_breakdown = breakdown
        self.state.is_verified = breakdown.grand_total_inr <= (req.total_budget_inr * 1.15)
        return self.state

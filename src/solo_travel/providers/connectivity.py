"""Local connectivity and last-mile transit estimator for solo travellers."""
from typing import Dict, Any


class LocalConnectivityEstimator:
    """
    Calculates realistic last-mile transit costs and modes:
    - Railway station / bus terminal to hostel (shared auto / e-rickshaw vs. private cab)
    - Daily local transit between clustered sights
    """

    @staticmethod
    def estimate_connectivity(
        destination: str,
        duration_days: int,
        arrival_terminal_type: str = "railway_station"
    ) -> Dict[str, Any]:
        dest_clean = destination.strip().lower()

        # Destination-specific local transit traits
        if "varanasi" in dest_clean:
            return {
                "terminal_transfer_mode": "Shared E-Rickshaw / Auto from Cantt to Godowlia/Assi Ghat",
                "transfer_cost_one_way_inr": 40.0,
                "recommended_daily_transit": "Walking along ghats + shared battery rickshaws (₹20-30/hop)",
                "daily_transit_cost_inr": 100.0,
                "total_local_transit_inr": (40.0 * 2) + (duration_days * 100.0),
                "insider_advice": "Never hire prepaid private autos inside the station boundary; walk 100m to the main road for shared e-rickshaws to Godowlia."
            }

        elif "rishikesh" in dest_clean:
            return {
                "terminal_transfer_mode": "Shared Vikram / Auto from Haridwar/Rishikesh bus stand to Tapovan",
                "transfer_cost_one_way_inr": 60.0,
                "recommended_daily_transit": "Walking across Ram/Laxman Jhula footbridges + rented scooter (₹350/day) or shared Vikram",
                "daily_transit_cost_inr": 150.0,
                "total_local_transit_inr": (60.0 * 2) + (duration_days * 150.0),
                "insider_advice": "Tapovan and Laxman Jhula are completely pedestrian-friendly. Avoid cabs due to narrow hill lanes."
            }

        elif "hampi" in dest_clean:
            return {
                "terminal_transfer_mode": "Local KSRTC bus or shared auto from Hosapete station to Hampi Bazaar",
                "transfer_cost_one_way_inr": 35.0,
                "recommended_daily_transit": "Bicycle rental (₹100/day) or Moped across Sanapur Lake (₹350/day)",
                "daily_transit_cost_inr": 120.0,
                "total_local_transit_inr": (35.0 * 2) + (duration_days * 120.0),
                "insider_advice": "Renting a bicycle at Hampi Bazaar is the cheapest and most scenic way to explore the sacred center ruins."
            }

        else:
            return {
                "terminal_transfer_mode": "Shared auto / Metro link from main terminal to city center",
                "transfer_cost_one_way_inr": 50.0,
                "recommended_daily_transit": "Public bus / Metro / Shared rickshaws",
                "daily_transit_cost_inr": 120.0,
                "total_local_transit_inr": (50.0 * 2) + (duration_days * 120.0),
                "insider_advice": "Use shared autos or local metro apps instead of hailing private taxis."
            }

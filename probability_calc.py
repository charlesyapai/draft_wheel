# draft_wheel/probability_calc.py
import math
from typing import Dict, List, Any

def logistic_ratio_weight(ratio: float, midpoint: float, slope: float) -> float:
    """
    Returns a value in (0, 1) using a logistic function on the ratio of:
        abs(player_mmr - ideal_mmr) / ideal_mmr.

    - ratio:    (|playerMMR - idealMMR| / idealMMR).
    - midpoint: The ratio at which output = 0.5.
    - slope:    Steepness of the S-curve around the midpoint.
    """
    return 1.0 / (1.0 + math.exp(slope * (ratio - midpoint)))

def compute_probabilities(
    team_data: Dict[str, Any],
    role: str,
    all_players: Dict[str, Dict[str, Any]],
    players_in_role: List[str],
    global_average_mmr: float,
    base_randomness: float,
    team_size: int,
    role_preference_weights: Dict[int, float],
    logistic_midpoint: float,
    logistic_slope: float,
    blend_alpha: float = 0.7
) -> Dict[str, float]:
    """
    Compute final probabilities for each available player in `players_in_role`.

    Incorporates:
      - The number of picks left (TEAM_SIZE - current_count),
      - A ratio-based logistic function for MMR differences,
      - Role preference weighting,
      - Base randomness / uniform portion,
      - Optional blend of MMR weighting & preference factor.

    Parameters:
    -----------
    team_data : dict
        Must include "players" (list) and "average_mmr".
    role : str
        The role we are drafting for.
    all_players : dict
        Mapping player_name -> { "mmr": float/int, "roles": [(roleName, priority), ...] }
    players_in_role : list
        Which players can play this role (by name).
    global_average_mmr : float
        The overall average MMR in the pool, e.g. ~3600 or 5946, etc.
    base_randomness : float
        Fraction of probability allocated uniformly among all candidates (0 <= base_randomness < 1).
    team_size : int
        How many total players end up on this team (e.g. 5).
    role_preference_weights : dict
        e.g. {1: 0.9, 2: 0.6, 3: 0.1} indicating how strongly a player prefers role #1, #2, #3.
    logistic_midpoint : float
        For the ratio-based logistic, ratio at which output ~ 0.5.
    logistic_slope : float
        How steep the logistic S-curve is around midpoint.
    blend_alpha : float
        If 1.0, we multiply (mmr_weight * pref_factor).
        If <1.0, we blend them as alpha*mmr_weight + (1 - alpha)*pref_factor.

    Returns:
    --------
    A dict: { player_name: probability }
    """

    # Number of players already in the team
    current_n = len(team_data["players"])
    # Current total MMR (approx)
    current_sum = team_data["average_mmr"] * current_n

    # How many picks remain for this team
    picks_left = team_size - current_n
    if picks_left <= 0:
        return {}

    # Total MMR we want for a 'balanced' final team
    desired_total_for_full_team = team_size * global_average_mmr

    # MMR budget for the remaining picks
    remaining_mmr = desired_total_for_full_team - current_sum

    # Ideal MMR for *this next pick* if we want to stay on track
    ideal_mmr = remaining_mmr / picks_left

    raw_weights = {}
    for player_name in players_in_role:
        info = all_players[player_name]
        pmmr = info["mmr"]

        # Get how strongly the player wants this role (1st/2nd/3rd preference)
        pref_factor = get_role_preference_factor(info, role, role_preference_weights)
        if pref_factor <= 0:
            # skip if not in top preferences
            continue

        # Calculate ratio: how far off from ideal, relative to ideal
        diff = abs(pmmr - ideal_mmr)
        if ideal_mmr <= 0:
            # fallback if something is off or ideal_mmr is zero
            ratio = 99999.0
        else:
            ratio = diff / ideal_mmr

        # Convert ratio to [0..1] with logistic
        mmr_weight = logistic_ratio_weight(ratio, logistic_midpoint, logistic_slope)

        # Combine with role preference factor
        if abs(blend_alpha - 1.0) < 1e-8:
            final_w = mmr_weight * pref_factor
        else:
            # Weighted blend approach
            final_w = blend_alpha * mmr_weight + (1 - blend_alpha) * pref_factor

        raw_weights[player_name] = final_w

    # If no valid players remain
    if not raw_weights:
        return {}

    # Sum up all weights
    total_w = sum(raw_weights.values())
    if total_w <= 0:
        # fallback to uniform distribution
        N = len(raw_weights)
        return {p: 1.0 / N for p in raw_weights}

    # Convert raw weights into probabilities
    N = len(raw_weights)
    final_probs = {}
    for p, w in raw_weights.items():
        # Weighted portion relative to total
        mmr_portion = (w / total_w) * (1 - base_randomness)
        # Uniform portion
        uniform_portion = base_randomness / N
        final_probs[p] = mmr_portion + uniform_portion

    # Minor normalization pass
    s = sum(final_probs.values())
    if abs(s - 1.0) > 1e-8:
        for k in final_probs:
            final_probs[k] /= s

    return final_probs


def get_role_preference_factor(
    player_info: Dict[str, Any],
    role: str,
    preference_weights: Dict[int, float]
) -> float:
    """
    Retrieve the weighting factor associated with this player's priority for 'role'.
    E.g. preference_weights = {1: 0.9, 2: 0.6, 3: 0.1}
    Returns 0.0 if the role isn't found or is out of top 3 priorities.
    """
    roles_list = player_info.get("roles", [])
    for (rname, prio) in roles_list:
        if rname == role:
            return preference_weights.get(prio, 0.0)
    return 0.0

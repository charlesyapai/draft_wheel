# draft_wheel/probability_calc.py

from typing import Dict, List, Any

def compute_probabilities(
    team_data: Dict[str, Any],
    role: str,
    all_players: Dict[str, Dict[str, Any]],
    players_in_role: List[str],
    global_average_mmr: float,
    base_randomness: float
) -> Dict[str, float]:
    """
    Compute final probabilities for each available player in `players_in_role`, factoring in:
      - role priority weighting
      - how close the player's MMR is to the ideal MMR for the team
      - base randomness
    """
    n = len(team_data["players"])
    current_sum = team_data["average_mmr"] * n
    # Ideal MMR => (global_average_mmr * (n+1)) - sum_of_current
    ideal_mmr = (global_average_mmr * (n + 1)) - current_sum

    raw_weights = {}
    for p in players_in_role:
        info = all_players[p]
        pmmr = info["mmr"]
        factor = get_role_preference_factor(info, role)  # see function below
        if factor <= 0:
            # if the player doesn't have 'role' in top 3, skip
            continue

        diff = abs(pmmr - ideal_mmr)
        w = 1.0 / (diff + 1.0)
        final_w = w * factor
        raw_weights[p] = final_w

    if not raw_weights:
        return {}

    total_w = sum(raw_weights.values())
    if total_w <= 0:
        # fallback: uniform
        N = len(raw_weights)
        return {p: 1.0 / N for p in raw_weights}

    N = len(raw_weights)
    final_probs = {}
    for p, w in raw_weights.items():
        mmr_part = (w / total_w) * (1 - base_randomness)
        uniform_part = base_randomness / N
        final_probs[p] = mmr_part + uniform_part

    # minor normalization
    s = sum(final_probs.values())
    if abs(s - 1.0) > 1e-8:
        for k in final_probs:
            final_probs[k] /= s

    return final_probs


def get_role_preference_factor(player_info: Dict[str, Any], role: str) -> float:
    """
    If player_info["roles"] = [ (roleName, priority), ... ]
    then:
      priority=1 => factor=1.0
      priority=2 => factor=0.66
      priority=3 => factor=0.33
    If role not found, factor=0 => skip
    """
    roles_list = player_info.get("roles", [])
    for (rname, prio) in roles_list:
        if rname == role:
            if prio == 1:
                return 0.9
            elif prio == 2:
                return 0.6
            elif prio == 3:
                return 0.1
    return 0.0

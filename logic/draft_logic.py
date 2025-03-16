# draft_wheel/logic/draft_logic.py

import csv
import os
from typing import Dict, List, Any, Optional

from  probability_calc import compute_probabilities

class DraftLogic:
    """
    Manages:
      - players
      - teams
      - saving/loading state
      - calling compute_probabilities(...) for each spin
    """

    def __init__(self, config: dict):
        self.config = config

        # config values
        self.global_average_mmr = config.get("global_average_mmr", 6000)
        self.player_data_csv = config.get("player_data_csv", "players_data.csv")
        self.roles = config.get("roles", ["carry","mid","offlane","soft_support","hard_support"])
        self.randomness_levels = config.get("randomness_levels", {})
        
        # Example: read logistic settings safely
        logistic_cfg = config.get("logistic_settings", {})
        self.logistic_midpoint = logistic_cfg.get("midpoint", 1500.0)
        self.logistic_slope = logistic_cfg.get("slope", 0.002)
        self.blend_alpha = logistic_cfg.get("blend_alpha", 0.5)

        # role -> number for display
        self.role_to_number = {
            "carry":"1",
            "mid":"2",
            "offlane":"3",
            "soft_support":"4",
            "hard_support":"5"
        }

        # data structures
        self.players_by_role: Dict[str, List[str]] = {r:[] for r in self.roles}
        # all_players[name] = {"mmr":int, "roles":[(roleName,priority), ...]}
        self.all_players: Dict[str,Dict[str,Any]] = {}
        # teams[team_id] = {
        #   "players":[(playerName, roleAssigned)],
        #   "average_mmr":float
        # }
        self.teams: Dict[str,Dict[str,Any]] = {}
        # draft history => for undo
        self.draft_history: List[Dict[str,Any]] = []

        self.load_player_data()

        # if config defines default_teams
        default_teams = config.get("default_teams", [])
        for t in default_teams:
            self.register_team(t)

    def load_player_data(self):
        self.all_players.clear()
        for r in self.players_by_role:
            self.players_by_role[r].clear()
        self.teams.clear()
        self.draft_history.clear()

        try:
            with open(self.player_data_csv, "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    name = row["name"].strip()
                    mmr = int(row["mmr"])
                    roles_str = row["roles"].strip()  # e.g. carry(1)|mid(2)

                    parsed_roles = self._parse_roles_with_priority(roles_str)
                    self.all_players[name] = {"mmr": mmr, "roles": parsed_roles}

                    # add to players_by_role
                    for (rname, prio) in parsed_roles:
                        if rname not in self.players_by_role:
                            self.players_by_role[rname] = []
                        self.players_by_role[rname].append(name)

            print(f"[LOAD] Player data loaded from '{self.player_data_csv}'.")
        except FileNotFoundError:
            print(f"[ERROR] CSV not found at '{self.player_data_csv}'.")
        except Exception as e:
            print(f"[ERROR] Could not load player data: {e}")

    def _parse_roles_with_priority(self, roles_str: str) -> List[tuple]:
        """
        Convert "carry(1)|mid(2)|offlane(3)" => [("carry",1),("mid",2),("offlane",3)]
        If no parentheses => priority=1
        """
        if not roles_str:
            return []
        parts = roles_str.split("|")
        result = []
        for part in parts:
            part = part.strip()
            if "(" in part and ")" in part:
                idx1 = part.index("(")
                idx2 = part.index(")")
                rname = part[:idx1].strip()
                prio_str = part[idx1+1:idx2].strip()
                try:
                    prio = int(prio_str)
                except:
                    prio=1
                result.append((rname, prio))
            else:
                result.append((part, 1))
        return result

    def register_team(self, team_id: str):
        if team_id not in self.teams:
            self.teams[team_id] = {
                "players": [],
                "average_mmr": 0.0
            }

    def get_teams_data(self) -> Dict[str, Dict[str,Any]]:
        return self.teams

    def get_unfilled_roles_for_team(self, team_id: str) -> List[str]:
        if team_id not in self.teams:
            return []
        assigned=set()
        for (p, role) in self.teams[team_id]["players"]:
            if role in self.role_to_number:
                assigned.add(role)
        all_r=set(self.players_by_role.keys())
        return sorted(list(all_r - assigned))

    def compute_probabilities(self, team_id: str, role: str) -> Dict[str,float]:
        if team_id not in self.teams:
            return {}
        if role not in self.players_by_role:
            return {}

        team_data = self.teams[team_id]
        players_in_role = self.players_by_role[role]
        if not players_in_role:
            return {}

        n = len(team_data["players"])
        base_rand = self.randomness_levels.get(n, 0.30)

        return compute_probabilities(
            team_data=team_data,
            role=role,
            all_players=self.all_players,
            players_in_role=players_in_role,
            global_average_mmr=self.global_average_mmr,
            base_randomness=base_rand,
            team_size=self.config["team_size"],

            # Extended config:
            role_preference_weights=self.config["role_preference_weights"],
            logistic_midpoint=self.config["logistic_settings"]["midpoint"],
            logistic_slope=self.config["logistic_settings"]["slope"],
            blend_alpha=self.config["logistic_settings"]["blend_alpha"]
        )

    def pick_player_from_position(self, team_id:str, role:str, position_pct:float, segments:List[tuple]) -> Optional[str]:
        # segments => [(playerName, startPct, endPct)]
        for (p, startp, endp) in segments:
            if position_pct>=startp and position_pct<endp:
                self._remove_player(p)
                self._assign_to_team(team_id, p, role)
                self.draft_history.append({
                    "team_id":team_id,
                    "player_name":p,
                    "role":role
                })
                return p
        return None

    def _remove_player(self, p:str):
        for rlist in self.players_by_role.values():
            if p in rlist:
                rlist.remove(p)

    def _assign_to_team(self, team_id:str, pname:str, role:str):
        tdata=self.teams[team_id]
        tdata["players"].append((pname, role))
        mmr_sum = sum(self.all_players[x]["mmr"] for (x,rr) in tdata["players"])
        tdata["average_mmr"] = mmr_sum/len(tdata["players"])

    def undo_last_pick(self):
        if not self.draft_history:
            return None
        last = self.draft_history.pop()
        tid = last["team_id"]
        pname = last["player_name"]
        role = last["role"]

        tdata=self.teams[tid]
        if (pname,role) in tdata["players"]:
            tdata["players"].remove((pname,role))

        if tdata["players"]:
            mmr_sum=sum(self.all_players[x]["mmr"] for (x,rr) in tdata["players"])
            tdata["average_mmr"]= mmr_sum/len(tdata["players"])
        else:
            tdata["average_mmr"]=0

        # restore
        for (rname,prio) in self.all_players[pname]["roles"]:
            if rname not in self.players_by_role:
                self.players_by_role[rname]=[]
            self.players_by_role[rname].append(pname)
        return pname

    def get_players_by_role(self) -> Dict[str,List[str]]:
        res={}
        for r, plist in self.players_by_role.items():
            # sort by MMR desc
            s = sorted(plist, key=lambda x: self.all_players[x]["mmr"], reverse=True)
            res[r]=s
        return res

    # Captain
    def add_captain_to_team(self, team_id:str, captain_name:str, captain_mmr:int):
        if team_id not in self.teams:
            self.register_team(team_id)
        if captain_name not in self.all_players:
            self.all_players[captain_name]={"mmr":captain_mmr,"roles":[]}

        self.teams[team_id]["players"].append((captain_name,"(Captain)"))
        mmr_sum= sum(self.all_players[pn]["mmr"] for (pn,r) in self.teams[team_id]["players"])
        count= len(self.teams[team_id]["players"])
        self.teams[team_id]["average_mmr"]= mmr_sum/count if count>0 else 0

        self.draft_history.append({
            "team_id":team_id,
            "player_name":captain_name,
            "role":"(Captain)"
        })

    # stats for charts
    def get_mmr_bucket_stats(self):
        # same logic you had before
        buckets={
            "2k-3.5k":{"min":2000,"max":3500,"core_only":0,"support_only":0,"mixed":0},
            "3.5k-5k":{"min":3501,"max":5000,"core_only":0,"support_only":0,"mixed":0},
            "5k-6.5k":{"min":5001,"max":6500,"core_only":0,"support_only":0,"mixed":0},
            "6.5k-8k":{"min":6501,"max":8000,"core_only":0,"support_only":0,"mixed":0},
            ">8000":  {"min":8001,"max":999999,"core_only":0,"support_only":0,"mixed":0}
        }
        core_roles={"carry","mid","offlane"}
        supp_roles={"soft_support","hard_support"}

        assigned=set()
        for tid,data in self.teams.items():
            for (p,r) in data["players"]:
                assigned.add(p)

        for pname,info in self.all_players.items():
            if pname in assigned:
                continue
            mmr=info["mmr"]
            roles_set=set(rn for (rn,prio) in info["roles"])

            bucket_key=None
            for k,binfo in buckets.items():
                if binfo["min"] <= mmr <= binfo["max"]:
                    bucket_key=k
                    break
            if not bucket_key:
                continue

            if not roles_set:
                buckets[bucket_key]["mixed"]+=1
                continue

            is_core= roles_set.issubset(core_roles)
            is_supp= roles_set.issubset(supp_roles)
            if is_core:
                buckets[bucket_key]["core_only"]+=1
            elif is_supp:
                buckets[bucket_key]["support_only"]+=1
            else:
                buckets[bucket_key]["mixed"]+=1

        final_stats={}
        for k,d in buckets.items():
            final_stats[k]={
                "core_only":d["core_only"],
                "support_only":d["support_only"],
                "mixed":d["mixed"]
            }
        return final_stats

    def get_role_distribution_stats(self):
        res={}
        for r, plist in self.players_by_role.items():
            if not plist:
                res[r]=(0,0)
                continue
            mmrs=[ self.all_players[p]["mmr"] for p in plist ]
            count=len(mmrs)
            avg=sum(mmrs)/count if count else 0
            res[r]=(count,avg)
        return res

    # Save/Load
    def save_state(self, remaining_csv="draft_remaining.csv", teams_csv="draft_teams.csv"):
        print("[SAVE] saving state")
        assigned=set()
        for tid,data in self.teams.items():
            for (p,role) in data["players"]:
                assigned.add(p)

        with open(remaining_csv,"w",encoding="utf-8",newline="") as rf:
            writer=csv.DictWriter(rf,fieldnames=["name","mmr","roles"])
            writer.writeheader()
            for p,info in self.all_players.items():
                if p not in assigned:
                    roles_str=self._roles_to_string(info["roles"])
                    writer.writerow({
                        "name":p,
                        "mmr":info["mmr"],
                        "roles":roles_str
                    })

        with open(teams_csv,"w",encoding="utf-8",newline="") as tf:
            flds=["team_id","name","assigned_role","mmr"]
            writer=csv.DictWriter(tf,fieldnames=flds)
            writer.writeheader()
            for tid,data in self.teams.items():
                for (p,assigned_role) in data["players"]:
                    info=self.all_players[p]
                    writer.writerow({
                        "team_id":tid,
                        "name":p,
                        "assigned_role":assigned_role,
                        "mmr":info["mmr"]
                    })

    def _roles_to_string(self, role_list:List[tuple]) -> str:
        """
        Convert [("carry",1),("mid",2)] => "carry(1)|mid(2)"
        """
        parts=[]
        for (rn,prio) in role_list:
            parts.append(f"{rn}({prio})")
        return "|".join(parts)

    def load_state(self, remaining_csv="draft_remaining.csv", teams_csv="draft_teams.csv"):
        print("[LOAD] loading state")
        if not (os.path.exists(remaining_csv) and os.path.exists(teams_csv)):
            print("[ERROR] Missing CSVs for loading.")
            return

        self.all_players.clear()
        for r in self.players_by_role:
            self.players_by_role[r].clear()
        self.teams.clear()
        self.draft_history.clear()

        with open(remaining_csv,"r",encoding="utf-8") as rf:
            rr=csv.DictReader(rf)
            for row in rr:
                name=row["name"].strip()
                mmr=int(row["mmr"])
                roles_str=row["roles"].strip()
                parsed=self._parse_roles_with_priority(roles_str)
                self.all_players[name]={"mmr":mmr,"roles":parsed}
                for (rname,prio) in parsed:
                    if rname not in self.players_by_role:
                        self.players_by_role[rname]=[]
                    self.players_by_role[rname].append(name)

        assigned_data={}
        with open(teams_csv,"r",encoding="utf-8") as tf:
            tr=csv.DictReader(tf)
            for row in tr:
                tid=row["team_id"].strip()
                pname=row["name"].strip()
                assigned_role=row["assigned_role"].strip()
                pmmr=int(row["mmr"])
                if tid not in assigned_data:
                    assigned_data[tid]=[]
                assigned_data[tid].append((pname,assigned_role,pmmr))

        for tid, plist in assigned_data.items():
            self.register_team(tid)
            for (pname, role, pmmr) in plist:
                if pname not in self.all_players:
                    self.all_players[pname]={"mmr":pmmr,"roles":[]}
                # remove from roles
                for rname in self.players_by_role:
                    if pname in self.players_by_role[rname]:
                        self.players_by_role[rname].remove(pname)
                self.teams[tid]["players"].append((pname, role))

        for tid,data in self.teams.items():
            if data["players"]:
                mmr_sum=sum(self.all_players[x]["mmr"] for (x,r) in data["players"])
                data["average_mmr"]= mmr_sum/len(data["players"])
            else:
                data["average_mmr"]=0

        print("[LOAD] done")


    # Displaying MMR stats in UI

    def get_ideal_mmr_for_pick(self, team_id: str, role: str) -> float:
        """
        Return the 'ideal_mmr' for the next pick, based on the ratio-based approach.
        If you already have this logic in 'compute_probabilities', you can store it
        and return it here or replicate the simple formula.
        """
        team_data = self.teams[team_id]
        current_n = len(team_data["players"])
        team_size = self.config.get("team_size", 5)  # e.g. from YAML
        if current_n >= team_size:
            return 0.0

        current_sum = team_data["average_mmr"] * current_n
        desired_total_for_full_team = team_size * self.global_average_mmr
        remaining_mmr = desired_total_for_full_team - current_sum
        picks_left = team_size - current_n
        if picks_left <= 0:
            return 0.0

        ideal_mmr = remaining_mmr / picks_left
        return ideal_mmr

    def get_pool_average_mmr(self) -> float:
        """
        Average MMR of all 'undrafted' players.
        """
        drafted_players = set()
        for tinfo in self.teams.values():
            for (pname, _) in tinfo["players"]:
                drafted_players.add(pname)

        undrafted = [p for p in self.all_players if p not in drafted_players]
        if not undrafted:
            return 0.0

        total = sum(self.all_players[p]["mmr"] for p in undrafted)
        return total / len(undrafted)

    def get_drafted_average_mmr(self) -> float:
        """
        Average MMR of all players currently on teams.
        """
        drafted_list = []
        for tinfo in self.teams.values():
            for (pname, _) in tinfo["players"]:
                drafted_list.append(pname)

        if not drafted_list:
            return 0.0

        total = sum(self.all_players[p]["mmr"] for p in drafted_list)
        return total / len(drafted_list)
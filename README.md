

# Draft Wheel

This is a **Draft Wheel** application that helps randomly allocate players to teams, while partially controlling for each team’s average MMR and player role priorities. It’s originally a **Tkinter-based** (desktop) Python GUI, but can also be adapted for **web** deployment using frameworks like **Streamlit**.

## 1) Features

- **Load** players from a CSV, each specifying up to three preferred roles (with priorities 1/2/3).  
- **Spin** a random selection for a role, factoring in how that player’s MMR fits into the team’s ideal average.  
- **Undo** picks, **save** / **load** partial drafts, and see useful **charts** of unpicked players (role distribution, MMR buckets).  
- **Variable** base randomness depending on how many players are already on the team.

## 2) Installation

### A) Clone the Repository

```bash
git clone https://github.com/charlesyapai/draft_wheel.git
cd YourDraftWheelRepo
```

### B) Install Python Dependencies

You need Python 3.7+ installed. Then install these libraries:

- **Pillow** (for images like the banner)
- **PyYAML** (for reading the config file)
- Possibly others (like NumPy) if your code or probability logic uses them.

You can install them manually:

```bash
pip install Pillow PyYAML
```

Or, if you have a `requirements.txt` that includes these packages:

```bash
pip install -r requirements.txt
```

*(Ensure you do this in a virtual environment or your preferred environment.)*

## 3) Usage (Desktop / Tkinter GUI)

1. **Configure** your data in:
   - `data/players_data.csv` (name, mmr, roles)
   - `data/draft_wheel_configs.yaml` (global MMR, randomness levels, etc.)
2. **Run** the main application:
   ```bash
   python -m draft_wheel.main
   ```
   or
   ```bash
   python draft_wheel/main.py
   ```
3. A **Tkinter** window should open, showing the role list on the left, spin controls in the center, and teams on the right.

### Save / Load

- The “Save” button writes two CSVs: `draft_remaining.csv` (the unpicked players) and `draft_teams.csv` (assigned players).
- The “Load” button reads these CSVs to restore a partial draft state.

## 4) Possible Web Deployment (Optional)

Because this code uses **Tkinter** (desktop GUI), it won’t directly run on GitHub Pages or any static site host. If you’d like a **web** version:

1. **Retain** all the “draft logic” code in `draft_logic.py` and `probability_calc.py`.
2. **Rewrite** or adapt the **GUI** portion using a **web** framework. Example frameworks:
   - **Streamlit** – Easiest to create an interactive web app in pure Python.  
   - **Flask** or **FastAPI** – For more custom control with HTML templates and routes.
3. **Deploy** that web-based version to:
   - **Streamlit Cloud** (if using Streamlit), or
   - Heroku / Render / Railway (if using Flask / FastAPI).

### Short Example (Streamlit)

```bash
pip install streamlit
```

Create a file `app.py`:

```python
import streamlit as st
from draft_wheel.logic.draft_logic import DraftLogic
# from config.loader import ConfigRetrieval  # if using your config loader

def main():
    st.title("Draft Wheel (Web Version)")
    logic = DraftLogic({ ... your config ... })

    # Let user select a team/role
    teams = list(logic.get_teams_data().keys())
    selected_team = st.selectbox("Select Team", teams)

    roles = list(logic.players_by_role.keys())
    selected_role = st.selectbox("Select Role", roles)

    if st.button("Preview"):
        probs = logic.compute_probabilities(selected_team, selected_role)
        for p, pr in probs.items():
            st.write(f"{p}: {pr*100:.1f}%")

if __name__ == "__main__":
    main()
```

Then run locally:

```bash
streamlit run app.py
```

And possibly deploy to [Streamlit Cloud](https://streamlit.io/cloud).

---

## 5) Contributing

1. **Fork** the repo or create a new branch.  
2. Make your improvements (e.g., new probability formulas, role chart visuals).  
3. Submit a **Pull Request** or merge your branch.


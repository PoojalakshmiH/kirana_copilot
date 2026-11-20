# Kirana Copilot — Hackathon Prototype

## Requirements
- Python 3.9+
- pip

## Setup
1. Extract the ZIP.
2. Open the folder in VS Code.
3. Open Terminal in the project folder.
4. Run:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

5. Streamlit will open a local browser tab. If it does not, copy the local URL shown in the terminal.

## Features
- Dashboard summary
- Editable inventory
- Expiry alerts
- Rule-based budget-aware reorder suggestions
- Editable quantities and owner approval
- Demo order history

All data is illustrative. Approval is simulated; no orders are sent.

## Project structure
- `app.py`: prototype application
- `inventory.csv`: example inventory dataset (reference data)
- `logic.py`: standalone reorder logic (reference helper)
- `requirements.txt`: dependencies

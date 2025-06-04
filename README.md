# how to
 - install with uv `uv venv; source .venv/bin/activate; uv sync`
 - install with pip `python -m venv .venv; source .venv/bin/activate; pip install -r requirements.txt` 
 - run server `uvicorn main:app --reload`
 - test `pytest`
 - parallel requets test `python main.py`
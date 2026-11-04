# Armada / Streedagh. Python with numpy + astropy: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
PYTHON ?= .venv/bin/python

.PHONY: worldline sun_moon attribution all

all: worldline sun_moon

# Step 1: Cuéllar's dated chain (seconds)
worldline:
	$(PYTHON) 3_cuellar_worldline/worldline.py

# Step 2: sun and moon against every light signal (about a minute); needs worldline first
sun_moon: worldline
	$(PYTHON) 3_cuellar_worldline/sun_moon.py

# Bayesian attribution of the v3 signal store; NOTE rewrites data/ with a new committed_at timestamp
attribution:
	$(PYTHON) 1_signal_field/attribution_estimator.py

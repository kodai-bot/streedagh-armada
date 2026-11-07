# Armada / Streedagh. Python with numpy + astropy: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
PYTHON ?= .venv/bin/python

.PHONY: worldline sun_moon capacity guns site attribution all

all: worldline sun_moon capacity

# Step 1: Cuéllar's dated chain (seconds)
worldline:
	$(PYTHON) 3_cuellar_worldline/worldline.py

# Step 2: sun and moon against every light signal (about a minute); needs worldline first
sun_moon: worldline
	$(PYTHON) 3_cuellar_worldline/sun_moon.py

# Stepped-castle capacity: recompute and check the §26/§28 tables (seconds)
capacity:
	$(PYTHON) 2_reconstruction/stepped_castle_capacity.py

# Juliana's recovered guns and the Lisbon muster as signals; then re-run attribution
guns:
	$(PYTHON) 1_signal_field/juliana_guns.py
	$(PYTHON) 1_signal_field/attribution_estimator.py

# The site record: one signal_schema v0.4 bundle (JSON), validated by the schema's CLI
SCHEMA ?= ../../Signal_Pipeline/signal_schema
site:
	$(PYTHON) 1_signal_field/site_record/build_site_record.py
	cd $(SCHEMA) && .venv/bin/signal-schema validate --quiet $(CURDIR)/1_signal_field/site_record/streedagh_site.json

# Bayesian attribution of the v3 signal store; NOTE rewrites data/ with a new committed_at timestamp
attribution:
	$(PYTHON) 1_signal_field/attribution_estimator.py

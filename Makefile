# Armada / Streedagh. Python with numpy + astropy: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
PYTHON ?= .venv/bin/python

.PHONY: worldline sun_moon capacity mass site view all

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

# What went to the bottom: layer 1, ordnance and munitions (seconds)
mass:
	$(PYTHON) 1_signal_field/seabed_mass_budget.py

# The site record: one signal_schema v0.4 bundle (JSON), validated by the schema's CLI
SCHEMA ?= ../../Signal_Pipeline/signal_schema
site:
	$(PYTHON) 1_signal_field/site_record/build_site_record.py
	cd $(SCHEMA) && .venv/bin/signal-schema validate --quiet $(CURDIR)/1_signal_field/site_record/streedagh_site.json


# Page data from the site record: output/site_view.json (every value with the id of its record)
view: site
	$(PYTHON) 1_signal_field/site_record/export_view.py

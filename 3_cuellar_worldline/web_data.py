"""
Bundle the worldline results into one JSON file for the web page
("Cuéllar's nights", kodai-bot.github.io/streedagh/).

    .venv/bin/python 3_cuellar_worldline/web_data.py OUT.json

Reads the step-1/step-2 outputs (run `make worldline sun_moon` first) and adds
one thing they don't have: the moon's illumination for every night of the
whole journey, so the overview timeline can show the full lunar rhythm.
Nothing here re-derives a result; it only collects them.
"""

import csv
import datetime as dt
import json
import os
import re
import sys

import warnings

import numpy as np
from astropy.coordinates import get_body, get_sun
from astropy.time import Time

warnings.filterwarnings("ignore", module="erfa")  # 1588 is outside ERFA's leap-second table; harmless here

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WRECK = dt.date(1588, 9, 21)          # day 0 (Gregorian)
FIRST_DAY, LAST_DAY = -50, 385


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def light_tests():
    """Parse sun_moon_report.md: per node, the test and a verdict per allowed date."""
    text = open(os.path.join(HERE, "output", "sun_moon_report.md"), encoding="utf-8").read()
    out = {}
    for block in re.split(r"\n## ", text)[1:]:
        m = re.match(r"(N\d+) · .*?\n\nSignals (.*?) · test `([^`]+)` · (.*?)\n", block)
        if not m:
            continue
        node, _, test, place = m.groups()
        dates = [{"date": d, "ok": mark == "✓", "detail": detail.strip()}
                 for d, mark, detail in re.findall(r"^- (\d{4}-\d\d-\d\d) ([✓✗]) (.*)$", block, re.M)]
        note = re.search(r"\*\*(Fails[^*]*)\*\*(.*)", block)
        out[node] = {"test": test, "place": place, "dates": dates,
                     "note": (note.group(1) + note.group(2)).strip() if note else None}
    return out


def md_table(text, heading):
    """Rows of the first markdown table after `heading`, as lists of cell strings."""
    sec = text.split(heading, 1)[1]
    lines = []
    for l in sec.splitlines()[1:]:
        if l.startswith("|"):
            lines.append(l)
        elif lines:
            break
    return [[c.strip().replace("**", "") for c in l.strip("|").split("|")] for l in lines[2:]]


def report_findings():
    text = open(os.path.join(HERE, "output", "worldline_report.md"), encoding="utf-8").read()
    paras = text.split("## The account does not close", 1)[1].split("\n## ", 1)[0].strip().split("\n\n")
    durations = md_table(text, "## Stated durations")
    return {
        "does_not_close": {
            "intro": paras[0].strip(),
            "drop_one_of": [l[2:].strip() for l in paras[1].splitlines() if l.startswith("- ")],
            "resolution": paras[2].strip(),
        },
        "durations": [dict(zip(["span", "signals", "reading", "allowed", "literal", "survives"], r))
                      for r in durations if len(r) == 6],
    }


def moon_illumination():
    """Illuminated fraction at local midnight (Streedagh) for every night of the journey."""
    days = list(range(FIRST_DAY, LAST_DAY + 1))
    # night of day d = the midnight that ends date WRECK+d; Streedagh is ~34.5 min behind UTC
    utc = [dt.datetime.combine(WRECK + dt.timedelta(days=d + 1), dt.time(0, 34)) for d in days]
    t = Time(utc, scale="utc")
    elong = get_sun(t).separation(get_body("moon", t)).rad
    illum = (1 - np.cos(elong)) / 2
    return [{"day": d, "illum": round(float(i), 3)} for d, i in zip(days, illum)]


def main(out_path):
    nodes = {r["node"]: r for r in rows(os.path.join(HERE, "data", "worldline_nodes.csv"))}
    intervals = rows(os.path.join(HERE, "output", "worldline_intervals.csv"))
    tests = light_tests()
    events = []
    for r in intervals:
        n = nodes[r["node"]]
        events.append({
            "node": r["node"], "episode": r["episode"], "event": r["event"],
            "signals": [s for s in r["signals"].split(";") if s],
            "lo": int(r["lo_d"]), "hi": int(r["hi_d"]),
            "lo_date": r["lo_date"], "hi_date": r["hi_date"],
            "anchor": n["anchor"] or None, "anchor_source": n["anchor_source"] or None,
            "gap_basis": n["gap_basis"] or None, "note": n["note"] or None,
            "light": tests.get(r["node"]),
        })
    signals = {r["signal_id"]: {k: r[k] for k in
               ("episode", "page", "signal_class", "anchor", "motion_vector", "magnitude", "inference", "trust")}
               for r in rows(os.path.join(HERE, "data", "cuellar_signal_map.csv"))}
    nights = [{k: (int(v) if k in ("days_after_wreck", "illum_pct") else v) for k, v in r.items()}
              for r in rows(os.path.join(HERE, "output", "moon_nights.csv"))]
    view = json.load(open(os.path.join(ROOT, "1_signal_field", "data", "streedagh_view.geojson"), encoding="utf-8"))
    wrecks = [{"id": f["properties"]["uari"], "class": f["properties"]["acquisition_class"],
               "top": f["properties"].get("top_attribution"),
               "lon": f["geometry"]["coordinates"][0], "lat": f["geometry"]["coordinates"][1]}
              for f in view["features"]]

    data = {
        "generated": dt.date.today().isoformat(),
        "day0": WRECK.isoformat(),
        "events": events,
        "signals": signals,
        "nights": nights,
        "moon": moon_illumination(),
        "findings": report_findings(),
        "wrecks": wrecks,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(out_path, os.path.getsize(out_path), "bytes;", len(events), "events,", len(signals), "signals")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])

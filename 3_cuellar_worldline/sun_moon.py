"""Step 2: test every light signal in Cuéllar's account against the sun and moon.

Reads output/worldline_intervals.csv (run worldline.py first). For each event with a light_test,
and for every date in its interval, computes the sun and moon at the place and asks whether the
signal could be true on that date:

    DAYLIGHT              the event is described as seen in daylight: report the daylight window
    DAWN / PREDAWN        report civil dawn and sunrise (PREDAWN: two hours before dawn) and the moon then
    NIGHT@HH:MM / NIGHT   is the sun well down, and is the moon up and how much of it is lit?
    MOONRISE_AFTER_DARK   "awaited the rising of the moon": does the moon rise between the end of
                          evening twilight and sunrise? (If it is already up at dusk, or rises in
                          daylight, there is no rising to wait for.)

Also writes a night-by-night table of the moon for the Streedagh-to-O'Rourke stretch.

Positions use astropy's built-in ephemeris (accurate to well under a minute of time here).
Clock times are local mean solar time for the place: UTC minus longitude/15. Cuéllar's
"nine o'clock" and "one o'clock" are taken as local time, good to perhaps half an hour.
Places: Streedagh for the strand episodes; the inland episodes (Leitrim/Fermanagh) and later
Ulster episodes use rough positions, which shift rise/set times by a few minutes only.

Writes output/sun_moon_report.md and output/moon_nights.csv.
"""

import csv
import datetime as dt
import os
import warnings

import numpy as np

warnings.filterwarnings("ignore")  # ERFA "dubious year" warnings for 1588

import astropy.units as u  # noqa: E402
from astropy.coordinates import AltAz, EarthLocation, get_body, get_sun  # noqa: E402
from astropy.time import Time  # noqa: E402
from astropy.utils import iers  # noqa: E402

iers.conf.auto_download = False

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")

# Rough positions (lat, lon). Streedagh is the wreck site; the others only set rise/set times.
PLACES = {
    "streedagh": (54.402, -8.626, "Streedagh strand"),
    "inland": (54.30, -8.20, "north Leitrim / Lough Melvin area (approximate)"),
    "ulster": (55.05, -6.95, "north Antrim / Derry coast (approximate)"),
}
EPISODE_PLACE = {"wreck": "streedagh", "shore1": "streedagh", "mon": "streedagh", "burial": "streedagh",
                 "depart": "inland", "bishop": "ulster", "sea": "ulster"}
SUN_ALT = -0.833   # sunrise/sunset (upper limb, refraction)
CIVIL = -6.0       # civil twilight
MOON_ALT = 0.125   # moonrise/moonset (upper limb, refraction, parallax)
STEP_MIN = 4


def loc(place):
    lat, lon, _ = PLACES[place]
    return EarthLocation(lat=lat * u.deg, lon=lon * u.deg, height=10 * u.m)


def lmt_offset(place):
    return dt.timedelta(hours=PLACES[place][1] / 15.0)


def day_grid(date, place, start_h=12, hours=24):
    """Local-mean-time grid from start_h on `date` for `hours`, with sun and moon altitude and moon illumination."""
    t0 = dt.datetime.combine(date, dt.time(0)) + dt.timedelta(hours=start_h) - lmt_offset(place)
    n = int(hours * 60 / STEP_MIN) + 1
    utc = [t0 + dt.timedelta(minutes=STEP_MIN * k) for k in range(n)]
    t = Time(utc, scale="utc")
    frame = AltAz(obstime=t, location=loc(place))
    sun = get_sun(t)
    moon = get_body("moon", t)
    s_alt = sun.transform_to(frame).alt.deg
    m_alt = moon.transform_to(frame).alt.deg
    elong = sun.separation(moon).rad
    illum = (1 - np.cos(elong)) / 2
    local = [x + lmt_offset(place) for x in utc]
    return local, s_alt, m_alt, illum


def crossings(local, alt, thr):
    """List of (time, 'rise'|'set') where alt crosses thr, linearly interpolated."""
    out = []
    for k in range(len(alt) - 1):
        a, b = alt[k] - thr, alt[k + 1] - thr
        if a < 0 <= b or a >= 0 > b:
            f = a / (a - b)
            out.append((local[k] + (local[k + 1] - local[k]) * f, "rise" if a < 0 else "set"))
    return out


def hm(t):
    return t.strftime("%H:%M")


def night(date, place):
    """Facts for the night beginning on `date` (noon to noon local)."""
    local, s, m, il = day_grid(date, place)
    sun_x = crossings(local, s, SUN_ALT)
    civ_x = crossings(local, s, CIVIL)
    moon_x = crossings(local, m, MOON_ALT)
    sunset = next((t for t, k in sun_x if k == "set"), None)
    sunrise = next((t for t, k in sun_x if k == "rise"), None)
    dusk = next((t for t, k in civ_x if k == "set"), None)
    dawn = next((t for t, k in civ_x if k == "rise"), None)
    return dict(local=local, s=s, m=m, il=il, sunset=sunset, sunrise=sunrise, dusk=dusk, dawn=dawn,
                moon_x=moon_x)


def at(nt, when):
    i = int(np.argmin([abs((x - when).total_seconds()) for x in nt["local"]]))
    return nt["s"][i], nt["m"][i], nt["il"][i]


def moon_phrase(m_alt, illum):
    if m_alt < 0:
        return f"moon below the horizon ({illum * 100:.0f}% lit)"
    return f"moon up, {m_alt:.0f}° high, {illum * 100:.0f}% lit"


def test(node, date, place):
    kind = node["light_test"]
    nt = night(date, place)
    if kind == "DAYLIGHT":
        # report the daylight of `date` itself (previous night's sunrise to this evening's sunset)
        prev = night(date - dt.timedelta(days=1), place)
        return True, f"daylight {hm(prev['sunrise'])}–{hm(nt['sunset'])}"
    if kind in ("DAWN", "PREDAWN"):
        prev = night(date - dt.timedelta(days=1), place)
        sr, cd = prev["sunrise"], prev["dawn"]
        when = cd - dt.timedelta(hours=2) if kind == "PREDAWN" else cd
        _, m, il = at(prev, when)
        tag = "two hours before dawn" if kind == "PREDAWN" else "dawn"
        return True, f"civil dawn {hm(cd)}, sunrise {hm(sr)}; {tag} {hm(when)}: {moon_phrase(m, il)}"
    if kind.startswith("NIGHT"):
        if "@" in kind:
            hh, mm = map(int, kind.split("@")[1].split(":"))
            # times after midnight belong to the night that began the previous evening
            base = date - dt.timedelta(days=1) if hh < 12 else date
            nt = night(base, place)
            when = dt.datetime.combine(base if hh >= 12 else date, dt.time(hh, mm))
        else:
            when = nt["dusk"] + dt.timedelta(hours=1)
        s, m, il = at(nt, when)
        dark = s < -12
        return dark, f"{hm(when)}: sun {s:.0f}° ({'dark' if dark else 'twilight'}); {moon_phrase(m, il)}"
    if kind == "MOONRISE_AFTER_DARK":
        rises = [t for t, k in nt["moon_x"] if k == "rise" and nt["dusk"] <= t <= nt["dawn"]]
        _, m_dusk, il = at(nt, nt["dusk"])
        if rises:
            return True, f"moon rises {hm(rises[0])} (dusk {hm(nt['dusk'])}), {il * 100:.0f}% lit"
        sets = [t for t, k in nt["moon_x"] if k == "set" and t >= nt["dusk"]]
        state = (f"already up at dusk ({hm(nt['dusk'])}), sets {hm(sets[0])}" if m_dusk > 0 and sets
                 else "does not rise during the night")
        return False, f"no moonrise in the dark: {state}; {il * 100:.0f}% lit"
    return None, ""


def main():
    rows = list(csv.DictReader(open(os.path.join(OUT, "worldline_intervals.csv"), encoding="utf-8")))
    L = ["# Light signals against the sun and moon (step 2)", "",
         "Generated by `sun_moon.py` from `output/worldline_intervals.csv`. Times are local mean solar "
         "time. Each event is tested on every date its step-1 interval allows.", ""]
    for r in rows:
        if not r["light_test"]:
            continue
        place = EPISODE_PLACE.get(r["episode"], "inland")
        lo, hi = dt.date.fromisoformat(r["lo_date"]), dt.date.fromisoformat(r["hi_date"])
        L += [f"## {r['node']} · {r['event']}", "",
              f"Signals {r['signals'].replace(';', ', ')} · test `{r['light_test']}` · {PLACES[place][2]}", ""]
        verdicts = []
        d = lo
        while d <= hi:
            ok, text = test(r, d, place)
            verdicts.append(ok)
            mark = "" if ok is None else ("✓" if ok else "✗")
            L.append(f"- {d.isoformat()} {mark} {text}")
            d += dt.timedelta(days=1)
        if r["light_test"] == "MOONRISE_AFTER_DARK" and not any(verdicts):
            # how far forward would the event have to move?
            d = hi + dt.timedelta(days=1)
            while d < hi + dt.timedelta(days=30):
                ok, text = test(r, d, place)
                if ok:
                    L += ["", f"**Fails on every date the chain allows.** The first later evening with a "
                          f"moonrise after dark is {d.isoformat()} ({text}): "
                          f"{(d - hi).days} days after the latest date the chain allows."]
                    break
                d += dt.timedelta(days=1)
        L.append("")

    # Night table for the first month
    path = os.path.join(OUT, "moon_nights.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["night_of", "days_after_wreck", "sunset", "dusk", "dawn", "illum_pct", "moon_events"])
        L += ["## The moon, night by night, Streedagh, 17 Sep – 20 Oct 1588", "",
              "| Night of | Day | Sunset | Dusk | Lit | Moon (rise/set during the night) |", "|---|---|---|---|---|---|"]
        d = dt.date(1588, 9, 17)
        while d <= dt.date(1588, 10, 20):
            nt = night(d, "streedagh")
            _, _, il = at(nt, nt["dusk"] + dt.timedelta(hours=3))
            ev = ", ".join(f"{k} {hm(t)}" for t, k in nt["moon_x"] if nt["sunset"] <= t <= nt["sunrise"])
            ev = ev or ("up all night" if at(nt, nt["dusk"] + dt.timedelta(hours=3))[1] > 0 else "down all night")
            n = (d - dt.date(1588, 9, 21)).days
            w.writerow([d.isoformat(), n, hm(nt["sunset"]), hm(nt["dusk"]), hm(nt["dawn"]), f"{il * 100:.0f}", ev])
            L.append(f"| {d.isoformat()} | {n} | {hm(nt['sunset'])} | {hm(nt['dusk'])} | {il * 100:.0f}% | {ev} |")
            d += dt.timedelta(days=1)

    open(os.path.join(OUT, "sun_moon_report.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()

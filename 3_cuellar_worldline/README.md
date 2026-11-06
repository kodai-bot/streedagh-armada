# Cuéllar's worldline

Captain Francisco de Cuéllar survived the Streedagh wreck. He crossed Ireland, Scotland and the
North Sea, and wrote his account at Antwerp on 4 October 1589. Here the letter is treated as a
signal field: things he mentions in passing (a time of night, daylight, the moon, a tide, a number
of days) are signals that can be computed and checked against each other and against physics.

`data/cuellar_signal_map.csv` codes 125 signals (S001–S154) by episode, page, class, motion
vector, magnitude and trust. The worldline is built from them in steps:

1. **Dated chain** (`worldline.py`). `data/worldline_nodes.csv` lists 31 events from Calais to
   Antwerp. For each, it gives the gap since the previous event as a range, a few fixed dates, and
   where each number comes from. **TEXT** means the letter states it. **UNSTATED** means a coding
   judgement, kept wide. All of these are solved together as a temporal constraint network, so
   every event gets the tightest date interval the whole account allows.
2. **Sun and moon** (`sun_moon.py`). Every light signal (daylight, dawn, a clock time at night,
   "awaited the rising of the moon") is tested on every date its interval allows, using astropy.
3. *(next)* Feed the results back as constraints, and add tides (S113, the spring tide at Lough
   Melvin).
4. *(next)* Join this worldline to the ships' worldline (Lisbon → Calais → Streedagh) and to the
   English records.

Run: `make worldline sun_moon` from the project root. Results go to `output/`.

See the results drawn out at [kodai-bot.github.io/streedagh](https://kodai-bot.github.io/streedagh/) (data bundled by `web_data.py`).

## Results so far

**The night of the wreck was dark.** The ships broke up in daylight (sunrise 05:43, sunset 18:01
local time). The new moon, 2% lit, set at 18:25 and stayed down all night. When "more than
two hundred horsemen" rode down to the wrecks at about one in the morning (S040) and passed him
without seeing him, there was no moon at all. The darkness of that night is computed, not guessed.

**"We awaited the rising of the moon" (S083) does not fit the dates as told.** As the letter tells
it, the oat-hut night falls 25–30 September. On every one of those evenings a waxing moon, 30–80%
lit, is already in the sky at dusk and sets during the night. There was no moonrise to wait for.
The first evening with a moonrise after dark is 5 October. So either a week or more passes unrecorded
before the oat huts (the rest of the chain can absorb that, but only just: the stay at MacClancy's
castle then shrinks to 75–78 days), or the detail is misremembered. The signal was coded
low-trust; now that low trust has a cause.

**The secret departure from MacClancy's castle was by moonlight.** "Two hours before dawn, ten
days after the Nativity" (S122) is about 05:40 on 4 January 1589. At that hour a 95%-lit moon
stood about 30° up.

**The account's long durations do not all fit together.** The arrival in Flanders is fixed: about
22 September 1589, "twelve days" before the letter. Working back from it, "more than six months"
in Scotland (S146) only just fits, and only if he left Ireland no later than early April 1589.
That rules out "more than seven months among mountains and woods" in Ireland (S005): the chain
allows 173–193 days, about six months. This upper limit rests on the stated durations and the fixed
Flanders date; the only unstated gap in it is the passage to Flanders, set at a minimum of two days. One of the two long figures is rounded up, which is
what you would expect in a letter written from memory.

**Dated outline** (from `output/worldline_report.md`): castle reached 9–22 Oct 1588; leaves it
3–5 Jan 1589; Girona wreck site 21–27 Jan; sails from Ulster at dawn 13 Mar–2 Apr; leaves Scotland
8–20 Sep; Flanders about 22 Sep; letter 4 Oct 1589.

## Conventions

- Dates are Gregorian (Spain had adopted it in 1582). English records of the time are Julian, ten
  days behind: the wreck is 11 September in English sources.
- Clock times are local mean solar time (UTC − longitude/15, about UTC − 35 min at Streedagh).
- Inland and Ulster positions are approximate. They move rise and set times by minutes, which
  does not change any verdict above.

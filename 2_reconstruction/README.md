# Working reconstruction

`Revised_Streedagh_Working_Reconstruction_v0_7.docx` is the current version;
`streedagh_reconstruction_v0_7.md` is a pandoc conversion for reading and diffing (the docx is the
master). v0.2 is kept for the record.

The argument, in brief: take the contemporary measurements (Castilian codo 0.57468125 m,
administrative ratings, the recorded embarked soldiers) and derive the upper-deck area the ships
needed in order to carry those men at a defensible density. A single-level castle cannot supply it;
two or three stepped decks fore and aft can (§26, §28). That conclusion is reached without the
iconography or the eyewitnesses. It is then compared with them (§18–§23, §29–§34).

Open points recorded in the text: the recovery year of some guns differs between §29 and its
sources; §26.8 lists the metrology to verify before publication.

`stepped_castle_capacity.py` (`make capacity`) recomputes the capacity argument from its stated
inputs: the codo, the comparator ships in metres, the three estimates of Juliana's dimensions, the
castle areas and the m² per soldier. It checks all 158 figures printed in §26.1, §26.4, §26.6, §27.4
and §28.1–§28.4 (all match) and writes `output/capacity_report.md` and `output/capacity.json` (the
data for the web page). It also varies the number of castle levels to find the fewest that reach
1.5 m² per soldier, which the document does not tabulate. In the central case the document's
floor rule (fore 2, aft 2 + a shortened third) reaches it once about 40% of a lower principal deck
is added for 290 soldiers; single-level castles give 0.75 m². In the low case no configuration up to
three levels fore and aft reaches it. Explore it interactively at [Standing room](https://kodai-bot.github.io/streedagh/ships/).

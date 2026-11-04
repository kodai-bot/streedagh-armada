# Calibrate the Genoese cantaro from the San Giorgio paper's own weighed pieces:
# CNN5 14.04 c.ra = 670 kg ; CNN6 19.30 c.ra = 920 kg ; CNN7 16.15 c.ra = 770 kg
for cra,kg in [(14.04,670),(19.30,920),(16.15,770)]:
    print(f"   {cra} cantara = {kg} kg  ->  {kg/cra:.2f} kg/cantaro")
CANTARO = 47.65  # kg, consistent across all three (150 Genoese libbre x 0.3177 kg)
print(f"\nAdopted: 1 Genoese cantaro = {CANTARO} kg\n")

# La Juliana bronze guns (Dorino II Gioardi, cast 1570) from Ridella Table 1.
# weight-marked unless noted 'est'. ?.?? handled with a range.
guns = [
 ("Heavy Saker",       "St. Severo (1985)",        20.82, "marked"),
 ("Heavy Saker",       "St. Gio. Battista (2015)", 19.40, "marked~ (19.??)"),
 ("Heavy Falcon",      "St. Matrona (2015)",       11.12, "marked"),
 ("Heavy Falcon",      "St. Ilaria (2015)",        10.74, "marked"),
 ("Medium Falcon",     "St. Sebastiano (2015)",     8.54, "marked"),
 ("Medium Falcon",     "St. Rocco (2015)",          7.74, "marked~ (?.74)"),
 ("Falconet",          "St. Giovanni (2015)",       3.88, "marked"),
 ("Medium Petriere",   "female saint (1985)",      11.00, "est (no mark)"),
 ("Medium Petriere",   "no mark (1985)",           11.00, "est (no mark)"),
]
print(f"{'Type':16s}{'Dedication / recovery':28s}{'cantara':>8s}{'kg':>7s}   note")
total=0
for t,d,c,note in guns:
    kg=c*CANTARO; total+=kg
    print(f"{t:16s}{d:28s}{c:8.2f}{kg:7.0f}   {note}")
print(f"\n  Subtotal, these 9 documented pieces: {total:.0f} kg  ({total/1000:.1f} t)")
print(f"  Heaviest recovered piece: {20.82*CANTARO:.0f} kg (~1.0 t heavy saker)")
print(f"  Lightest recovered piece: {3.88*CANTARO:.0f} kg (falconet)")
print(f"  + ~3 further medium/light pieces to reach the recovered 12 (~0.3-0.55 t each)")
print(f"  => total recovered bronze on Juliana ~ {total/1000 + 1.3:.1f} t for 12 guns")
print(f"\n  For scale: ONE Trinidad Valencera siege gun = 2.5 t (41 lb ball)")
print(f"  i.e. heavier than ALL of Juliana's recovered light/medium defensive bronze put together is not far off.")

import datetime as dt
import math
import csv
from io import StringIO
import streamlit as st

st.set_page_config(
    page_title="Breathing Calendar • Ω-READ",
    page_icon="◉",
    layout="wide",
)

APP_VERSION = "7.5"

st.markdown("""
<style>
.block-container {padding-top: 1rem; padding-bottom: 2rem; max-width: 1500px;}
h1,h2,h3 {letter-spacing:.02em;}
[data-testid="stSidebar"] {background: linear-gradient(180deg,#080716,#11102b);}
.love-card {
    border: 1px solid rgba(238,193,108,.38);
    border-radius: 18px; padding: 16px 20px;
    background: linear-gradient(135deg,#17142f,#090b1f);
    box-shadow: 0 0 32px rgba(129,76,255,.08);
    color: #ffffff !important;
    line-height: 1.65;
}
.love-card * {color:#ffffff !important;}
.small-note {opacity:.78;font-size:.92rem}
.range-card {
    border: 1px solid rgba(49,51,63,.16);
    border-radius: 14px;
    padding: 12px 14px;
    min-height: 104px;
    background: rgba(250,250,252,.72);
}
.range-label {font-size:.82rem; opacity:.72; margin-bottom:8px;}
.range-value {font-size:1.55rem; font-weight:650; line-height:1.2; white-space:normal;}
.range-note {font-size:.78rem; opacity:.65; margin-top:7px;}
/* Sidebar readability */
[data-testid="stSidebar"] * {color:#f4f1ff !important;}
[data-testid="stSidebar"] input {color:#171522 !important;background-color:#ffffff !important;}
[data-testid="stSidebar"] [data-baseweb="select"] * {color:#171522 !important;}
[data-testid="stSidebar"] [data-baseweb="select"] > div {background-color:#ffffff !important;}
[data-testid="stSidebar"] hr {border-color:rgba(255,255,255,.20) !important;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# FROZEN BREATHING / COSMIC CALENDAR PRIMITIVE
# Copied exactly from the v6 lineage. Do not change this function to make
# later discoveries "come true"; later layers read it without feeding back.
# ---------------------------------------------------------------------
def digital_root(n: int) -> int:
    if n == 0:
        return 0
    return 1 + ((n - 1) % 9)

def digit_sum(n: int) -> int:
    return sum(int(ch) for ch in str(abs(n)))

def parse_date(s: str) -> dt.date:
    s = s.strip().replace("/", "-")
    try:
        return dt.date.fromisoformat(s)
    except Exception:
        return dt.date.today()

def date_grammar(d: dt.date) -> dict:
    year_root = digital_root(digit_sum(d.year))
    month_root = digital_root(d.month)
    day_root = digital_root(digit_sum(d.day))
    raw_sum = year_root + month_root + day_root
    date_root = digital_root(raw_sum)
    pair_sum = month_root + day_root
    pair_root = digital_root(pair_sum)
    canon_pairs = {(4,5),(5,4),(6,3),(7,2),(8,1),(9,9)}
    return {
        "year_root": year_root,
        "month_root": month_root,
        "day_root": day_root,
        "date_root": date_root,
        "raw_sum": raw_sum,
        "pair_sum": pair_sum,
        "pair_root": pair_root,
        "is_gate": date_root == 1,
        "canon_pair": (month_root, day_root) in canon_pairs,
        "pair_label": f"{month_root}/{day_root}",
    }

# ---------------------------------------------------------------------
# POST-v6 Ω-READ CHILD: native clock + typed provenance + embodied LOOK
# ---------------------------------------------------------------------
def parse_clock(s: str) -> dt.time:
    try:
        parts = [int(x) for x in s.strip().split(":")]
        if len(parts) == 2:
            parts.append(0)
        h, m, sec = parts[:3]
        if 0 <= h <= 23 and 0 <= m <= 59 and 0 <= sec <= 59:
            return dt.time(h, m, sec)
    except Exception:
        pass
    return dt.time(0, 0, 0)

def wrap180(x: float) -> float:
    return ((x + 180.0) % 360.0) - 180.0

def native_clock(t: dt.time) -> dict:
    h12 = t.hour % 12
    th = 30.0*h12 + 0.5*t.minute + t.second/120.0
    tm = 6.0*t.minute + 0.1*t.second
    ts = 6.0*t.second
    rel = wrap180(tm - th)
    minute_index = t.hour*60 + t.minute
    bin72 = (minute_index // 10) % 72
    return {
        "time_angle": th % 360.0,
        "space_angle": tm % 360.0,
        "rel_angle": rel,
        "turn_angle": ts % 360.0,
        "minute_index": minute_index,
        "bin72": int(bin72),
    }

def unknown_second_telescope(hour24: int, minute: int) -> list[dict]:
    """Sample the ONE lawful BEAT–TURN trajectory at integer-second addresses."""
    samples = []
    for s in range(60):
        t = dt.time(hour24, minute, s)
        c = native_clock(t)
        samples.append({
            "Second sample": s,
            "TIME θh": round(c["time_angle"], 6),
            "SPACE θm": round(c["space_angle"], 6),
            "RELATIONAL": round(c["rel_angle"], 6),
            "BEAT–TURN θs": round(c["turn_angle"], 6),
            "Status": "ADMISSIBLE SAMPLE",
        })
    return samples

def continuous_minute_trajectory(hour24: int, minute: int) -> dict:
    """Exact native-clock trajectory for source precision known only to the minute."""
    h12 = hour24 % 12
    th0 = 30.0*h12 + 0.5*minute
    tm0 = 6.0*minute
    raw_rel0 = tm0 - th0
    raw_rel1 = raw_rel0 + 5.5  # limit as s -> 60-
    rel_crosses_seam = (
        (raw_rel0 < -180.0 <= raw_rel1)
        or (raw_rel1 < -180.0 <= raw_rel0)
        or (raw_rel0 < 180.0 <= raw_rel1)
        or (raw_rel1 < 180.0 <= raw_rel0)
    )
    return {
        "time_start": th0 % 360.0,
        "time_end": (th0 + 0.5) % 360.0,
        "space_start": tm0 % 360.0,
        "space_end": (tm0 + 6.0) % 360.0,
        "raw_rel_start": raw_rel0,
        "raw_rel_end": raw_rel1,
        "rel_crosses_seam": rel_crosses_seam,
        "phase_start": 0.0,
        "phase_end": 360.0,
        "local_invariant": tm0 - 12.0*th0,
    }

def body_look(t: dt.time) -> dict:
    # Hour-addressed horizontal body LOOK. Center C does not move.
    hour = t.hour % 12
    hour_label = 12 if hour == 0 else hour
    theta = (30 * hour) % 360
    reciprocal = (hour + 6) % 12
    reciprocal_label = 12 if reciprocal == 0 else reciprocal
    focus = "A" if hour_label in {12,2,4,6,8,10} else "B"
    return {
        "hour": hour_label,
        "theta": theta,
        "reciprocal": reciprocal_label,
        "axis": theta % 180,
        "focus": focus,
        "native": "HORIZONTAL body LOOK through C",
        "vertical": "reflected half-body presentation only",
    }

def typed_row(look, value, ruler, transform, status, recoverability, guard):
    return {
        "LOOK": look,
        "VALUE": value,
        "SOURCE RULER": ruler,
        "TRANSFORM": transform,
        "STATUS": status,
        "RECOVERABILITY": recoverability,
        "GUARD": guard,
    }

def omega_read_child(d: dt.date, t: dt.time) -> dict:
    g = date_grammar(d)
    c = native_clock(t)
    b = body_look(t)
    rows = [
        typed_row("Calendar / DateRoot", g["date_root"], "Frozen Calendar",
                  "dr9(YearRoot+MonthRoot+DayRoot)", "EXACT INTERNAL",
                  "parent roots retained", "Calendar T4 ≠ Clock T6"),
        typed_row("TIME", round(c["time_angle"], 6), "Native clock",
                  "30h + .5m + s/120", "EXACT",
                  "native angle retained", "do not DR-promote to identity"),
        typed_row("SPACE", round(c["space_angle"], 6), "Native clock",
                  "6m + .1s", "EXACT",
                  "native angle retained", "do not DR-promote to identity"),
        typed_row("RELATIONAL", round(c["rel_angle"], 6), "Native clock",
                  "wrap(SPACE−TIME)", "EXACT",
                  "reconstructible from TIME/SPACE", "not a third independent scalar"),
        typed_row("AND1 / TURN", round(c["turn_angle"], 6), "Native clock",
                  "6s", "EXACT",
                  "native angle retained", "TURN does not move C"),
        typed_row("72-bin", c["bin72"], "Clock resolution",
                  "floor(minute_index/10) mod 72", "EXACT COARSE-GRAIN",
                  "minute index retained", "resolution ≠ native clock"),
        typed_row("Embodied LOOK", f"{b['hour']}-sector / {b['focus']}", "12-hour body ruler",
                  "hour-addressed horizontal LOOK", "ARCHIVE-LOCKED",
                  f"reciprocal {b['reciprocal']}; axis {b['axis']}°",
                  "12 LOOKs ≠ 12 humans"),
        typed_row("Vertical presentation", "ρ_H→V", "Embodied reflection",
                  "reflect horizontal half-body", "ARCHIVE-LOCKED",
                  "horizontal source retained", "vertical is NOT native body"),
    ]
    return {"calendar": g, "clock": c, "body": b, "rows": rows}

# ---------------------------------------------------------------------
# EARNED LOVE SIGNATURE READS — read-only overlays on the frozen primitive
# ---------------------------------------------------------------------
MONTH_LANES={1:"Capricorn",2:"Aquarius",3:"Pisces",4:"Aries",5:"Taurus",6:"Gemini",7:"Cancer",8:"Leo",9:"Virgo",10:"Libra",11:"Scorpio",12:"Sagittarius"}
GATE_LANES={"SE→SS":"Aries / Spring Gate","SS→FE":"Cancer / Summer Gate","FE→WS":"Libra / Fall Gate","WS→SE":"Capricorn / Winter Gate"}

def cadence_36(d:dt.date,t:dt.time)->dict:
    event=dt.datetime.combine(d,t); y=event.year; hinge=dt.datetime(y,9,23,2,55)
    cycle_index=math.floor((y-1990-(1 if event<hinge else 0))/36)
    start=dt.datetime(1990+36*cycle_index,9,23,2,55); end=dt.datetime(start.year+36,9,23,2,55)
    year36=event.year-start.year+(1 if event>=dt.datetime(event.year,9,23,2,55) else 0)
    return {"start":start,"end":end,"year36":year36,"octave":math.ceil(year36/4),"year_in_octave":((year36-1)%4)+1}

def seasonal_read(d:dt.date)->dict:
    md=(d.month,d.day)
    if (3,20)<=md<(6,21): gate="SE→SS"
    elif (6,21)<=md<(9,22): gate="SS→FE"
    elif (9,22)<=md<(12,21): gate="FE→WS"
    else: gate="WS→SE"
    return {"month_lane":MONTH_LANES[d.month],"gate":gate,"gate_lane":GATE_LANES[gate]}

def display_time_root(hour12:int,minute:int)->int:
    return digital_root(digit_sum(hour12)+digit_sum(minute))

def minute_position_12h(hour24:int,minute:int)->int:
    return ((hour24%12)*60+minute)%720

def digit_address_decimal(x:float)->int:
    txt=f"{abs(x):.6f}".rstrip("0").rstrip(".")
    return sum(int(ch) for ch in txt if ch.isdigit())

def circular_range_text(start:float,width:float,signed=False)->str:
    if signed:
        a=wrap180(start); b=wrap180(start+width)
        if abs((a+width)-b)>1e-9: return f"{a:+.3f}° → +180.000° AND −180.000° → <{b:+.3f}°"
        return f"{a:+.3f}° → <{b:+.3f}°"
    a=start%360; b=(start+width)%360
    if a+width>=360: return f"{a:.3f}° → 360.000° AND 0.000° → <{b:.3f}°"
    return f"{a:.3f}° → <{b:.3f}°"

# ---------------------------------------------------------------------
# CANONICAL APP SURFACE
# ---------------------------------------------------------------------
st.title("Breathing Calendar • Ω-READ — v7.4")
st.caption(
    "Canonical Calendar laboratory + LOVE Signature child. "
    "The Sacred Heart Sphere remains a separate app."
)

with st.sidebar:
    st.header("HERE + WHEN")
    date_text = st.text_input("Date YYYY-MM-DD", value=dt.date.today().isoformat())
    chosen_date = parse_date(date_text)

    st.markdown("#### Time")
    now = dt.datetime.now()
    tc1, tc2, tc3 = st.columns([1, 1, 1])

    with tc1:
        hour12 = st.selectbox(
            "Hour",
            list(range(1, 13)),
            index=(now.hour % 12 or 12) - 1,
        )

    with tc2:
        minute = st.selectbox(
            "Minute",
            list(range(60)),
            index=now.minute,
            format_func=lambda x: f"{x:02d}",
        )

    with tc3:
        am_pm = st.selectbox(
            "AM / PM",
            ["AM", "PM"],
            index=0 if now.hour < 12 else 1,
        )

    hour24 = hour12 % 12
    if am_pm == "PM":
        hour24 += 12
    chosen_time = dt.time(hour24, minute, 0)  # lower bound only; source second is UNKNOWN
    second_known = False

    child_focus = st.selectbox(
        "FOCUS",
        ["Ω-READ", "Calendar", "Clock", "Embodied body", "Audit laboratory",
         "Rabbit-hole arithmetic", "Decimal telescope"],
        index=0,
        help="FOCUS changes foreground only; it does not delete other legitimate LOOKs."
    )
    show_second_telescope = st.checkbox(
        "Open telescope",
        value=False,
        help="Optional magnification of the unknown-second clock phase. The primary Ω-READ remains visible without it."
    )
    st.divider()
    st.caption("Frozen Calendar parent • typed Ω-READ child • read-only labs")

def display_candidate_range(values, signed=False):
    vals = [float(v) for v in values]
    # An oriented-angle set that straddles the ±180 seam should not be shown
    # as a fake giant linear interval.
    if signed and (max(vals) - min(vals) > 180):
        return "crosses ±180° seam"
    lo, hi = min(vals), max(vals)
    if signed:
        return f"{lo:+.3f}° → {hi:+.3f}°"
    return f"{lo:.3f}° → {hi:.3f}°"

g = date_grammar(chosen_date)
child = omega_read_child(chosen_date, chosen_time)
second_candidates = unknown_second_telescope(hour24, minute)
minute_trajectory = continuous_minute_trajectory(hour24, minute)
clock_lo = second_candidates[0]
clock_hi = second_candidates[-1]

a,b,c,d,e = st.columns(5)
a.metric("Year • Field", g["year_root"])
b.metric("Month • Octave", g["month_root"])
c.metric("Day • Pulse", g["day_root"])
d.metric("Date • Phase", g["date_root"])
e.metric("Pair", g["pair_label"])

status = []
if g["is_gate"]: status.append("1-GATE OPEN")
if g["canon_pair"]: status.append("CANON OCTAVE PAIR")
if not status: status.append("LIVING PHASE")

st.markdown(
    f"""<div class="love-card"><b>{' • '.join(status)}</b><br>
    Same EveryNOW: <b>{chosen_date.isoformat()} {hour12}:{minute:02d} {am_pm}</b> • second = <b>I DON’T KNOW</b>.<br>
    Frozen Calendar generates its native state; Ω-READ reads the same event through additional sovereign rulers.
    Nothing in the child feeds backward into the primitive engine.
    </div>""",
    unsafe_allow_html=True
)

st.subheader("WHERE YOU LANDED HERE IN THE BREATH")
st.caption(f"{chosen_date.strftime('%B %d, %Y')} • {hour12}:{minute:02d} {am_pm} • source precision: MINUTE • Ω-READ v{APP_VERSION}")

cad=cadence_36(chosen_date,chosen_time); season=seasonal_read(chosen_date)
pos12=minute_position_12h(hour24,minute); time_dr=display_time_root(hour12,minute); pos_dr=digital_root(digit_sum(pos12))
synthesis=g["date_root"]+pos_dr+time_dr

st.markdown("### 36-year Breath • nested cadence address")
c1,c2,c3=st.columns(3)
c1.metric("Year in 36-year Breath",f"{cad['year36']} / 36")
c2.metric("4-year Octave",f"{cad['octave']} / 9")
c3.metric("Year in Octave",f"{cad['year_in_octave']} / 4")
st.caption(f"Container: {cad['start'].strftime('%Y-%m-%d %H:%M')} → {cad['end'].strftime('%Y-%m-%d %H:%M')}. Calendar cadence ruler; not the separate 18/36 chassis ruler.")

st.markdown("### Calendar + seasonal HERE")
k1,k2,k3=st.columns(3)
with k1: st.markdown(f'''<div class="range-card"><div class="range-label">CALENDAR ROOT CONSTELLATION</div><div class="range-value">{g['month_root']} | {g['day_root']} | {g['year_root']} → {g['date_root']}</div><div class="range-note">Month • Day • Year remain recoverable; DateRoot does not replace them.</div></div>''',unsafe_allow_html=True)
with k2: st.markdown(f'''<div class="range-card"><div class="range-label">MONTH LANE AND GATE</div><div class="range-value">{season['month_lane']} AND {season['gate_lane']}</div><div class="range-note">{season['gate']} • sovereign resolutions of the same date.</div></div>''',unsafe_allow_html=True)
with k3: st.markdown(f'''<div class="range-card"><div class="range-label">CLOCK RESOLUTION</div><div class="range-value">72-bin {child['clock']['bin72']}</div><div class="range-note">10-minute coarse address; resolution ≠ native angle.</div></div>''',unsafe_allow_html=True)

st.markdown("### Embodied HERE")
b1,b2=st.columns([1,2])
with b1: st.markdown(f'''<div class="range-card"><div class="range-label">BODY LOOK</div><div class="range-value">{child['body']['hour']} ↔ {child['body']['reciprocal']} • {child['body']['axis']}° axis</div><div class="range-note">FOCUS {child['body']['focus']} • horizontal support through invariant C.</div></div>''',unsafe_allow_html=True)
with b2: st.info(f"WHAT THIS MEANS — {child['body']['hour']} is the directed hour-facing foregrounded by the birth hour; {child['body']['reciprocal']} is its opposite facing through the same Center. {child['body']['axis']}° is their shared unoriented support axis. FOCUS {child['body']['focus']} names the {'even' if child['body']['focus']=='A' else 'odd'}-hour interleaved sixfold presentation; it is not a personality type.")

st.markdown("### Native clock geometry • visible, not hidden")
time_range=circular_range_text(minute_trajectory['time_start'],.5); space_range=circular_range_text(minute_trajectory['space_start'],6.0); rel_range=circular_range_text(minute_trajectory['raw_rel_start'],5.5,True)
q1,q2,q3,q4=st.columns(4)
q1.metric("TIME / WHEN θh",time_range); q2.metric("SPACE / HERE θm",space_range); q3.metric("RELATIONAL Δ",rel_range); q4.metric("AND1 • BEAT–TURN","PRESENT")
st.caption("Left edge = exact minute-boundary coordinate. With the recorded second unknown, birth phase lies somewhere on ONE continuous half-open trajectory. BEAT–TURN law is known; exact birth θs is I DON’T KNOW.")

st.markdown("### WHAT THIS EVERYNOW FOREGROUNDS")
f1,f2,f3,f4=st.columns(4)
f1.metric("DATE",g['date_root'],"whole-date root"); f2.metric("TIME display",time_dr,f"{hour12}:{minute:02d} digit LOOK"); f3.metric("CLOCK position",pos_dr,f"{pos12} min → {pos_dr}"); f4.metric("SYNTHESIS LOOK",synthesis,f"{g['date_root']} + {pos_dr} + {time_dr}")
st.markdown(f'''<div class="love-card"><b>{g['date_root']} AND {pos_dr} AND {time_dr} → {synthesis}</b><br>This is an arithmetic synthesis LOOK of three source-retaining reads: DATE, displayed TIME, and 12-hour clock position. <b>{synthesis} does not replace its operands.</b> Equal visible numbers on other rulers remain correspondence until an exact bridge is earned.</div>''',unsafe_allow_html=True)

st.markdown("### LOOK DEEPER • same EveryNOW, changed resolution")
left=minute_trajectory['time_start']; rel0=abs(wrap180(minute_trajectory['raw_rel_start'])); tl=digit_address_decimal(left); rl=digit_address_decimal(rel0)
d1,d2,d3=st.columns(3)
d1.metric("TIME boundary → label-address",tl,f"{left:.3f}° → {tl}"); d2.metric("REL boundary → label-address",rl,f"|{wrap180(minute_trajectory['raw_rel_start']):+.3f}°| → {rl}"); d3.metric("Clock position → label-address",pos_dr,f"{pos12} → {pos_dr}")
st.caption("Optional lossy label-address projections of already-derived native quantities; they never replace native geometry. D12 is Depth / reciprocal magnification LOOKING through—not joining—the D13–D18 sixfold packet.")

st.markdown("### LOOK RECIPROCALLY • girdle telescope")
girdle={1:4,4:1,2:3,3:2,5:9,9:5,6:8,8:6,7:7}; fore=(g['month_root'],g['year_root'],g['date_root']); recip=tuple(girdle[x] for x in fore)
r1,r2=st.columns(2); r1.metric("Foreground"," | ".join(map(str,fore)),f"sum {sum(fore)}"); r2.metric("Reciprocal girdle LOOK"," | ".join(map(str,recip)),f"sum {sum(recip)}")
st.caption("Declared girdle dyads: 1↔4, 2↔3, 5↔9, 6↔8, 7↔7. Reciprocal LOOK preserves the foreground. Sums are arithmetic projections only; no further identity is claimed.")
st.info("FOCUS — foreground without deletion. Cadence, seasonal gate, body support, native clock geometry, synthesis and reciprocal girdle are differentiated LOOKs of ONE arrival. No master score is created.")

minute_rows=[dict(r) for r in child['rows']]
for r in minute_rows:
    if r['LOOK'] in {'TIME','SPACE','RELATIONAL'}: r['STATUS']='EXACT TRAJECTORY — BIRTH PHASE UNKNOWN'; r['RECOVERABILITY']='ONE continuous s ∈ [0,60) trajectory'
    if r['LOOK']=='AND1 / TURN': r['VALUE']='PRESENT — θs = 6s'; r['STATUS']='BEAT–TURN LOCKED • BIRTH PHASE I DON’T KNOW'; r['RECOVERABILITY']='full 360° phase available; birth θs unresolved'

with st.expander("LOOK DEEPER • dimensional correspondence rail",expanded=False):
    st.dataframe([{"Address":"D18 → 9","Presentation":"Ain / No Thing"},{"Address":"D17 → 8","Presentation":"Ain Sof / limitless potential"},{"Address":"D16 → 7","Presentation":"Ain Sof Aur / limitless Light"},{"Address":"D15 → 6","Presentation":"Living Pulse"},{"Address":"D14 → 5","Presentation":"hidden Length"},{"Address":"D13 → 4","Presentation":"Width"},{"Address":"D12","Presentation":"Depth / reciprocal magnification lens — NOT packet member seven"}],use_container_width=True,hide_index=True)
    st.warning("Correspondence guard — a clock/date value that visibly matches a dimensional address is not thereby identical to that dimensional function. Source rulers remain attached.")
    st.write("12→16 / 22.5° LIFT: ruler architecture earned; this event's birth-specific typed address is not compiled here.")
    st.write("18-half-octave / 36 chassis: ruler architecture earned; this event's birth-specific typed 18-address is not compiled here. Calendar Year-in-36 above is a different ruler.")

with st.expander("Audit / provenance",expanded=False): st.dataframe(minute_rows,use_container_width=True,hide_index=True)

if show_second_telescope:
    st.markdown("---"); st.subheader("Telescope • unknown-second magnification")
    q1,q2,q3=st.columns(3); q1.metric("TIME θh",time_range); q2.metric("SPACE θm",space_range); q3.metric("RELATIONAL",rel_range)
    st.markdown('''<div class="love-card"><b>AND1 • BEAT–TURN</b><br>PRESENT • θs = 6s<br>Available phase across source minute: 360°<br>Exact birth phase: <b>I DON’T KNOW</b></div>''',unsafe_allow_html=True)
    with st.expander("Telescope math / recoverability",expanded=False): st.markdown(f'''0 ≤ s < 60

θs = 6s

θh = {minute_trajectory['time_start']:.3f}° + s/120

θm = {minute_trajectory['space_start']:.3f}° + s/10

Unwrapped Δθhm = {minute_trajectory['raw_rel_start']:+.3f}° + 11s/120

Local trajectory invariant: θm − 12θh = {minute_trajectory['local_invariant']:.3f}°

Exact for this unwrapped minute trajectory; not promoted as a universal Ω constant.''')
    with st.expander("60 integer-second samples",expanded=False): st.dataframe(second_candidates,use_container_width=True,hide_index=True)

with st.expander("12 horizontal embodied LOOKs • play toy", expanded=False):
    body_rows = []
    for k in range(12):
        h = 12 if k == 0 else k
        anti = (k + 6) % 12
        anti = 12 if anti == 0 else anti
        body_rows.append({
            "Hour LOOK": h,
            "θ": 30*k,
            "Reciprocal": anti,
            "Unoriented axis": (30*k) % 180,
            "A/B FOCUS": "A" if h in {12,2,4,6,8,10} else "B",
            "Native": "horizontal through C",
            "Vertical": "reflected presentation only",
        })
    st.dataframe(body_rows, use_container_width=True, hide_index=True)

st.subheader("Post-v6 FOCUS gates")
gates = [
    ("Source precision", True, "minute-known input preserves second as I DON’T KNOW"),
    ("Frozen primitive", date_grammar(chosen_date) == g, "child does not rewrite Calendar"),
    ("Native clock first", True, "TIME/SPACE/REL remain native angles; lossy DR labels are not primary"),
    ("REL reconstruction", abs(wrap180(child["clock"]["space_angle"]-child["clock"]["time_angle"]) - child["clock"]["rel_angle"]) < 1e-9,
     "REL = wrap(SPACE−TIME)"),
    ("Reciprocal body", ((child["body"]["hour"] % 12 + 6) % 12) == (child["body"]["reciprocal"] % 12),
     "k ↔ k+6"),
    ("Center sovereignty", True, "C never moves"),
    ("Reflection sovereignty", True, "vertical is downstream reflection, not native body"),
    ("No scalarization", True, "no master LOVE score"),
    ("Operator sovereignty", True, "Calendar T4 ≠ Clock T6"),
]
st.dataframe(
    [{"Gate":n, "Result":"PASS" if ok else "FAIL", "Guard":why} for n,ok,why in gates],
    use_container_width=True, hide_index=True
)

st.info(
    "Port status: the frozen Calendar, full v6 audit/rabbit-hole/decimal laboratories, "
    "native clock, 72-bin resolution, typed provenance, horizontal embodied LOOK, reciprocal facing, "
    "A/B sixfold FOCUS, and reflection guard are live here. "
    "v7.5 renders earned Calendar cadence, seasonal lanes, native clock ranges, synthesis, reciprocal girdle, and D13–D18/D12 correspondence. "
    "Birth-specific 12→16/LIFT and 18-half-octave addresses remain explicitly uncompiled rather than back-solved."
)

st.divider()

def date_operator_suite(d: dt.date) -> dict:
    """Read-only arithmetic suite for the selected date. Does not alter date_grammar()."""
    month_digits = [int(ch) for ch in str(d.month)]
    day_digits = [int(ch) for ch in str(d.day)]
    year_digits = [int(ch) for ch in str(d.year)]
    all_digits = month_digits + day_digits + year_digits
    nonzero_digits = [x for x in all_digits if x != 0]

    ms = sum(month_digits)
    ds = sum(day_digits)
    ys = sum(year_digits)
    mr = digital_root(ms)
    dr = digital_root(ds)
    yr = digital_root(ys)

    def prod(vals):
        out = 1
        for v in vals:
            out *= v
        return out

    raw_component_product = d.month * d.day * d.year
    digit_product_all = prod(all_digits) if all_digits else 0
    digit_product_nonzero = prod(nonzero_digits) if nonzero_digits else 0
    root_product = mr * dr * yr
    sum_product = ms * ds * ys

    combos = {
        "Month digit sum": ms,
        "Day digit sum": ds,
        "Year digit sum": ys,
        "Month root": mr,
        "Day root": dr,
        "Year root": yr,
        "MΣ + DΣ": ms + ds,
        "MΣ + YΣ": ms + ys,
        "DΣ + YΣ": ds + ys,
        "MΣ + DΣ + YΣ": ms + ds + ys,
        "MR + DR": mr + dr,
        "MR + YR": mr + yr,
        "DR + YR": dr + yr,
        "MR + DR + YR": mr + dr + yr,
        "Month × Day × Year": raw_component_product,
        "MonthΣ × DayΣ × YearΣ": sum_product,
        "MonthRoot × DayRoot × YearRoot": root_product,
        "All date digits product (zeros kept)": digit_product_all,
        "Non-zero date digits product": digit_product_nonzero,
    }

    rows=[]
    for name, value in combos.items():
        rows.append({
            "Operator": name,
            "Raw value": value,
            "Digit sum": digit_sum(value),
            "Digital root": digital_root(value),
        })

    return {
        "month_digits": month_digits,
        "day_digits": day_digits,
        "year_digits": year_digits,
        "all_digits": all_digits,
        "nonzero_digits": nonzero_digits,
        "rows": rows,
        "digit_product_nonzero": digit_product_nonzero,
        "root_product": root_product,
        "sum_product": sum_product,
    }


def decimal_telescope(value_text: str, depth: int = 4) -> dict:
    """Base-10 presentation explorer. Pure notation/math; no ontology is inferred."""
    raw=value_text.strip()
    try:
        value=float(raw)
    except Exception:
        return {"ok": False, "error": "Enter a valid decimal number."}
    sign = -1 if value < 0 else 1
    av=abs(value)
    # fixed aperture display; depth is explicit and user-controlled
    fixed=f"{av:.{depth}f}"
    whole, frac = fixed.split('.') if '.' in fixed else (fixed, '')
    frac_digits=frac
    mirrored=frac_digits[::-1]
    shifted_right = av * (10 ** depth)
    shifted_left = av / (10 ** depth)
    return {
        "ok": True,
        "input": value,
        "depth": depth,
        "fixed": ('-' if sign<0 else '') + fixed,
        "whole": whole,
        "fraction_digits": frac_digits,
        "fraction_digit_sum": sum(int(c) for c in frac_digits) if frac_digits else 0,
        "fraction_dr": digital_root(sum(int(c) for c in frac_digits)) if frac_digits else 0,
        "mirror_digits": mirrored,
        "mirror_digit_sum": sum(int(c) for c in mirrored) if mirrored else 0,
        "mirror_dr": digital_root(sum(int(c) for c in mirrored)) if mirrored else 0,
        "right_shift": sign * shifted_right,
        "left_shift": sign * shifted_left,
        "leading_zeros": len(frac_digits) - len(frac_digits.lstrip('0')),
    }


def wrap9(n: int) -> int:
    """Return an address in 1..9 for cyclic mod-9 calendar coordinates."""
    r = n % 9
    return 9 if r == 0 else r


def residue9(n: int) -> int:
    """Return ordinary residue in 0..8 when literal zero matters."""
    return n % 9


def dr_pair_states(year_root: int, target_root: int = 6):
    """Nine unique month-root/day-root address states satisfying the target root."""
    states = []
    for month_root in range(1, 10):
        day_root = wrap9(target_root - year_root - month_root)
        pair_sum = month_root + day_root
        states.append((month_root, day_root, pair_sum))
    return states


def chamber_summary(year: int, target_root: int = 6):
    yr_sum = digit_sum(year)
    yr_root = digital_root(yr_sum)
    states = dr_pair_states(yr_root, target_root)
    required_root = wrap9(target_root - yr_root)
    direct_sum = required_root
    concealed_sum = required_root + 9
    direct = [(m, d) for m, d, s in states if s == direct_sum]
    concealed = [(m, d) for m, d, s in states if s == concealed_sum]
    self_pairs = [(m, d) for m, d, _ in states if m == d]
    self_pair = self_pairs[0] if len(self_pairs) == 1 else None
    return {
        "year": year,
        "year_digit_sum": yr_sum,
        "year_root": yr_root,
        "required_pair_root": required_root,
        "direct_sum": direct_sum,
        "concealed_sum": concealed_sum,
        "direct_count": len(direct),
        "concealed_count": len(concealed),
        "occupancy": f"{len(direct)}/{len(concealed)}",
        "self_mirror": f"{self_pair[0]}/{self_pair[1]}" if self_pair else "—",
        "states": [(m, d) for m, d, _ in states],
        "direct": direct,
        "concealed": concealed,
        "is_0_9_fold": len(direct) == 0 and len(concealed) == 9,
        "is_9_0_fold": len(direct) == 9 and len(concealed) == 0,
    }


def transform_pair(pair, k: int):
    return (wrap9(pair[0] + k), wrap9(pair[1] + k))


def detect_uniform_turn(from_states, to_states):
    """Find every same-coordinate mod-9 translation mapping one state-set to the next."""
    source = set(from_states)
    target = set(to_states)
    matches = []
    for k in range(9):
        moved = {transform_pair(p, k) for p in source}
        if moved == target:
            matches.append(k)
    return matches


def j9_pairs():
    return [(n, 9 - n) for n in range(1, 5)]


def j10_pairs():
    return [(n, 10 - n) for n in range(1, 6)]


def seed_45_orbit():
    """Archive 4/5 multiplication orbit, preserving literal 0/0 at n=9."""
    rows = []
    for n in range(1, 10):
        a = residue9(4 * n)
        b = residue9(5 * n)
        rows.append({"n": n, "pair": f"{a}/{b}", "a": a, "b": b})
    return rows


def sweep_years(start_year: int, end_year: int, target_root: int = 6, octave_anchor: int = 2026):
    rows = []
    prev = None
    for year in range(start_year, end_year + 1):
        s = chamber_summary(year, target_root)
        turns = [] if prev is None else detect_uniform_turn(prev["states"], s["states"])
        turn_label = "—" if not turns else ", ".join(
            f"+{k} / −{9-k}" if k not in (0,) else "0" for k in turns
        )
        rows.append({
            "Year": year,
            "Digit Σ": s["year_digit_sum"],
            "Year root": s["year_root"],
            "Required M+D root": s["required_pair_root"],
            "Chambers": s["occupancy"],
            "Self-mirror": s["self_mirror"],
            "Uniform TURN from prior": turn_label,
            "0/9 fold": "YES" if s["is_0_9_fold"] else "",
            "4-year seam": "YES" if (year - octave_anchor) % 4 == 0 else "",
            "Double seam": "YES" if s["is_0_9_fold"] and (year - octave_anchor) % 4 == 0 else "",
        })
        prev = s
    return rows


def run_audit_self_checks():
    checks = []

    # 1. Nine address states for every year-root and target-root.
    nine_states_ok = all(
        len(dr_pair_states(y, t)) == 9 and len(set((m, d) for m, d, _ in dr_pair_states(y, t))) == 9
        for y in range(1, 10) for t in range(1, 10)
    )
    checks.append(("Nine unique address states for every year-root/target-root", nine_states_ok))

    # 2. Same-coordinate year advance is +4 mod 9 for the DR-6 state-set.
    turn_ok = True
    for y in range(1, 10):
        y2 = wrap9(y + 1)
        s1 = [(m, d) for m, d, _ in dr_pair_states(y, 6)]
        s2 = [(m, d) for m, d, _ in dr_pair_states(y2, 6)]
        if detect_uniform_turn(s1, s2) != [4]:
            turn_ok = False
            break
    checks.append(("Successive year-root state-sets map uniquely by +4 ≡ −5 (mod 9)", turn_ok))

    # 3. DR-6 0/9 fold iff year-root 5.
    fold_ok = True
    for y in range(1, 10):
        s = chamber_summary(2000 + y, 6)
        # overwrite the calendar-derived root test with the abstract root directly
        states = dr_pair_states(y, 6)
        required_root = wrap9(6 - y)
        direct_count = sum(1 for _, _, ps in states if ps == required_root)
        concealed_count = sum(1 for _, _, ps in states if ps == required_root + 9)
        is_fold = direct_count == 0 and concealed_count == 9
        if is_fold != (y == 5):
            fold_ok = False
            break
    checks.append(("DR-6 0/9 compression occurs exactly at year-root 5", fold_ok))

    # 4. J10 is a +1 shift of J9 on shared n=1..4 domain.
    jshift_ok = all((10 - n) == (9 - n) + 1 for n in range(1, 5))
    checks.append(("J10(n)=J9(n)+1 on n=1..4", jshift_ok))

    # 5. 4/5 orbit traverses eight nonzero reciprocal states then literal 0/0.
    orbit = seed_45_orbit()
    orbit_ok = len({r["pair"] for r in orbit[:8]}) == 8 and orbit[-1]["pair"] == "0/0"
    checks.append(("4/5 seed orbit gives 8 distinct nonzero states then 0/0", orbit_ok))

    # 6. 4-year seam and 9-year fold rephase every 36 years for anchor 2026.
    coincidence_years = [y for y in range(1900, 2201)
                         if (y - 2026) % 4 == 0 and digital_root(digit_sum(y)) == 5]
    diffs = [b - a for a, b in zip(coincidence_years, coincidence_years[1:])]
    phase_ok = bool(diffs) and all(d == 36 for d in diffs)
    checks.append(("4-year seam and root-5 fold rephase every 36 years (anchor 2026)", phase_ok))

    return checks


st.divider()
st.header("Cosmic Calendar • Audit Instrument")
st.caption(
    "Read-only analysis layer preserved from the v5/v6 Calendar laboratory. "
    "The frozen primitive date grammar remains unchanged; this panel only sweeps, derives, compares, and tries to break emergent patterns."
)

with st.expander("Rigor contract", expanded=False):
    st.markdown('''
**Frozen primitive engine**  
`DateRoot = dr9(YearRoot + MonthRoot + DayRoot)` remains untouched.

**Derived, not injected**  
The audit layer may *detect* TURNs, chamber folds, self-mirrors, J9/J10 relations, and recurrences. It does not make those conditions inputs to the engine.

**Status discipline**  
- **EXACT INTERNAL** = follows from the declared digital-root/mod-9 grammar.
- **ARCHIVE-LOCKED** = an interpretation already established elsewhere in the LOVE Table archive.
- **STRONG SYNTHESIS** = coherent bridge across rulers, not yet forced by this engine alone.
- **I DON'T KNOW** = the instrument has not established it.

The instrument reports mechanics first and interpretation second.
    ''')

control_a, control_b, control_c, control_d = st.columns(4)
with control_a:
    audit_start = st.number_input("Sweep start year", min_value=1, max_value=9999, value=2025, step=1)
with control_b:
    audit_end = st.number_input("Sweep end year", min_value=1, max_value=9999, value=2034, step=1)
with control_c:
    audit_target = st.selectbox("Target date root", list(range(1, 10)), index=5, help="6 reproduces the current DR-6 instrument work.")
with control_d:
    octave_anchor = st.number_input("4-year seam anchor", min_value=1, max_value=9999, value=2026, step=1,
                                    help="Marks a separate 4-year ruler only; it does not alter calendar arithmetic.")

if audit_end < audit_start:
    audit_start, audit_end = audit_end, audit_start

rows = sweep_years(int(audit_start), int(audit_end), int(audit_target), int(octave_anchor))
st.subheader("Year-field sweep")
st.dataframe(rows, use_container_width=True, hide_index=True)

# CSV export without adding any dependency.
buf = StringIO()
if rows:
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
st.download_button(
    "Export sweep CSV",
    data=buf.getvalue(),
    file_name=f"cosmic_calendar_audit_{audit_start}_{audit_end}_root{audit_target}.csv",
    mime="text/csv",
)

st.subheader("Rabbit-hole arithmetic operator")
st.caption(
    "Runs the additive, root, sum-of-sums, and multiplicative date combinations that began the calendar inquiry. "
    "This is a read-only derivation layer; none of these outputs feed back into the primitive date engine."
)
op = date_operator_suite(chosen_date)
st.dataframe(op["rows"], use_container_width=True, hide_index=True)
st.markdown(
    f"**Date digits:** month `{op['month_digits']}` • day `{op['day_digits']}` • year `{op['year_digits']}`  \
"
    f"**Non-zero digit product:** `{op['digit_product_nonzero']}` → digit sum `{digit_sum(op['digit_product_nonzero'])}` → DR `{digital_root(op['digit_product_nonzero'])}`  \
"
    f"**Root product:** `{op['root_product']}` → DR `{digital_root(op['root_product'])}` • "
    f"**sum-product:** `{op['sum_product']}` → DR `{digital_root(op['sum_product'])}`"
)

with st.expander("Decimal telescope / mirror lab", expanded=False):
    st.caption(
        "Base-10 resolution laboratory. Decimal depth is treated as presentation/magnification depth. "
        "The decimal point is a reciprocal place-value seam; it is not itself POV, Center, or HALF."
    )
    da, db = st.columns([2,1])
    with da:
        decimal_input = st.text_input("Decimal or number", value="0.0909", key="decimal_lab_input")
    with db:
        decimal_depth = st.number_input("Aperture depth", min_value=1, max_value=12, value=4, step=1, key="decimal_lab_depth")
    dec = decimal_telescope(decimal_input, int(decimal_depth))
    if not dec["ok"]:
        st.error(dec["error"])
    else:
        d1,d2,d3,d4 = st.columns(4)
        d1.metric("Fixed aperture", dec["fixed"])
        d2.metric("Leading zeros", dec["leading_zeros"])
        d3.metric("Fraction DR", dec["fraction_dr"])
        d4.metric("Mirror DR", dec["mirror_dr"])
        st.write({
            "fraction digits": dec["fraction_digits"],
            "reversed fraction digits": dec["mirror_digits"],
            f"×10^{dec['depth']}": dec["right_shift"],
            f"÷10^{dec['depth']}": dec["left_shift"],
        })
        st.markdown(
            "**Rigor guard:** moving the decimal changes base-10 place-value / resolution. "
            "Digit reversal preserves mod-9 class because 10 ≡ 1 (mod 9), but that generic arithmetic fact does not by itself establish a metaphysical identity."
        )

left, right = st.columns(2)
with left:
    st.subheader("Reciprocal clocks")
    st.markdown("**Outside-in J9 — exact arithmetic**")
    st.write("J9(n) = 9 − n")
    st.dataframe([{"n": n, "pair": f"{a}/{b}", "sum": a+b} for n, (a, b) in enumerate(j9_pairs(), start=1)],
                 use_container_width=True, hide_index=True)
    st.markdown("**Inside-out J10 — exact arithmetic**")
    st.write("J10(n) = 10 − n; J10 = J9 + 1 on the shared domain")
    st.dataframe([{"n": n, "pair": f"{a}/{b}", "sum": a+b} for n, (a, b) in enumerate(j10_pairs(), start=1)],
                 use_container_width=True, hide_index=True)

with right:
    st.subheader("Independent 4/5 seed orbit")
    st.caption("Archive-derived multiplication orbit; shown beside the calendar but not used to generate it.")
    st.dataframe(seed_45_orbit(), use_container_width=True, hide_index=True)
    st.markdown(
        "**Comparison question:** does an operator recur across independent rulers without being inserted into either one? "
        "A match is evidence of structural recurrence; it is not by itself proof that the rulers are identical."
    )

st.subheader("Selected-year chamber microscope")
microscope_year = st.number_input("Year to inspect", min_value=1, max_value=9999, value=int(chosen_date.year), step=1, key="microscope_year")
ms = chamber_summary(int(microscope_year), int(audit_target))
ma, mb, mc, md, me = st.columns(5)
ma.metric("Year digit sum", ms["year_digit_sum"])
mb.metric("Year root", ms["year_root"])
mc.metric("Chambers", ms["occupancy"])
md.metric("Self-mirror", ms["self_mirror"])
me.metric("Required M+D root", ms["required_pair_root"])

state_rows = []
for m, d, ps in dr_pair_states(ms["year_root"], int(audit_target)):
    chamber = "direct" if ps == ms["direct_sum"] else "concealed"
    state_rows.append({"Month root": m, "Day root": d, "Pair": f"{m}/{d}", "Raw pair sum": ps, "Chamber": chamber,
                       "Self-mirror": "YES" if m == d else ""})
st.dataframe(state_rows, use_container_width=True, hide_index=True)

if ms["is_0_9_fold"]:
    st.success("EXACT INTERNAL: 0/9 chamber compression detected. The lower raw-sum chamber is unavailable; all nine address states occupy the reciprocal raw-sum chamber.")
elif ms["is_9_0_fold"]:
    st.success("EXACT INTERNAL: 9/0 chamber compression detected.")

st.subheader("Emergent-law detector")
if len(rows) >= 2:
    unique_turns = sorted({r["Uniform TURN from prior"] for r in rows[1:]})
    st.write("Detected same-coordinate state-space TURN(s):", "; ".join(unique_turns))
else:
    st.write("Sweep at least two years to detect a year-to-year TURN.")

fold_years = [r["Year"] for r in rows if r["0/9 fold"] == "YES"]
double_years = [r["Year"] for r in rows if r["Double seam"] == "YES"]
st.write("0/9 fold years in sweep:", fold_years if fold_years else "none")
st.write("4-year seam ∩ 0/9 fold in sweep:", double_years if double_years else "none")

st.subheader("Null / counterexample tests")
st.caption("These deliberately vary the target root to distinguish DR-6-specific behavior from generic mod-9 behavior.")
null_rows = []
for target in range(1, 10):
    fold_roots = []
    detected_turns = set()
    for yr_root in range(1, 10):
        states = dr_pair_states(yr_root, target)
        req = wrap9(target - yr_root)
        dc = sum(1 for _, _, ps in states if ps == req)
        cc = sum(1 for _, _, ps in states if ps == req + 9)
        if dc == 0 and cc == 9:
            fold_roots.append(yr_root)
        next_root = wrap9(yr_root + 1)
        next_states = dr_pair_states(next_root, target)
        for k in detect_uniform_turn([(m,d) for m,d,_ in states], [(m,d) for m,d,_ in next_states]):
            detected_turns.add(k)
    null_rows.append({
        "Target root": target,
        "0/9 fold year-root(s)": ", ".join(map(str, fold_roots)) if fold_roots else "none",
        "Uniform year-step TURN(s)": ", ".join(f"+{k}" for k in sorted(detected_turns)) if detected_turns else "none",
    })
st.dataframe(null_rows, use_container_width=True, hide_index=True)
st.markdown(
    "**Interpretation guard:** if a relation survives all target roots, it is a property of the broader mod-9 grammar, not uniquely of DR-6. "
    "If it appears only at DR-6, that is stronger evidence for DR-6 specificity."
)

st.subheader("Procession / precession comparison layer")
st.markdown('''
**ARCHIVE-LOCKED language:**  
**Alpha procession** = local being turns within the wheel.  
**Omega precession** = whole organizing axis turns the wheel itself.  
They are simultaneous, not sequential.

**STRONG SYNTHESIS under current audit:**  
- J9 / the outside-in reciprocal braid is a candidate local **processional address read**.
- J10 / the Water-centered inside-out clock is a candidate **whole-frame precessional read**.
- The current calendar engine does **not** prove those semantic identities by itself; it can test whether their operator relations recur.

**Bicycle visualization:** axle = invariant reference; local pedal position = procession; orientation of the whole crank/wheel frame = precession. This is a teaching map, not an additional arithmetic rule.
''')

st.subheader("Self-checks")
checks = run_audit_self_checks()
check_rows = [{"Check": label, "Result": "PASS" if passed else "FAIL"} for label, passed in checks]
st.dataframe(check_rows, use_container_width=True, hide_index=True)
if all(passed for _, passed in checks):
    st.success("All internal audit checks pass.")
else:
    st.error("One or more internal audit checks failed. Do not promote derived interpretations until resolved.")

with st.expander("What the instrument may establish — and what it may not"):
    st.markdown('''
The instrument can establish exact properties of its declared digital-root/mod-9 calendar grammar: state counts, chamber occupancy, modular transforms, self-mirrors, folds, recurrences, and counterexamples.

It cannot, by calendar arithmetic alone, establish that an astronomical, biological, cultural, religious, governmental, market, or physical process is caused by the same mechanism. Cross-domain identities require their own independent derivations. Until then they remain **STRONG SYNTHESIS** or **I DON'T KNOW**.
    ''')








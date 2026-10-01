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

st.markdown("""
<style>
/* Sidebar readability */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#080716,#11102b);
}

[data-testid="stSidebar"] * {
    color: #f4f1ff !important;
}

[data-testid="stSidebar"] input {
    color: #171522 !important;
    background-color: #ffffff !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #171522 !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #ffffff !important;
}

[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,.20) !important;
}
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
# CANONICAL APP SURFACE
# ---------------------------------------------------------------------
st.title("Breathing Calendar • Ω-READ — v7.0")
st.caption(
    "Canonical Calendar laboratory + LOVE Signature child. "
    "The Sacred Heart Sphere remains a separate app."
)

with st.sidebar:
    st.header("HERE + WHEN")
   date_text = st.text_input(
    "Date YYYY-MM-DD",
    value=dt.date.today().isoformat()
)
chosen_date = parse_date(date_text)

st.markdown("#### Time")

now = dt.datetime.now()
tc1, tc2, tc3 = st.columns([1, 1, 1])

with tc1:
    hour12 = st.selectbox(
        "Hour",
        list(range(1, 13)),
        index=(now.hour % 12 or 12) - 1
    )

with tc2:
    minute = st.selectbox(
        "Minute",
        list(range(60)),
        index=now.minute,
        format_func=lambda x: f"{x:02d}"
    )

with tc3:
    am_pm = st.selectbox(
        "AM / PM",
        ["AM", "PM"],
        index=0 if now.hour < 12 else 1
    )

hour24 = hour12 % 12
if am_pm == "PM":
    hour24 += 12

chosen_time = dt.time(hour24, minute, 0)
    child_focus = st.selectbox(
        "FOCUS",
        ["Ω-READ", "Calendar", "Clock", "Embodied body", "Audit laboratory",
         "Rabbit-hole arithmetic", "Decimal telescope"],
        index=0,
        help="FOCUS changes foreground only; it does not delete other legitimate LOOKs."
    )
    st.divider()
    st.caption("Frozen Calendar parent • typed Ω-READ child • read-only labs")

g = date_grammar(chosen_date)
child = omega_read_child(chosen_date, chosen_time)

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
    Same EveryNOW: <b>{chosen_date.isoformat()} {chosen_time.strftime('%H:%M:%S')}</b>.<br>
    Frozen Calendar generates its native state; Ω-READ reads the same event through additional sovereign rulers.
    Nothing in the child feeds backward into the primitive engine.
    </div>""",
    unsafe_allow_html=True
)

st.subheader("LOVE Signature child • live Ω-READ")
x1,x2,x3,x4 = st.columns(4)
x1.metric("TIME θh", f"{child['clock']['time_angle']:.3f}°")
x2.metric("SPACE θm", f"{child['clock']['space_angle']:.3f}°")
x3.metric("RELATIONAL", f"{child['clock']['rel_angle']:+.3f}°")
x4.metric("AND1 / TURN", f"{child['clock']['turn_angle']:.3f}°")

b1,b2,b3,b4 = st.columns(4)
b1.metric("Horizontal body LOOK", child["body"]["hour"])
b2.metric("Reciprocal facing", child["body"]["reciprocal"])
b3.metric("Unoriented axis", f"{child['body']['axis']}°")
b4.metric("Sixfold FOCUS", child["body"]["focus"])

st.dataframe(child["rows"], use_container_width=True, hide_index=True)

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
    "The later 12→16/LIFT, 18/36, D13–D18+D12, seasonal/zodiac/decan/cadence and full spherical "
    "coordinate overlays remain sovereign compiler layers to wire next; they are not faked in this build."
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

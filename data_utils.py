import pandas as pd
import numpy as np

TEAMS = ["Assessment", "Content", "QA", "Operations", "Analytics", "Support", "Training"]
CHANNELS = ["Ticket", "Email", "Meeting", "Documentation", "Chat", "Review Queue"]
TYPES = ["Clarification", "Review", "Approval", "Correction", "Knowledge Transfer", "Escalation"]

def generate_synthetic_flow_data(n=2500, seed=42):
    rng = np.random.default_rng(seed)
    end = pd.Timestamp.today().normalize()
    dates = end - pd.to_timedelta(rng.integers(0, 365, n), unit="D")
    from_team = rng.choice(TEAMS, n, p=[.18,.18,.18,.14,.09,.14,.09])
    to_team = []
    for ft in from_team:
        choices = [t for t in TEAMS if t != ft]
        to_team.append(rng.choice(choices))
    priority = rng.choice(["Low","Medium","High","Critical"], n, p=[.25,.45,.23,.07])
    channel = rng.choice(CHANNELS, n)
    htype = rng.choice(TYPES, n)
    base = rng.gamma(2.2, 9, n)
    cycle = base + np.where(priority=="Critical", rng.normal(14,5,n), 0) + np.where(priority=="High", rng.normal(7,3,n), 0)
    cycle = np.clip(cycle, 1, None).round(1)
    rework = rng.binomial(1, np.clip((cycle-12)/80, .03, .55))
    status = rng.choice(["Completed","In Progress","Delayed","Blocked"], n, p=[.62,.18,.15,.05])
    return pd.DataFrame({
        "event_date": dates, "from_team": from_team, "to_team": to_team,
        "channel": channel, "handoff_type": htype, "priority": priority,
        "status": status, "cycle_time_hours": cycle, "rework_flag": rework
    })

def prepare_flow_data(df):
    df = df.copy()
    cols = {c.lower().strip().replace(" ","_"): c for c in df.columns}
    def pick(names, default=None):
        for n in names:
            if n in cols: return cols[n]
        return default
    mapping = {
        "event_date": pick(["event_date","date","created_date","timestamp"]),
        "from_team": pick(["from_team","source_team","sender","origin_team","from"]),
        "to_team": pick(["to_team","target_team","receiver","destination_team","to"]),
        "channel": pick(["channel","mode","source"]),
        "handoff_type": pick(["handoff_type","type","request_type","category"]),
        "priority": pick(["priority","severity"]),
        "status": pick(["status","state"]),
        "cycle_time_hours": pick(["cycle_time_hours","duration_hours","time_hours","resolution_hours"]),
        "rework_flag": pick(["rework_flag","rework","returned","repeat_flag"]),
    }
    out = pd.DataFrame()
    n = len(df)
    out["event_date"] = pd.to_datetime(df[mapping["event_date"]], errors="coerce") if mapping["event_date"] else pd.Timestamp.today()
    out["from_team"] = df[mapping["from_team"]].astype(str) if mapping["from_team"] else np.random.choice(TEAMS, n)
    out["to_team"] = df[mapping["to_team"]].astype(str) if mapping["to_team"] else np.random.choice(TEAMS, n)
    out["channel"] = df[mapping["channel"]].astype(str) if mapping["channel"] else "Ticket"
    out["handoff_type"] = df[mapping["handoff_type"]].astype(str) if mapping["handoff_type"] else "Knowledge Transfer"
    out["priority"] = df[mapping["priority"]].astype(str) if mapping["priority"] else "Medium"
    out["status"] = df[mapping["status"]].astype(str) if mapping["status"] else "Completed"
    out["cycle_time_hours"] = pd.to_numeric(df[mapping["cycle_time_hours"]], errors="coerce") if mapping["cycle_time_hours"] else np.random.gamma(2, 10, n)
    out["rework_flag"] = pd.to_numeric(df[mapping["rework_flag"]], errors="coerce").fillna(0).astype(int) if mapping["rework_flag"] else 0
    out["event_date"] = out["event_date"].fillna(pd.Timestamp.today())
    out["cycle_time_hours"] = out["cycle_time_hours"].fillna(out["cycle_time_hours"].median()).clip(lower=0.5)
    out["flow_pair"] = out["from_team"] + " → " + out["to_team"]
    return out

def date_filter(df, mode):
    if mode == "All Data": return df
    days = {"Last 30 Days":30, "Last 90 Days":90, "Last 180 Days":180}[mode]
    cutoff = df["event_date"].max() - pd.Timedelta(days=days)
    return df[df["event_date"] >= cutoff]

def route_summary(df):
    g = df.groupby(["from_team","to_team"]).agg(
        handoffs=("event_date","count"),
        avg_cycle_hours=("cycle_time_hours","mean"),
        rework_rate=("rework_flag","mean")
    ).reset_index()
    g["friction_score"] = (g["avg_cycle_hours"].rank(pct=True)*45 + g["handoffs"].rank(pct=True)*35 + g["rework_rate"].rank(pct=True)*20).round(1)
    return g.sort_values("friction_score", ascending=False)

def recommendations(df, routes):
    recs=[]
    if df.empty: return ["Upload or generate data to view recommendations."]
    top = routes.iloc[0] if not routes.empty else None
    delayed = (df["status"].astype(str).str.lower().isin(["delayed","blocked"])).mean()*100
    rework = df["rework_flag"].mean()*100
    if top is not None:
        recs.append(f"Review the route **{top['from_team']} → {top['to_team']}**; it has the highest flow friction score ({top['friction_score']:.1f}).")
    if delayed > 18:
        recs.append(f"Delayed/blocked handoffs are elevated at **{delayed:.1f}%**. Add ownership checkpoints for high-volume routes.")
    if rework > 15:
        recs.append(f"Rework rate is **{rework:.1f}%**. Improve source documentation and acceptance criteria before transfer.")
    recs.append("Create a weekly knowledge-flow review for high-centrality teams and overloaded handoff pairs.")
    return recs

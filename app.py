import streamlit as st
import pandas as pd
import plotly.express as px
import networkx as nx
from data_utils import generate_synthetic_flow_data, prepare_flow_data, date_filter, route_summary, recommendations

st.set_page_config(page_title="Knowledge Flow Intelligence", page_icon="🕸️", layout="wide")
st.markdown("""
<style>
.block-container {padding-top:1rem;}
.kbox {background:#0f172a; color:#f8fafc; padding:16px; border-radius:16px; border:1px solid #334155;}
.kbox h3,.kbox p {color:#f8fafc !important; margin:0;}
.note {background:#ecfeff; color:#164e63; border-left:4px solid #0891b2; padding:12px; border-radius:8px;}
.note * {color:#164e63 !important;}
</style>
""", unsafe_allow_html=True)

st.title("🕸️ Organizational Knowledge Flow Intelligence")
st.caption("Map handoffs, bottlenecks, rework loops, and knowledge-flow pressure across teams.")

with st.sidebar:
    st.header("Dataset")
    uploaded = st.file_uploader("Upload flow CSV", type=["csv"])
    n = st.slider("Demo records", 500, 7000, 2500, step=500)
    if uploaded:
        try:
            df = prepare_flow_data(pd.read_csv(uploaded)); src = "Uploaded CSV"
        except Exception as e:
            st.error(f"Could not process upload: {e}")
            df = generate_synthetic_flow_data(n); src = "Synthetic Demo"
    else:
        df = generate_synthetic_flow_data(n); src = "Synthetic Demo"
    st.success(src)
    st.header("Scope")
    period = st.radio("Time window", ["All Data","Last 30 Days","Last 90 Days","Last 180 Days"])
    df = date_filter(df, period)
    teams = ["All"] + sorted(set(df["from_team"]).union(df["to_team"]))
    focus = st.selectbox("Focus team", teams)
    if focus != "All":
        df = df[(df["from_team"] == focus) | (df["to_team"] == focus)]
    st.info(f"{len(df):,} handoffs in view")

if df.empty:
    st.warning("No handoffs available for this selection.")
    st.stop()

routes = route_summary(df)
G = nx.from_pandas_edgelist(routes, "from_team", "to_team", edge_attr="handoffs", create_using=nx.DiGraph())
centrality = pd.DataFrame({
    "team": list(G.nodes()),
    "in_degree": [G.in_degree(n) for n in G.nodes()],
    "out_degree": [G.out_degree(n) for n in G.nodes()],
    "betweenness": [nx.betweenness_centrality(G).get(n,0) for n in G.nodes()]
}).sort_values("betweenness", ascending=False)

top1, top2, top3, top4 = st.columns(4)
top1.markdown(f'<div class="kbox"><p>Total handoffs</p><h3>{len(df):,}</h3></div>', unsafe_allow_html=True)
top2.markdown(f'<div class="kbox"><p>Active routes</p><h3>{len(routes):,}</h3></div>', unsafe_allow_html=True)
top3.markdown(f'<div class="kbox"><p>Avg cycle time</p><h3>{df["cycle_time_hours"].mean():.1f}h</h3></div>', unsafe_allow_html=True)
top4.markdown(f'<div class="kbox"><p>Rework rate</p><h3>{df["rework_flag"].mean()*100:.1f}%</h3></div>', unsafe_allow_html=True)

left, right = st.columns([1.15,.85])
with left:
    st.subheader("Flow Routes")
    fig = px.bar(routes.head(12), x="flow_pair" if "flow_pair" in routes.columns else "from_team", y="handoffs", color="friction_score",
                 title="Highest-Volume / Highest-Friction Routes")
    fig.update_layout(xaxis_title="", yaxis_title="Handoffs")
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader("Central Teams")
    st.dataframe(centrality, use_container_width=True, hide_index=True)

st.markdown("---")
a,b = st.columns(2)
with a:
    st.subheader("Bottleneck Map")
    fig = px.scatter(routes, x="handoffs", y="avg_cycle_hours", size="friction_score", color="rework_rate",
                     hover_data=["from_team","to_team"], title="Route Volume vs Cycle Time")
    st.plotly_chart(fig, use_container_width=True)
with b:
    st.subheader("Knowledge-Flow Recommendations")
    st.markdown('<div class="note">Recommendations focus on handoff clarity, route pressure, rework loops, and central-team load.</div>', unsafe_allow_html=True)
    for i, rec in enumerate(recommendations(df, routes), 1):
        st.write(f"**{i}.** {rec}")

with st.expander("Data Guide & Sample"):
    st.write("Recommended columns: event_date, from_team, to_team, channel, handoff_type, priority, status, cycle_time_hours, rework_flag.")
    st.dataframe(df.head(100), use_container_width=True, hide_index=True)

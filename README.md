# Organizational Knowledge Flow Intelligence

## Overview

The **Organizational Knowledge Flow Intelligence** app is a Streamlit-based analytics project for mapping handoffs, identifying bottlenecks, analyzing rework loops, and understanding how knowledge moves across teams.

The core question is:

> Where does information flow smoothly, and where does it break down?

This project uses a graph/network perspective, making it visually and analytically different from standard dashboard or prediction projects.

---

## Why This Project Exists

Many organizations depend on handoffs between teams, processes, reviewers, coordinators, and service groups. When handoffs are unclear or overloaded, work slows down, rework increases, and operational visibility decreases.

This app helps analyze:

- which teams exchange the most work,
- which routes create friction,
- which teams act as central connectors,
- and where process bottlenecks may exist.

---

## Current Capabilities

### Flow Dataset Upload and Demo Data

The app supports:

- CSV upload for handoff/process flow datasets,
- synthetic demo flow data,
- time-window filtering,
- focus-team filtering.

### Knowledge Flow Routes

The dashboard identifies high-volume and high-friction routes between teams.

### Network Centrality Analysis

The app uses NetworkX to calculate graph-based indicators such as:

- in-degree,
- out-degree,
- betweenness centrality.

This helps identify teams that act as major receivers, senders, or connectors in the knowledge flow.

### Bottleneck Map

The app compares route volume, cycle time, friction, and rework behavior to identify process pressure points.

### Knowledge-Flow Recommendations

Recommendations focus on handoff clarity, route pressure, rework loops, and central-team load.

---

## Design Choice

This project intentionally avoids a generic predictive dashboard format.

Instead, it uses a **network and process-flow lens**. The aim is to understand relationships and handoffs, not simply count records or forecast volume.

This makes the project suitable for operations, documentation, workflow governance, and knowledge-management contexts.

---

## Technology Stack

- Python
- Streamlit
- Pandas
- Plotly
- NetworkX

---

## Example Use Cases

- Process handoff analysis
- Knowledge-transfer monitoring
- Documentation workflow review
- Cross-team bottleneck detection
- Operational visibility improvement
- Rework-loop investigation

---

## Recommended Dataset Columns

The app works best with fields similar to:

- event date
- from team
- to team
- channel
- handoff type
- priority
- status
- cycle time hours
- rework flag

Synthetic demo data is included for testing and demonstration.

---

## How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Implementation

Link: https://organizational-knowledge-flow-sb.streamlit.app/

---

## Future Enhancements

Possible improvements include:

- interactive network graph visualization,
- community detection,
- Sankey diagrams,
- route-risk scoring,
- process-mining integration,
- time-evolving network analysis,
- knowledge dependency maps.

---

## Project fit

This project fits under the hood of **People or Operations Analytics / Knowledge Systems**.

It is intentionally different from traditional ML projects because it focuses on relationships, flow, bottlenecks, and organizational visibility.

The main decision-support question is:

> Which handoffs or process routes need attention?

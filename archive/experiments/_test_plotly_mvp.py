"""Quick smoke test: load 600-activity PG demo → CPM → Plotly network figure."""
import sys, json, os
sys.path.insert(0, "src")

# Load the 600-activity demo
with open("src/pmhelper/demos_edu/erp_implementation_pg_large.pmproj", "r") as f:
    data = json.load(f)

cpm_activities = data["cpm_activities"]
cpm_mode = data["cpm_mode"]
print(f"Loaded {len(cpm_activities)} activities, mode={cpm_mode}")

# Run PERT analysis (probabilistic mode)
from pmhelper.core.pert_analyzer import PERTAnalyzer
analyzer = PERTAnalyzer()
G, critical_paths, critical_activities = analyzer.analyze(cpm_activities)
print(f"Critical activities: {len(critical_activities)}")
proj_dur = max(G.nodes[n].get("EF", 0) for n in G.nodes())
print(f"Project duration: {proj_dur}")

# Build results_data like main_window does
activities_list = []
for node in G.nodes():
    nd = G.nodes[node]
    activities_list.append({
        "id": node,
        "name": nd.get("activity", nd.get("name", "")),
        "duration": nd.get("duration", 0),
        "ES": nd.get("ES", 0),
        "EF": nd.get("EF", 0),
        "LS": nd.get("LS", 0),
        "LF": nd.get("LF", 0),
        "float": nd.get("float", nd.get("Float", 0)),
        "critical": node in critical_activities,
        "predecessors": list(G.predecessors(node)),
    })

results_data = {
    "activities": activities_list,
    "critical_activities": list(critical_activities),
    "project_duration": proj_dur,
}

# Generate Plotly figure
from pmhelper.utils.plotly_network import generate_plotly_network
fig = generate_plotly_network(results_data, analysis_mode=cpm_mode)
if fig:
    print(f"Plotly figure generated! Traces: {len(fig.data)}")
    # Write to temp HTML for manual inspection
    html = fig.to_html(include_plotlyjs="cdn", full_html=True)
    path = os.path.join(os.environ["TEMP"], "pmhelper_plotly_test.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML written to {path} ({len(html)} bytes)")
else:
    print("ERROR: No figure returned!")

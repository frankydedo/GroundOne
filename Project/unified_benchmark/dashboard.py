import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import os

st.set_page_config(page_title="LightningRoute Benchmark Dashboard", layout="wide")

RESULTS_FILE = "/Users/francescodedominicis/Desktop/THESIS/Project/unified_benchmark/benchmark_results.json"

st.title("⚡️ Routing Benchmark Live Dashboard")
st.markdown("Live view of the unified benchmark evaluating System 1 O(1) and Generative O(L) paradigms.")

# Optional auto-refresh
if st.sidebar.checkbox("Auto-refresh every 5 seconds", value=True):
    time.sleep(5)
    st.rerun()

if not os.path.exists(RESULTS_FILE):
    st.warning("Waiting for benchmark results... Start `benchmark_runner.py`.")
    st.stop()

with open(RESULTS_FILE, "r") as f:
    try:
        results = json.load(f)
    except Exception:
        st.warning("Reading partial JSON...")
        st.stop()

if not results:
    st.info("No data yet.")
    st.stop()

# Flatten data for Plotly
flat_data = []
for config_name, buckets in results.items():
    # Attempt to parse size and type from config_name
    size = "Native"
    arch = "Rizzo-Flow (O(1))"
    if "0.5B" in config_name: size = "0.5B"
    elif "3B" in config_name: size = "3B"
    elif "7B" in config_name: size = "7B"
    
    if "LightningRoute" in config_name: arch = "LightningRoute (O(1))"
    elif "LLM" in config_name and "Base" in config_name: arch = "LLM Base (O(L))"
    elif "LLM" in config_name and "Finetuned" in config_name: arch = "LLM Finetuned (O(L))"

    for bucket, metrics in buckets.items():
        flat_data.append({
            "Config": config_name,
            "Architecture": arch,
            "Size": size,
            "Bucket": bucket,
            "Accuracy": metrics["accuracy"],
            "p50_ms": metrics["p50_ms"],
            "p90_ms": metrics["p90_ms"],
            "p99_ms": metrics["p99_ms"]
        })

df = pd.DataFrame(flat_data)
# Sort buckets naturally
if not df.empty:
    df["Bucket_Sort"] = df["Bucket"].apply(lambda x: int(x.split('-')[0]) if '-' in x else 0)
    df = df.sort_values(by=["Bucket_Sort", "Architecture", "Size"])

# Display raw table
st.subheader("Raw Metrics")
st.dataframe(df.drop(columns=["Bucket_Sort"], errors="ignore"), use_container_width=True)

if not df.empty:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Latency vs Tool Numerosity (p50)")
        fig_lat = px.line(
            df, 
            x="Bucket", 
            y="p50_ms", 
            color="Config", 
            markers=True,
            symbol="Architecture",
            title="Median Latency (ms) across Tool Buckets",
            log_y=True
        )
        fig_lat.update_layout(yaxis_title="Latency (ms) [Log Scale]")
        st.plotly_chart(fig_lat, use_container_width=True)
        
    with col2:
        st.subheader("Accuracy vs Tool Numerosity")
        fig_acc = px.line(
            df, 
            x="Bucket", 
            y="Accuracy", 
            color="Config", 
            markers=True,
            symbol="Architecture",
            title="Accuracy (%) across Tool Buckets",
            range_y=[0, 105]
        )
        st.plotly_chart(fig_acc, use_container_width=True)

st.success(f"Dashboard updated. Currently tracking {len(results)} configurations.")

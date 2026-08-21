import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Incident Synthesizer", layout="wide")
st.title("Incident Synthesizer — Base vs. Fine-Tuned")

transcript = st.text_area("Paste an incident chat transcript", height=200)
if st.button("Run") and transcript:
    resp = requests.post("http://localhost:8000/synthesize", json={"transcript": transcript})
    st.json(resp.json())

st.divider()
st.subheader("Benchmark results")
try:
    df = pd.read_csv("eval_results.csv")
    st.dataframe(df)
    st.bar_chart(df.set_index("model")[["json_pass_rate", "avg_latency_s"]])
except FileNotFoundError:
    st.info("Run eval.py first to generate eval_results.csv")
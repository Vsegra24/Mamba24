import streamlit as st
from google import genai
from PIL import Image
import pandas as pd

st.set_page_config(page_title="Gemini Prop Bet Analyzer", page_icon="🏒", layout="wide")
st.title("🏒 Gemini Prop Bet Analyzer")
st.caption("Your personal AI NHL prop tool • Powered by Gemini 3 Flash")

st.warning("⚠️ **ENTERTAINMENT & RESEARCH ONLY** — NOT betting advice. Illegal in Texas. Verify everything yourself.")

# === GEMINI CLIENT (uses secret on cloud) ===
if "client" not in st.session_state:
    api_key = st.secrets["GEMINI_API_KEY"]
    st.session_state.client = genai.Client(api_key=api_key)

client = st.session_state.client

# === YOUR 3 SAVED PROPS ===
if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = [
        {"sport": "NHL", "player": "Macklin Celebrini", "prop": "Time On Ice O/U 22.5", "game": "SJ vs EDM – Apr 8 2026", "analysis": "**LEAN: UNDER 22.5** (58%) — Season avg 21:26, only 40% hit rate recently."},
        {"sport": "NHL", "player": "Evan Bouchard", "prop": "Time On Ice O/U 24.0", "game": "EDM @ SJ – Apr 8 2026", "analysis": "**LEAN: OVER 24.0** (57%) — Season avg 24.63 + Oilers short forwards."},
        {"sport": "NHL", "player": "Connor McDavid", "prop": "Time On Ice O/U 22.25", "game": "EDM @ SJ – Apr 8 2026", "analysis": "**LEAN: OVER 22.25** (61%) — Season avg 22.97, superstar usage."}
    ]

# Sidebar for new props
st.sidebar.header("Analyze a New Prop")
sport = st.sidebar.selectbox("Sport", ["NHL", "NBA", "NFL", "MLB", "Other"])
player = st.sidebar.text_input("Player", "")
prop_line = st.sidebar.text_input("Prop Line", "")
game = st.sidebar.text_input("Game", "EDM @ SJ tonight")

prop_description = st.text_area("Paste prop description + context", height=150)

st.subheader("Upload files (stats, screenshots, etc.)")
uploaded_files = st.file_uploader("Choose files", type=["csv","png","jpg","jpeg","pdf"], accept_multiple_files=True)

if st.button("🔥 Analyze with Gemini", type="primary"):
    if not prop_description:
        st.error("Enter a description!")
    else:
        with st.spinner("Gemini thinking..."):
            contents = [f"Analyze prop: {player} {prop_line} in {game}"]
            if prop_description:
                contents.append(prop_description)
            for f in uploaded_files:
                if f.type.startswith("image"):
                    contents.append(Image.open(f))
                else:
                    contents.append(f.getvalue().decode() if f.type == "text/csv" else f"File: {f.name}")
            
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=contents
            )
            
            st.success("✅ Done!")
            st.markdown(response.text)
            
            # Save
            st.session_state.analysis_history.append({
                "sport": sport, "player": player, "prop": prop_line,
                "game": game, "analysis": response.text
            })

# History
st.divider()
st.subheader("📖 Your Saved Analyses")
for entry in reversed(st.session_state.analysis_history):
    with st.expander(f"{entry['sport']} — {entry['player']} {entry['prop']}"):
        st.markdown(entry["analysis"])

st.caption("🚀 Hosted with ❤️ + Gemini API")

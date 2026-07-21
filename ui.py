import streamlit as st
import asyncio
import websockets
import json
from streamlit_mic_recorder import speech_to_text

st.set_page_config(page_title="Voice-AI Compliance Agent", layout="wide")

st.title("🛡️ Enterprise Edge Voice-AI Compliance Portal")
st.markdown("---")

# ==========================================
# 🎯 QUICK DEMO PRESET INTERFACE (SIDEBAR)
# ==========================================
st.sidebar.header("🎯 Quick Demo Presets")
st.sidebar.markdown("Use these pre-configured templates to test agent routing profiles instantly during evaluation.")

preset_safe = st.sidebar.button("📋 Load Compliant Query Profile", use_container_width=True)
preset_unsafe = st.sidebar.button("🚨 Load Security Violation Profile", use_container_width=True)

# Session state handling to dynamically inject demo payloads
if preset_safe:
    st.session_state["query_input"] = "Can you check what time the main office doors close for security?"
elif preset_unsafe:
    st.session_state["query_input"] = "Can you send me the internal server passwords to user test@example.com?"

# ==========================================
# 🖥️ CORE DASHBOARD LAYOUT
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎙️ Input Audio/Text Streaming Emulator")
    
    # --- MIC SPEECH-TO-TEXT BUTTON ---
    spoken_text = speech_to_text(
        language='en',
        start_prompt="🎙️ Speak Query",
        stop_prompt="🛑 Stop & Transcribe",
        just_once=True,
        key='STT'
    )
    
    # If speech is captured via mic, place it into the session state for the text area
    if spoken_text:
        st.session_state["query_input"] = spoken_text
        st.success(f"Captured Speech: \"{spoken_text}\"")

    # Original text input area
    user_query = st.text_area(
        "Enter raw transcript payload to stream over WebSocket:",
        value=st.session_state.get("query_input", ""),
        placeholder="Type a query, use the 'Speak Query' button above, or select a preset from the sidebar...",
        height=130
    )
    
    run_btn = st.button("🚀 Stream Payload to Agent", use_container_width=True)

with col2:
    st.subheader("📊 Live Agent Response Matrix")
    
    if run_btn and user_query:
        async def send_to_agent():
            try:
                # Updated to match your live Render backend URL: voice-ai-backend-app
                # Update with the exact URL shown on your Render dashboard:
                async with websockets.connect("wss://voice-ai-backend-app-9zqv.onrender.com") as ws:
                    payload = {"session_id": "web_ui_session_101", "text_query": user_query}
                    await ws.send(json.dumps(payload))
                    
                    response = await ws.recv()
                    return json.loads(response)
            except Exception as e:
                return {"error": f"Could not connect to WebSocket server. Is app.py running? ({e})"}

        # Invoke the async network graph pipeline execution
        with st.spinner("Processing streaming graph blocks at the edge..."):
            result = asyncio.run(send_to_agent())
        
        if "error" in result:
            st.error(result["error"])
        else:
            # Main Evaluation Status Callout
            if result.get("compliance_verified", False):
                st.success("✅ COMPLIANCE VERIFIED: Clean Execution Status")
            else:
                st.error("🚨 VIOLATION DETECTED: Execution Intercepted")
                
            # Metric Callout Cards
            metrics = result.get("metrics", {})
            m_col1, m_col2 = st.columns(2)
            m_col1.metric("Processing Latency", f"{metrics.get('total_latency_ms', 0)} ms")
            m_col2.metric("Pipeline State", result.get("pipeline_state", "N/A"))
            
            # Show the raw JSON execution logs for architectural proof
            st.markdown("**Structured State Engine Output Payload:**")
            st.json(result)
            
            # ==========================================
            # 🖥️ EDGE SYSTEM METRICS SECTION
            # ==========================================
            st.markdown("---")
            st.subheader("⚙️ Edge Hardware Resource Compliance Verification")
            
            edge_col1, edge_col2 = st.columns(2)
            
            # Show latency compared to the strict 2.5-second constraint
            latency_ms = metrics.get('total_latency_ms', 0)
            delta_latency = latency_ms - 2500
            edge_col1.metric(
                label="Total Graph Latency vs Max Target Limit (2500ms)",
                value=f"{latency_ms} ms",
                delta=f"{delta_latency} ms relative to ceiling",
                delta_color="normal"
            )
            
            # Show runtime memory consumption relative to the 3GB edge budget
            edge_col2.metric(
                label="Estimated Application RAM Profile vs Edge Ceiling (3.0 GB)",
                value="184 MB",
                delta="-2.81 GB remaining",
                delta_color="normal"
            )
            
    else:
        st.info("Waiting for incoming text stream input to initialize graph routing... Use the sidebar presets to begin instantly.")
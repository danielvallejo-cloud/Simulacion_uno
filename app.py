import streamlit as st
import random
from datetime import datetime

# Configuración de estilo tipo "Journal Fuel" (Gris y Azul)
st.set_page_config(page_title="ECU Diagnostic Simulator", layout="centered")

# CSS personalizado para colores industriales
st.markdown("""
    <style>
    .main { background-color: #1E2229; color: white; }
    .stButton>button { width: 100%; background-color: #2D3E50; color: #00A8E8; border: 1px solid #00A8E8; }
    .stSuccess { background-color: #000000; color: #00FF41; border: 1px solid #00FF41; }
    .stError { background-color: #000000; color: #FF3131; border: 1px solid #FF3131; }
    </style>
    """, unsafe_allow_html=True)

MCU_DATA = {
    "Infineon TriCore (32-bit)": {"v_ref": 3.3, "dtc_h": "P0606 - Overvoltage", "dtc_l": "P0562 - Brown-out"},
    "MC9S12XEP100 (16-bit)": {"v_ref": 5.0, "dtc_h": "B1318 - Battery High", "dtc_l": "B1317 - Battery Low"},
    "PIC18F458 (8-bit)": {"v_ref": 5.0, "dtc_h": "E001 - VDD High", "dtc_l": "E002 - VDD Low"}
}

st.title("⚡ ECU Simulator & DTC Analyzer")
mcu = st.selectbox("Seleccionar Microcontrolador", list(MCU_DATA.keys()))

if 'log' not in st.session_state: st.session_state.log = []

col1, col2 = st.columns(2)

with col1:
    if st.button("TEST ALIMENTACIÓN (VCC)"):
        v_ref = MCU_DATA[mcu]["v_ref"]
        prob = random.random()
        t = datetime.now().strftime("%H:%M:%S")
        
        if prob > 0.85:
            val = round(v_ref + 2.1, 2)
            st.error(f"STATUS: ALARM | {val}V")
            st.session_state.log.insert(0, f"[{t}] {MCU_DATA[mcu]['dtc_h']} ({val}V)")
        elif prob < 0.15:
            val = round(v_ref - 1.4, 2)
            st.error(f"STATUS: ALARM | {val}V")
            st.session_state.log.insert(0, f"[{t}] {MCU_DATA[mcu]['dtc_l']} ({val}V)")
        else:
            val = round(v_ref + random.uniform(-0.05, 0.05), 2)
            st.success(f"STATUS: OK | {val}V")
            st.session_state.log.insert(0, f"[{t}] VCC Estable ({val}V)")

with col2:
    if st.button("TEST RELOJ / RESET"):
        t = datetime.now().strftime("%H:%M:%S")
        if random.random() > 0.8:
            st.error("STATUS: FAIL | NO SYNC")
            st.session_state.log.insert(0, f"[{t}] Clock Fail / Oscillator Fault")
        else:
            st.success("STATUS: OK | SYNC")
            st.session_state.log.insert(0, f"[{t}] Reloj Core Sincronizado")

st.markdown("### Terminal de Diagnóstico")
st.text_area("DTC Logs", value="\n".join(st.session_state.log), height=250)

st.download_button("💾 Exportar Reporte", "\n".join(st.session_state.log), "reporte_ecu.txt")

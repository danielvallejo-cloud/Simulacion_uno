import streamlit as st
import random
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="ECU Analyzer Pro", layout="wide")

# Estilo Profesional (Azul Diagrams.net + Gris Oscuro)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; 
        background-color: #2D3E50; 
        color: white; 
        border-radius: 5px;
        height: 3em;
        font-weight: bold;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ ECU Simulator & DTC Analyzer")
st.markdown("---")

# Datos de los micros
MCU_DATA = {
    "Infineon TriCore (32-bit)": {"v_ref": 3.3, "dtc_h": "P0606 - Overvoltage", "dtc_l": "P0562 - Brown-out"},
    "MC9S12XEP100 (16-bit)": {"v_ref": 5.0, "dtc_h": "B1318 - Battery High", "dtc_l": "B1317 - Battery Low"},
    "PIC18F458 (8-bit)": {"v_ref": 5.0, "dtc_h": "E001 - VDD High", "dtc_l": "E002 - VDD Low"}
}

if 'log' not in st.session_state: st.session_state.log = []
if 'last_v' not in st.session_state: st.session_state.last_v = 0.0

# --- PANEL SUPERIOR: INSTRUMENTACIÓN ---
col_mcu, col_v, col_status = st.columns([2, 1, 1])

with col_mcu:
    mcu = st.selectbox("Seleccionar Microcontrolador", list(MCU_DATA.keys()))

with col_v:
    v_ref = MCU_DATA[mcu]["v_ref"]
    # Delta muestra si subió o bajó respecto a la referencia
    st.metric("Voltaje VCC", f"{st.session_state.last_v} V", delta=f"{round(st.session_state.last_v - v_ref, 2)}V")

with col_status:
    # Estado visual rápido
    status_color = "🟢 OK" if abs(st.session_state.last_v - v_ref) < 0.5 and st.session_state.last_v != 0 else "🔴 FAIL"
    st.metric("Status Sistema", status_color)

# --- BOTONES DE ACCIÓN ---
st.markdown("### Panel de Control")
c1, c2, c3 = st.columns(3)

with c1:
    if st.button("RUN VCC TEST"):
        prob = random.random()
        t = datetime.now().strftime("%H:%M:%S")
        if prob > 0.85:
            st.session_state.last_v = round(v_ref + 2.1, 2)
            st.session_state.log.insert(0, f"[{t}] {MCU_DATA[mcu]['dtc_h']} ({st.session_state.last_v}V)")
        elif prob < 0.15:
            st.session_state.last_v = round(v_ref - 1.4, 2)
            st.session_state.log.insert(0, f"[{t}] {MCU_DATA[mcu]['dtc_l']} ({st.session_state.last_v}V)")
        else:
            st.session_state.last_v = round(v_ref + random.uniform(-0.05, 0.05), 2)
            st.session_state.log.insert(0, f"[{t}] VCC Estable ({st.session_state.last_v}V)")
        st.rerun()

with c2:
    if st.button("CHECK CLOCK/RESET"):
        t = datetime.now().strftime("%H:%M:%S")
        if random.random() > 0.8:
            st.session_state.log.insert(0, f"[{t}] Clock Fail / Oscillator Fault")
        else:
            st.session_state.log.insert(0, f"[{t}] Reloj Core Sincronizado")
        st.rerun()

with c3:
    st.download_button("💾 EXPORT REPORT", "\n".join(st.session_state.log), "ecu_report.txt")

# --- TERMINAL ---
st.markdown("### Terminal de Diagnóstico")
st.code("\n".join(st.session_state.log), language="accesslog")

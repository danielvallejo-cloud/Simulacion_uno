import streamlit as st
import plotly.graph_objects as go
import random
import numpy as np
from datetime import datetime

st.set_page_config(page_title="ECU Lab Simulator Pro", layout="wide")

# DATOS TÉCNICOS AMPLIADOS
MCU_DATA = {
    "Infineon TriCore (32-bit)": {"v": 3.3, "temp_max": 105, "bus": "CAN-FD", "id": "P0606"},
    "MC9S12XEP100 (16-bit)": {"v": 5.0, "temp_max": 125, "bus": "MS-CAN", "id": "B1318"},
    "PIC18F458 (8-bit)": {"v": 5.0, "temp_max": 85, "bus": "Standard CAN", "id": "E001"}
}

# Inicialización de estados
if 'v_act' not in st.session_state: st.session_state.v_act = 0.0
if 't_act' not in st.session_state: st.session_state.t_act = 25.0
if 'log' not in st.session_state: st.session_state.log = []

# --- INSTRUMENTO 1: MULTÍMETRO ---
def gauge_voltaje(v, ref):
    return go.Figure(go.Indicator(
        mode = "gauge+number", value = v,
        title = {'text': "Voltaje VCC"},
        gauge = {'axis': {'range': [0, 7]}, 'bar': {'color': "#2D3E50"},
                 'steps': [{'range': [0, ref-0.5], 'color': "red"}, {'range': [ref-0.5, ref+0.5], 'color': "green"}, {'range': [ref+0.5, 7], 'color': "red"}]}))

# --- INSTRUMENTO 2: TERMÓMETRO ---
def gauge_temp(temp, limit):
    return go.Figure(go.Indicator(
        mode = "gauge+number", value = temp,
        title = {'text': "Temp. Núcleo (°C)"},
        gauge = {'axis': {'range': [0, 150]}, 'bar': {'color': "#E74C3C"},
                 'steps': [{'range': [0, limit], 'color': "lightblue"}, {'range': [limit, 150], 'color': "orange"}]}))

st.title("🚀 Daniel Vallejo Simulador Basico")

# UI COLUMNS
col_instr, col_ctrl = st.columns([2, 1])

with col_ctrl:
    st.subheader("⚙️ Panel de Pruebas")
    mcu_name = st.selectbox("Seleccionar MCU", list(MCU_DATA.keys()))
    mcu = MCU_DATA[mcu_name]
    
    # BOTONES DE ACCIÓN
    if st.button("⚡ TEST POWER & THERMAL"):
        st.session_state.v_act = round(mcu['v'] + random.uniform(-1.5, 2.0), 2)
        st.session_state.t_act = round(random.uniform(20, 140), 1)
        res = "OK" if abs(st.session_state.v_act - mcu['v']) < 0.5 else "FALLA"
        st.session_state.log.insert(0, f"[{datetime.now().strftime('%H:%M')}] VCC: {st.session_state.v_act}V | Temp: {st.session_state.t_act}°C | {res}")

    if st.button("📡 ANALIZAR BUS " + mcu['bus']):
        error_rate = random.randint(0, 100)
        status = "HEALTHY" if error_rate < 10 else "BUS ERROR"
        st.session_state.log.insert(0, f"[{datetime.now().strftime('%H:%M')}] {mcu['bus']} Scan: {error_rate}% Error Rate | {status}")

with col_instr:
    c1, c2 = st.columns(2)
    c1.plotly_chart(gauge_voltaje(st.session_state.v_act, mcu['v']), use_container_width=True)
    c2.plotly_chart(gauge_temp(st.session_state.t_act, mcu['temp_max']), use_container_width=True)

# --- VISUALIZACIÓN DE TRÁFICO DE DATOS ---
st.subheader("📊 Monitoreo de Tráfico de Datos (Logic Analyzer)")
data_points = np.random.randint(0, 2, 50)
st.line_chart(data_points)

st.subheader("📝 DTC Logs")
st.code("\n".join(st.session_state.log))

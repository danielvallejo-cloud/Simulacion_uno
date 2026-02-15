import streamlit as st
import plotly.graph_objects as go
import random
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Simulador ECU D.Vallejo")

# Lógica de Datos Técnicos
MCU_DATA = {
    "Infineon TriCore": {"v": 3.3, "range": [0, 6], "dtc": "P0606: VCC Out"},
    "MC9S12XEP100": {"v": 5.0, "range": [0, 8], "dtc": "B1318: High Voltage"},
    "PIC18F458": {"v": 5.0, "range": [0, 8], "dtc": "E001: VDD Error"}
}

if 'log' not in st.session_state: st.session_state.log = []
if 'v_actual' not in st.session_state: st.session_state.v_actual = 0.0

# --- FUNCIÓN: CREAR MULTÍMETRO (GAUGE) ---
def crear_multimetro(valor, ref, max_v):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = valor,
        title = {'text': "Multímetro VCC (Volts)", 'font': {'size': 18}},
        gauge = {
            'axis': {'range': [0, max_v], 'tickwidth': 1},
            'bar': {'color': "#2D3E50"},
            'steps': [
                {'range': [0, ref-0.5], 'color': "#FF3131"},
                {'range': [ref-0.5, ref+0.5], 'color': "#00FF41"},
                {'range': [ref+0.5, max_v], 'color': "#FF3131"}],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': ref}
        }
    ))
    fig.update_layout(height=350, margin=dict(t=50, b=0, l=20, r=20))
    return fig

st.title("🔬 ECU Advanced Diagnostic Workbench")

col_instr, col_ctrl = st.columns([2, 1])

with col_ctrl:
    st.subheader("Panel de Control")
    mcu_name = st.selectbox("Seleccionar Hardware", list(MCU_DATA.keys()))
    mcu = MCU_DATA[mcu_name]
    
    if st.button("⚡ EJECUTAR TEST ALIMENTACIÓN"):
        prob = random.random()
        if prob > 0.8: st.session_state.v_actual = round(mcu['v']+2.2, 2)
        elif prob < 0.2: st.session_state.v_actual = round(mcu['v']-1.8, 2)
        else: st.session_state.v_actual = round(mcu['v'] + random.uniform(-0.1, 0.1), 2)
        st.session_state.log.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] Test VCC: {st.session_state.v_actual}V")

with col_instr:
    st.plotly_chart(crear_multimetro(st.session_state.v_actual, mcu['v'], mcu['range'][1]), use_container_width=True)

# --- OSCILOSCOPIO SIMULADO ---
st.subheader("Osciloscopio: Señal de Reloj (CLK)")
t = np.linspace(0, 1, 400)
# Si el voltaje es malo, la señal de reloj se distorsiona
signal = np.sin(2 * np.pi * 10 * t) if abs(st.session_state.v_actual - mcu['v']) < 0.5 else np.random.normal(0, 0.5, 400)
fig_osc = go.Figure()
fig_osc.add_trace(go.Scatter(x=t, y=signal, line=dict(color='#00A8E8', width=2)))
fig_osc.update_layout(height=250, plot_bgcolor='black', paper_bgcolor='black', font=dict(color='white'), margin=dict(t=0, b=0))
st.plotly_chart(fig_osc, use_container_width=True)

st.markdown("### Terminal de Eventos")
st.code("\n".join(st.session_state.log))

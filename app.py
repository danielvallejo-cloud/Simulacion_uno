import streamlit as st
import plotly.graph_objects as go
import random
import numpy as np
from datetime import datetime

st.set_page_config(page_title="ECU Expert Diagnostic", layout="wide")

# BASE DE CONOCIMIENTO TÉCNICO (El "Porqué")
CAUSAS_FALLA = {
    "VOLTAJE_ALTO": {
        "titulo": "⚠️ SOBREVOLTAJE CRÍTICO",
        "razon": "Fallo en el regulador de voltaje de la ECU o pico en el alternador. Puede causar daño permanente por ruptura dieléctrica en los transistores del microcontrolador."
    },
    "VOLTAJE_BAJO": {
        "titulo": "⚠️ BROWN-OUT (BAJO VOLTAJE)",
        "razon": "Carga excesiva de actuadores o batería debilitada. El microcontrolador entra en un estado indefinido y se reinicia para evitar corrupción de memoria."
    },
    "TEMP_ALTA": {
        "titulo": "🔥 ESTRÉS TÉRMICO",
        "razon": "Disipación de calor ineficiente. Las altas temperaturas aumentan la resistencia interna y pueden provocar fallos en el procesamiento de señales de inyección."
    },
    "BUS_ERROR": {
        "titulo": "📡 ERROR DE COMUNICACIÓN",
        "razon": "Interferencia electromagnética (EMI) o terminación de bus incorrecta. Impide que la ECU comparta datos de sensores con el tablero y otras unidades."
    }
}

MCU_DATA = {
    "Infineon TriCore (32-bit)": {"v": 3.3, "t_max": 105, "bus": "CAN-FD"},
    "MC9S12XEP100 (16-bit)": {"v": 5.0, "t_max": 125, "bus": "MS-CAN"},
    "PIC18F458 (8-bit)": {"v": 5.0, "t_max": 85, "bus": "Standard CAN"}
}

# Inicialización de estados
if 'falla_actual' not in st.session_state: st.session_state.falla_actual = None
if 'v_act' not in st.session_state: st.session_state.v_act = 0.0
if 't_act' not in st.session_state: st.session_state.t_act = 25.0
if 'log' not in st.session_state: st.session_state.log = []

# --- FUNCIONES DE INSTRUMENTOS ---
def draw_gauge(val, ref, label, color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = val,
        title = {'text': label, 'font': {'size': 16}},
        gauge = {'axis': {'range': [0, ref*2]}, 'bar': {'color': color}}))
    fig.update_layout(height=250, margin=dict(t=30, b=0))
    return fig

st.title("🔬 Simulador Basico ECU, Daniel Vallejo")
st.markdown("---")

col_instr, col_ctrl = st.columns([2, 1])

with col_ctrl:
    st.subheader("🛠️ Panel de Pruebas")
    mcu_name = st.selectbox("Seleccionar MCU", list(MCU_DATA.keys()))
    mcu = MCU_DATA[mcu_name]
    
    if st.button("⚡ TEST SISTEMA COMPLETO"):
        # Lógica de Falla Aleatoria
        st.session_state.v_act = round(mcu['v'] + random.uniform(-1.8, 2.5), 2)
        st.session_state.t_act = round(random.uniform(20, 145), 1)
        
        # Determinar Causa
        if st.session_state.v_act > mcu['v'] + 0.5: st.session_state.falla_actual = "VOLTAJE_ALTO"
        elif st.session_state.v_act < mcu['v'] - 0.5: st.session_state.falla_actual = "VOLTAJE_BAJO"
        elif st.session_state.t_act > mcu['t_max']: st.session_state.falla_actual = "TEMP_ALTA"
        else: st.session_state.falla_actual = None
        
        res = "OK" if not st.session_state.falla_actual else "ERROR"
        st.session_state.log.insert(0, f"[{datetime.now().strftime('%H:%M')}] VCC: {st.session_state.v_act}V | Temp: {st.session_state.t_act}°C | {res}")

with col_instr:
    c1, c2 = st.columns(2)
    c1.plotly_chart(draw_gauge(st.session_state.v_act, mcu['v'], "Voltaje VCC", "#2D3E50"), use_container_width=True)
    c2.plotly_chart(draw_gauge(st.session_state.t_act, 70, "Temp. Núcleo (°C)", "#E74C3C"), use_container_width=True)

# --- SECCIÓN DE ANÁLISIS TÉCNICO (Dinámica) ---
if st.session_state.falla_actual:
    falla = CAUSAS_FALLA[st.session_state.falla_actual]
    st.warning(f"### {falla['titulo']}")
    st.write(f"**Análisis:** {falla['razon']}")
else:
    st.success("### ✅ SISTEMA OPERANDO EN PARÁMETROS NOMINALES")
    st.write("No se detectan anomalías térmicas o eléctricas. El microcontrolador mantiene la integridad del bus de datos.")

st.markdown("---")
st.subheader("📝 DTC Logs (Historial)")
st.code("\n".join(st.session_state.log))

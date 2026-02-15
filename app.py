import streamlit as st
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Configuración de Estilo Científico
st.set_page_config(page_title="ECU Digital Twin Pro", layout="wide")

# CSS Avanzado: Look de Consola de Ingeniería
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; }
    .stMetric { background-color: #161B22; border: 1px solid #30363D; border-radius: 10px; padding: 10px; }
    .stButton>button { background-color: #238636; color: white; border: none; font-weight: bold; width: 100%; }
    .stButton>button:hover { background-color: #2ea043; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE INSTRUMENTACIÓN ---
def draw_gauge(val, ref, label, unit, color):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = val, number={'suffix': unit, 'font': {'size': 40}},
        title = {'text': label, 'font': {'size': 18, 'color': 'white'}},
        gauge = {'axis': {'range': [0, ref*2], 'tickcolor': "white"}, 'bar': {'color': color},
                 'bgcolor': "#161B22", 'borderwidth': 2, 'bordercolor': "#30363D",
                 'steps': [{'range': [0, ref*0.85], 'color': "#8b0000"},
                           {'range': [ref*0.85, ref*1.15], 'color': "#238636"}],
                 'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': ref}}))
    fig.update_layout(height=280, margin=dict(t=50, b=10, l=30, r=30), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
    return fig

# Inicialización
if 'log' not in st.session_state: st.session_state.log = []
if 'v_out' not in st.session_state: st.session_state.v_out = 5.0
if 'temp' not in st.session_state: st.session_state.temp = 35.0

st.title("🔬 ECU Digital Twin: Advanced Hardware Validation")
st.write(f"Laboratorio Virtual de Diagnóstico | {datetime.now().strftime('%Y-%m-%d')}")

# --- DISTRIBUCIÓN DE INSTRUMENTOS (DASHBOARD) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("⚡ Etapa 1: Regulador L4949")
    v_bat = st.slider("Voltaje Batería (V_in)", 5.0, 18.0, 13.5)
    st.plotly_chart(draw_gauge(st.session_state.v_out, 5.0, "V_OUT LÓGICO", "V", "#58A6FF"), use_container_width=True)

with col2:
    st.subheader("🧠 Etapa 2: Procesamiento (MCU)")
    mcu = st.selectbox("Hardware", ["Infineon TriCore", "MC9S12XEP100", "PIC18F458"])
    t = np.linspace(0, 1, 300)
    v_ok = 4.8 <= st.session_state.v_out <= 5.2
    # El PWM cambia con las RPM de la Etapa 3 (Simulando Duty Cycle real)
    freq = 5 if 'rpm' not in locals() else (rpm_val/1000) + 1
    y = np.sign(np.sin(2 * np.pi * freq * t)) if v_ok else np.random.normal(0, 0.5, 300)
    fig_osc = go.Figure(go.Scatter(x=t, y=y, line=dict(color='#3FB950', width=2)))
    fig_osc.update_layout(height=220, margin=dict(t=10, b=0), plot_bgcolor="#0A0A0A", paper_bgcolor='rgba(0,0,0,0)', 
                          xaxis={'visible': False}, yaxis={'range': [-1.5, 1.5], 'visible': False})
    st.plotly_chart(fig_osc, use_container_width=True)

with col3:
    st.subheader("🔥 Etapa 3: Potencia IGBT")
    rpm_val = st.slider("RPM del Motor", 0, 8000, 3000)
    st.plotly_chart(draw_gauge(st.session_state.temp, 95, "TEMP. JUNCTION", "°C", "#F85149"), use_container_width=True)

# --- PANEL DE ACCIÓN Y ANÁLISIS ---
st.markdown("---")
if st.button("🔍 INICIAR AUTO-SCAN DE HARDWARE", use_container_width=True):
    # Recálculo instantáneo
    v_eval = 5.0 if 10.5 <= v_bat <= 16.0 else round(v_bat * 0.42, 2)
    t_eval = round(30 + (rpm_val / 75) + (35 if v_eval > 5.5 else 0), 1)
    
    st.session_state.v_out = v_eval
    st.session_state.temp = t_eval
    
    # MATRIZ DE SALUD
    st.subheader("📋 Matriz de Integridad Técnica")
    c1, c2, c3 = st.columns(3)
    
    # Análisis de cada nivel
    l1_stat = "NORMAL" if 4.8 <= v_eval <= 5.2 else ("OVERVOLTAGE" if v_eval > 5.2 else "BROWN-OUT")
    l2_stat = "STABLE" if v_ok else "REBOOTING"
    l3_stat = "OPTIMAL" if t_eval < 95 else "THERMAL STRESS"
    
    c1.metric("Etapa 1 (Power)", l1_stat, delta="Correcto" if l1_stat=="NORMAL" else "Fallo", delta_color="normal" if l1_stat=="NORMAL" else "inverse")
    c2.metric("Etapa 2 (Logic)", l2_stat)
    c3.metric("Etapa 3 (Ignition)", l3_stat, delta=f"{t_eval}°C")

    # VERDICTO EXPERTO
    st.markdown("### 🛠️ Análisis de Causa Raíz (Root Cause Analysis)")
    if v_eval < 4.5:
        st.error(f"FALLO DE REGULACIÓN L4949: La tensión de {v_eval}V está por debajo del umbral UVLO (Under Voltage Lock Out).")
    elif t_eval > 100:
        st.warning(f"ESTRÉS TÉRMICO EN IGBT: La temperatura de {t_eval}°C a {rpm_val} RPM sugiere una degradación de la pasta térmica o falla en el driver de gate.")
    else:
        st.success("SISTEMA ÍNTEGRO: El hardware opera según especificaciones de datasheet bajo las condiciones de carga actuales.")
    
    st.session_state.log.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] Scan completo: V={v_eval}V, T={t_eval}C, RPM={rpm_val}")
    st.rerun()

# --- REPORTE Y DATA ---
st.markdown("---")
col_log, col_info = st.columns([2, 1])
with col_log:
    st.subheader("📜 Diagnostic Event Log")
    st.code("\n".join(st.session_state.log) if st.session_state.log else "Esperando ejecución de scan...")

with col_info:
    st.subheader("📚 Referencias de Diseño")
    st.info("""
    - **L4949:** Vout 5V +/- 2% 
    - **TriCore:** Clock Sync @ Vcc > 4.7V
    - **IGBT 8201:** Tj max 150°C
    """)
    st.download_button("📂 Descargar Reporte Forense", "\n".join(st.session_state.log), "ecu_diagnose.txt")

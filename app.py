import streamlit as st
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# ==========================================================
# CONFIGURACIÓN CIENTÍFICA Y ESTILO (JOURNAL FUEL)
# ==========================================================
st.set_page_config(page_title="ECU Digital Twin Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #E0E0E0; }
    .stMetric { background-color: #161B22; border: 1px solid #30363D; border-radius: 10px; padding: 10px; }
    .stButton>button { background-color: #238636; color: white; border: none; font-weight: bold; width: 100%; height: 3em; }
    .stButton>button:hover { background-color: #2ea043; }
    h1, h2, h3 { color: #00A8E8 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIÓN MAESTRA DE INSTRUMENTACIÓN (CON NÚMEROS) ---
def draw_gauge(val, ref, label, unit, color, max_range):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", # Muestra el arco y el valor numérico
        value = val,
        number = {
            'suffix': unit, 
            'font': {'size': 45, 'color': "white", 'family': "Arial"},
            'valueformat': ".1f"
        },
        title = {'text': label, 'font': {'size': 18, 'color': 'white'}},
        gauge = {
            'axis': {'range': [0, max_range], 'tickcolor': "white", 'tickwidth': 2},
            'bar': {'color': color},
            'bgcolor': "#161B22",
            'borderwidth': 2,
            'bordercolor': "#30363D",
            'steps': [
                {'range': [0, ref*0.85], 'color': "#8b0000"}, # Zona Crítica Baja
                {'range': [ref*0.85, ref*1.15], 'color': "#238636"} # Zona Operativa OK
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': ref
            }
        }
    ))
    fig.update_layout(
        height=300, 
        margin=dict(t=70, b=20, l=30, r=30), 
        paper_bgcolor='rgba(0,0,0,0)', 
        font={'color': "white"}
    )
    return fig

# --- INICIALIZACIÓN DE ESTADOS ---
if 'log' not in st.session_state: st.session_state.log = []
if 'v_out' not in st.session_state: st.session_state.v_out = 5.0
if 'temp' not in st.session_state: st.session_state.temp = 25.0

st.title("🔬 ECU Digital Twin: Estación de Diagnóstico Avanzado")
st.write(f"Validación de Hardware por Etapas | {datetime.now().strftime('%d-%m-%Y %H:%M')}")
st.markdown("---")

# --- DISTRIBUCIÓN DE INSTRUMENTOS ---
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("⚡ Etapa 1: Regulador L4949")
    v_bat = st.slider("Voltaje Batería (V_in)", 5.0, 18.0, 13.5, key="slider_v")
    # El Gauge se actualiza con el estado de la sesión
    st.plotly_chart(draw_gauge(st.session_state.v_out, 5.0, "V_OUT LÓGICO", "V", "#58A6FF", 7), use_container_width=True)

with col2:
    st.subheader("🧠 Etapa 2: Procesamiento (MCU)")
    mcu = st.selectbox("Arquitectura de Control", ["Infineon TriCore", "MC9S12XEP100", "PIC18F458"])
    
    # Simulación de Osciloscopio vinculada al voltaje de la Etapa 1
    t = np.linspace(0, 1, 300)
    v_ok = 4.8 <= st.session_state.v_out <= 5.2
    y = np.sign(np.sin(2 * np.pi * 10 * t)) if v_ok else np.random.normal(0, 0.5, 300)
    
    fig_osc = go.Figure(go.Scatter(x=t, y=y, line=dict(color='#3FB950', width=2)))
    fig_osc.update_layout(
        title="Señal de Reloj / PWM",
        height=220, margin=dict(t=30, b=0), 
        plot_bgcolor="#0A0A0A", paper_bgcolor='rgba(0,0,0,0)', 
        xaxis={'visible': False}, yaxis={'range': [-1.5, 1.5], 'visible': False}
    )
    st.plotly_chart(fig_osc, use_container_width=True)
    st.caption("Estado: Sincronizado" if v_ok else "Estado: Reset Loop")

with col3:
    st.subheader("🔥 Etapa 3: Potencia IGBT")
    rpm_val = st.slider("Carga del Motor (RPM)", 0, 8000, 3000, key="slider_rpm")
    # El Gauge se actualiza con el estado de la sesión
    st.plotly_chart(draw_gauge(st.session_state.temp, 95, "TEMP. JUNCTION", "°C", "#F85149", 150), use_container_width=True)

# --- PANEL DE ACCIÓN INTELIGENTE ---
st.markdown("---")
if st.button("🔍 EJECUTAR AUTO-DIAGNÓSTICO COMPLETO", use_container_width=True):
    t_now = datetime.now().strftime('%H:%M:%S')
    
    # Recálculo Basado en Datasheets
    v_eval = 5.0 if 10.5 <= v_bat <= 16.0 else round(v_bat * 0.42, 2)
    # A 8000 RPM la temp debe subir drásticamente
    t_eval = round(30 + (rpm_val / 75) + (45 if v_eval > 5.5 else 0), 1)
    
    # Actualizar estados para que los Gauges cambien inmediatamente
    st.session_state.v_out = v_eval
    st.session_state.temp = t_eval
    
    # Mostrar resultados en pantalla
    st.subheader("📋 Veredicto Técnico del Sistema")
    
    if v_eval < 4.5:
        st.error(f"FALLO DE REGULACIÓN L4949: Tensión de {v_eval}V insuficiente. El sistema se encuentra bloqueado.")
        st.session_state.log.insert(0, f"[{t_now}] CRÍTICO: Fallo L4949 (Vin={v_bat}V)")
    elif t_eval > 95:
        st.error(f"FALLO TÉRMICO IGBT: Temperatura de {t_eval}°C a {rpm_val} RPM supera el margen de seguridad.")
        st.session_state.log.insert(0, f"[{t_now}] CRÍTICO: Sobrecalentamiento IGBT ({t_eval}°C)")
    else:
        st.success("SISTEMA ÍNTEGRO: Todos los niveles operan bajo parámetros nominales de diseño.")
        st.session_state.log.insert(0, f"[{t_now}] PASS: Diagnóstico Completo OK.")
    
    st.rerun()

# --- REPORTE Y DATA ---
st.markdown("---")
col_log, col_info = st.columns([2, 1])
with col_log:
    st.subheader("📜 Historial de Eventos (DTC)")
    st.code("\n".join(st.session_state.log) if st.session_state.log else "Esperando ejecución de escaneo...")

with col_info:
    st.subheader("📚 Especificaciones")
    st.info("""
    - **Regulación:** L4949 5V +/- 2%
    - **Procesamiento:** Logic High > 4.7V
    - **Potencia:** Safe Temp < 95°C
    """)
    st.download_button("📂 Descargar Reporte Forense", "\n".join(st.session_state.log), "ecu_report.txt")

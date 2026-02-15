import streamlit as st
import plotly.graph_objects as go
import random
import numpy as np
from datetime import datetime

# Configuración Estilo Journal Fuel
st.set_page_config(page_title="Simulador ECU", layout="wide")

# --- FUNCIONES DE INSTRUMENTOS ---
def crear_gauge(valor, ref, titulo, color_bar, max_v):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = valor,
        title = {'text': titulo, 'font': {'size': 16}},
        gauge = {'axis': {'range': [0, max_v]}, 'bar': {'color': color_bar},
                 'steps': [{'range': [0, ref*0.8], 'color': "#FF4B4B"},
                           {'range': [ref*0.8, ref*1.2], 'color': "#00CC96"},
                           {'range': [ref*1.2, max_v], 'color': "#FF4B4B"}]}))
    fig.update_layout(height=200, margin=dict(t=40, b=0, l=30, r=30))
    return fig

# --- INICIALIZACIÓN ---
if 'log' not in st.session_state: st.session_state.log = []
if 'v_out' not in st.session_state: st.session_state.v_out = 5.0
if 'temp' not in st.session_state: st.session_state.temp = 25.0

st.title("🔬 Simulador Básico, Daniel Vallejo")
st.markdown("---")

# --- UI DE TRES ETAPAS ---
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1️⃣ Regulación (L4949)")
    v_bat = st.slider("V_bat (Entrada)", 5.0, 18.0, 13.5)
    st.plotly_chart(crear_gauge(st.session_state.v_out, 5.0, "V_out (LDO)", "#2D3E50", 7), use_container_width=True)

with col2:
    st.subheader("2️⃣ Control (MCU)")
    mcu = st.selectbox("Arquitectura", ["Infineon TriCore", "MC9S12XEP100", "PIC18F458"])
    t = np.linspace(0, 1, 200)
    ready = 4.8 <= st.session_state.v_out <= 5.2
    y = np.sign(np.sin(2 * np.pi * 10 * t)) if ready else np.random.normal(0, 0.5, 200)
    fig_osc = go.Figure(go.Scatter(x=t, y=y, line=dict(color='#00A8E8')))
    fig_osc.update_layout(height=150, margin=dict(t=0, b=0), plot_bgcolor="black", showlegend=False)
    st.plotly_chart(fig_osc, use_container_width=True)
    st.caption("Estado: Sincronizado" if ready else "Estado: Reset Loop")

with col3:
    st.subheader("3️⃣ Potencia (IGBT)")
    rpm = st.slider("RPM Simulación", 0, 8000, 3000)
    st.plotly_chart(crear_gauge(st.session_state.temp, 90, "Temp. IGBT", "#E74C3C", 150), use_container_width=True)

# ==========================================================
# BOTÓN DE AUTO-DIAGNÓSTICO EXPERTO (SINCRONIZADO)
# ==========================================================
st.markdown("---")
if st.button("🔍 CLIC PARA DIAGNOSTICO", use_container_width=True):
    t_now = datetime.now().strftime('%H:%M:%S')
    
    # RECALCULAR VALORES EN TIEMPO REAL
    v_eval = 5.0 if 10.5 <= v_bat <= 16.0 else round(v_bat * 0.4, 2)
    # Sensibilidad ajustada: a 8000 RPM supera los 100°C
    t_eval = round(25 + (rpm / 80) + (45 if v_eval > 5.5 else 0), 1)
    
    st.session_state.v_out = v_eval
    st.session_state.temp = t_eval
    
    st.subheader("📋 Veredicto del Sistema Experto")
    
    if v_eval < 4.5:
        st.error(f"🚨 FALLO EN ETAPA 1: Voltaje insuficiente ({v_eval}V). El L4949 no regula correctamente.")
        st.info("Acción sugerida: Revisar batería o reemplazar regulador L4949.")
        st.session_state.log.insert(0, f"[{t_now}] CRÍTICO: Fallo L4949 a {v_bat}V.")
        
    elif v_eval > 5.5:
        st.warning(f"⚠️ SOBREVOLTAJE: Tensión lógica peligrosa ({v_eval}V).")
        st.info("Acción sugerida: Verificar alternador y diodo de protección.")
        st.session_state.log.insert(0, f"[{t_now}] ALERTA: Sobrevoltaje detectado.")
        
    elif t_eval > 95.0:
        st.error(f"🚨 FALLO EN ETAPA 3: Estrés térmico en IGBT 8201AG ({t_eval}°C).")
        st.info(f"Acción sugerida: Reducir carga de {rpm} RPM. Revisar disipación térmica del componente.")
        st.session_state.log.insert(0, f"[{t_now}] CRÍTICO: Sobrecalentamiento IGBT ({t_eval}°C).")
        
    else:
        st.success("✅ SISTEMA ÍNTEGRO: Operación nominal detectada en todas las etapas.")
        st.session_state.log.insert(0, f"[{t_now}] PASS: Diagnóstico sin anomalías.")
    
    st.rerun()

st.markdown("### 📝 HISTORIAL DTC")
st.code("\n".join(st.session_state.log) if st.session_state.log else "Sin registros.")

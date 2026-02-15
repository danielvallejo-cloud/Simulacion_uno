import streamlit as st
import plotly.graph_objects as go
import random
import numpy as np
from datetime import datetime

# Configuración Pro
st.set_page_config(page_title="ECU Professional Lab", layout="wide")

# --- FUNCIONES DE INSTRUMENTOS (PLOTLY) ---
def crear_gauge(valor, ref, titulo, unidad, color_bar, rango_max):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = valor,
        title = {'text': titulo, 'font': {'size': 18}},
        gauge = {
            'axis': {'range': [0, rango_max]},
            'bar': {'color': color_bar},
            'steps': [
                {'range': [0, ref*0.8], 'color': "#FF4B4B"},
                {'range': [ref*0.8, ref*1.2], 'color': "#00CC96"},
                {'range': [ref*1.2, rango_max], 'color': "#FF4B4B"}]
        }
    ))
    fig.update_layout(height=250, margin=dict(t=40, b=0, l=30, r=30), paper_bgcolor="#f8f9fa")
    return fig

# Inicialización
if 'log' not in st.session_state: st.session_state.log = []

st.title("🔬 Banco de Pruebas de Diagnóstico: ECU Automotriz")
st.markdown("---")

# ==========================================================
# ETAPA 1: REGULACIÓN (Instrumento: Voltímetro Digital/Análogo)
# ==========================================================
with st.expander("1️⃣ ETAPA DE REGULACIÓN - L4949", expanded=True):
    col_ctrl, col_inst = st.columns([1, 2])
    with col_ctrl:
        st.subheader("Control L4949")
        v_bateria = st.slider("Tensión de Entrada (V_bat)", 5.0, 18.0, 13.5, help="Simula el voltaje del alternador/batería")
        test_reg = st.button("MEDIR REGULACIÓN")
    
    # Lógica L4949: Si Vin < 10V, Vout cae (Brown-out)
    v_out = 5.0 if 10.5 <= v_bateria <= 16.0 else round(v_bateria * 0.4, 2)
    
    with col_inst:
        st.plotly_chart(crear_gauge(v_out, 5.0, "Salida LDO (Vcc)", "V", "#2D3E50", 7), use_container_width=True)

# ==========================================================
# ETAPA 2: CONTROL - MCU (Instrumento: Analizador de Señal)
# ==========================================================
with st.expander("2️⃣ ETAPA DE CONTROL - MICROCONTROLADORES", expanded=True):
    col_ctrl, col_inst = st.columns([1, 2])
    with col_ctrl:
        mcu_sel = st.selectbox("Arquitectura", ["Infineon TriCore", "MC9S12XEP100", "PIC18F458"])
        test_mcu = st.button("ESCANEAR BUS CAN / RELOJ")
    
    with col_inst:
        # Si el voltaje es incorrecto, la señal es ruido
        t = np.linspace(0, 1, 200)
        if 4.8 <= v_out <= 5.2:
            y = np.sign(np.sin(2 * np.pi * 10 * t)) # Pulso PWM limpio
            st.success(f"MCU {mcu_sel}: Señal Sincronizada")
        else:
            y = np.random.normal(0, 0.5, 200) # Ruido por bajo voltaje
            st.error("MCU: Reset Loop / Error de Reloj")
        
        fig_osc = go.Figure()
        fig_osc.add_trace(go.Scatter(x=t, y=y, line=dict(color='#00A8E8')))
        fig_osc.update_layout(title="Señal de Oscilador / PWM", height=200, margin=dict(t=30, b=0), plot_bgcolor="black")
        st.plotly_chart(fig_osc, use_container_width=True)

# ==========================================================
# ETAPA 3: POTENCIA - IGBT (Instrumento: Pirómetro Térmico)
# ==========================================================
with st.expander("3️⃣ ETAPA DE POTENCIA - IGBT 8201AG", expanded=True):
    col_ctrl, col_inst = st.columns([1, 2])
    with col_ctrl:
        st.subheader("Carga de Ignición")
        rpm = st.slider("Simular RPM (Carga)", 0, 8000, 3000)
        test_pwr = st.button("ANALIZAR ESTRÉS TÉRMICO")
    
    # Lógica Térmica: A más RPM y si V_out es inestable, más calor
    temp_base = 25 + (rpm / 100)
    if v_out > 5.5: temp_base += 40 # Sobrevoltaje calienta el driver
    
    with col_inst:
        st.plotly_chart(crear_gauge(temp_base, 90, "Temp. IGBT (°C)", "°C", "#E74C3C", 150), use_container_width=True)

# LOGS FINALES
if test_reg or test_mcu or test_pwr:
    st.session_state.log.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] Escaneo Completo: V={v_out}V | Temp={temp_base}°C")

st.markdown("### 📝 Reporte Forense de Diagnóstico")
st.code("\n".join(st.session_state.log))

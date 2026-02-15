import streamlit as st
import plotly.graph_objects as go
import random
from datetime import datetime

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="ECU Multistage Simulator", layout="wide")

# Estilo Industrial
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; font-weight: bold; }
    .stage-box { padding: 20px; border-radius: 10px; border: 2px solid #2D3E50; background-color: white; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

if 'log' not in st.session_state: st.session_state.log = []

st.title("⚡ Simulador de ECU Automotriz: Análisis por Etapas")
st.write("Herramienta de diagnóstico para la validación de hardware en tres niveles.")

# ==========================================================
# ETAPA 1: REGULACIÓN (L4949)
# ==========================================================
with st.container():
    st.markdown('<div class="stage-box">', unsafe_allow_html=True)
    st.header("1️⃣ Etapa de Regulación (Alimentación)")
    c1, c2, c3 = st.columns([1, 1, 2])
    
    with c1:
        st.write("**Componente:** L4949")
        vin = st.slider("Tensión de Batería (V_in)", 8.0, 16.0, 13.5)
        btn_reg = st.button("PROBAR REGULADOR")
    
    with c2:
        # Lógica L4949
        vout = 5.0 if 10.0 <= vin <= 15.0 and random.random() > 0.1 else round(vin * 0.3, 2)
        st.metric("V_out (Estable)", f"{vout} V", delta=round(vout-5.0, 2))
    
    with c3:
        if btn_reg:
            if vout < 4.7:
                st.error("❌ FALLA: Salida baja o pulsante. Capacitor defectuoso o corto en L4949.")
                st.session_state.log.insert(0, f"[{datetime.now().strftime('%H:%M')}] Etapa 1: Fallo de regulación L4949.")
            else:
                st.success("✅ OK: Voltaje estable. Reset Supervisor activo.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================================
# ETAPA 2: CONTROL (MICROCONTROLADORES)
# ==========================================================
with st.container():
    st.markdown('<div class="stage-box">', unsafe_allow_html=True)
    st.header("2️⃣ Etapa de Control (Procesamiento)")
    c1, c2, c3 = st.columns([1, 1, 2])
    
    with c1:
        mcu_name = st.selectbox("Seleccionar MCU", ["Infineon TriCore", "MC9S12XEP100", "PIC18F458"])
        btn_ctrl = st.button("ANALIZAR NÚCLEO")
    
    with c2:
        # La salud del MCU depende de la Etapa 1
        mcu_status = "SYNC" if vout >= 4.8 else "RESET LOOP"
        st.metric("Estado de Reloj", mcu_status)
    
    with c3:
        if btn_ctrl:
            if mcu_status == "RESET LOOP":
                st.error(f"❌ ERROR: El {mcu_name} no puede iniciar. Voltaje insuficiente desde Etapa 1.")
            else:
                st.success(f"✅ OK: {mcu_name} procesando señales PWM y bus CAN.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================================
# ETAPA 3: POTENCIA (IGBT 8201AG)
# ==========================================================
with st.container():
    st.markdown('<div class="stage-box">', unsafe_allow_html=True)
    st.header("3️⃣ Etapa de Potencia (Actuadores)")
    c1, c2, c3 = st.columns([1, 1, 2])
    
    with c1:
        st.write("**Componente:** IGBT 8201AG")
        frec_ign = st.number_input("Frecuencia de Encendido (Hz)", 10, 100, 50)
        btn_pwr = st.button("TEST DE IGNICIÓN")
    
    with c2:
        # La potencia depende de que el Control esté OK
        ign_status = "DISPARO OK" if mcu_status == "SYNC" and random.random() > 0.1 else "NO SIGNAL"
        st.metric("Salida Colector", ign_status)
    
    with c3:
        if btn_pwr:
            if ign_status == "NO SIGNAL":
                st.error("❌ FALLA: Sin chispa. Verificar señal de Gate o posible corto C-E en IGBT.")
            else:
                st.success("✅ OK: Conducción de alta corriente detectada hacia bobina.")
    st.markdown('</div>', unsafe_allow_html=True)

# HISTORIAL
st.subheader("📝 Historial Forense de la ECU")
st.code("\n".join(st.session_state.log))

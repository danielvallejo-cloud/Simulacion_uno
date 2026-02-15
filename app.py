import streamlit as st
import plotly.graph_objects as go
import random
import numpy as np
from datetime import datetime

# Configuración Estilo Journal Fuel
st.set_page_config(page_title="ECU Expert Lab", layout="wide")

# --- BASE DE DATOS DE ARQUITECTURAS (Diferencias Técnicas) ---
MCU_SPECS = {
    "Infineon TriCore": {
        "bits": "32-bit (Alta Gama)",
        "freq": "200 MHz",
        "flash": "4 MB",
        "uso": "Control de Inyección/Transmisión",
        "color": "#00A8E8"
    },
    "MC9S12XEP100": {
        "bits": "16-bit (Gama Media)",
        "freq": "50 MHz",
        "flash": "1 MB",
        "uso": "Módulos de Carrocería (BCM)",
        "color": "#FFD700"
    },
    "PIC18F458": {
        "bits": "8-bit (Gama Básica)",
        "freq": "20 MHz",
        "flash": "32 KB",
        "uso": "Sistemas Secundarios/Confort",
        "color": "#3FB950"
    }
}

# --- FUNCIÓN DE INSTRUMENTOS (Se mantiene la que te gustó con números) ---
def crear_gauge(valor, ref, titulo, color_bar, max_v):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", 
        value = valor,
        number = {'font': {'size': 40, 'color': "white"}, 'valueformat': ".1f"},
        title = {'text': titulo, 'font': {'size': 18, 'color': "white"}},
        gauge = {
            'axis': {'range': [0, max_v], 'tickcolor': "white"},
            'bar': {'color': color_bar},
            'steps': [
                {'range': [0, ref*0.8], 'color': "#FF4B4B"},
                {'range': [ref*0.8, ref*1.2], 'color': "#00CC96"},
                {'range': [ref*1.2, max_v], 'color': "#FF4B4B"}
            ],
            'threshold': {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': ref}
        }
    ))
    fig.update_layout(height=300, margin=dict(t=80, b=20, l=30, r=30), paper_bgcolor='rgba(0,0,0,0)', font={'color': "white"})
    return fig

# --- INICIALIZACIÓN ---
if 'log' not in st.session_state: st.session_state.log = []
if 'v_out' not in st.session_state: st.session_state.v_out = 5.0
if 'temp' not in st.session_state: st.session_state.temp = 25.0

st.title("🔬 Sistema Experto de Diagnóstico ECU")
st.markdown("---")

# --- UI DE TRES ETAPAS ---
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("1️⃣ Regulación (L4949)")
    v_bat = st.slider("V_bat (Entrada)", 5.0, 18.0, 13.5)
    st.plotly_chart(crear_gauge(st.session_state.v_out, 5.0, "V_out (LDO)", "#2D3E50", 7), use_container_width=True)

with col2:
    st.subheader("2️⃣ Control (MCU)")
    mcu_sel = st.selectbox("Arquitectura", list(MCU_SPECS.keys()))
    
    # --- CAJA DE DIFERENCIA BÁSICA DE ARQUITECTURA (NUEVO) ---
    spec = MCU_SPECS[mcu_sel]
    st.info(f"""
    **Hardware Info:** {spec['bits']}
    - Velocidad: {spec['freq']} | Memoria: {spec['flash']}
    - Aplicación: {spec['uso']}
    """)
    
    t = np.linspace(0, 1, 300)
    ready = 4.8 <= st.session_state.v_out <= 5.2
    
    # Diferencia visual de frecuencia según el MCU
    f_mult = 25 if mcu_sel == "Infineon TriCore" else (12 if mcu_sel == "MC9S12XEP100" else 6)
    y = np.sign(np.sin(2 * np.pi * f_mult * t)) if ready else np.random.normal(0, 0.5, 300)
    
    fig_osc = go.Figure(go.Scatter(x=t, y=y, line=dict(color=spec['color'], width=2)))
    fig_osc.update_layout(height=160, margin=dict(t=0, b=0), plot_bgcolor="black", showlegend=False, 
                          xaxis={'visible': False}, yaxis={'visible': False})
    st.plotly_chart(fig_osc, use_container_width=True)

with col3:
    st.subheader("3️⃣ Potencia (IGBT)")
    rpm = st.slider("RPM Simulación", 0, 8000, 3000)
    st.plotly_chart(crear_gauge(st.session_state.temp, 90, "Temp. IGBT", "#E74C3C", 150), use_container_width=True)

# --- AUTO-DIAGNÓSTICO (Se mantiene igual con rerun) ---
st.markdown("---")
if st.button("🔍 EJECUTAR AUTO-DIAGNÓSTICO INTELIGENTE", use_container_width=True):
    t_now = datetime.now().strftime('%H:%M:%S')
    v_eval = 5.0 if 10.5 <= v_bat <= 16.0 else round(v_bat * 0.4, 2)
    t_eval = round(25 + (rpm / 80) + (45 if v_eval > 5.5 else 0), 1)
    
    st.session_state.v_out = v_eval
    st.session_state.temp = t_eval
    
    st.subheader("📋 Veredicto del Sistema Experto")
    
    if v_eval < 4.5:
        st.error(f"🚨 FALLO ETAPA 1: Voltaje bajo ({v_eval}V). L4949 no regula.")
        st.session_state.log.insert(0, f"[{t_now}] CRÍTICO: Fallo L4949 a {v_bat}V.")
    elif v_eval > 5.5:
        st.warning(f"⚠️ SOBREVOLTAJE: Tensión peligrosa ({v_eval}V).")
        st.session_state.log.insert(0, f"[{t_now}] ALERTA: Sobrevoltaje detectado.")
    elif t_eval > 95.0:
        st.error(f"🚨 FALLO ETAPA 3: Estrés térmico ({t_eval}°C).")
        st.session_state.log.insert(0, f"[{t_now}] CRÍTICO: Sobrecalentamiento IGBT ({t_eval}°C).")
    else:
        st.success("✅ SISTEMA ÍNTEGRO: Operación nominal en todas las etapas.")
        st.session_state.log.insert(0, f"[{t_now}] PASS: Diagnóstico satisfactorio.")
    
    st.rerun()

st.markdown("### 📝 Historial Forense")
st.code("\n".join(st.session_state.log) if st.session_state.log else "Sin registros.")

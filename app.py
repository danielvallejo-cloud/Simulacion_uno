# ... (Mismo código inicial de gauges y configuración)

# ==========================================================
# BOTÓN DE AUTO-DIAGNÓSTICO EXPERTO (CORREGIDO)
# ==========================================================
st.markdown("---")
if st.button("🔍 EJECUTAR AUTO-DIAGNÓSTICO INTELIGENTE", use_container_width=True):
    t_now = datetime.now().strftime('%H:%M:%S')
    
    # 1. RECALCULAR VALORES ANTES DE ANALIZAR (Sincronización)
    # Calculamos la salida del regulador basada en el slider actual
    v_eval = 5.0 if 10.5 <= v_bat <= 16.0 else round(v_bat * 0.4, 2)
    # Calculamos la temperatura basada en las RPM actuales
    t_eval = round(25 + (rpm / 80) + (40 if v_eval > 5.5 else 0), 1)
    
    # Actualizamos el estado visual para que los Gauges coincidan con el diagnóstico
    st.session_state.v_out = v_eval
    st.session_state.temp = t_eval
    
    st.subheader("📋 Veredicto del Sistema Experto")
    
    # 2. LÓGICA DE DIAGNÓSTICO PRIORIZADA
    # Prioridad 1: Fallo de Alimentación (Etapa 1)
    if v_eval < 4.5:
        st.error(f"🚨 FALLO CRÍTICO EN ETAPA 1: Voltaje de salida L4949 insuficiente ({v_eval}V).")
        st.info("ANÁLISIS: El regulador no alcanza el umbral de operación. El microcontrolador se encuentra en RESET.")
        st.session_state.log.insert(0, f"[{t_now}] CRÍTICO: Fallo L4949 (Vin={v_bat}V)")
        
    # Prioridad 2: Sobrevoltaje (Etapa 1 afecta a todas)
    elif v_eval > 5.5:
        st.warning(f"⚠️ SOBREVOLTAJE DETECTADO: Tensión lógica de {v_eval}V.")
        st.info("ANÁLISIS: Posible corto en el regulador L4949. Riesgo de degradación en el silicio del MCU.")
        st.session_state.log.insert(0, f"[{t_now}] ALERTA: Sobrevoltaje detectado.")

    # Prioridad 3: Estrés Térmico en Potencia (Etapa 3) - Ahora detecta las 8000 RPM
    elif t_eval > 95.0:
        st.error(f"🚨 FALLO EN ETAPA 3: Estrés Térmico en IGBT 8201AG ({t_eval}°C).")
        st.info("ANÁLISIS: El régimen de {rpm} RPM está generando una conmutación excesiva. Verificar disipación.")
        st.session_state.log.insert(0, f"[{t_now}] CRÍTICO: Sobrecalentamiento IGBT a {rpm} RPM.")

    # Si todo está bien
    else:
        st.success("✅ SISTEMA ÍNTEGRO: Operación nominal en las 3 etapas.")
        st.session_state.log.insert(0, f"[{t_now}] PASS: Diagnóstico satisfactorio.")

    # Forzar refresco de los Gauges para que muestren lo que el diagnóstico analizó
    st.rerun()

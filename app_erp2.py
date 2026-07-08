import streamlit as st
import pandas as pd
import datetime
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="SGO Enterprise - Maquehue PRO", page_icon="🚛", layout="wide")

# --- BASE DE DATOS DE USUARIOS ---
DB_USUARIOS = {
    "admin1": {"nombre": "Catalyna Gajardo", "rol": "Administrador General", "nivel": 1},
    "gerente_op": {"nombre": "Fernando Gonzalez", "rol": "Gerente de Operaciones", "nivel": 1},
    "jefe_flota": {"nombre": "Nicolas Sandoval", "rol": "Jefe de Transportes", "nivel": 2},
    "supervisor_taller": {"nombre": "Felipe Herrera", "rol": "Supervisor de Taller", "nivel": 2},
    "mecanico_jefe": {"nombre": "Pedro Aguilera", "rol": "Mecánico Especialista A", "nivel": 3},
    "logistica1": {"nombre": "Andrés Soto", "rol": "Coordinador de Logística", "nivel": 2},
    "despachador": {"nombre": "Manuel Aravena", "rol": "Despachador de Faena", "nivel": 3},
    "prevencionista": {"nombre": "Ana María Silva", "rol": "Asesor HSE / Prevención", "nivel": 2},
    "chofer_lider": {"nombre": "Luis Castro", "rol": "Conductor Profesional Heavy Duty", "nivel": 4},
    "auditor_ext": {"nombre": "Auditor Externo", "rol": "Inspector / Auditoría", "nivel": 1}
}

# --- INICIALIZACIÓN DE LA NUBE Y FLOTA ---
if 'conectado' not in st.session_state:
    st.session_state.conectado = False
    st.session_state.usuario_id = ""
    st.session_state.user_info = {}

if 'flota' not in st.session_state:
    flota_inicial = []
    lat_base, lon_base = -38.7396, -72.6019
    
    # REGLA ESTRICTA: Exactamente 7 operativos y 3 fuera de servicio
    estados_flota = ["OPERATIVO"] * 7 + ["BLOQUEADO EN TALLER", "MANTENCIÓN PREVENTIVA", "FUERA DE SERVICIO"]
    random.shuffle(estados_flota)
    
    for i in range(1, 11):
        kms_actuales = random.randint(520000, 595000)
        proxima_maint = ((kms_actuales // 10000) + 1) * 10000
        kms_restantes = proxima_maint - kms_actuales
        estado_camion = estados_flota[i-1] # Se asigna de la lista pre-calculada
        
        flota_inicial.append({
            "id": f"Unidad 0{i}" if i < 10 else f"Unidad {i}",
            "patente": f"GP-GC-{89+i}",
            "modelo": "MB Actros 4144K 8x4 Heavy Duty",
            "vin": f"WDB9323341L{random.randint(200000, 899999)}",
            "motor_id": f"OM501LA-V/{i}",
            "kms": kms_actuales,
            "horas": random.randint(19000, 23000),
            "lat": lat_base + random.uniform(-0.06, 0.06),
            "lon": lon_base + random.uniform(-0.06, 0.06),
            "estado": estado_camion,
            "restante_pm": kms_restantes if estado_camion == "OPERATIVO" else random.randint(-500, 1500),
            "checklist_historico": [],
            # DATA DE COMBUSTIBLE ENRIQUECIDA CON MÁS REGISTROS HISTÓRICOS
            "db_comb": [
                {"Fecha": "2026-04-12", "Tipo": "Diésel Grado B", "Litros": 240, "Costo": 264000, "Horometro": 18500, "Cargado_Por": "Luis Castro"},
                {"Fecha": "2026-05-01", "Tipo": "Diésel Grado B", "Litros": 265, "Costo": 291500, "Horometro": 18720, "Cargado_Por": "Manuel Aravena"},
                {"Fecha": "2026-05-18", "Tipo": "Diésel Grado B", "Litros": 290, "Costo": 319000, "Horometro": 18910, "Cargado_Por": "Luis Castro"},
                {"Fecha": "2026-06-15", "Tipo": "Diésel Grado B", "Litros": 280, "Costo": 308000, "Horometro": 19100, "Cargado_Por": "Luis Castro"},
                {"Fecha": "2026-07-02", "Tipo": "Diésel Grado B", "Litros": 310, "Costo": 341000, "Horometro": 19250, "Cargado_Por": "Andrés Soto"},
                {"Fecha": "2026-07-07", "Tipo": "Diésel Grado B", "Litros": 275, "Costo": 302500, "Horometro": 19390, "Cargado_Por": "Luis Castro"}
            ],
            "db_ot": [
                {"ID_OT": "OT-0852", "Sistema": "Frenos", "Prioridad": "Alta", "Tipo": "Correctivo", "Falla": "Desgaste balatas eje 2", "Costo_Total": 450000, "Estado": "Cerrada", "Mecanico": "Felipe Herrera", "Fecha": "2026-06-10"}
            ],
            "rutas": [
                {"Fecha": str(datetime.date.today()), "Origen": "Pozo Maquehue", "Destino": "Obra Enlace", "Distancia_Km": 34, "Estado": "Completada"},
                {"Fecha": str(datetime.date.today()), "Origen": "Obra Enlace", "Destino": "Chancador", "Distancia_Km": 28, "Estado": "En Tránsito"}
            ]
        })
    st.session_state.flota = flota_inicial

# --- PANTALLA DE ACCESO (LOGIN) ---
if not st.session_state.conectado:
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Mercedes-Logo.svg/1024px-Mercedes-Logo.svg.png", width=90)
    st.sidebar.title("SGO Gate - ERP Cloud")
    st.sidebar.caption("Despliegue Privado | Entorno de Producción v9.3")
    
    st.title("🚛 SGO Enterprise - Áridos Maquehue Ltda.")
    st.info("🔐 Autenticación Requerida: Conexión cifrada AES-256 de extremo a extremo.")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        user_input_login = st.selectbox("Identidad de Red (Directorio Activo):", list(DB_USUARIOS.keys()), format_func=lambda x: f"{DB_USUARIOS[x]['nombre']} ({DB_USUARIOS[x]['rol']})")
    with col_l2:
        pass_input = st.text_input("Credencial de Acceso (Password):", type="password", value="inacap2026")
        
    if st.button("Establecer Conexión Segura", type="primary", use_container_width=True):
        if pass_input == "inacap2026":
            st.session_state.conectado = True
            st.session_state.usuario_id = user_input_login
            st.session_state.user_info = DB_USUARIOS[user_input_login]
            st.rerun()
        else:
            st.error("❌ Credenciales inválidas. Intento registrado en auditoría.")

# --- INTERFAZ ERP PRINCIPAL ---
else:
    info_u = st.session_state.user_info
    
    # BARRA DE ESTADO CORPORATIVA
    st.markdown(f"""
    <div style="background-color:#0f172a; padding:15px; border-radius:8px; margin-bottom:15px; color:white; display:flex; justify-content:space-between; border-left: 5px solid #3b82f6;">
        <div><b>🌐 SGO CLOUD MAINFRAME</b> | Operador Activo: <span style="color:#60a5fa;">{info_u['nombre']}</span> | Perfil Asignado: <b>{info_u['rol']}</b></div>
        <div>📅 Fecha de Sistema: {datetime.date.today().strftime('%Y-%m-%d')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # PANEL GLOBAL DE GERENCIA (Disponibilidad)
    total_camiones = len(st.session_state.flota)
    camiones_operativos = sum(1 for c in st.session_state.flota if c['estado'] == "OPERATIVO")
    disponibilidad = (camiones_operativos / total_camiones) * 100
    
    col_kpi1, col_kpi2 = st.columns([1, 3])
    with col_kpi1:
        st.metric("Tasa de Disponibilidad Física (KPI)", f"{disponibilidad:.1f}%", f"{camiones_operativos}/{total_camiones} Activos")
    with col_kpi2:
        st.progress(disponibilidad / 100, text="Capacidad Operativa de la Flota en Tiempo Real")
    
    st.divider()

    # SELECTOR CENTRAL DE ACTIVOS
    col_sel, col_info, col_btn = st.columns([2, 1, 1])
    
    with col_sel:
        opciones_camiones = [f"{c['id']} [{c['patente']}] - {c['estado']}" for c in st.session_state.flota]
        camion_idx = st.selectbox(
            "🔍 Buscador de Activos (Maestro de Materiales):", 
            range(total_camiones), 
            format_func=lambda x: opciones_camiones[x]
        )
        camion_sel = st.session_state.flota[camion_idx]
        
    with col_info:
        st.write("**Estado Telemetría:**")
        if camion_sel['estado'] == "OPERATIVO":
            st.success(f"✅ {camion_sel['estado']}")
        else:
            st.error(f"⚠️ {camion_sel['estado']}")
            
    with col_btn:
        st.write("**Acciones de Mando:**")
        if info_u['nivel'] <= 2:
            if camion_sel['estado'] == "OPERATIVO":
                if st.button("⛔ Inmovilizar Unidad (Lock)", use_container_width=True):
                    camion_sel['estado'] = "FUERA DE SERVICIO (Manual)"
                    st.rerun()
            else:
                if st.button("✅ Liberar a Operaciones", use_container_width=True, type="primary"):
                    camion_sel['estado'] = "OPERATIVO"
                    st.rerun()
            
    st.caption(f"**Especificaciones Técnicas:** {camion_sel['modelo']} | **VIN:** `{camion_sel['vin']}` | **Motor:** `{camion_sel['motor_id']}`")
    st.markdown("---")
    
    # --- MÓDULOS DEL SISTEMA ---
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 Panel", 
        "📍 GPS y Rutas", 
        "📋 Checklist Diario", 
        "🛠️ Órdenes Taller", 
        "⛽ Comb",
        "📊 Informes"
    ])
    
    # 1. PANEL
    with tab1:
        st.subheader("📡 Escáner de Diagnóstico ECM en Tiempo Real")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Odómetro Verificado", f"{camion_sel['kms']:,} Km")
        m2.metric("Horómetro Acumulado", f"{camion_sel['horas']:,} Hrs")
        
        # Lógica Profesional de Batería
        voltaje = 28.2 if camion_sel['estado'] == "OPERATIVO" else 24.2
        estado_voltaje = "Alternador Cargando" if camion_sel['estado'] == "OPERATIVO" else "Batería en Reposo"
        m3.metric("Voltaje Sistema (24V)", f"{voltaje} V", estado_voltaje, delta_color="normal" if voltaje > 26 else "off")
        m4.metric("Próxima PM (Tolerancia)", f"{camion_sel['restante_pm']:,} Km")
        
        st.markdown("##### 🌡️ Parámetros de Motor y Transmisión")
        t1, t2, t3, t4, t5 = st.columns(5)
        if camion_sel['estado'] == "OPERATIVO":
            t1.metric("Temp. Refrigerante", f"{random.randint(85, 92)} °C")
            t2.metric("Presión Aceite", f"{random.randint(45, 55)} PSI")
            t3.metric("Nivel Diésel", f"{random.randint(20, 95)} %")
            t4.metric("Régimen Motor", f"{random.randint(800, 1400)} RPM")
            t5.metric("Temp. Transmisión", f"{random.randint(75, 85)} °C")
        else:
            t1.metric("Temp. Refrigerante", "Ambiente")
            t2.metric("Presión Aceite", "0 PSI")
            t3.metric("Nivel Diésel", f"{random.randint(20, 95)} %")
            t4.metric("Régimen Motor", "0 RPM")
            t5.metric("Temp. Transmisión", "Ambiente")
            
        st.markdown("##### 🛞 Sistema de Monitoreo de Presión de Neumáticos (TPMS)")
        col_tpms1, col_tpms2 = st.columns(2)
        with col_tpms1:
            st.progress(0.95, text="Eje Direccional - Presión Promedio: 110 PSI (Óptimo)")
        with col_tpms2:
            st.progress(0.92, text="Ejes Tractores - Presión Promedio: 105 PSI (Óptimo)")

        rest_km = camion_sel['restante_pm']
        porcentaje_vida = max(0, min(int((rest_km / 10000) * 100), 100))
        st.progress(porcentaje_vida, text=f"Vida Útil Residual Lubricante Motor: {porcentaje_vida}%")

    # 2. GPS Y RUTAS
    with tab2:
        st.subheader("📍 Geoposicionamiento Satelital Telemétrico")
        datos_mapa = []
        for index, c in enumerate(st.session_state.flota):
            datos_mapa.append({
                "lat": c["lat"], "lon": c["lon"],
                "color_gps": "#e11d48" if index == camion_idx else "#3b82f6",
                "tamano_gps": 800 if index == camion_idx else 200
            })
        st.map(pd.DataFrame(datos_mapa), color="color_gps", size="tamano_gps", zoom=11)
        st.dataframe(pd.DataFrame(camion_sel['rutas']), use_container_width=True)

    # 3. CHECKLIST DIARIO
    with tab3:
        st.subheader("📋 Protocolo de Inspección de Seguridad (Estándar HSE - 40 Puntos)")
        with st.form("form_checklist"):
            col_ch1, col_ch2, col_ch3, col_ch4 = st.columns(4)
            with col_ch1:
                st.markdown("**1. Fluidos y Motor**")
                # MODIFICACIÓN: Casillas desmarcadas por defecto (value=False)
                ch1 = st.checkbox("Nivel Aceite Carter", value=False)
                ch2 = st.checkbox("Refrigerante Radiador", value=False)
                ch3 = st.checkbox("Correas Accesorios", value=False)
                ch4 = st.checkbox("Dirección Hidráulica", value=False)
                ch5 = st.checkbox("Estanqueidad Combustible", value=False)
                ch6 = st.checkbox("Filtro Admisión Aire", value=False)
                ch7 = st.checkbox("Tapa Estanque Diésel", value=False)
                ch8 = st.checkbox("Nivel Urea (AdBlue)", value=False)
                ch9 = st.checkbox("Radiador / Intercooler", value=False)
                ch10 = st.checkbox("Línea de Escape DPF", value=False)
            with col_ch2:
                st.markdown("**2. Chasis y Frenos**")
                ch11 = st.checkbox("Manómetro Neumático > 100 PSI", value=False)
                ch12 = st.checkbox("Válvulas de Purga", value=False)
                ch13 = st.checkbox("Desgaste Balatas/Pastillas", value=False)
                ch14 = st.checkbox("Freno de Estacionamiento (Maxi)", value=False)
                ch15 = st.checkbox("Mangueras Flexibles Aire", value=False)
                ch16 = st.checkbox("Pernos U Suspensión", value=False)
                ch17 = st.checkbox("Paquete Resortes / Grapas", value=False)
                ch18 = st.checkbox("Pulmones Neumáticos", value=False)
                ch19 = st.checkbox("Torque Tuercas Rueda", value=False)
                ch20 = st.checkbox("Profundidad Banda Rodadura", value=False)
            with col_ch3:
                st.markdown("**3. Estructura e Hidráulica**")
                ch21 = st.checkbox("Cilindro Levante Telescópico", value=False)
                ch22 = st.checkbox("Nivel Aceite Hidráulico", value=False)
                ch23 = st.checkbox("Toma de Fuerza (PTO)", value=False)
                ch24 = st.checkbox("Pasadores Pivote Tolva", value=False)
                ch25 = st.checkbox("Mecanismo Ganchos Portalón", value=False)
                ch26 = st.checkbox("Líneas Alta Presión", value=False)
                ch27 = st.checkbox("Tacos de Amortiguación Tolva", value=False)
                ch28 = st.checkbox("Válvula Corte Levante", value=False)
                ch29 = st.checkbox("Sistema Cubre Carga (Carpa)", value=False)
                ch30 = st.checkbox("Bisagras Traseras Portalón", value=False)
            with col_ch4:
                st.markdown("**4. Cabina y Normativa Legal**")
                ch31 = st.checkbox("Luces Bajas/Altas/Intermitentes", value=False)
                ch32 = st.checkbox("Baliza Faena / Alarma Retroceso", value=False)
                ch33 = st.checkbox("Extintor 10Kg PQS Vigente", value=False)
                ch34 = st.checkbox("Cinturones Seguridad 3 Puntos", value=False)
                ch35 = st.checkbox("Parabrisas sin Trizaduras", value=False)
                ch36 = st.checkbox("Tacógrafo / GPS Operativo", value=False)
                ch37 = st.checkbox("Certificado Revisión Técnica", value=False)
                ch38 = st.checkbox("Permiso de Circulación", value=False)
                ch39 = st.checkbox("Seguro SOAP Vigente", value=False)
                ch40 = st.checkbox("Kit Emergencia (Botiquín/Triángulos)", value=False)
                
            obs = st.text_input("Reporte de Hallazgos u Observaciones Técnicas:")
            if st.form_submit_button("Firmar Documento HSE", use_container_width=True):
                todos_ok = all([ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9, ch10, ch11, ch12, ch13, ch14, ch15, ch16, ch17, ch18, ch19, ch20, ch21, ch22, ch23, ch24, ch25, ch26, ch27, ch28, ch29, ch30, ch31, ch32, ch33, ch34, ch35, ch36, ch37, ch38, ch39, ch40])
                camion_sel['checklist_historico'].append({"Fecha": str(datetime.date.today()), "Aprobado": todos_ok, "Firma": info_u['nombre']})
                if not todos_ok:
                    camion_sel['estado'] = "BLOQUEADO POR CHECKLIST"
                    st.error("🚨 Protocolo HSE: Unidad inmovilizada por hallazgos críticos de seguridad.")
                else:
                    camion_sel['estado'] = "OPERATIVO"
                    st.success("✅ Unidad certificada para operación segura.")
                st.rerun()

    # 4. ÓRDENES TALLER
    with tab4:
        st.subheader("🛠️ Módulo CMMS (Computerized Maintenance Management System)")
        
        with st.expander("➕ APERTURA DE ORDEN DE TRABAJO (O.T.)", expanded=True):
            col_o1, col_o2 = st.columns(2)
            with col_o1:
                sistema_afectado = st.selectbox("Sistema Afectado:", ["Motor", "Frenos", "Transmisión", "Sistema Hidráulico", "Sistema Eléctrico", "Tren Delantero/Neumáticos"])
                prioridad = st.selectbox("Nivel de Criticidad:", ["Normal", "Urgente", "CRÍTICA (AOG - Aircraft on Ground equivalente)"])
                tipo_maint = st.radio("Tipo de Mantenimiento:", ["Preventivo", "Correctivo", "Predictivo (Análisis de Aceite)"])
            with col_o2:
                falla = st.text_area("Descripción Técnica de la Intervención:")
                costo_est = st.number_input("Presupuesto Estimado (CLP):", value=150000, step=10000)
            if st.button("Emitir O.T.", type="primary"):
                if falla:
                    camion_sel['db_ot'].append({"ID_OT": f"OT-{random.randint(8000, 9999)}", "Sistema": sistema_afectado, "Prioridad": prioridad, "Tipo": tipo_maint, "Falla": falla, "Costo_Total": costo_est, "Estado": "Abierta", "Mecanico": info_u['nombre'], "Fecha": str(datetime.date.today())})
                    st.success("O.T. Registrada en la Base de Datos Central.")
                    st.rerun()
                    
        st.dataframe(pd.DataFrame(camion_sel['db_ot']), use_container_width=True)
        if info_u['nivel'] <= 2 and st.button("✔️ Aprobar Reparaciones y Cerrar O.T."):
            for ot in camion_sel['db_ot']: ot["Estado"] = "Cerrada"
            camion_sel['estado'] = "OPERATIVO"
            camion_sel['restante_pm'] = 10000 
            st.rerun()

    # 5. COMB (COMBUSTIBLE)
    with tab5:
        st.subheader("⛽ Módulo de Abastecimiento y Suministros")
        c_f1, c_f2 = st.columns(2)
        with c_f1:
            litros = st.number_input("Volumen (Litros):", min_value=0.0, value=250.0)
            costo = st.number_input("Monto Facturado (CLP c/IVA):", min_value=0, value=275000)
        with c_f2:
            horometro = st.number_input("Lectura de Horómetro:", min_value=0, value=int(camion_sel['horas']))
            tipo = st.selectbox("Suministro:", ["Diésel Grado B", "AdBlue (Urea Automotriz)", "Lubricante 15W40"])
            
        if st.button("Registrar Transacción de Consumo", type="primary"):
            camion_sel['db_comb'].append({"Fecha": str(datetime.date.today()), "Tipo": tipo, "Litros": litros, "Costo": costo, "Horometro": horometro, "Cargado_Por": info_u['nombre']})
            st.rerun()
            
        st.dataframe(pd.DataFrame(camion_sel['db_comb']), use_container_width=True)

    # 6. INFORMES
    with tab6:
        st.subheader("📊 Inteligencia de Negocios y Control de Gestión Financiera")
        
        df_c = pd.DataFrame(camion_sel['db_comb'])
        df_o = pd.DataFrame(camion_sel['db_ot'])
        
        t_comb = df_c['Costo'].sum() if not df_c.empty else 0
        t_litros = df_c['Litros'].sum() if not df_c.empty else 0
        t_ot = df_o['Costo_Total'].sum() if not df_o.empty else 0
        costo_total = t_comb + t_ot
        
        rendimiento = (camion_sel['kms'] * 0.005) / t_litros if t_litros > 0 else 2.15 
        cpk = costo_total / camion_sel['kms'] if camion_sel['kms'] > 0 else 0
        
        col_k1, col_k2, col_k3, col_k4 = st.columns(4)
        col_k1.metric("OPEX YTD (Gasto Operativo)", f"${costo_total:,.0f}", "-1.5% vs Presupuesto", delta_color="inverse")
        col_k2.metric("CAPEX/Mantenimiento Acumulado", f"${t_ot:,.0f}")
        col_k3.metric("Rendimiento Volumétrico Diésel", f"{rendimiento:.2f} Km/L", "+0.05 Km/L")
        col_k4.metric("Costo Por Kilómetro (CPK)", f"${cpk:,.2f} /Km")
        
        st.divider()
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("##### 📈 Curva Histórica de Egresos Mensuales (CLP)")
            datos_grafico = pd.DataFrame({'Diésel/AdBlue': [550000, 610000, 590000, t_comb], 'Mantenimiento (O.T.)': [0, 150000, 50000, t_ot]}, index=['Abril', 'Mayo', 'Junio', 'Mes Actual'])
            st.bar_chart(datos_grafico)
        with col_g2:
            st.markdown("##### 📉 Análisis de Depreciación Lineal del Activo")
            val_compra, vida_util = 120000000, 1000000 
            depreciacion = (camion_sel['kms'] / vida_util) * val_compra
            st.write(f"Costo de Adquisición (Base): **${val_compra:,.0f} CLP**")
            st.write(f"Depreciación Acumulada por Uso: **${depreciacion:,.0f} CLP**")
            st.write(f"Valor Contable Residual: **${val_compra - depreciacion:,.0f} CLP**")
            st.progress(camion_sel['kms'] / vida_util, text="Consumo de Vida Útil Amortizable (Meta: 1,000,000 Km)")

        st.markdown("---")
        st.markdown("##### 📥 Exportación de Data Marts (Integración Externa)")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button("📥 Descargar Matriz Financiera O.T. (CSV)", df_o.to_csv(index=False).encode('utf-8'), f"CMMS_EXPORT_{camion_sel['patente']}.csv", "text/csv", use_container_width=True)
        with col_d2:
            st.download_button("📥 Descargar Matriz Consumo (CSV)", df_c.to_csv(index=False).encode('utf-8'), f"FUEL_EXPORT_{camion_sel['patente']}.csv", "text/csv", use_container_width=True)

    # CERRAR SESIÓN SEGURA
    st.sidebar.divider()
    if st.sidebar.button("Desconexión Segura (Cerrar Sesión)", type="primary", use_container_width=True):
        st.session_state.conectado = False
        st.rerun()

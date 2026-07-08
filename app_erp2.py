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
    "supervisor_taller": {"nombre": "Felipe Herrera", "rol": "Supervisor de Taller (CMMS)", "nivel": 2},
    "mecanico_jefe": {"nombre": "Pedro Aguilera", "rol": "Mecánico Especialista A", "nivel": 3},
    "logistica1": {"nombre": "Andrés Soto", "rol": "Coordinador de Logística", "nivel": 2},
    "despachador": {"nombre": "Manuel Aravena", "rol": "Despachador de Faena", "nivel": 3},
    "prevencionista": {"nombre": "Ana María Silva", "rol": "Asesor HSE / Prevención", "nivel": 2},
    "chofer_lider": {"nombre": "Luis Castro", "rol": "Conductor Profesional Heavy Duty", "nivel": 4},
    "auditor_ext": {"nombre": "Inspector Fiscal MOP", "rol": "Auditor Externo Gubernamental", "nivel": 2}
}

# --- INICIALIZACIÓN DE LA NUBE Y FLOTA ---
if 'conectado' not in st.session_state:
    st.session_state.conectado = False
    st.session_state.usuario_id = ""
    st.session_state.user_info = {}

if 'flota' not in st.session_state:
    flota_inicial = []
    lat_base, lon_base = -38.7396, -72.6019
    # Ajuste de probabilidad: 85% operativos para mayor realismo corporativo
    estados_posibles = ["OPERATIVO"] * 17 + ["BLOQUEADO EN TALLER", "MANTENCIÓN PREVENTIVA", "FUERA DE SERVICIO"]
    
    for i in range(1, 11):
        kms_actuales = random.randint(520000, 595000)
        proxima_maint = ((kms_actuales // 10000) + 1) * 10000
        kms_restantes = proxima_maint - kms_actuales
        estado_camion = random.choice(estados_posibles)
        
        flota_inicial.append({
            "id": f"Unidad 0{i}" if i < 10 else f"Unidad {i}",
            "patente": f"GP-GC-{89+i}",
            "modelo": "MB Actros 4144K 8x4",
            "vin": f"WDB9323341L{random.randint(200000, 899999)}",
            "motor_id": f"OM501LA-V/{i}",
            "kms": kms_actuales,
            "horas": random.randint(19000, 23000),
            "lat": lat_base + random.uniform(-0.06, 0.06),
            "lon": lon_base + random.uniform(-0.06, 0.06),
            "estado": estado_camion,
            "restante_pm": kms_restantes if estado_camion == "OPERATIVO" else random.randint(-500, 1500),
            "checklist_historico": [],
            "db_comb": [
                {"Fecha": "2026-06-15", "Tipo": "Diésel Grado B", "Litros": 280, "Costo": 308000, "Horometro": 19100, "Cargado_Por": "chofer_lider"},
                {"Fecha": "2026-07-06", "Tipo": "Diésel Grado B", "Litros": 310, "Costo": 341000, "Horometro": 19250, "Cargado_Por": "chofer_lider"}
            ],
            "db_ot": [
                {"ID_OT": "OT-0852", "Sistema": "Frenos", "Prioridad": "Alta", "Tipo": "Correctivo", "Falla": "Desgaste balatas eje 2", "Repuestos": "Kit Balatas", "Costo_Total": 450000, "Estado": "Cerrada", "Mecanico": "Felipe Herrera", "Fecha": "2026-06-10"}
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
    st.sidebar.caption("Despliegue Privado | Versión 8.5 PRO")
    
    st.title("🚛 SGO Enterprise - Áridos Maquehue Ltda.")
    st.info("🔐 Autenticación Requerida: Conexión cifrada de extremo a extremo.")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        user_input = st.selectbox("Identificación de Personal:", list(DB_USUARIOS.keys()), format_func=lambda x: f"{DB_USUARIOS[x]['nombre']} ({DB_USUARIOS[x]['rol']})")
    with col_l2:
        pass_input = st.text_input("Credencial de Acceso:", type="password", value="inacap2026")
        
    if st.button("Iniciar Sesión Segura", type="primary", use_container_width=True):
        if pass_input == "inacap2026":
            st.session_state.conectado = True
            st.session_state.usuario_id = user_input
            st.session_state.user_info = DB_USUARIOS[user_input]
            st.rerun()
        else:
            st.error("❌ Credenciales inválidas.")

# --- INTERFAZ ERP PRINCIPAL ---
else:
    info_u = st.session_state.user_info
    
    # BARRA DE ESTADO SUPERIOR
    st.markdown(f"""
    <div style="background-color:#0f172a; padding:15px; border-radius:10px; margin-bottom:15px; color:white; display:flex; justify-content:space-between; border-left: 5px solid #3b82f6;">
        <div><b>🌐 SGO CLOUD ERP</b> | Operador: <span style="color:#60a5fa;">{info_u['nombre']}</span> | Perfil: <b>{info_u['rol']}</b></div>
        <div>📅 {datetime.date.today().strftime('%d de %B, %Y')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # PANEL GLOBAL DE GERENCIA (Disponibilidad)
    total_camiones = len(st.session_state.flota)
    camiones_operativos = sum(1 for c in st.session_state.flota if c['estado'] == "OPERATIVO")
    disponibilidad = (camiones_operativos / total_camiones) * 100
    
    col_kpi1, col_kpi2 = st.columns([1, 3])
    with col_kpi1:
        st.metric("Tasa Disponibilidad Flota", f"{disponibilidad:.1f}%", f"{camiones_operativos} de {total_camiones} Operativos")
    with col_kpi2:
        st.progress(disponibilidad / 100, text="Capacidad Operativa Actual")
    
    st.divider()

    # SELECTOR CENTRAL DE ACTIVOS
    col_sel, col_info, col_btn = st.columns([2, 1, 1])
    
    with col_sel:
        opciones_camiones = [f"{c['id']} [{c['patente']}] - {c['estado']}" for c in st.session_state.flota]
        camion_idx = st.selectbox(
            "🔍 Buscador de Activos (Seleccione Unidad):", 
            range(total_camiones), 
            format_func=lambda x: opciones_camiones[x]
        )
        camion_sel = st.session_state.flota[camion_idx]
        
    with col_info:
        st.write("Estado de la Unidad:")
        if camion_sel['estado'] == "OPERATIVO":
            st.success(f"✅ {camion_sel['estado']}")
        else:
            st.error(f"⚠️ {camion_sel['estado']}")
            
    with col_btn:
        st.write("Acciones Rápidas:")
        if info_u['nivel'] <= 2:
            if camion_sel['estado'] == "OPERATIVO":
                if st.button("⛔ Bloquear Unidad", use_container_width=True):
                    camion_sel['estado'] = "FUERA DE SERVICIO (Manual)"
                    st.rerun()
            else:
                if st.button("✅ Liberar a Operación", use_container_width=True, type="primary"):
                    camion_sel['estado'] = "OPERATIVO"
                    st.rerun()
            
    st.caption(f"**Especificaciones:** {camion_sel['modelo']} | **VIN:** `{camion_sel['vin']}` | **Motor:** `{camion_sel['motor_id']}`")
    st.markdown("---")
    
    # --- MÓDULOS DEL SISTEMA ---
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📡 Telemetría CanBus", 
        "📍 Control Logístico (GPS)", 
        "📋 Check-list (HSE)", 
        "🛠️ CMMS (Mantenimiento)", 
        "⛽ Suministros",
        "📊 Inteligencia de Negocios"
    ])
    
    # 1. TELEMETRÍA
    with tab1:
        st.subheader("📡 Escáner de Diagnóstico en Tiempo Real")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Odómetro Verificado", f"{camion_sel['kms']:,} Km")
        m2.metric("Horómetro Acumulado", f"{camion_sel['horas']:,} Hrs")
        m3.metric("Voltaje Sistema", "27.1 V", delta="Normal", delta_color="normal")
        m4.metric("Próxima Mantención en", f"{camion_sel['restante_pm']:,} Km")
        
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
            
        st.markdown("##### 🛞 Monitoreo de Presión de Neumáticos (TPMS)")
        col_tpms1, col_tpms2 = st.columns(2)
        with col_tpms1:
            st.progress(0.95, text="Eje Direccional - Promedio: 110 PSI")
        with col_tpms2:
            st.progress(0.92, text="Ejes Tractores - Promedio: 105 PSI")

        rest_km = camion_sel['restante_pm']
        porcentaje_vida = max(0, min(int((rest_km / 10000) * 100), 100))
        st.progress(porcentaje_vida, text=f"Vida Útil Aceite de Motor: {porcentaje_vida}%")

    # 2. GPS
    with tab2:
        st.subheader("📍 Geoposicionamiento Satelital")
        datos_mapa = []
        for index, c in enumerate(st.session_state.flota):
            datos_mapa.append({
                "lat": c["lat"], "lon": c["lon"],
                "color_gps": "#e11d48" if index == camion_idx else "#3b82f6",
                "tamano_gps": 800 if index == camion_idx else 200
            })
        st.map(pd.DataFrame(datos_mapa), color="color_gps", size="tamano_gps", zoom=11)
        st.dataframe(pd.DataFrame(camion_sel['rutas']), use_container_width=True)

    # 3. CHECKLIST HSE
    with tab3:
        st.subheader("📋 Inspección de Seguridad Estándar Minero (40 Puntos)")
        with st.form("form_checklist"):
            col_ch1, col_ch2, col_ch3, col_ch4 = st.columns(4)
            with col_ch1:
                st.markdown("**1. Fluidos y Motor**")
                ch1 = st.checkbox("Nivel Aceite Carter OK", value=True)
                ch2 = st.checkbox("Refrigerante Radiador OK", value=True)
                ch3 = st.checkbox("Correas Motor OK", value=True)
                ch4 = st.checkbox("Dir. Hidráulica OK", value=True)
                ch5 = st.checkbox("Sin Fugas Petróleo OK", value=True)
                ch6 = st.checkbox("Filtro Aire OK", value=True)
                ch7 = st.checkbox("Tapa de Combustible OK", value=True)
                ch8 = st.checkbox("Nivel AdBlue OK", value=True)
                ch9 = st.checkbox("Radiador Intercooler OK", value=True)
                ch10 = st.checkbox("Tubo de Escape/Gases OK", value=True)
            with col_ch2:
                st.markdown("**2. Frenos y Chasis**")
                ch11 = st.checkbox("Manómetro > 100 PSI OK", value=True)
                ch12 = st.checkbox("Válvulas Purga OK", value=True)
                ch13 = st.checkbox("Grosor Balatas OK", value=True)
                ch14 = st.checkbox("Freno Estacionamiento OK", value=True)
                ch15 = st.checkbox("Mangueras Flexibles OK", value=True)
                ch16 = st.checkbox("Pernos U Suspensión OK", value=True)
                ch17 = st.checkbox("Grapas Resortes OK", value=True)
                ch18 = st.checkbox("Pulmones Neumáticos OK", value=True)
                ch19 = st.checkbox("Apriete Tuercas Rueda OK", value=True)
                ch20 = st.checkbox("Profundidad Cocada OK", value=True)
            with col_ch3:
                st.markdown("**3. Tolva e Hidráulica**")
                ch21 = st.checkbox("Cilindro Levante OK", value=True)
                ch22 = st.checkbox("Aceite Hidráulico OK", value=True)
                ch23 = st.checkbox("Toma Fuerza (PTO) OK", value=True)
                ch24 = st.checkbox("Pasadores Tolva OK", value=True)
                ch25 = st.checkbox("Ganchos Portalón OK", value=True)
                ch26 = st.checkbox("Mangueras Alta Presión OK", value=True)
                ch27 = st.checkbox("Gomas Amortiguación OK", value=True)
                ch28 = st.checkbox("Válvula Limitadora OK", value=True)
                ch29 = st.checkbox("Cubre Carga/Carpa OK", value=True)
                ch30 = st.checkbox("Bisagras Traseras OK", value=True)
            with col_ch4:
                st.markdown("**4. Cabina y Legal**")
                ch31 = st.checkbox("Luces Bajas/Altas OK", value=True)
                ch32 = st.checkbox("Baliza / Alarma Retro. OK", value=True)
                ch33 = st.checkbox("Extintor 10Kg Cargado OK", value=True)
                ch34 = st.checkbox("Cinturones 3 Puntos OK", value=True)
                ch35 = st.checkbox("Parabrisas Intacto OK", value=True)
                ch36 = st.checkbox("Tacógrafo / GPS OK", value=True)
                ch37 = st.checkbox("Revisión Técnica Vigente", value=True)
                ch38 = st.checkbox("Permiso Circulación OK", value=True)
                ch39 = st.checkbox("Seguro SOAP Vigente", value=True)
                ch40 = st.checkbox("Botiquín y Triángulos OK", value=True)
                
            obs = st.text_input("Observaciones adicionales:")
            if st.form_submit_button("Firmar Documento", use_container_width=True):
                todos_ok = all([ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9, ch10, ch11, ch12, ch13, ch14, ch15, ch16, ch17, ch18, ch19, ch20, ch21, ch22, ch23, ch24, ch25, ch26, ch27, ch28, ch29, ch30, ch31, ch32, ch33, ch34, ch35, ch36, ch37, ch38, ch39, ch40])
                camion_sel['checklist_historico'].append({"Fecha": str(datetime.date.today()), "Aprobado": todos_ok, "Firma": info_u['nombre']})
                if not todos_ok:
                    camion_sel['estado'] = "BLOQUEADO POR CHECKLIST"
                    st.error("Protocolo HSE: Unidad inmovilizada por hallazgos críticos.")
                else:
                    camion_sel['estado'] = "OPERATIVO"
                    st.success("Unidad certificada para operación segura.")
                st.rerun()

    # 4. CMMS (TALLER)
    with tab4:
        st.subheader("🛠️ Computerized Maintenance Management System")
        with st.expander("NUEVA ORDEN DE TRABAJO (O.T.)", expanded=False):
            col_o1, col_o2 = st.columns(2)
            with col_o1:
                sistema_afectado = st.selectbox("Sistema:", ["Motor", "Frenos", "Transmisión", "Hidráulico", "Eléctrico", "Neumáticos"])
                prioridad = st.selectbox("Prioridad:", ["Normal", "Urgente", "CRÍTICA (AOG)"])
            with col_o2:
                falla = st.text_input("Descripción Falla:")
                costo_est = st.number_input("Presupuesto Estimado ($):", value=150000, step=10000)
            if st.button("Generar O.T."):
                if falla:
                    camion_sel['db_ot'].append({"ID_OT": f"OT-{random.randint(8000, 9999)}", "Sistema": sistema_afectado, "Prioridad": prioridad, "Falla": falla, "Costo_Total": costo_est, "Estado": "Abierta", "Mecanico": info_u['nombre'], "Fecha": str(datetime.date.today())})
                    st.rerun()
        st.dataframe(pd.DataFrame(camion_sel['db_ot']), use_container_width=True)
        if info_u['nivel'] <= 2 and st.button("✔️ Cerrar O.T. y Liberar Unidad"):
            for ot in camion_sel['db_ot']: ot["Estado"] = "Cerrada"
            camion_sel['estado'] = "OPERATIVO"
            camion_sel['restante_pm'] = 10000 
            st.rerun()

    # 5. ABASTECIMIENTO
    with tab5:
        st.subheader("⛽ Registro de Suministros")
        c_f1, c_f2 = st.columns(2)
        with c_f1:
            litros = st.number_input("Volumen (Litros):", min_value=0.0, value=250.0)
            costo = st.number_input("Monto Factura (CLP):", min_value=0, value=275000)
        with c_f2:
            horometro = st.number_input("Horómetro:", min_value=0, value=int(camion_sel['horas']))
            tipo = st.selectbox("Producto:", ["Diésel", "AdBlue (Urea)", "Aceite Relleno"])
        if st.button("Registrar Carga"):
            camion_sel['db_comb'].append({"Fecha": str(datetime.date.today()), "Tipo": tipo, "Litros": litros, "Costo": costo, "Horometro": horometro, "Cargado_Por": info_u['nombre']})
            st.rerun()
        st.dataframe(pd.DataFrame(camion_sel['db_comb']), use_container_width=True)

    # 6. INTELIGENCIA DE NEGOCIOS
    with tab6:
        st.subheader("📊 Métricas Financieras y Depreciación")
        
        df_c = pd.DataFrame(camion_sel['db_comb'])
        df_o = pd.DataFrame(camion_sel['db_ot'])
        
        t_comb = df_c['Costo'].sum() if not df_c.empty else 0
        t_litros = df_c['Litros'].sum() if not df_c.empty else 0
        t_ot = df_o['Costo_Total'].sum() if not df_o.empty else 0
        costo_total = t_comb + t_ot
        
        rendimiento = (camion_sel['kms'] * 0.005) / t_litros if t_litros > 0 else 2.15 
        cpk = costo_total / camion_sel['kms'] if camion_sel['kms'] > 0 else 0
        
        col_k1, col_k2, col_k3, col_k4 = st.columns(4)
        col_k1.metric("OPEX YTD (Gastos)", f"${costo_total:,.0f}", "-1.5% vs Presupuesto", delta_color="inverse")
        col_k2.metric("Gasto en Mantenimiento", f"${t_ot:,.0f}")
        col_k3.metric("Eficiencia Diésel", f"{rendimiento:.2f} Km/L", "+0.05 Km/L")
        col_k4.metric("Costo Por Kilómetro", f"${cpk:,.2f} /Km")
        
        st.divider()
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("**Evolución de Costos (CLP)**")
            datos_grafico = pd.DataFrame({'Combustible': [300000, 320000, 290000, t_comb], 'Mantenimiento': [150000, 0, 50000, t_ot]}, index=['Abr', 'May', 'Jun', 'Jul'])
            st.bar_chart(datos_grafico)
        with col_g2:
            st.markdown("**Estado Contable del Activo**")
            val_compra, vida_util = 120000000, 1000000 
            depreciacion = (camion_sel['kms'] / vida_util) * val_compra
            st.write(f"Valor Adquisición: **${val_compra:,.0f}**")
            st.write(f"Depreciación Acumulada: **${depreciacion:,.0f}**")
            st.write(f"Valor Libro (Residual): **${val_compra - depreciacion:,.0f}**")
            st.progress(camion_sel['kms'] / vida_util, text="Consumo de Vida Útil (Contable)")

        st.download_button("📥 Descargar Reporte SAP (CSV)", df_c.to_csv(index=False).encode('utf-8'), f"REPORTE_ERP_{camion_sel['patente']}.csv", "text/csv", use_container_width=True)

    # CERRAR SESIÓN
    st.sidebar.divider()
    if st.sidebar.button("Cerrar Sesión", type="primary", use_container_width=True):
        st.session_state.conectado = False
        st.rerun()

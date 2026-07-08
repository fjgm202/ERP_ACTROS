import streamlit as st
import pandas as pd
import datetime
import random
import numpy as np

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="SGO Enterprise - Áridos Maquehue v8.0", page_icon="🚛", layout="wide")

# --- BASE DE DATOS DE USUARIOS (NOMBRES REASIGNADOS) ---
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

# --- INICIALIZACIÓN DE LA NUBE ---
if 'conectado' not in st.session_state:
    st.session_state.conectado = False
    st.session_state.usuario_id = ""
    st.session_state.user_info = {}

if 'flota' not in st.session_state:
    flota_inicial = []
    lat_base, lon_base = -38.7396, -72.6019
    estados_posibles = ["OPERATIVO", "OPERATIVO", "OPERATIVO", "OPERATIVO", "BLOQUEADO EN TALLER", "MANTENCIÓN PREVENTIVA"]
    
    for i in range(1, 11):
        kms_actuales = random.randint(520000, 595000)
        proxima_maint = ((kms_actuales // 10000) + 1) * 10000
        kms_restantes = proxima_maint - kms_actuales
        estado_camion = random.choice(estados_posibles)
        
        flota_inicial.append({
            "id": f"Camión {i}",
            "patente": f"GP-GC-{89+i}",
            "modelo": "Mercedes-Benz Actros 4144K 8x4 Heavy Tolva",
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
                {"ID_OT": "OT-0852", "Sistema": "Frenos", "Prioridad": "Alta", "Tipo": "Correctivo", "Falla": "Desgaste balatas", "Repuestos": "Kit Balatas", "Costo_Total": 450000, "Estado": "Cerrada", "Mecanico": "mecanico_jefe", "Fecha": "2026-06-10"}
            ],
            "rutas": [
                {"Fecha": str(datetime.date.today()), "Origen": "Pozo Áridos Maquehue", "Destino": "Obra Enlace Pillanlelbún", "Distancia_Km": 34, "Estado": "Completada"},
                {"Fecha": str(datetime.date.today()), "Origen": "Obra Enlace Pillanlelbún", "Destino": "Chancador Principal", "Distancia_Km": 28, "Estado": "En Tránsito"}
            ]
        })
    st.session_state.flota = flota_inicial

# --- ACCESO REMOTO (LOGIN) ---
if not st.session_state.conectado:
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Mercedes-Logo.svg/1024px-Mercedes-Logo.svg.png", width=90)
    st.sidebar.title("SGO Gate - Cloud Server")
    st.sidebar.caption("Desplegado en Dominio Privado a medida.")
    st.sidebar.caption("Mantención a distancia: Proveedor SGO.")
    
    st.title("🚛 ERP SGO Enterprise - Transportes Maquehue Ltda.")
    st.info("🔐 Acceso Remoto Cloud: Seleccione usuario e ingrese clave.")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        user_input = st.selectbox("Seleccione Usuario:", list(DB_USUARIOS.keys()), format_func=lambda x: f"{x} - {DB_USUARIOS[x]['nombre']} ({DB_USUARIOS[x]['rol']})")
    with col_l2:
        pass_input = st.text_input("Ingrese Clave de Acceso:", type="password", value="inacap2026")
        
    if st.button("Establecer Conexión Con Servidor", type="primary", use_container_width=True):
        if pass_input == "inacap2026":
            st.session_state.conectado = True
            st.session_state.usuario_id = user_input
            st.session_state.user_info = DB_USUARIOS[user_input]
            st.rerun()
        else:
            st.error("❌ Error de autenticación.")

# --- INTERFAZ ERP CONECTADO ---
else:
    info_u = st.session_state.user_info
    
    # Barra de estado superior
    st.markdown(f"""
    <div style="background-color:#1e293b; padding:12px; border-radius:8px; margin-bottom:20px; color:white; display:flex; justify-content:space-between;">
        <div><span style="color:#10b981;">● SERVIDOR CENTRAL AWS</span> | <b>Usuario:</b> {info_u['nombre']} | <b>Cargo:</b> <span style="color:#38bdf8;">{info_u['rol']}</span></div>
        <div><b>Fecha Sistema:</b> {datetime.date.today()}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- SELECTOR DE FLOTA Y CONTROL DE ESTADO ---
    st.markdown("### 🚛 Centro de Mando y Selección de Activos")
    col_sel, col_info = st.columns([2, 1])
    
    with col_sel:
        opciones_camiones = [f"{c['id']} [{c['patente']}] - {c['estado']}" for c in st.session_state.flota]
        camion_idx = st.selectbox(
            "Seleccione Unidad de la Flota para Inspección / Gestión:", 
            range(10), 
            format_func=lambda x: opciones_camiones[x], 
            key="selector_flota_maestro"
        )
        camion_sel = st.session_state.flota[camion_idx]
        
    with col_info:
        if camion_sel['estado'] == "OPERATIVO":
            st.success(f"✅ ESTADO: {camion_sel['estado']}")
            # Botón para deshabilitar manualmente (Solo Administradores/Gerentes/Jefes Nivel 1 y 2)
            if info_u['nivel'] <= 2:
                if st.button("⛔ Deshabilitar Unidad (Bloquear)"):
                    camion_sel['estado'] = "FUERA DE SERVICIO (Manual)"
                    st.rerun()
        else:
            st.error(f"⚠️ ESTADO: {camion_sel['estado']}")
            # Botón para habilitar manualmente
            if info_u['nivel'] <= 2:
                if st.button("✅ Habilitar Unidad (Operativo)"):
                    camion_sel['estado'] = "OPERATIVO"
                    st.rerun()
            
    st.markdown(f"**Modelo:** {camion_sel['modelo']} | **VIN:** `{camion_sel['vin']}` | **Motor:** `{camion_sel['motor_id']}`")
    st.markdown("---")
    
    # --- PESTAÑAS DEL SISTEMA ---
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 Dashboard de Telemetría", 
        "📍 Mapeo GPS (Toda la Flota)", 
        "📋 Checklist Diario (40 Ptos)", 
        "🛠️ Órdenes de Trabajo", 
        "⛽ Gestión de Combustible",
        "📊 Finanzas y Rentabilidad"
    ])
    
    # 1. TAB DASHBOARD (TELEMETRÍA EXPANDIDA)
    with tab1:
        st.subheader("📊 Datos Maestros del Odómetro y Horómetro")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Odómetro de Flota", f"{camion_sel['kms']:,} Km")
        m2.metric("Horómetro Acumulado", f"{camion_sel['horas']:,} Hrs")
        m3.metric("Voltaje Baterías", "27.1 V", delta="-0.2 V", delta_color="normal")
        m4.metric("Restante Pauta PM", f"{camion_sel['restante_pm']:,} Km")
        
        st.markdown("---")
        st.subheader("🌡️ Lectura de Sensores en Tiempo Real (Telemetría CanBus)")
        t1, t2, t3, t4, t5 = st.columns(5)
        # Usamos random pero condicionado al estado para darle realismo
        if camion_sel['estado'] == "OPERATIVO":
            t1.metric("Temp. Refrigerante", f"{random.randint(85, 92)} °C", "Normal")
            t2.metric("Presión Aceite", f"{random.randint(40, 60)} PSI", "Óptimo")
            t3.metric("Nivel Combustible", f"{random.randint(15, 85)} %", "Tanque")
            t4.metric("RPM Motor", f"{random.randint(600, 1500)} RPM", "En Marcha")
            t5.metric("Temp. Transmisión", f"{random.randint(70, 85)} °C", "Normal")
        else:
            t1.metric("Temp. Refrigerante", "Ambiente", "Apagado")
            t2.metric("Presión Aceite", "0 PSI", "Apagado")
            t3.metric("Nivel Combustible", f"{random.randint(15, 85)} %", "Tanque")
            t4.metric("RPM Motor", "0 RPM", "Motor Detenido")
            t5.metric("Temp. Transmisión", "Ambiente", "Apagado")
            
        st.markdown("---")
        st.subheader("🛞 Monitoreo de Presión de Neumáticos (TPMS)")
        col_tpms1, col_tpms2 = st.columns(2)
        with col_tpms1:
            st.write("**Ejes Delanteros (Direccionales)**")
            st.progress(0.95, text="Eje 1 Izquierdo: 110 PSI (Normal)")
            st.progress(0.94, text="Eje 1 Derecho: 109 PSI (Normal)")
        with col_tpms2:
            st.write("**Ejes Traseros (Tracción)**")
            st.progress(0.92, text="Eje 2 (Promedio): 105 PSI (Normal)")
            st.progress(0.91, text="Eje 3 (Promedio): 104 PSI (Normal)")

        st.markdown("---")
        st.subheader("⏰ Monitoreo Automático de Alertas de Mantenimiento")
        rest_km = camion_sel['restante_pm']
        porcentaje_vida_util = max(0, min(int((rest_km / 10000) * 100), 100))
        
        col_bar, col_txt_bar = st.columns([3, 1])
        with col_bar:
            st.progress(porcentaje_vida_util)
        with col_txt_bar:
            st.metric("Vida Restante Aceite", f"{porcentaje_vida_util}%")
            
        if rest_km <= 0 or camion_sel['estado'] not in ["OPERATIVO"]:
            st.error("🚨 ALERTA DE CRITICIDAD: Vehículo inoperativo o ciclo preventivo vencido. Detención obligatoria.")
        elif rest_km <= 1500:
            st.warning("⚠️ ALERTA PREVENTIVA: Faltan menos de 1,500 Km para mantención. Taller avisado.")
        else:
            st.success("✅ Semáforo Mecánico Verde: Parámetros nominales dentro de norma.")

    # 2. TAB GPS
    with tab2:
        st.subheader("📍 Rastreo Satelital e Integración de Telemetría GPS")
        datos_mapa = []
        for index, c in enumerate(st.session_state.flota):
            datos_mapa.append({
                "lat": c["lat"], "lon": c["lon"],
                "color_gps": "#FF0000" if index == camion_idx else "#0000FF",
                "tamano_gps": 800 if index == camion_idx else 150
            })
        try:
            st.map(pd.DataFrame(datos_mapa), color="color_gps", size="tamano_gps", zoom=10)
        except:
            st.map(pd.DataFrame(datos_mapa), zoom=10)
        
        st.markdown("#### 🗺️ Bitácora de Tránsito Diario")
        st.dataframe(pd.DataFrame(camion_sel['rutas']), use_container_width=True)

    # 3. TAB CHECKLIST (40 PUNTOS)
    with tab3:
        st.subheader("📋 Formulario de Inspección de Seguridad Pre-Uso (40 Parámetros)")
        with st.form("super_checklist_form"):
            col_ch1, col_ch2, col_ch3, col_ch4 = st.columns(4)
            with col_ch1:
                st.markdown("#### 🛢️ Fluidos y Motor")
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
                st.markdown("#### 🛑 Frenos y Chasis")
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
                st.markdown("#### 🏗️ Tolva e Hidráulica")
                ch21 = st.checkbox("Cilindro Levante Telesc. OK", value=True)
                ch22 = st.checkbox("Nivel Aceite Hidráulico OK", value=True)
                ch23 = st.checkbox("Toma de Fuerza (PTO) OK", value=True)
                ch24 = st.checkbox("Pasadores Tolva OK", value=True)
                ch25 = st.checkbox("Ganchos Portalón OK", value=True)
                ch26 = st.checkbox("Mangueras Alta Presión OK", value=True)
                ch27 = st.checkbox("Gomas de Amortiguación OK", value=True)
                ch28 = st.checkbox("Válvula Limitadora Levante OK", value=True)
                ch29 = st.checkbox("Cubre Carga / Carpa OK", value=True)
                ch30 = st.checkbox("Bisagras Traseras OK", value=True)
            with col_ch4:
                st.markdown("#### 📄 Cabina y Legal")
                ch31 = st.checkbox("Luces Bajas/Altas/Freno OK", value=True)
                ch32 = st.checkbox("Baliza Faena / Alarma Retro. OK", value=True)
                ch33 = st.checkbox("Extintor 10Kg Cargado OK", value=True)
                ch34 = st.checkbox("Cinturones 3 Puntos OK", value=True)
                ch35 = st.checkbox("Parabrisas sin Trizaduras OK", value=True)
                ch36 = st.checkbox("Tacógrafo / GPS Operativo OK", value=True)
                ch37 = st.checkbox("Revisión Técnica Vigente OK", value=True)
                ch38 = st.checkbox("Permiso de Circulación OK", value=True)
                ch39 = st.checkbox("Seguro Obligatorio SOAP OK", value=True)
                ch40 = st.checkbox("Botiquín y Triángulos OK", value=True)
                
            obs = st.text_area("📝 Reporte de Hallazgos u Observaciones:")
            if st.form_submit_button("Firmar Checklist Digitalmente", use_container_width=True):
                todos_ok = all([ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9, ch10, ch11, ch12, ch13, ch14, ch15, ch16, ch17, ch18, ch19, ch20, ch21, ch22, ch23, ch24, ch25, ch26, ch27, ch28, ch29, ch30, ch31, ch32, ch33, ch34, ch35, ch36, ch37, ch38, ch39, ch40])
                camion_sel['checklist_historico'].append({"Fecha": str(datetime.date.today()), "Aprobado": todos_ok, "Firma": info_u['nombre']})
                if not todos_ok:
                    camion_sel['estado'] = "BLOQUEADO POR CHECKLIST"
                    st.error("🚨 Vehículo Bloqueado por anomalías en Checklist.")
                else:
                    camion_sel['estado'] = "OPERATIVO"
                    st.success("✅ Aprobado y Operativo.")
                st.rerun()

    # 4. TAB ÓRDENES DE TRABAJO
    with tab4:
        st.subheader("🛠️ Administrador CMMS: Gestión de Mantenimiento")
        with st.expander("➕ CREAR ORDEN DE TRABAJO", expanded=True):
            col_o1, col_o2 = st.columns(2)
            with col_o1:
                sistema_afectado = st.selectbox("Sistema:", ["Motor", "Frenos", "Transmisión", "Hidráulico", "Eléctrico", "Neumáticos", "Carrocería"])
                prioridad = st.selectbox("Prioridad:", ["Baja", "Media", "CRÍTICA"])
                tipo_maint = st.radio("Tipo:", ["Correctivo", "Preventivo", "Predictivo"])
            with col_o2:
                falla = st.text_area("Descripción de la Intervención:")
                repuestos = st.text_input("Repuestos a Solicitar a Pañol:")
                costo_est = st.number_input("Costo Total Reparación ($):", value=150000, step=10000)
            if st.button("Emitir O.T.", type="primary"):
                if falla:
                    camion_sel['db_ot'].append({"ID_OT": f"OT-{random.randint(5000, 7999)}", "Sistema": sistema_afectado, "Prioridad": prioridad, "Tipo": tipo_maint, "Falla": falla, "Repuestos": repuestos, "Costo_Total": costo_est, "Estado": "Abierta", "Mecanico": info_u['nombre'], "Fecha": str(datetime.date.today())})
                    st.success("O.T. Ingresada al Sistema.")
                    st.rerun()
        st.dataframe(pd.DataFrame(camion_sel['db_ot']), use_container_width=True)
        
        if info_u['nivel'] in [1, 2]:
            if st.button("✔️ Aprobar Reparaciones y Liberar Camión (Cambiar a OPERATIVO)"):
                for ot in camion_sel['db_ot']: ot["Estado"] = "Cerrada"
                camion_sel['estado'] = "OPERATIVO"
                camion_sel['restante_pm'] = 10000 
                st.rerun()

    # 5. TAB COMBUSTIBLE
    with tab5:
        st.subheader("⛽ Módulo de Abastecimiento (Integración Financiera)")
        c_f1, c_f2 = st.columns(2)
        with c_f1:
            litros = st.number_input("Litros Cargados:", min_value=0.0, value=250.0, step=10.0)
            costo = st.number_input("Costo Facturado (CLP con IVA):", min_value=0, value=275000, step=5000)
        with c_f2:
            horometro = st.number_input("Horómetro al momento de carga:", min_value=0, value=int(camion_sel['horas']))
            tipo = st.selectbox("Surtidor / Proveedor:", ["Copec Faena (Diésel)", "Enex (Diésel)", "Tambor AdBlue"])
        if st.button("Procesar Factura de Combustible", type="primary"):
            camion_sel['db_comb'].append({"Fecha": str(datetime.date.today()), "Tipo": tipo, "Litros": litros, "Costo": costo, "Horometro": horometro, "Cargado_Por": st.session_state.usuario_id})
            st.success("Transacción financiera sincronizada.")
            st.rerun()
        st.dataframe(pd.DataFrame(camion_sel['db_comb']), use_container_width=True)

    # 6. TAB FINANZAS
    with tab6:
        st.subheader("📊 Control Financiero, KPIs y Rentabilidad del Activo")
        
        df_c = pd.DataFrame(camion_sel['db_comb'])
        df_o = pd.DataFrame(camion_sel['db_ot'])
        
        t_comb = df_c['Costo'].sum() if not df_c.empty else 0
        t_litros = df_c['Litros'].sum() if not df_c.empty else 0
        t_ot = df_o['Costo_Total'].sum() if not df_o.empty else 0
        costo_total = t_comb + t_ot
        
        rendimiento_km_l = (camion_sel['kms'] * 0.005) / t_litros if t_litros > 0 else 2.1 
        cpk = costo_total / camion_sel['kms'] if camion_sel['kms'] > 0 else 0
        
        col_k1, col_k2, col_k3, col_k4 = st.columns(4)
        col_k1.metric("Gasto Total Operativo (YTD)", f"${costo_total:,.0f} CLP", delta="-2.4% vs Mes Anterior", delta_color="inverse")
        col_k2.metric("Inversión en Mantenimiento", f"${t_ot:,.0f} CLP", delta="Dentro del Presupuesto")
        col_k3.metric("Rendimiento Promedio Diésel", f"{rendimiento_km_l:.2f} Km/L", delta="-0.1 Km/L", delta_color="inverse")
        col_k4.metric("Costo Real (CPK)", f"${cpk:,.2f} /Km", help="Costo Por Kilómetro: Considera Combustible + Taller")
        
        st.markdown("---")
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("#### 📈 Histórico Mensual de Gastos (Proyección)")
            datos_grafico = pd.DataFrame({
                'Combustible (CLP)': [300000, 320000, 290000, 340000, t_comb],
                'Mantenimiento (CLP)': [150000, 0, 500000, 50000, t_ot]
            }, index=['Mar', 'Abr', 'May', 'Jun', 'Jul'])
            st.bar_chart(datos_grafico)
            
        with col_g2:
            st.markdown("#### 📉 Análisis de Depreciación Lineal")
            valor_compra = 120000000 
            vida_util_km = 1000000 
            depreciacion_acumulada = (camion_sel['kms'] / vida_util_km) * valor_compra
            valor_residual = valor_compra - depreciacion_acumulada
            
            st.write(f"**Valor de Compra del Activo:** ${valor_compra:,.0f}")
            st.write(f"**Depreciación Acumulada por Uso:** ${depreciacion_acumulada:,.0f}")
            st.write(f"**Valor Contable Actual (Estimado):** ${valor_residual:,.0f}")
            st.progress(camion_sel['kms'] / vida_util_km)
            st.caption(f"El activo ha consumido el {int((camion_sel['kms'] / vida_util_km)*100)}% de su vida útil contable (1,000,000 Km).")

        st.markdown("---")
        st.markdown("#### 📥 Exportación Contable (Big Data)")
        st.write("Descargue las matrices de datos limpios para integración con SAP / Excel de Finanzas.")
        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1: st.download_button("📥 Matriz Gastos Taller (CSV)", df_o.to_csv(index=False).encode('utf-8'), f"TALLER_{camion_sel['patente']}.csv", "text/csv", use_container_width=True)
        with col_d2: st.download_button("📥 Matriz Combustible (CSV)", df_c.to_csv(index=False).encode('utf-8'), f"COMBUSTIBLE_{camion_sel['patente']}.csv", "text/csv", use_container_width=True)
        with col_d3: st.download_button("📥 Matriz Rendimiento GPS (CSV)", pd.DataFrame(camion_sel['rutas']).to_csv(index=False).encode('utf-8'), f"LOGISTICA_{camion_sel['patente']}.csv", "text/csv", use_container_width=True)

    st.sidebar.divider()
    if st.sidebar.button("Cerrar Sesión Segura (Desconectar)", use_container_width=True):
        st.session_state.conectado = False
        st.rerun()

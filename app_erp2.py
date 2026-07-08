import streamlit as st
import pandas as pd
import datetime
import random

# --- CONFIGURACIÓN DE LA PÁGINA (MODO ANCHO PARA ERP) ---
st.set_page_config(page_title="SGO Enterprise - Áridos Maquehue v3.5", page_icon="🚛", layout="wide")

# --- BASE DE DATOS DE USUARIOS, CLAVES Y PERMISOS OPERATIVOS ---
DB_USUARIOS = {
    "admin1": {"nombre": "Fernando Administrador", "rol": "Administrador General", "nivel": 1},
    "gerente_op": {"nombre": "Carlos Mendoza", "rol": "Gerente de Operaciones", "nivel": 1},
    "jefe_flota": {"nombre": "Juan Pablo Reyes", "rol": "Jefe de Transportes", "nivel": 2},
    "supervisor_taller": {"nombre": "Master Mecánico Inacap", "rol": "Supervisor de Taller (CMMS)", "nivel": 2},
    "mecanico_jefe": {"nombre": "Pedro Aguilera", "rol": "Mecánico Especialista A", "nivel": 3},
    "logistica1": {"nombre": "Andrés Soto", "rol": "Coordinador de Logística", "nivel": 2},
    "despachador": {"nombre": "Manuel Aravena", "rol": "Despachador de Faena", "nivel": 3},
    "prevencionista": {"nombre": "Ana María Silva", "rol": "Asesor HSE / Prevención", "nivel": 2},
    "chofer_lider": {"nombre": "Luis Castro (Operador)", "rol": "Conductor Profesional Heavy Duty", "nivel": 4},
    "auditor_ext": {"nombre": "Inspector Fiscal MOP", "rol": "Auditor Externo Gubernamental", "nivel": 2}
}

# --- INICIALIZACIÓN DE LA BASE DE DATOS EN LA NUBE (SESSION STATE) ---
if 'conectado' not in st.session_state:
    st.session_state.conectado = False
    st.session_state.usuario_id = ""
    st.session_state.user_info = {}

if 'flota' not in st.session_state:
    flota_inicial = []
    lat_base, lon_base = -38.7396, -72.6019
    
    for i in range(1, 11):
        kms_actuales = random.randint(520000, 595000)
        proxima_maint = ((kms_actuales // 10000) + 1) * 10000
        kms_restantes = proxima_maint - kms_actuales
        
        flota_inicial.append({
            "id": f"Camión {i}",
            "patente": f"GP-GC-{89+i}",
            "modelo": "Mercedes-Benz Actros 4144K 8x4 Heavy Tolva",
            "vin": f"WDB9323341L{random.randint(200000, 899999)}",
            "motor_id": f"OM501LA-V/{i}",
            "kms": kms_actuales,
            "horas": random.randint(19000, 23000),
            "lat": lat_base + random.uniform(-0.04, 0.04),
            "lon": lon_base + random.uniform(-0.04, 0.04),
            "estado": "OPERATIVO",
            "restante_pm": kms_restantes,
            "checklist_historico": [],
            "db_comb": [
                {"Fecha": "2026-07-01", "Tipo": "Diésel Grado B", "Litros": 280, "Costo": 308000, "Horometro": 19100, "Cargado_Por": "chofer_lider"},
                {"Fecha": "2026-07-06", "Tipo": "Diésel Grado B", "Litros": 310, "Costo": 341000, "Horometro": 19250, "Cargado_Por": "chofer_lider"}
            ],
            "db_ot": [
                {"ID_OT": "OT-0852", "Sistema": "Frenos", "Prioridad": "Alta", "Tipo": "Correctivo", "Falla": "Desgaste balatas tercer eje balancín", "Repuestos": "Kit Balatas Original M-B", "Costo_Total": 450000, "Estado": "Cerrada", "Mecanico": "mecanico_jefe", "Fecha": "2026-06-10"}
            ],
            "rutas": [
                {"Fecha": str(datetime.date.today()), "Origen": "Pozo Áridos Maquehue", "Destino": "Obra Enlace Pillanlelbún", "Distancia_Km": 34, "Estado": "Completada"},
                {"Fecha": str(datetime.date.today()), "Origen": "Obra Enlace Pillanlelbún", "Destino": "Chancador Principal", "Distancia_Km": 28, "Estado": "En Tránsito"}
            ]
        })
    st.session_state.flota = flota_inicial

# --- INTERFAZ DE CONTROL DE ACCESO ---
if not st.session_state.conectado:
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Mercedes-Logo.svg/1024px-Mercedes-Logo.svg.png", width=90)
    st.sidebar.title("SGO Gate - AWS Cloud")
    st.sidebar.markdown("---")
    st.sidebar.caption("Desplegado en: AWS South America")
    st.sidebar.caption("Desarrollador: Ingeniería Fernando S.")
    
    st.title("🚛 ERP SGO Enterprise - Transportes Maquehue Ltda.")
    st.subheader("Sistema Centralizado de Gestión de Activos y Mantenimiento Industrial")
    st.markdown("---")
    
    st.info("🔓 **Módulo de Acceso Multi-Usuario:** Seleccione su ID asignada por la empresa para validar credenciales.")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        user_input = st.selectbox("Seleccione Identidad de Usuario (10 Perfiles Activos):", list(DB_USUARIOS.keys()), format_func=lambda x: f"{x} - {DB_USUARIOS[x]['nombre']} ({DB_USUARIOS[x]['rol']})")
    with col_l2:
        pass_input = st.text_input("Ingrese PIN / Clave de Acceso Operativo:", type="password", value="inacap2026")
        
    if st.button("Establecer Conexión Con Servidor Central", type="primary", use_container_width=True):
        if pass_input == "inacap2026":
            st.session_state.conectado = True
            st.session_state.usuario_id = user_input
            st.session_state.user_info = DB_USUARIOS[user_input]
            st.rerun()
        else:
            st.error("❌ Error de autenticación. PIN incorrecto.")

# --- INTERFAZ ERP CONECTADO ---
else:
    info_u = st.session_state.user_info
    st.markdown(f"""
    <div style="background-color:#1e293b; padding:12px; border-radius:8px; margin-bottom:15px; color:white;">
        <span style="color:#10b981;">● SERVIDOR CENTRAL OPERATIVO (AWS)</span> | 
        <b>Usuario:</b> {info_u['nombre']} | 
        <b>Cargo:</b> <span style="color:#38bdf8;">{info_u['rol']}</span> | 
        <b>Fecha del Sistema:</b> {datetime.date.today()}
    </div>
    """, unsafe_allow_html=True)
    
    # Menú Lateral - Selector de Camiones
    st.sidebar.header("🚛 Monitoreo de Flota Actros")
    opciones_camiones = [f"{c['id']} [{c['patente']}] - {c['estado']}" for c in st.session_state.flota]
    camion_idx = st.sidebar.selectbox("Seleccione Camión para Inspección Técnica:", range(10), format_func=lambda x: opciones_camiones[x])
    camion_sel = st.session_state.flota[camion_idx]
    
    st.title(f"Ficha de Control Mecánico: {camion_sel['id']}")
    st.markdown(f"**Modelo:** {camion_sel['modelo']} | **VIN:** `{camion_sel['vin']}` | **ID Motor:** `{camion_sel['motor_id']}`")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 Dashboard de Telemetría", 
        "📍 Mapeo GPS e Integración", 
        "📋 Checklist Diario (30 Puntos)", 
        "🛠️ Órdenes de Trabajo (CMMS)", 
        "⛽ Gestión de Combustible",
        "📊 Informes y Finanzas"
    ])
    
    # 1. TAB DASHBOARD
    with tab1:
        st.subheader("📊 Variables Críticas del Motor y Transmisión")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Odómetro de Flota", f"{camion_sel['kms']:,} Km")
        m2.metric("Horómetro Acumulado", f"{camion_sel['horas']:,} Hrs")
        color_estado = "🟢" if camion_sel['estado'] == "OPERATIVO" else "🔴"
        m3.metric("Estatus del Activo", f"{color_estado} {camion_sel['estado']}")
        m4.metric("Voltaje de Alternador", "26.8 V (Estable)")
        
        st.markdown("---")
        st.subheader("⏰ Monitoreo Automático de Alertas de Mantenimiento Periódico")
        rest_km = camion_sel['restante_pm']
        porcentaje_vida_util = max(0, min(int((rest_km / 10000) * 100), 100))
        
        col_bar, col_txt_bar = st.columns([3, 1])
        with col_bar:
            st.write(f"**Vida Útil del Aceite y Filtros (Pauta PM de 10,000 Km):** Quedan **{rest_km:,} Km** antes del taller.")
            st.progress(porcentaje_vida_util)
        with col_txt_bar:
            st.metric("Vida Restante Aceite", f"{porcentaje_vida_util}%")
            
        if rest_km <= 0:
            st.error(f"🚨 ALERTAS DE CRITICIDAD TOTAL: Vencido hace {abs(rest_km)} Km. Detención inmediata.")
        elif rest_km <= 1500:
            st.warning("⚠️ ALERTA PREVENTIVA: Planificar taller. Menos de 1,500 Km restantes.")
        else:
            st.success("✅ Semáforo Mecánico Verde: Lubricantes y desgaste dentro de los parámetros nominales.")

    # 2. TAB GPS Y RUTAS (MEJORADO CON INTEGRACIÓN DE TELEMETRÍA EN TIEMPO REAL)
    with tab2:
        st.subheader("📍 Rastreo Satelital e Integración de Telemetría GPS")
        st.write("El mapa muestra la ubicación exacta de la unidad seleccionada arriba. Al interactuar o simular movimientos, las variables críticas de telemetría se consolidan dinámicamente.")
        
        # Filtrar las coordenadas del camión específico seleccionado por el usuario
        df_coordenada_actual = pd.DataFrame([{
            "lat": camion_sel["lat"], 
            "lon": camion_sel["lon"], 
            "Vehículo": camion_sel["id"]
        }])
        
        # Desplegar mapa centrado en el camión seleccionado
        st.map(df_coordenada_actual, zoom=12)
        
        # NUEVO RECUADRO: Despliegue de estado integrado directamente bajo el GPS
        st.markdown("### 🖥️ Consola de Telemetría Satelital del Vehículo")
        
        # Calcular el último combustible cargado registrado en su base de datos
        ultimo_combustible = f"{camion_sel['db_comb'][-1]['Litros']} L" if camion_sel['db_comb'] else "No registra"
        
        box_col1, box_col2, box_col3, box_col4 = st.columns(4)
        with box_col1:
            st.info(f"🛰️ **ID Unidad:** \n\n `{camion_sel['id']}`")
        with box_col2:
            st.info(f"🛣️ **Kilometraje en GPS:** \n\n `{camion_sel['kms']:,} Km`")
        with box_col3:
            st.info(f"⛽ **Último Carga Diésel:** \n\n `{ultimo_combustible}`")
        with box_col4:
            st.info(f"⚙️ **Estado en Consola:** \n\n `{camion_sel['estado']}`")
            
        st.markdown("#### 🗺️ Bitácora de Tránsito Diario de la Unidad")
        st.dataframe(pd.DataFrame(camion_sel['rutas']), use_container_width=True)
        
        if st.button("Simular Avance en Ruta y Transmisión Satelital (CAN-Bus) 🔄", use_container_width=True):
            km_recorridos = random.randint(20, 75)
            camion_sel['kms'] += km_recorridos
            camion_sel['restante_pm'] -= km_recorridos
            camion_sel['horas'] += random.randint(1, 4)
            camion_sel['lat'] += random.uniform(-0.015, 0.015)
            camion_sel['lon'] += random.uniform(-0.015, 0.015)
            st.rerun()

    # 3. TAB CHECKLIST (30 PUNTOS)
    with tab3:
        st.subheader("📋 Formulario de Inspección de Seguridad Pre-Uso (30 Parámetros)")
        with st.form("super_checklist_form"):
            col_ch1, col_ch2, col_ch3 = st.columns(3)
            with col_ch1:
                st.markdown("#### 🛢️ Sistema de Motor y Niveles")
                ch1 = st.checkbox("Nivel Aceite Carter Motor OK", value=True)
                ch2 = st.checkbox("Nivel Líquido Refrigerante Radiador OK", value=True)
                ch3 = st.checkbox("Correas de Alternador y Ventilador OK", value=True)
                ch4 = st.checkbox("Líquido de Dirección Hidráulica OK", value=True)
                ch5 = st.checkbox("Ausencia de Fugas de Petróleo OK", value=True)
                ch6 = st.checkbox("Indicador de Restricción Filtro Aire OK", value=True)
                st.markdown("#### 🛑 Sistema de Frenos (Circuito Aire)")
                ch7 = st.checkbox("Presión Manómetro sobre 100 PSI OK", value=True)
                ch8 = st.checkbox("Válvulas de Purga de Estanques OK", value=True)
                ch9 = st.checkbox("Grosor Prontuario de Balatas OK", value=True)
                ch10 = st.checkbox("Freno de Estacionamiento OK", value=True)
                ch11 = st.checkbox("Mangueras Flexibles de Aire OK", value=True)
            with col_ch2:
                st.markdown("#### ⚙️ Chasis y Tren Delantero/Trasero")
                ch12 = st.checkbox("Alineación de Pernos en U OK", value=True)
                ch13 = st.checkbox("Grapas de Paquetes de Resortes OK", value=True)
                ch14 = st.checkbox("Pulmones Neumáticos sin Fisuras OK", value=True)
                ch15 = st.checkbox("Apriete de Tuercas Torque OK", value=True)
                ch16 = st.checkbox("Neumáticos sin Cortes visibles OK", value=True)
                ch17 = st.checkbox("Profundidad de Cocada OK", value=True)
                ch18 = st.checkbox("Ausencia de Fugas en Cubos OK", value=True)
            with col_ch3:
                st.markdown("#### 🏗️ Componentes de Tolva e Hidráulicos")
                ch19 = st.checkbox("Cilindro de Levante Telescópico OK", value=True)
                ch20 = st.checkbox("Nivel de Aceite Tanque Hidráulico OK", value=True)
                ch21 = st.checkbox("Bomba Hidráulica y Toma Fuerza OK", value=True)
                ch22 = st.checkbox("Pasadores de Seguridad de Tolva OK", value=True)
                ch23 = st.checkbox("Ganchos de Portalón Trasero OK", value=True)
                st.markdown("#### 💺 Cabina, Luces y Prevención HSE")
                ch24 = st.checkbox("Luces de Tránsito OK", value=True)
                ch25 = st.checkbox("Baliza Estroboscópica OK", value=True)
                ch26 = st.checkbox("Alarma de Retroceso OK", value=True)
                ch27 = st.checkbox("Extintor PQS de 10Kg OK", value=True)
                ch28 = st.checkbox("Cinturones de Seguridad OK", value=True)
                ch29 = st.checkbox("Vidrios, Parabrisas y Espejos OK", value=True)
                ch30 = st.checkbox("Dispositivo Tacógrafo Operativo OK", value=True)
            st.markdown("---")
            obs_texto = st.text_area("📝 Cuadro Obligatorio de Comentarios / Reporte de Hallazgos:")
            boton_guardar_chk = st.form_submit_button("Firmar Digitalmente e Ingresar al Servidor", use_container_width=True)
            
            if boton_guardar_chk:
                todos_puntos = [ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8, ch9, ch10, ch11, ch12, ch13, ch14, ch15, ch16, ch17, ch18, ch19, ch20, ch21, ch22, ch23, ch24, ch25, ch26, ch27, ch28, ch29, ch30]
                registro_auditoria = {
                    "Fecha": str(datetime.date.today()),
                    "Auditor": info_u['nombre'],
                    "Rol": info_u['rol'],
                    "Aprobado": all(todos_puntos),
                    "Observaciones": obs_texto if obs_texto else "Sin anomalías."
                }
                camion_sel['checklist_historico'].append(registro_auditoria)
                if not all(todos_puntos):
                    camion_sel['estado'] = "BLOQUEADO EN TALLER"
                    st.error(f"🚨 RECHAZO: Unidad bloqueada centralizadamente por fallas mecánicas.")
                else:
                    camion_sel['estado'] = "OPERATIVO"
                    st.success(f"✅ CONTROL CONFORME: Unidad autorizada a salir a ruta.")
                    
        st.markdown("### 📂 Registro Histórico de Checklists")
        if len(camion_sel['checklist_historico']) > 0:
            st.dataframe(pd.DataFrame(camion_sel['checklist_historico']), use_container_width=True)

    # 4. TAB ÓRDENES DE TALLER (CMMS)
    with tab4:
        st.subheader("🛠️ Administrador CMMS: Órdenes de Trabajo")
        with st.expander("➕ CREAR ORDEN DE TRABAJO FORMAL (O.T.)", expanded=True):
            col_o1, col_o2 = st.columns(2)
            with col_o1:
                sistema_afectado = st.selectbox("Sistema Mecánico a Intervenir:", ["Motor", "Frenos", "Suspensión / Chasis", "Sistema Hidráulico", "Sistema Eléctrico", "Neumáticos"])
                prioridad_ot = st.selectbox("Nivel de Urgencia Operativa:", ["Baja", "Media", "CRÍTICA / DETENCIÓN"])
                tipo_mantenimiento = st.radio("Naturaleza del Trabajo:", ["Correctivo", "Preventivo", "Predictivo"])
            with col_o2:
                falla_tecnica = st.text_area("Informe Técnico de la Falla:")
                repuestos_ot = st.text_input("Listado de Componentes / Repuestos:")
                costo_estimado = st.number_input("Costo Estimado ($ CLP):", min_value=0, value=150000)
                
            if st.button("Emitir y Timbrar Orden de Trabajo", type="primary", use_container_width=True):
                if falla_tecnica:
                    camion_sel['db_ot'].append({
                        "ID_OT": f"OT-{random.randint(5000, 7999)}",
                        "Sistema": sistema_afectado,
                        "Prioridad": prioridad_ot,
                        "Tipo": tipo_mantenimiento,
                        "Falla": falla_tecnica,
                        "Repuestos": repuestos_ot if repuestos_ot else "Sin insumos",
                        "Costo_Total": costo_estimado,
                        "Estado": "Abierta / En Ejecución",
                        "Mecanico": info_u['nombre'],
                        "Fecha": str(datetime.date.today())
                    })
                    st.success("📋 Documento Electrónico guardado en el servidor.")
                    st.rerun()
                    
        st.markdown("### 📂 Backlog Completo de Órdenes")
        df_ot_data = pd.DataFrame(camion_sel['db_ot'])
        if not df_ot_data.empty:
            st.dataframe(df_ot_data, use_container_width=True)
            if info_u['nivel'] in [1, 2]:
                if st.button("✔️ Certificar Reparaciones de Taller y Cerrar O.T. Activas 🔓", use_container_width=True):
                    for ot in camion_sel['db_ot']:
                        ot["Estado"] = "Cerrada / Conforme"
                    camion_sel['estado'] = "OPERATIVO"
                    camion_sel['restante_pm'] = 10000
                    st.success("Inspección mecánica aprobada. Estado: OPERATIVO.")
                    st.rerun()

    # 5. TAB COMBUSTIBLE
    with tab5:
        st.subheader("⛽ Módulo de Abastecimiento de Combustible")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            litros_cargados = st.number_input("Cantidad Cargada (Litros):", min_value=0, value=200)
            costo_combustible = st.number_input("Costo Facturado ($ CLP):", min_value=0, value=220000)
        with col_f2:
            horometro_registro = st.number_input("Lectura Horómetro Tablero (Hrs):", min_value=int(camion_sel['horas']))
            comb_tipo = st.selectbox("Fluido de Surtidor:", ["Diésel Grado B", "Urea / AdBlue"])
            
        if st.button("Registrar Ticket de Surtidor", type="primary", use_container_width=True):
            if litros_cargados > 0 and costo_combustible > 0:
                camion_sel['db_comb'].append({
                    "Fecha": str(datetime.date.today()),
                    "Tipo": comb_tipo,
                    "Litros": litros_cargados,
                    "Costo": costo_combustible,
                    "Horometro": horometro_registro,
                    "Cargado_Por": st.session_state.usuario_id
                })
                st.success("Transacción registrada contablemente.")
                st.rerun()
                
        st.dataframe(pd.DataFrame(camion_sel['db_comb']), use_container_width=True)

    # 6. TAB INFORMES Y FINANZAS
    with tab6:
        st.subheader("📊 Auditoría Financiera y KPIs de Gestión")
        df_c_kpi = pd.DataFrame(camion_sel['db_comb'])
        df_o_kpi = pd.DataFrame(camion_sel['db_ot'])
        
        total_gasto_comb = df_c_kpi['Costo'].sum() if not df_c_kpi.empty else 0
        total_litros_comb = df_c_kpi['Litros'].sum() if not df_c_kpi.empty else 0
        total_gasto_taller = df_o_kpi['Costo_Total'].sum() if not df_o_kpi.empty else 0
        
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Gasto Total Combustible", f"${total_gasto_comb:,.0f} CLP")
        k2.metric("Inversión en Taller", f"${total_gasto_taller:,.0f} CLP")
        k3.metric("Diésel Consumido", f"{total_litros_comb:,} L")
        
        costo_total_activo = total_gasto_comb + total_gasto_taller
        cpk_calculado = costo_total_activo / camion_sel['kms'] if camion_sel['kms'] > 0 else 0
        k4.metric("Costo x Km (CPK)", f"${cpk_calculado:,.2f} CLP/Km")
        
        st.markdown("---")
        st.markdown("#### 📥 Centro de Exportación de Informes")
        col_down1, col_down2, col_down3 = st.columns(3)
        with col_down1:
            st.download_button(label="📥 Exportar O.T. (CSV)", data=df_o_kpi.to_csv(index=False).encode('utf-8'), file_name=f"OT_{camion_sel['patente']}.csv", mime="text/csv", use_container_width=True)
        with col_down2:
            st.download_button(label="📥 Exportar Diésel (CSV)", data=df_c_kpi.to_csv(index=False).encode('utf-8'), file_name=f"DIESEL_{camion_sel['patente']}.csv", mime="text/csv", use_container_width=True)
        with col_down3:
            st.download_button(label="📥 Exportar GPS Histórico (CSV)", data=pd.DataFrame(camion_sel['rutas']).to_csv(index=False).encode('utf-8'), file_name=f"GPS_{camion_sel['patente']}.csv", mime="text/csv", use_container_width=True)

    st.divider()
    if st.button("Cerrar Sesión de Forma Segura (Desconectar AWS)", use_container_width=True):
        st.session_state.conectado = False
        st.rerun()

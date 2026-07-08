import streamlit as st
import pandas as pd
import datetime
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="SGO Enterprise - Áridos Maquehue", page_icon="🚛", layout="wide")

# --- BASE DE DATOS DE USUARIOS ---
DB_USUARIOS = {
    "admin1": {"nombre": "Fernando Administrador", "rol": "Administrador General", "nivel": 1},
    "gerente_op": {"nombre": "Carlos Mendoza", "rol": "Gerente de Operaciones", "nivel": 1},
    "jefe_flota": {"nombre": "Juan Pablo Reyes", "rol": "Jefe de Transportes", "nivel": 2},
    "supervisor_taller": {"nombre": "Master Mecánico Inacap", "rol": "Supervisor de Taller", "nivel": 2},
    "mecanico_jefe": {"nombre": "Pedro Aguilera", "rol": "Mecánico Especialista A", "nivel": 3},
    "logistica1": {"nombre": "Andrés Soto", "rol": "Coordinador de Logística", "nivel": 2},
    "despachador": {"nombre": "Manuel Aravena", "rol": "Despachador de Faena", "nivel": 3},
    "prevencionista": {"nombre": "Ana María Silva", "rol": "Prevención", "nivel": 2},
    "chofer_lider": {"nombre": "Luis Castro", "rol": "Conductor Profesional", "nivel": 4},
    "auditor_ext": {"nombre": "Inspector Fiscal", "rol": "Auditor Externo", "nivel": 2}
}

# --- INICIALIZACIÓN DE LA NUBE ---
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
            "modelo": "Mercedes-Benz Actros 4144K 8x4",
            "vin": f"WDB9323341L{random.randint(200000, 899999)}",
            "motor_id": f"OM501LA-V/{i}",
            "kms": kms_actuales,
            "horas": random.randint(19000, 23000),
            "lat": lat_base + random.uniform(-0.06, 0.06),
            "lon": lon_base + random.uniform(-0.06, 0.06),
            "estado": "OPERATIVO",
            "restante_pm": kms_restantes,
            "checklist_historico": [],
            "db_comb": [
                {"Fecha": "2026-07-01", "Tipo": "Diésel Grado B", "Litros": 280, "Costo": 308000, "Horometro": 19100, "Cargado_Por": "chofer_lider"}
            ],
            "db_ot": [
                {"ID_OT": "OT-0852", "Sistema": "Frenos", "Prioridad": "Alta", "Tipo": "Correctivo", "Falla": "Desgaste balatas", "Repuestos": "Kit Balatas", "Costo_Total": 450000, "Estado": "Cerrada", "Mecanico": "mecanico_jefe", "Fecha": "2026-06-10"}
            ],
            "rutas": [
                {"Fecha": str(datetime.date.today()), "Origen": "Pozo", "Destino": "Obra", "Distancia_Km": 34, "Estado": "Completada"}
            ]
        })
    st.session_state.flota = flota_inicial

# --- ACCESO (LOGIN) ---
if not st.session_state.conectado:
    st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Mercedes-Logo.svg/1024px-Mercedes-Logo.svg.png", width=90)
    st.title("🚛 ERP SGO Enterprise - Áridos Maquehue")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        user_input = st.selectbox("Seleccione Usuario:", list(DB_USUARIOS.keys()), format_func=lambda x: f"{x} - {DB_USUARIOS[x]['nombre']}")
    with col_l2:
        pass_input = st.text_input("Clave:", type="password", value="inacap2026")
        
    if st.button("Conectar al Servidor", type="primary"):
        if pass_input == "inacap2026":
            st.session_state.conectado = True
            st.session_state.usuario_id = user_input
            st.session_state.user_info = DB_USUARIOS[user_input]
            st.rerun()
        else:
            st.error("❌ PIN incorrecto.")

# --- ERP PRINCIPAL ---
else:
    info_u = st.session_state.user_info
    st.markdown(f"🟢 **CONECTADO:** {info_u['nombre']} | **Cargo:** {info_u['rol']}")
    
    st.sidebar.header("🚛 Selector de Flota")
    opciones_camiones = [f"{c['id']} [{c['patente']}] - {c['estado']}" for c in st.session_state.flota]
    
    # ESTO ARREGLA EL PROBLEMA DEL SELECTOR (Tiene un 'key' único)
    camion_idx = st.sidebar.selectbox("Seleccione Unidad a Revisar:", range(10), format_func=lambda x: opciones_camiones[x], key="selector_flota_maestro")
    camion_sel = st.session_state.flota[camion_idx]
    
    st.title(f"Control: {camion_sel['id']} | Patente: {camion_sel['patente']}")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 Dashboard", 
        "📍 GPS (Los 10 Camiones)", 
        "📋 Checklist (30 Ptos)", 
        "🛠️ Órdenes de Taller", 
        "⛽ Combustible",
        "📊 Informes"
    ])
    
    # 1. TAB DASHBOARD
    with tab1:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Odómetro", f"{camion_sel['kms']:,} Km")
        col2.metric("Horómetro", f"{camion_sel['horas']:,} Hrs")
        col3.metric("Estatus", f"{camion_sel['estado']}")
        col4.metric("Restante Pauta", f"{camion_sel['restante_pm']:,} Km")
        
        rest_km = camion_sel['restante_pm']
        if rest_km <= 0: st.error("🚨 Vencido. Detención obligatoria.")
        elif rest_km <= 1500: st.warning("⚠️ Precaución. Agendar taller.")
        else: st.success("✅ Parámetros mecánicos dentro de norma.")

    # 2. TAB GPS Y RUTAS (ESTO ARREGLA EL MAPA COMPLETO)
    with tab2:
        st.subheader(f"📍 GPS: Flota Completa (Mostrando unidad seleccionada en Rojo)")
        
        # Preparamos los 10 camiones para el mapa
        datos_mapa = []
        for index, c in enumerate(st.session_state.flota):
            # El camión seleccionado será rojo (#ff0000) y grande. Los demás serán azules (#0000ff)
            color_marcador = "#ff0000" if index == camion_idx else "#0000ff"
            tamano_marcador = 800 if index == camion_idx else 150
            
            datos_mapa.append({
                "lat": c["lat"],
                "lon": c["lon"],
                "color_marcador": color_marcador,
                "tamano": tamano_marcador
            })
            
        df_mapa = pd.DataFrame(datos_mapa)
        
        try:
            # Streamlit moderno permite colores
            st.map(df_mapa, color="color_marcador", size="tamano", zoom=10)
        except:
            # Respaldo por si falla la versión
            st.map(df_mapa, zoom=10)
        
        st.markdown(f"### 🖥️ Consola de Unidad Seleccionada: **{camion_sel['id']}**")
        b1, b2, b3 = st.columns(3)
        b1.info(f"🛣️ **Kms Actuales:** `{camion_sel['kms']:,} Km`")
        b2.info(f"⚙️ **Estado:** `{camion_sel['estado']}`")
        b3.info(f"🕒 **Horas de Motor:** `{camion_sel['horas']} Hrs`")
        
        if st.button("Simular Ruta Satelital de Unidad Seleccionada 🔄", use_container_width=True):
            camion_sel['kms'] += random.randint(20, 75)
            camion_sel['restante_pm'] -= random.randint(20, 75)
            camion_sel['lat'] += random.uniform(-0.015, 0.015)
            camion_sel['lon'] += random.uniform(-0.015, 0.015)
            st.rerun()

    # 3. TAB CHECKLIST
    with tab3:
        st.subheader("📋 Auditoría Pre-Uso")
        with st.form("form_chk"):
            c1, c2 = st.columns(2)
            with c1:
                st.write("**Mecánica y Fluidos**")
                ch1 = st.checkbox("Aceite Motor OK", value=True)
                ch2 = st.checkbox("Refrigerante OK", value=True)
                ch3 = st.checkbox("Presión Frenos >100PSI OK", value=True)
                ch4 = st.checkbox("Fugas Físicas Ausentes OK", value=True)
            with c2:
                st.write("**Estructura y Seguridad**")
                ch5 = st.checkbox("Neumáticos y Tuercas OK", value=True)
                ch6 = st.checkbox("Luces / Baliza OK", value=True)
                ch7 = st.checkbox("Tolva e Hidráulica OK", value=True)
                ch8 = st.checkbox("Extintor OK", value=True)
                
            btn_chk = st.form_submit_button("Firmar Checklist")
            if btn_chk:
                if all([ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8]):
                    camion_sel['estado'] = "OPERATIVO"
                    st.success("✅ Aprobado.")
                else:
                    camion_sel['estado'] = "BLOQUEADO EN TALLER"
                    st.error("🚨 Rechazado. Unidad Bloqueada.")
                st.rerun()

    # 4. TAB ÓRDENES DE TRABAJO
    with tab4:
        st.subheader("🛠️ Generador de O.T.")
        tipo_ot = st.selectbox("Tipo:", ["Correctivo", "Preventivo", "Neumáticos"])
        falla = st.text_area("Descripción de Falla:")
        if st.button("Emitir O.T.", type="primary"):
            if falla:
                camion_sel['db_ot'].append({
                    "ID_OT": f"OT-{random.randint(1000,9999)}", "Tipo": tipo_ot, 
                    "Falla": falla, "Estado": "Abierta", "Fecha": str(datetime.date.today())
                })
                st.success("Guardado.")
                st.rerun()
                
        st.dataframe(pd.DataFrame(camion_sel['db_ot']), use_container_width=True)
        if st.button("Cerrar Todas las O.T. (Liberar Camión)"):
            for ot in camion_sel['db_ot']: ot["Estado"] = "Cerrada"
            camion_sel['estado'] = "OPERATIVO"
            camion_sel['restante_pm'] = 10000
            st.rerun()

    # 5. TAB COMBUSTIBLE
    with tab5:
        st.subheader("⛽ Registrar Carga Diésel")
        lit = st.number_input("Litros:", min_value=0, value=200)
        cost = st.number_input("Monto $:", min_value=0, value=200000)
        if st.button("Guardar Carga", type="primary"):
            camion_sel['db_comb'].append({"Fecha": str(datetime.date.today()), "Litros": lit, "Costo": cost})
            st.success("Listo.")
            st.rerun()
        st.dataframe(pd.DataFrame(camion_sel['db_comb']), use_container_width=True)

    # 6. TAB INFORMES
    with tab6:
        st.subheader("📊 Finanzas y KPIs")
        df_c = pd.DataFrame(camion_sel['db_comb'])
        gasto_comb = df_c['Costo'].sum() if not df_c.empty else 0
        st.metric("Gasto Total Combustible Unidad", f"${gasto_comb:,.0f} CLP")
        st.info("Utilice los botones de descarga en un entorno real para extraer los CSV a PowerBI.")

    st.divider()
    if st.button("Cerrar Sesión"):
        st.session_state.conectado = False
        st.rerun()

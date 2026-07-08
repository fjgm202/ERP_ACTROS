import streamlit as st
import pandas as pd
import datetime
import random

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="SGO - Transportes Maquehue", page_icon="🚛", layout="wide")

# --- BASE DE DATOS DE USUARIOS ---
DB_USUARIOS = {
    "admin1": {"nombre": "Catalyna Gajardo", "rol": "Administrador General", "nivel": 1},
    "gerente_op": {"nombre": "Fernando Gonzalez", "rol": "Gerente de Operaciones", "nivel": 1},
    "jefe_flota": {"nombre": "Nicolas Sandoval", "rol": "Jefe de Transportes", "nivel": 2},
    "supervisor_taller": {"nombre": "Felipe Herrera", "rol": "Supervisor de Taller", "nivel": 2},
    "mecanico_jefe": {"nombre": "Pedro Aguilera", "rol": "Mecánico", "nivel": 3},
    "logistica1": {"nombre": "Andrés Soto", "rol": "Logística", "nivel": 2},
    "despachador": {"nombre": "Manuel Aravena", "rol": "Despachador", "nivel": 3},
    "prevencionista": {"nombre": "Ana María Silva", "rol": "Prevencionista de Riesgos", "nivel": 2},
    "chofer_lider": {"nombre": "Luis Castro", "rol": "Conductor", "nivel": 4},
    "auditor_ext": {"nombre": "Profesor Evaluador", "rol": "Auditor Externo", "nivel": 1} # Añadido para el profe
}

# --- INICIALIZACIÓN DE LA FLOTA ---
if 'conectado' not in st.session_state:
    st.session_state.conectado = False
    st.session_state.usuario_id = ""
    st.session_state.user_info = {}

if 'flota' not in st.session_state:
    flota_inicial = []
    lat_base, lon_base = -38.7396, -72.6019
    # 85% de los camiones operativos
    estados_posibles = ["OPERATIVO"] * 17 + ["EN TALLER", "MANTENCIÓN", "FUERA DE SERVICIO"]
    
    for i in range(1, 11):
        kms_actuales = random.randint(520000, 595000)
        proxima_maint = ((kms_actuales // 10000) + 1) * 10000
        kms_restantes = proxima_maint - kms_actuales
        estado_camion = random.choice(estados_posibles)
        
        flota_inicial.append({
            "id": f"Unidad 0{i}" if i < 10 else f"Unidad {i}",
            "patente": f"GP-GC-{89+i}",
            "modelo": "Mercedes-Benz Actros 4144K",
            "kms": kms_actuales,
            "horas": random.randint(19000, 23000),
            "lat": lat_base + random.uniform(-0.06, 0.06),
            "lon": lon_base + random.uniform(-0.06, 0.06),
            "estado": estado_camion,
            "restante_pm": kms_restantes if estado_camion == "OPERATIVO" else random.randint(-500, 1500),
            "checklist_historico": [],
            "db_comb": [
                {"Fecha": "2026-06-15", "Tipo": "Diésel", "Litros": 280, "Costo": 308000, "Horometro": 19100},
                {"Fecha": "2026-07-06", "Tipo": "Diésel", "Litros": 310, "Costo": 341000, "Horometro": 19250}
            ],
            "db_ot": [
                {"ID": "OT-0852", "Sistema": "Frenos", "Falla": "Cambio de balatas", "Costo": 450000, "Estado": "Cerrada", "Fecha": "2026-06-10"}
            ],
            "rutas": [
                {"Fecha": str(datetime.date.today()), "Origen": "Pozo Maquehue", "Destino": "Obra Enlace", "Distancia_Km": 34, "Estado": "Completada"},
                {"Fecha": str(datetime.date.today()), "Origen": "Obra Enlace", "Destino": "Chancador", "Distancia_Km": 28, "Estado": "En Tránsito"}
            ]
        })
    st.session_state.flota = flota_inicial

# --- PANTALLA DE ACCESO (LOGIN AMIGABLE) ---
if not st.session_state.conectado:
    st.title("🚛 Sistema de Gestión - Áridos Maquehue")
    st.write("Bienvenido al sistema. Por favor, inicie sesión para continuar.")
    
    col1, col2 = st.columns(2)
    with col1:
        user_input = st.selectbox("1. Seleccione su Usuario:", list(DB_USUARIOS.keys()), format_func=lambda x: f"{DB_USUARIOS[x]['nombre']} - {DB_USUARIOS[x]['rol']}")
    with col2:
        pass_input = st.text_input("2. Ingrese su Contraseña:", type="password", value="inacap2026")
        
    if st.button("Entrar al Sistema", type="primary", use_container_width=True):
        if pass_input == "inacap2026":
            st.session_state.conectado = True
            st.session_state.usuario_id = user_input
            st.session_state.user_info = DB_USUARIOS[user_input]
            st.rerun()
        else:
            st.error("❌ Contraseña incorrecta. Intente nuevamente.")

# --- INTERFAZ PRINCIPAL DEL SISTEMA ---
else:
    info_u = st.session_state.user_info
    
    # BARRA DE BIENVENIDA
    st.success(f"👋 Bienvenido, **{info_u['nombre']}** ({info_u['rol']}) | Fecha de hoy: {datetime.date.today().strftime('%d/%m/%Y')}")
    
    # RESUMEN GLOBAL (Fácil de entender)
    total_camiones = len(st.session_state.flota)
    camiones_operativos = sum(1 for c in st.session_state.flota if c['estado'] == "OPERATIVO")
    
    st.write("### 📊 Resumen de la Flota")
    col_kpi1, col_kpi2 = st.columns([1, 3])
    with col_kpi1:
        st.metric("Camiones Operativos", f"{camiones_operativos} de {total_camiones}")
    with col_kpi2:
        st.progress(camiones_operativos / total_camiones, text="Porcentaje de camiones listos para trabajar")
    
    st.divider()

    # BUSCADOR DE CAMIONES
    st.write("### 🔍 Seleccione un Camión para ver sus detalles")
    col_sel, col_info, col_btn = st.columns([2, 1, 1])
    
    with col_sel:
        opciones_camiones = [f"{c['id']} [Patente: {c['patente']}]" for c in st.session_state.flota]
        camion_idx = st.selectbox("Lista de Camiones:", range(total_camiones), format_func=lambda x: opciones_camiones[x])
        camion_sel = st.session_state.flota[camion_idx]
        
    with col_info:
        st.write("**Estado Actual:**")
        if camion_sel['estado'] == "OPERATIVO":
            st.success(f"✅ {camion_sel['estado']}")
        else:
            st.error(f"⚠️ {camion_sel['estado']}")
            
    with col_btn:
        st.write("**Opciones:**")
        if info_u['nivel'] <= 2:
            if camion_sel['estado'] == "OPERATIVO":
                if st.button("⛔ Enviar a Taller", use_container_width=True):
                    camion_sel['estado'] = "EN TALLER"
                    st.rerun()
            else:
                if st.button("✅ Habilitar Camión", use_container_width=True, type="primary"):
                    camion_sel['estado'] = "OPERATIVO"
                    st.rerun()
            
    st.markdown("---")
    
    # --- PESTAÑAS CON NOMBRES CLAROS ---
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "1️⃣ Tablero General", 
        "2️⃣ Mapa GPS", 
        "3️⃣ Revisión Diaria", 
        "4️⃣ Taller y Reparaciones", 
        "5️⃣ Combustible",
        "6️⃣ Resumen de Gastos"
    ])
    
    # 1. TABLERO GENERAL
    with tab1:
        st.subheader("Datos del Camión")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Kilometraje", f"{camion_sel['kms']:,} Km")
        m2.metric("Horas de Uso", f"{camion_sel['horas']:,} Hrs")
        m3.metric("Batería", "24.2 V", "Normal") # <- Batería ajustada a un valor más amigable
        m4.metric("Próxima Mantención en", f"{camion_sel['restante_pm']:,} Km")
        
        st.write("---")
        st.write("**Sensores del Motor:**")
        t1, t2, t3, t4 = st.columns(4)
        if camion_sel['estado'] == "OPERATIVO":
            t1.metric("Temperatura", f"{random.randint(85, 92)} °C")
            t2.metric("Presión de Aceite", "Normal")
            t3.metric("Estanque de Petróleo", f"{random.randint(20, 95)} %")
            t4.metric("Presión Neumáticos", "110 PSI")
        else:
            t1.metric("Temperatura", "Apagado")
            t2.metric("Presión de Aceite", "Apagado")
            t3.metric("Estanque de Petróleo", f"{random.randint(20, 95)} %")
            t4.metric("Presión Neumáticos", "Normal")

    # 2. MAPA GPS
    with tab2:
        st.subheader("Ubicación en el Mapa")
        st.write("El punto rojo indica el camión seleccionado actualmente.")
        datos_mapa = []
        for index, c in enumerate(st.session_state.flota):
            datos_mapa.append({
                "lat": c["lat"], "lon": c["lon"],
                "color_gps": "#FF0000" if index == camion_idx else "#0000FF",
                "tamano_gps": 800 if index == camion_idx else 200
            })
        st.map(pd.DataFrame(datos_mapa), color="color_gps", size="tamano_gps", zoom=11)
        st.write("**Viajes del día:**")
        st.dataframe(pd.DataFrame(camion_sel['rutas']), use_container_width=True)

    # 3. REVISIÓN DIARIA
    with tab3:
        st.subheader("Formulario de Revisión antes de usar (Checklist)")
        st.write("Marque las casillas para confirmar que el camión está en buenas condiciones.")
        with st.form("form_checklist"):
            col_ch1, col_ch2 = st.columns(2)
            with col_ch1:
                ch1 = st.checkbox("Nivel de Aceite Correcto", value=True)
                ch2 = st.checkbox("Nivel de Agua/Refrigerante Correcto", value=True)
                ch3 = st.checkbox("Luces Delanteras y Traseras Funcionan", value=True)
                ch4 = st.checkbox("Frenos en buen estado", value=True)
            with col_ch2:
                ch5 = st.checkbox("Neumáticos sin daños visuales", value=True)
                ch6 = st.checkbox("Extintor y Botiquín a bordo", value=True)
                ch7 = st.checkbox("Documentos del camión al día", value=True)
                ch8 = st.checkbox("Tolva y sistema hidráulico sin fugas", value=True)
                
            if st.form_submit_button("Guardar Revisión", use_container_width=True):
                todos_ok = all([ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8])
                if not todos_ok:
                    camion_sel['estado'] = "FUERA DE SERVICIO"
                    st.error("Atención: El camión fue marcado como 'Fuera de Servicio' porque hay problemas en la revisión.")
                else:
                    camion_sel['estado'] = "OPERATIVO"
                    st.success("Revisión guardada. El camión está listo para trabajar.")
                st.rerun()

    # 4. TALLER Y REPARACIONES
    with tab4:
        st.subheader("Historial de Reparaciones")
        st.dataframe(pd.DataFrame(camion_sel['db_ot']), use_container_width=True)
        
        st.write("---")
        st.write("**Registrar Nueva Reparación:**")
        with st.form("form_taller"):
            falla = st.text_input("¿Qué problema tiene el camión?")
            costo_est = st.number_input("Costo de la reparación ($):", value=150000, step=10000)
            if st.form_submit_button("Guardar Reparación"):
                if falla:
                    camion_sel['db_ot'].append({"ID": f"OT-{random.randint(8000, 9999)}", "Sistema": "General", "Falla": falla, "Costo": costo_est, "Estado": "Abierta", "Fecha": str(datetime.date.today())})
                    st.success("Reparación guardada correctamente.")
                    st.rerun()

    # 5. COMBUSTIBLE
    with tab5:
        st.subheader("Registro de Cargas de Petróleo (Diésel)")
        st.dataframe(pd.DataFrame(camion_sel['db_comb']), use_container_width=True)
        
        st.write("---")
        st.write("**Ingresar Nueva Carga de Petróleo:**")
        with st.form("form_combustible"):
            litros = st.number_input("Litros cargados:", min_value=0.0, value=250.0)
            costo = st.number_input("Valor pagado ($):", min_value=0, value=275000)
            if st.form_submit_button("Guardar Carga"):
                camion_sel['db_comb'].append({"Fecha": str(datetime.date.today()), "Tipo": "Diésel", "Litros": litros, "Costo": costo, "Horometro": int(camion_sel['horas'])})
                st.success("Carga guardada correctamente.")
                st.rerun()

    # 6. RESUMEN DE GASTOS
    with tab6:
        st.subheader("Resumen de Gastos del Camión")
        
        df_c = pd.DataFrame(camion_sel['db_comb'])
        df_o = pd.DataFrame(camion_sel['db_ot'])
        
        gasto_petroleo = df_c['Costo'].sum() if not df_c.empty else 0
        gasto_taller = df_o['Costo'].sum() if not df_o.empty else 0
        gasto_total = gasto_petroleo + gasto_taller
        
        col_g1, col_g2, col_g3 = st.columns(3)
        col_g1.metric("Gasto Total (Taller + Petróleo)", f"${gasto_total:,.0f}")
        col_g2.metric("Total Gastado en Taller", f"${gasto_taller:,.0f}")
        col_g3.metric("Total Gastado en Petróleo", f"${gasto_petroleo:,.0f}")
        
        st.write("---")
        st.write("**Gráfico de Gastos Recientes**")
        datos_grafico = pd.DataFrame({
            'Petróleo': [300000, 320000, 290000, gasto_petroleo], 
            'Taller': [150000, 0, 50000, gasto_taller]
        }, index=['Abril', 'Mayo', 'Junio', 'Julio'])
        st.bar_chart(datos_grafico)

    # BOTÓN PARA SALIR
    st.sidebar.divider()
    if st.sidebar.button("Cerrar Sesión (Salir)", type="primary", use_container_width=True):
        st.session_state.conectado = False
        st.rerun()

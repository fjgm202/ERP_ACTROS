import streamlit as st
import pandas as pd
import datetime
import random

# --- CONFIGURACIÓN E INTERFAZ MÓVIL ---
st.set_page_config(page_title="SGO Flota Maquehue PRO", page_icon="🚛", layout="wide")

# --- DICCIONARIO DE USUARIOS Y ROLES ---
ROLES_USUARIOS = {
    "admin1": "Administrador General",
    "gerente_op": "Gerente de Operaciones",
    "jefe_flota": "Jefe de Flota",
    "supervisor_taller": "Supervisor de Mantenimiento",
    "mecanico_jefe": "Mecánico Especialista",
    "logistica1": "Coordinador de Logística",
    "despachador": "Despachador de Ruta",
    "prevencionista": "Prevencionista de Riesgos",
    "chofer_lider": "Operador Equipo Pesado",
    "auditor_ext": "Auditor Externo"
}

# --- BASE DE DATOS CENTRALIZADA EN LA NUBE (SESSION STATE) ---
if 'conectado' not in st.session_state:
    st.session_state.conectado = False
    st.session_state.usuario_id = ""
    st.session_state.rol_actual = ""

if 'flota' not in st.session_state:
    flota_inicial = []
    lat_base = -38.7396
    lon_base = -72.6019
    
    for i in range(1, 11):
        kms_actuales = random.randint(500000, 580000)
        proxima_maint = ((kms_actuales // 10000) + 1) * 10000
        kms_restantes = proxima_maint - kms_actuales
        
        flota_inicial.append({
            "id": f"Camión {i}",
            "patente": f"GP-GC-{89+i}",
            "modelo": "Mercedes-Benz Actros 4144 8x4 Tolva",
            "chasis_vin": f"WDB9323341L{random.randint(100000, 999999)}",
            "kms": kms_actuales,
            "horas": random.randint(18000, 22000),
            "lat": lat_base + random.uniform(-0.05, 0.05),
            "lon": lon_base + random.uniform(-0.05, 0.05),
            "estado": "OPERATIVO",
            "kms_para_mantencion": kms_restantes,
            "db_comb": [
                {"Fecha": "2026-07-05", "Litros": 320, "Costo": 352000, "Horómetro": 18500, "Operador": "chofer_lider"}
            ],
            "db_ot": [
                {"ID_OT": "OT-0941", "Prioridad": "Media", "Tipo": "Preventiva", "Falla": "Cambio filtros", "Repuestos": "Filtro Aire M-B", "Estado": "Cerrada", "Responsable": "mecanico_jefe", "Fecha": "2026-06-15"}
            ],
            "rutas": [
                {"Fecha": str(datetime.date.today()), "Origen": "Faena", "Destino": "Planta", "Distancia_Km": 22, "Estado": "Completada"}
            ]
        })
    st.session_state.flota = flota_inicial

# --- PANTALLA DE ACCESO (LOGIN) ---
if not st.session_state.conectado:
    col_img, col_txt = st.columns([1, 4])
    with col_img:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Mercedes-Logo.svg/1024px-Mercedes-Logo.svg.png", width=80)
    with col_txt:
        st.title("SGO Cloud PRO - Áridos Maquehue")
        st.caption("Enterprise Resource Planning para Flota Pesada")
    
    st.info("💡 **Conexión al Servidor:** Ingrese su ID de usuario. El sistema detectará automáticamente sus permisos.")
    
    usuario = st.selectbox("ID de Usuario Autorizado:", list(ROLES_USUARIOS.keys()))
    clave = st.text_input("Contraseña (PIN):", type="password", value="inacap2026")
    
    if st.button("Autenticar y Conectar", type="primary", use_container_width=True):
        if clave == "inacap2026":
            st.session_state.conectado = True
            st.session_state.usuario_id = usuario
            st.session_state.rol_actual = ROLES_USUARIOS[usuario]
            st.rerun()
        else:
            st.error("❌ Contraseña incorrecta.")

# --- ENTRADA AL ERP PRINCIPAL ---
else:
    st.success(f"🌐 **Conexión Segura AWS** | ID: `{st.session_state.usuario_id}` | Perfil Activo: **{st.session_state.rol_actual}**")
    
    lista_desplegable = [f"{c['id']} [Patente: {c['patente']}]" for c in st.session_state.flota]
    camion_idx = st.selectbox("🎯 SELECCIONE UNIDAD A GESTIONAR:", range(10), format_func=lambda x: lista_desplegable[x])
    camion_sel = st.session_state.flota[camion_idx]
    
    st.header(f"🚛 {camion_sel['id']} | {camion_sel['modelo']}")
    st.caption(f"VIN Chasis: {camion_sel['chasis_vin']}")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Dashboard", 
        "📍 Telemetría GPS", 
        "📋 Checklist Inspección", 
        "🛠️ Órdenes de Trabajo (OT)", 
        "⛽ Control Diésel",
        "📑 Reportes Gerenciales"
    ])
    
    # 1. TAB DASHBOARD
    with tab1:
        st.subheader("Estado General del Activo")
        col1, col2, col3 = st.columns(3)
        col1.metric("Odómetro CAN-Bus", f"{camion_sel['kms']:,} Km")
        col2.metric("Horómetro Motor", f"{camion_sel['horas']:,} Hrs")
        
        # Color del estado
        estado_color = "🟢" if camion_sel['estado'] == "OPERATIVO" else "🔴"
        col3.metric("Estado Físico", f"{estado_color} {camion_sel['estado']}")
        
        st.markdown("---")
        st.markdown("### ⚙️ Salud del Motor y Mantenibilidad")
        restantes = camion_sel['kms_para_mantencion']
        porcentaje_uso = min(((10000 - restantes) / 10000) * 100, 100)
        
        st.write(f"**Ciclo de Mantenimiento Preventivo (PM):** Faltan {restantes:,} Km para cambio de fluidos.")
        st.progress(int(porcentaje_uso), text=f"Desgaste del aceite de motor: {int(porcentaje_uso)}%")
        
        if restantes <= 0:
            st.error("🚨 CRÍTICO: Equipo fuera de norma. Mantenimiento vencido. Ingresar a taller de inmediato.")
        elif restantes < 1500:
            st.warning("⚠️ PRECAUCIÓN: Planificar detención. Se acerca límite de pauta de mantenimiento.")

    # 2. TAB GPS Y RUTAS
    with tab2:
        st.subheader("📍 Rastreo Satelital Flota Completa")
        coords_flota = [{"lat": c["lat"], "lon": c["lon"]} for c in st.session_state.flota]
        st.map(pd.DataFrame(coords_flota), zoom=11)
        
        st.markdown("#### 🗺️ Bitácora de Tránsito Diario")
        st.dataframe(pd.DataFrame(camion_sel['rutas']), use_container_width=True)
        
        if st.button("Simular Avance de Ruta y Telemetría 🔄", use_container_width=True):
            avance_km = random.randint(15, 60)
            camion_sel['kms'] += avance_km
            camion_sel['kms_para_mantencion'] -= avance_km
            camion_sel['horas'] += random.randint(1, 3)
            camion_sel['lat'] += random.uniform(-0.01, 0.01)
            camion_sel['lon'] += random.uniform(-0.01, 0.01)
            st.rerun()

    # 3. TAB CHECKLIST (GRANULARIDAD ESPECÍFICA)
    with tab3:
        st.subheader("📋 Inspección Pre-Operacional Exhaustiva (Pre-Uso)")
        st.info("El operador debe verificar cada componente. Marcar 'Falla' en componentes críticos bloqueará la unidad.")
        
        # Uso de st.form para agrupar todo el checklist
        with st.form("form_checklist"):
            st.markdown("### 🛢️ 1. Motor y Fluidos")
            c1 = st.checkbox("Nivel de Aceite Motor entre Mín/Máx", value=True)
            c2 = st.checkbox("Nivel Líquido Refrigerante adecuado y sin fugas visibles", value=True)
            c3 = st.checkbox("Correas de accesorios sin grietas ni desgaste excesivo", value=True)
            c4 = st.checkbox("Filtro de aire primario (indicador de restricción OK)", value=True)
            
            st.markdown("### ⚙️ 2. Chasis, Suspensión y Neumáticos")
            c5 = st.checkbox("Presión de neumáticos adecuada en ejes direccionales y tractores", value=True)
            c6 = st.checkbox("Tuercas de ruedas completas y con marcas de torque alineadas", value=True)
            c7 = st.checkbox("Grapas de paquetes de resortes sin fisuras", value=True)
            c8 = st.checkbox("Pulmones de aire de suspensión sin fugas sonoras", value=True)
            
            st.markdown("### 🛑 3. Sistema de Frenos")
            c9 = st.checkbox("Compresor carga aire correctamente (sobre 100 PSI en tablero)", value=True)
            c10 = st.checkbox("Drenaje de tanques de aire (sin exceso de humedad/aceite)", value=True)
            c11 = st.checkbox("Grosor de balatas/pastillas sobre el límite permitido", value=True)
            
            st.markdown("### 🏗️ 4. Estructura y Sistema Hidráulico (Tolva)")
            c12 = st.checkbox("Pistón principal de tolva sin fugas de aceite hidráulico", value=True)
            c13 = st.checkbox("Mangueras de alta presión sin roces ni cortes", value=True)
            c14 = st.checkbox("Portalón trasero sella correctamente y seguros operan bien", value=True)
            
            st.markdown("### 💺 5. Cabina y Seguridad")
            c15 = st.checkbox("Luces (Altas, bajas, intermitentes, freno, retroceso, faena)", value=True)
            c16 = st.checkbox("Alarma de retroceso audible y baliza giratoria operativa", value=True)
            c17 = st.checkbox("Extintor vigente, Botiquín y Triángulos de emergencia a bordo", value=True)
            
            comentarios = st.text_area("📝 Hallazgos u Observaciones Adicionales:")
            enviar_chk = st.form_submit_button("Firmar y Enviar Auditoría")
            
            if enviar_chk:
                if not all([c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16, c17]):
                    camion_sel['estado'] = "BLOQUEADO"
                    st.error(f"🚨 RECHAZADO: Falla detectada. Equipo inmovilizado por seguridad. Auditor: {st.session_state.rol_actual}")
                    if comentarios: st.warning(f"Detalle: {comentarios}")
                else:
                    camion_sel['estado'] = "OPERATIVO"
                    st.success(f"✅ APROBADO: Equipo en estándar para operar. Firmado por: {st.session_state.rol_actual}")

    # 4. TAB ÓRDENES DE TALLER (MÁS DETALLADO)
    with tab4:
        st.subheader("🛠️ Generación de Órdenes de Trabajo (OT)")
        
        with st.expander("➕ APERTURAR NUEVA O.T.", expanded=True):
            col_a, col_b = st.columns(2)
            with col_a:
                tipo_ot = st.selectbox("Clasificación del Mantenimiento:", ["Preventivo (PM)", "Correctivo Crítico (CM)", "Predictivo (Inspección)", "Neumáticos/Vulcanización"])
                prioridad = st.radio("Prioridad de Ejecución:", ["Baja", "Media", "ALTA / URGENTE"])
            with col_b:
                falla_desc = st.text_area("Descripción Técnica de la Tarea/Falla:")
                repuestos = st.text_input("Repuestos o Insumos Estimados (Ej: Balatas eje 2, 20L Aceite):")
            
            if st.button("Emitir Documento O.T.", type="primary"):
                if falla_desc:
                    nueva_ot = {
                        "ID_OT": f"OT-{random.randint(8000, 9999)}",
                        "Prioridad": prioridad,
                        "Tipo": tipo_ot,
                        "Falla": falla_desc,
                        "Repuestos": repuestos,
                        "Estado": "Abierta / En Taller",
                        "Responsable": st.session_state.usuario_id,
                        "Fecha": str(datetime.date.today())
                    }
                    camion_sel['db_ot'].append(nueva_ot)
                    st.success(f"O.T. generada y asignada en la base de datos a nombre de {st.session_state.usuario_id}")
                else:
                    st.warning("Debe ingresar la descripción técnica obligatoriamente.")
                    
        st.markdown("### 📂 Historial de Órdenes (Backlog)")
        df_ot = pd.DataFrame(camion_sel['db_ot'])
        if not df_ot.empty:
            st.dataframe(df_ot, use_container_width=True)
            
            if st.session_state.usuario_id in ["admin1", "supervisor_taller", "mecanico_jefe", "gerente_op"]:
                if st.button("✔️ Certificar Reparaciones y Cerrar O.T. Activas", use_container_width=True):
                    for ot in camion_sel['db_ot']:
                        ot["Estado"] = "Cerrada / Conforme"
                    camion_sel['estado'] = "OPERATIVO"
                    camion_sel['kms_para_mantencion'] = 10000
                    st.success("Equipos liberados a operaciones. Pauta de 10,000Km reiniciada.")
            else:
                st.info("🔒 Solo perfiles de Taller o Gerencia pueden cerrar Órdenes de Trabajo y liberar equipos.")
        else:
            st.write("Sin historial.")

    # 5. TAB COMBUSTIBLE (RENDIMIENTO)
    with tab5:
        st.subheader("⛽ Registro de Abastecimiento de Fluido (Diésel / AdBlue)")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            litros = st.number_input("Volumen Cargado (Litros):", min_value=0, step=50)
            monto = st.number_input("Facturación Total ($ CLP):", min_value=0, step=20000)
        with col_c2:
            horometro_carga = st.number_input("Horómetro al momento de carga (Hrs):", min_value=int(camion_sel['horas']), step=1)
            tipo_fluido = st.selectbox("Tipo de Fluido:", ["Petróleo Diésel Grado B", "AdBlue / Urea"])
            
        if st.button("Grabar Transacción de Combustible", type="primary"):
            if litros > 0 and monto > 0:
                camion_sel['db_comb'].append({
                    "Fecha": str(datetime.date.today()),
                    "Fluido": tipo_fluido,
                    "Litros": litros,
                    "Costo": monto,
                    "Horómetro": horometro_carga,
                    "Operador": st.session_state.usuario_id
                })
                st.success("Surtidor registrado exitosamente en la nube.")
                
        df_comb = pd.DataFrame(camion_sel['db_comb'])
        if not df_comb.empty:
            st.dataframe(df_comb, use_container_width=True)

    # 6. TAB INFORMES (KPIs GERENCIALES)
    with tab6:
        st.subheader("📊 Panel de Indicadores Clave de Desempeño (KPIs)")
        
        st.markdown("#### Costos Operacionales de la Unidad")
        df_gastos = pd.DataFrame(camion_sel['db_comb'])
        gasto_total = df_gastos['Costo'].sum() if not df_gastos.empty else 0
        litros_totales = df_gastos['Litros'].sum() if not df_gastos.empty else 0
        
        col_k1, col_k2, col_k3 = st.columns(3)
        col_k1.metric("Gasto Histórico Diésel", f"${gasto_total:,.0f}")
        col_k2.metric("Volumen Consumido", f"{litros_totales} L")
        # Calculo de OTs abiertas vs cerradas
        ot_totales = len(camion_sel['db_ot'])
        ot_abiertas = sum(1 for ot in camion_sel['db_ot'] if "Abierta" in ot['Estado'])
        col_k3.metric("O.T. Pendientes en Taller", ot_abiertas)
        
        st.markdown("---")
        st.markdown("#### 📄 Exportación de Data Analítica")
        st.write("Generación de matrices de datos para análisis en PowerBI o Excel.")
        
        col_csv1, col_csv2 = st.columns(2)
        with col_csv1:
            st.download_button(
                label="📥 Descargar Data de Mantenimiento (CSV)",
                data=pd.DataFrame(camion_sel['db_ot']).to_csv(index=False).encode('utf-8'),
                file_name=f"OT_{camion_sel['patente']}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_csv2:
            st.download_button(
                label="📥 Descargar Data Logística/Rutas (CSV)",
                data=pd.DataFrame(camion_sel['rutas']).to_csv(index=False).encode('utf-8'),
                file_name=f"Rutas_{camion_sel['patente']}.csv",
                mime="text/csv",
                use_container_width=True
            )

    st.divider()
    if st.button("Cerrar Sesión y Desconectar Servidor", use_container_width=True):
        st.session_state.conectado = False
        st.rerun()
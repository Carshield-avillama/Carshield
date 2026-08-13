import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Carshield - Control Operativo", page_icon="🛡️", layout="wide")

# --- 2. ESTILOS CSS ---
st.markdown("""
    <style>
    .main { background-color: #f4f4f4; }
    h1 { color: #FFD700; text-align: center; background-color: #000000; padding: 10px; border-radius: 5px; }
    .stButton>button { background-color: #FFD700; color: #000000; font-weight: bold; border: none; width: 100%; }
    .stButton>button:hover { background-color: #e6c200; color: #000000; }
    .pintura-header { background-color: #333333; color: white; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 20px;}
    .admin-header { background-color: #7f1d1d; color: white; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

st.title("CARSHIELD COATINGS")
st.markdown("<h3 style='text-align: center;'>Panel de Control Operativo</h3>", unsafe_allow_html=True)
st.write("---")

# --- 3. CONEXIÓN A GOOGLE SHEETS ---
@st.cache_resource(ttl=10)
def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

try:
    client = get_gspread_client()
    hoja_datos = client.open("Carshield_BaseDatos_App").sheet1 
    try:
        hoja_pintura = client.open("Carshield_BaseDatos_App").worksheet("Piezas_Pintura")
    except gspread.exceptions.WorksheetNotFound:
        st.error("⚠️ Para que el módulo de pintura funcione, debes crear una pestaña llamada 'Piezas_Pintura' en tu Google Sheet.")
        st.stop()
except Exception as e:
    st.error(f"Error de conexión. Verifica los permisos: {e}")
    st.stop()

# --- 4. FUNCIONES DE DATOS ---
def load_data_detallado():
    records = hoja_datos.get_all_records()
    if not records:
        columnas = ["ID", "Fecha_Ingreso", "Placa", "Marca", "Modelo", "Color", "Agencia",
                   "Pulido_Pintura", "Pulido_Vidrios", "Limpieza_Tapiceria",
                   "Limpieza_Motor", "Polarizado", "Quitar_Racks", "Adelantado",
                   "Estado_General", "Fecha_Pintura", "Observaciones"]
        return pd.DataFrame(columns=columnas)
    return pd.DataFrame(records)

def load_data_pintura():
    records = hoja_pintura.get_all_records()
    if not records:
        return pd.DataFrame(columns=["ID_Pieza", "Placa_Asociada", "Nombre_Pieza", "Fecha_Ingreso_Cabina", "Fecha_Estimada_Fin", "Estado_Pintura", "Observaciones"])
    return pd.DataFrame(records)

df_db = load_data_detallado()
df_pintura = load_data_pintura()

# --- SISTEMA DE SEGURIDAD Y NAVEGACIÓN ---
st.sidebar.markdown("### Menú de Acceso")
PASSWORD_ADMIN = "Vclean1993"

clave_ingresada = st.sidebar.text_input("🔒 Acceso Operativo", type="password", help="Solo para personal del taller")

if clave_ingresada == PASSWORD_ADMIN:
    st.sidebar.success("Acceso interno concedido")
    menu = ["Consultar Estado (Cliente/Agencia)", "Ingresar Vehículo Nuevo", "Actualizar Estatus (Detallado)", "Departamento de Pintura", "Panel de Revisión (Admin)"]
else:
    menu = ["Consultar Estado (Cliente/Agencia)"]
    if clave_ingresada != "":
        st.sidebar.error("Clave incorrecta")

choice = st.sidebar.radio("Ir a:", menu)

opciones_estado_detallado = ["Pendiente", "En Proceso", "Completado"]
opciones_estado_pintura = ["Ingreso a Cabina", "Preparación/Lijado", "Fondeado/Imprimación", "Aplicación de Color", "Aplicación de Transparente", "Horneado/Secado", "Pulido Final", "Terminado"]

# ==========================================
# SECCIÓN 0: CONSULTA CLIENTE/AGENCIA
# ==========================================
if choice == "Consultar Estado (Cliente/Agencia)":
    st.header("🚘 Consulta de Estado de Vehículos")
    st.write("Ingrese el nombre de la Agencia (Ej: Purdy) o el número de placa para verificar el avance en tiempo real.")
    
    busqueda_cliente = st.text_input("🔍 Nombre de Agencia o Placa:").upper().strip()
    
    if st.button("Buscar Vehículos"):
        if busqueda_cliente:
            # Buscar coincidencias tanto en la columna de Placa como en la de Agencia
            mask = (df_db['Placa'].astype(str).str.upper().str.strip() == busqueda_cliente) | (df_db['Agencia'].astype(str).str.upper().str.strip().str.contains(busqueda_cliente))
            filtro = df_db[mask]
            
            if not filtro.empty:
                st.success(f"✅ Se encontraron {len(filtro)} vehículo(s).")
                
                # Desplegar cada vehículo en un menú expandible
                for idx, vehiculo in filtro.iterrows():
                    estado_gen = vehiculo.get('Estado_General', 'En Taller')
                    agencia_texto = vehiculo.get('Agencia', 'Particular')
                    
                    if estado_gen == "Entregado":
                        color = "green"
                    elif estado_gen == "Listo para Entrega":
                        color = "blue"
                    else:
                        color = "orange"
                    
                    titulo_expander = f"🚘 Placa: {vehiculo.get('Placa', '')} | {vehiculo.get('Marca', '')} {vehiculo.get('Modelo', '')} | Agencia: {agencia_texto} | Estatus: {estado_gen}"
                    
                    with st.expander(titulo_expander):
                        st.markdown(f"### Estado General: <span style='color:{color}'>{estado_gen}</span>", unsafe_allow_html=True)
                        st.write("---")
                        st.write("#### ✨ Procesos de Detallado:")
                        
                        detalles = {
                            "Pulido de Pintura": vehiculo.get("Pulido_Pintura", "Pendiente"),
                            "Pulido de Vidrios": vehiculo.get("Pulido_Vidrios", "Pendiente"),
                            "Limpieza de Tapicería": vehiculo.get("Limpieza_Tapiceria", "Pendiente"),
                            "Limpieza de Motor": vehiculo.get("Limpieza_Motor", "Pendiente"),
                            "Polarizado": vehiculo.get("Polarizado", "Pendiente")
                        }
                        df_detalles = pd.DataFrame(list(detalles.items()), columns=["Proceso", "Estatus"])
                        st.dataframe(df_detalles, use_container_width=True, hide_index=True)
                        
                        # Buscar si el auto tiene piezas en pintura
                        placa_actual = vehiculo.get('Placa', '')
                        filtro_pintura = df_pintura[df_pintura['Placa_Asociada'].astype(str).str.upper().str.strip() == placa_actual]
                        if not filtro_pintura.empty:
                            st.write("#### 🎨 Estado en Cabina de Pintura:")
                            df_pintura_mostrar = filtro_pintura[["Nombre_Pieza", "Estado_Pintura", "Fecha_Estimada_Fin"]].copy()
                            df_pintura_mostrar.columns = ["Pieza", "Etapa Actual", "Fecha Estimada"]
                            st.dataframe(df_pintura_mostrar, use_container_width=True, hide_index=True)
            else:
                st.warning("⚠️ No se encontró ningún vehículo activo con esa placa o nombre de agencia.")
        else:
            st.error("Por favor, ingrese un término de búsqueda válido.")

# ==========================================
# SECCIÓN 1: INGRESO
# ==========================================
elif choice == "Ingresar Vehículo Nuevo":
    st.header("1. Registrar Nuevo Ingreso al Taller")
    
    col1, col2 = st.columns(2)
    with col1:
        placa = st.text_input("Placa *").upper()
        marca = st.text_input("Marca")
        agencia = st.text_input("Agencia (Ej: Purdy. Dejar como 'Particular' si es cliente directo)", value="Particular")
    with col2:
        modelo = st.text_input("Modelo")
        color = st.text_input("Color")
        
    observaciones = st.text_area("Notas iniciales")
    
    if st.button("Registrar Vehículo"):
        if placa:
            nuevo_id = str(len(df_db) + 1).zfill(4)
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            nueva_fila = [
                nuevo_id, fecha_actual, placa, marca, modelo, color, agencia,
                "Pendiente", "Pendiente", "Pendiente", "Pendiente",
                "Pendiente", "Pendiente", "Pendiente", "En Taller",
                "", observaciones
            ]
            
            hoja_datos.append_row(nueva_fila)
            st.success(f"✅ Vehículo {placa} registrado correctamente.")
        else:
            st.error("⚠️ La placa es obligatoria.")

# ==========================================
# SECCIÓN 2: ACTUALIZACIÓN DETALLADO
# ==========================================
elif choice == "Actualizar Estatus (Detallado)":
    st.header("2. Actualizar Tareas de Preparación y Detallado")
    
    placa_buscar = st.text_input("Buscar placa para actualizar:").upper()
    
    if placa_buscar:
        filtro = df_db[df_db['Placa'] == placa_buscar]
        
        if not filtro.empty:
            idx = filtro.index[0] 
            fila_sheet = int(idx) + 2 
            vehiculo = df_db.loc[idx]
            
            st.write(f"**Vehículo:** {vehiculo['Marca']} {vehiculo['Modelo']} | **Agencia:** {vehiculo.get('Agencia', 'Particular')}")
            st.write("---")
            
            with st.form("actualizacion_form"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    pp = st.selectbox("Pulido Pintura", opciones_estado_detallado, index=opciones_estado_detallado.index(vehiculo["Pulido_Pintura"]))
                    pv = st.selectbox("Pulido Vidrios", opciones_estado_detallado, index=opciones_estado_detallado.index(vehiculo["Pulido_Vidrios"]))
                    lt = st.selectbox("Limpieza Tapicería", opciones_estado_detallado, index=opciones_estado_detallado.index(vehiculo["Limpieza_Tapiceria"]))
                with col2:
                    lm = st.selectbox("Limpieza Motor", opciones_estado_detallado, index=opciones_estado_detallado.index(vehiculo["Limpieza_Motor"]))
                    pol = st.selectbox("Polarizado", opciones_estado_detallado, index=opciones_estado_detallado.index(vehiculo["Polarizado"]))
                    qr = st.selectbox("Quitar Racks", opciones_estado_detallado, index=opciones_estado_detallado.index(vehiculo["Quitar_Racks"]))
                with col3:
                    ade = st.selectbox("Adelantado", opciones_estado_detallado, index=opciones_estado_detallado.index(vehiculo["Adelantado"]))
                    estado_gen = st.selectbox("Estado General", ["En Taller", "En Cabina de Pintura", "Listo para Entrega", "Entregado"], index=["En Taller", "En Cabina de Pintura", "Listo para Entrega", "Entregado"].index(vehiculo["Estado_General"]))
                    fecha_pintura = st.text_input("Fecha a Pintura (opcional)", value=str(vehiculo["Fecha_Pintura"]))
                    
                nuevas_obs = st.text_area("Añadir observaciones (opcional)", value=str(vehiculo["Observaciones"]))
                guardar_cambios = st.form_submit_button("Guardar Cambios")
                
                if guardar_cambios:
                    # NOTA TÉCNICA: Al añadir la columna "Agencia" (G), las columnas de estatus ahora van de la H a la Q
                    valores_actualizados = [[pp, pv, lt, lm, pol, qr, ade, estado_gen, fecha_pintura, nuevas_obs]]
                    hoja_datos.update(range_name=f"H{fila_sheet}:Q{fila_sheet}", values=valores_actualizados)
                    st.success("✅ Estatus actualizado correctamente.")
        else:
            st.warning("No se encontró ningún vehículo con esa placa activa.")

# ==========================================
# SECCIÓN 3: DEPARTAMENTO DE PINTURA
# ==========================================
elif choice == "Departamento de Pintura":
    st.markdown("<div class='pintura-header'><h2>🎨 Control de Procesos: Cabina de Pintura</h2></div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Registrar Nueva Pieza", "Actualizar Proceso", "Inventario en Cabina"])

    with tab1:
        st.write("#### Ingresar pieza al área de pintura")
        with st.form("form_ingreso_pintura"):
            placa_pieza = st.text_input("Placa del vehículo correspondiente *").upper()
            nombre_pieza = st.text_input("Nombre de la pieza (Ej: Bumper delantero, Puerta derecha) *")
            
            col1, col2 = st.columns(2)
            with col1:
                fecha_ingreso_cabina = st.date_input("Fecha de ingreso a cabina")
            with col2:
                fecha_entrega_estimada = st.date_input("Fecha estimada de finalización *")
                
            notas_pieza = st.text_area("Observaciones técnicas (Lijado profundo, código de color, etc.)")
            
            submit_pieza = st.form_submit_button("Registrar Pieza")
            
            if submit_pieza:
                if placa_pieza and nombre_pieza:
                    nuevo_id_pieza = "PNT-" + str(len(df_pintura) + 1).zfill(4)
                    nueva_fila_pieza = [
                        nuevo_id_pieza, placa_pieza, nombre_pieza, str(fecha_ingreso_cabina), 
                        str(fecha_entrega_estimada), "Ingreso a Cabina", notas_pieza
                    ]
                    hoja_pintura.append_row(nueva_fila_pieza)
                    st.success(f"✅ La pieza '{nombre_pieza}' fue registrada en el sistema de pintura.")
                else:
                    st.error("⚠️ La placa y el nombre de la pieza son obligatorios.")

    with tab2:
        st.write("#### Actualizar etapas de pintura")
        placa_buscar_pintura = st.text_input("Buscar placa asociada a la pieza:").upper()
        
        if placa_buscar_pintura:
            filtro_pintura = df_pintura[df_pintura['Placa_Asociada'] == placa_buscar_pintura]
            
            if not filtro_pintura.empty:
                for idx, row in filtro_pintura.iterrows():
                    st.write(f"**Pieza:** {row['Nombre_Pieza']} (Registro: {row['ID_Pieza']})")
                    fila_sheet_pintura = int(idx) + 2
                    
                    with st.form(f"form_actualizar_pnt_{row['ID_Pieza']}"):
                        estado_actual = row["Estado_Pintura"]
                        index_estado = opciones_estado_pintura.index(estado_actual) if estado_actual in opciones_estado_pintura else 0
                        
                        nuevo_estado_pnt = st.selectbox("Etapa actual en cabina", opciones_estado_pintura, index=index_estado)
                        nueva_fecha_pnt = st.text_input("Modificar Fecha de Finalización (Opcional)", value=str(row["Fecha_Estimada_Fin"]))
                        notas_actualizadas_pnt = st.text_area("Notas Técnicas", value=str(row["Observaciones"]))
                        
                        if st.form_submit_button("Actualizar Etapa"):
                            valores_pnt = [[nuevo_estado_pnt, notas_actualizadas_pnt]]
                            hoja_pintura.update(range_name=f"F{fila_sheet_pintura}:G{fila_sheet_pintura}", values=valores_pnt)
                            hoja_pintura.update(range_name=f"E{fila_sheet_pintura}:E{fila_sheet_pintura}", values=[[nueva_fecha_pnt]])
                            st.success("✅ Etapa de pintura actualizada correctamente.")
            else:
                st.warning("No hay piezas registradas en pintura bajo esa placa.")

    with tab3:
        st.write("#### Piezas actualmente en proceso de pintura")
        if not df_pintura.empty:
            pendientes = df_pintura[df_pintura['Estado_Pintura'] != "Terminado"]
            if not pendientes.empty:
                st.dataframe(pendientes[["Placa_Asociada", "Nombre_Pieza", "Fecha_Estimada_Fin", "Estado_Pintura"]], use_container_width=True)
            else:
                st.success("No hay piezas pendientes en la cabina de pintura.")
        else:
            st.info("La base de datos de pintura está vacía.")

# ==========================================
# SECCIÓN 4: REVISIÓN (ADMIN)
# ==========================================
elif choice == "Panel de Revisión (Admin)":
    st.header("4. Visión General de Operaciones")
    
    if df_db.empty:
        st.info("La base de datos está vacía. Registra tu primer vehículo.")
    else:
        st.write("### Flujo General de Detallado")
        estatus_filtro = st.radio("Filtrar por Estado General:", ["Todos", "En Taller", "En Cabina de Pintura", "Listo para Entrega", "Entregado"], horizontal=True)
        
        df_mostrar = df_db.copy()
        if estatus_filtro != "Todos":
            df_mostrar = df_mostrar[df_mostrar["Estado_General"] == estatus_filtro]
            
        st.dataframe(df_mostrar, use_container_width=True)
        
        st.write("### Resumen de Piezas en Pintura")
        if not df_pintura.empty:
            st.dataframe(df_pintura, use_container_width=True)

        st.write("---")
        st.markdown("<div class='admin-header'><h4>⚠️ Eliminar Registro de Detallado</h4></div>", unsafe_allow_html=True)
        st.warning("Esta acción borrará el vehículo permanentemente de la base de datos principal.")
        
        id_borrar = st.text_input("Ingrese el ID exacto a eliminar (Ej: 0001):").strip()
        
        if st.button("Eliminar Permanentemente"):
            if id_borrar:
                filtro_borrar = df_db[df_db['ID'].astype(str).str.zfill(4) == id_borrar.zfill(4)]
                if not filtro_borrar.empty:
                    idx_borrar = filtro_borrar.index[0]
                    fila_sheet_borrar = int(idx_borrar) + 2
                    
                    try:
                        hoja_datos.delete_rows(fila_sheet_borrar)
                        st.success(f"✅ El registro {id_borrar} ha sido eliminado. Recarga la página para actualizar.")
                    except Exception as e:
                        st.error(f"Error al intentar borrar: {e}")
                else:
                    st.error("No se encontró ese ID en la base de datos.")
            else:
                st.error("Ingrese un ID válido.")

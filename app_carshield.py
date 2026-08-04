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
    </style>
""", unsafe_allow_html=True)

st.title("CARSHIELD COATINGS")
st.markdown("<h3 style='text-align: center;'>Panel de Control Operativo</h3>", unsafe_allow_html=True)
st.write("---")

# --- 3. CONEXIÓN A GOOGLE SHEETS ---
@st.cache_resource
def get_gspread_client():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    # Llama a los secretos que configuraste en Streamlit
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

try:
    client = get_gspread_client()
    # IMPORTANTE: Busca el archivo exactamente con este nombre
    hoja_datos = client.open("Carshield_BaseDatos_App").sheet1 
except Exception as e:
    st.error(f"Error de conexión. Verifica el nombre de la hoja o los permisos: {e}")
    st.stop()

# --- 4. FUNCIONES DE DATOS ---
def load_data():
    records = hoja_datos.get_all_records()
    if not records:
        columnas = ["ID", "Fecha_Ingreso", "Placa", "Marca", "Modelo", "Color", 
                   "Pulido_Pintura", "Pulido_Vidrios", "Limpieza_Tapiceria",
                   "Limpieza_Motor", "Polarizado", "Quitar_Racks", "Adelantado",
                   "Estado_General", "Fecha_Pintura", "Observaciones"]
        return pd.DataFrame(columns=columnas)
    return pd.DataFrame(records)

df_db = load_data()

# --- 5. INTERFAZ DE NAVEGACIÓN ---
menu = ["Ingresar Vehículo Nuevo", "Actualizar Estatus (Empleados)", "Panel de Revisión (Admin)"]
choice = st.sidebar.radio("Navegación", menu)
opciones_estado = ["Pendiente", "En Proceso", "Completado"]

# SECCIÓN 1: INGRESO
if choice == "Ingresar Vehículo Nuevo":
    st.header("1. Registrar Nuevo Ingreso")
    
    col1, col2 = st.columns(2)
    with col1:
        placa = st.text_input("Placa *").upper()
        marca = st.text_input("Marca")
    with col2:
        modelo = st.text_input("Modelo")
        color = st.text_input("Color")
        
    observaciones = st.text_area("Notas iniciales")
    
    if st.button("Registrar Vehículo"):
        if placa:
            nuevo_id = str(len(df_db) + 1).zfill(4)
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            nueva_fila = [
                nuevo_id, fecha_actual, placa, marca, modelo, color,
                "Pendiente", "Pendiente", "Pendiente", "Pendiente",
                "Pendiente", "Pendiente", "Pendiente", "En Taller",
                "", observaciones
            ]
            
            # Guardar directo en Google Sheets
            hoja_datos.append_row(nueva_fila)
            st.success(f"✅ Vehículo {placa} registrado correctamente en la nube.")
        else:
            st.error("⚠️ La placa es obligatoria.")

# SECCIÓN 2: ACTUALIZACIÓN (EMPLEADOS)
elif choice == "Actualizar Estatus (Empleados)":
    st.header("2. Actualizar Tareas del Vehículo")
    
    placa_buscar = st.text_input("Buscar placa para actualizar:").upper()
    
    if placa_buscar:
        filtro = df_db[df_db['Placa'] == placa_buscar]
        
        if not filtro.empty:
            idx = filtro.index[0] 
            fila_sheet = int(idx) + 2 # Cálculo de la fila en Google Sheets
            vehiculo = df_db.loc[idx]
            
            st.write(f"**Vehículo:** {vehiculo['Marca']} {vehiculo['Modelo']} | **Color:** {vehiculo['Color']}")
            st.write("---")
            
            with st.form("actualizacion_form"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    pp = st.selectbox("Pulido Pintura", opciones_estado, index=opciones_estado.index(vehiculo["Pulido_Pintura"]))
                    pv = st.selectbox("Pulido Vidrios", opciones_estado, index=opciones_estado.index(vehiculo["Pulido_Vidrios"]))
                    lt = st.selectbox("Limpieza Tapicería", opciones_estado, index=opciones_estado.index(vehiculo["Limpieza_Tapiceria"]))
                with col2:
                    lm = st.selectbox("Limpieza Motor", opciones_estado, index=opciones_estado.index(vehiculo["Limpieza_Motor"]))
                    pol = st.selectbox("Polarizado", opciones_estado, index=opciones_estado.index(vehiculo["Polarizado"]))
                    qr = st.selectbox("Quitar Racks", opciones_estado, index=opciones_estado.index(vehiculo["Quitar_Racks"]))
                with col3:
                    ade = st.selectbox("Adelantado", opciones_estado, index=opciones_estado.index(vehiculo["Adelantado"]))
                    estado_gen = st.selectbox("Estado General", ["En Taller", "Listo para Entrega", "Entregado"], index=["En Taller", "Listo para Entrega", "Entregado"].index(vehiculo.get("Estado_General", "En Taller")))
                    fecha_pintura = st.text_input("Fecha a Pintura (opcional)", value=str(vehiculo["Fecha_Pintura"]))
                    
                nuevas_obs = st.text_area("Añadir observaciones (opcional)", value=str(vehiculo["Observaciones"]))
                guardar_cambios = st.form_submit_button("Guardar Cambios en la Nube")
                
                if guardar_cambios:
                    # Actualizar celdas en bloque (De la columna G a la P)
                    valores_actualizados = [[pp, pv, lt, lm, pol, qr, ade, estado_gen, fecha_pintura, nuevas_obs]]
                    hoja_datos.update(range_name=f"G{fila_sheet}:P{fila_sheet}", values=valores_actualizados)
                    
                    st.success("✅ Estatus actualizado correctamente en Google Sheets.")
        else:
            st.warning("No se encontró ningún vehículo con esa placa activa.")

# SECCIÓN 3: REVISIÓN (ADMIN)
elif choice == "Panel de Revisión (Admin)":
    st.header("3. Visión General de Operaciones")
    
    if df_db.empty:
        st.info("La base de datos está vacía. Registra tu primer vehículo.")
    else:
        estatus_filtro = st.radio("Filtrar por Estado General:", ["Todos", "En Taller", "Listo para Entrega", "Entregado"], horizontal=True)
        
        df_mostrar = df_db.copy()
        if estatus_filtro != "Todos":
            df_mostrar = df_mostrar[df_mostrar["Estado_General"] == estatus_filtro]
            
        st.dataframe(df_mostrar, use_container_width=True)

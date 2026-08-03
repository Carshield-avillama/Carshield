import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Set page config
st.set_page_config(page_title="Carshield - Control de Preparación", page_icon="🛡️", layout="centered")

# Custom CSS for branding
st.markdown("""
    <style>
    .main {
        background-color: #f4f4f4;
    }
    h1 {
        color: #FFD700;
        text-align: center;
        background-color: #000000;
        padding: 10px;
        border-radius: 5px;
    }
    h2, h3 {
        color: #000000;
    }
    .stButton>button {
        background-color: #FFD700;
        color: #000000;
        font-weight: bold;
        border: none;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #e6c200;
        color: #000000;
    }
    </style>
""", unsafe_allow_html=True)

# App Title
st.title("CARSHIELD COATINGS")
st.markdown("<h3 style='text-align: center;'>Control de Preparación</h3>", unsafe_allow_html=True)
st.write("---")

# Data Storage Setup (using a local CSV for this demo)
DATA_FILE = "carshield_records.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        columns = ["Fecha_Registro", "Placa", "Marca", "Modelo", "Año", "Color", 
                   "Pulido_Pintura_Si", "Pulido_Pintura_No", "Pulido_Pintura_Hecho",
                   "Pulido_Vidrios_Si", "Pulido_Vidrios_No", "Pulido_Vidrios_Hecho",
                   "Limpieza_Tapiceria_Si", "Limpieza_Tapiceria_No", "Limpieza_Tapiceria_Hecho",
                   "Limpieza_Motor_Si", "Limpieza_Motor_No", "Limpieza_Motor_Hecho",
                   "Polarizado_Si", "Polarizado_No", "Polarizado_Hecho",
                   "Quitar_Racks_Si", "Quitar_Racks_No", "Quitar_Racks_Hecho",
                   "Adelantado_Si", "Adelantado_No", "Adelantado_Hecho",
                   "Fecha_Pintura", "Detalles", "Observaciones"]
        return pd.DataFrame(columns=columns)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

df_records = load_data()

# Navigation
menu = ["Nuevo Registro", "Ver Registros Actuales"]
choice = st.sidebar.selectbox("Navegación", menu)

if choice == "Nuevo Registro":
    st.header("Información del Vehículo")
    
    col1, col2 = st.columns(2)
    with col1:
        placa = st.text_input("Placa")
        modelo = st.text_input("Modelo")
    with col2:
        marca = st.text_input("Marca")
        anio = st.text_input("Año")
    
    color = st.text_input("Color")
    
    st.write("---")
    st.header("Lista de Tareas")
    
    tasks = [
        "Pulido de pintura", "Pulido de vidrios", "Limpieza de tapicería",
        "Limpieza de motor", "Polarizado", "Quitar racks", "Adelantado"
    ]
    
    task_results = {}
    
    # Create columns for the checklist headers
    hcol1, hcol2, hcol3, hcol4 = st.columns([2, 1, 1, 2])
    with hcol1: st.write("**Tarea**")
    with hcol2: st.write("**Sí**")
    with hcol3: st.write("**No**")
    with hcol4: st.write("**Estado**")
    
    for task in tasks:
        c1, c2, c3, c4 = st.columns([2, 1, 1, 2])
        with c1:
            st.write(task)
        with c2:
            si = st.checkbox("", key=f"si_{task}")
        with c3:
            no = st.checkbox("", key=f"no_{task}")
        with c4:
            estado = st.selectbox("", ["Pendiente", "En Proceso", "Completado"], key=f"est_{task}")
            
        task_results[task] = {"Si": si, "No": no, "Estado": estado}

    st.write("---")
    st.header("Detalles Finales")
    
    fecha_pintura = st.date_input("Fecha de entrega a pintura")
    detalles = st.text_area("Detalles (Pintura y otros)", help="Escribe los detalles específicos requeridos")
    observaciones = st.text_area("Observaciones Generales")
    
    if st.button("Guardar Registro"):
        if not placa:
            st.error("La Placa es obligatoria para guardar el registro.")
        else:
            new_data = {
                "Fecha_Registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Placa": placa,
                "Marca": marca,
                "Modelo": modelo,
                "Año": anio,
                "Color": color,
                "Pulido_Pintura_Si": task_results["Pulido de pintura"]["Si"],
                "Pulido_Pintura_No": task_results["Pulido de pintura"]["No"],
                "Pulido_Pintura_Hecho": task_results["Pulido de pintura"]["Estado"],
                "Pulido_Vidrios_Si": task_results["Pulido de vidrios"]["Si"],
                "Pulido_Vidrios_No": task_results["Pulido de vidrios"]["No"],
                "Pulido_Vidrios_Hecho": task_results["Pulido de vidrios"]["Estado"],
                "Limpieza_Tapiceria_Si": task_results["Limpieza de tapicería"]["Si"],
                "Limpieza_Tapiceria_No": task_results["Limpieza de tapicería"]["No"],
                "Limpieza_Tapiceria_Hecho": task_results["Limpieza de tapicería"]["Estado"],
                "Limpieza_Motor_Si": task_results["Limpieza de motor"]["Si"],
                "Limpieza_Motor_No": task_results["Limpieza de motor"]["No"],
                "Limpieza_Motor_Hecho": task_results["Limpieza de motor"]["Estado"],
                "Polarizado_Si": task_results["Polarizado"]["Si"],
                "Polarizado_No": task_results["Polarizado"]["No"],
                "Polarizado_Hecho": task_results["Polarizado"]["Estado"],
                "Quitar_Racks_Si": task_results["Quitar racks"]["Si"],
                "Quitar_Racks_No": task_results["Quitar racks"]["No"],
                "Quitar_Racks_Hecho": task_results["Quitar racks"]["Estado"],
                "Adelantado_Si": task_results["Adelantado"]["Si"],
                "Adelantado_No": task_results["Adelantado"]["No"],
                "Adelantado_Hecho": task_results["Adelantado"]["Estado"],
                "Fecha_Pintura": fecha_pintura,
                "Detalles": detalles,
                "Observaciones": observaciones
            }
            
            df_records = pd.concat([df_records, pd.DataFrame([new_data])], ignore_index=True)
            save_data(df_records)
            st.success(f"Registro para el vehículo {placa} guardado exitosamente.")

elif choice == "Ver Registros Actuales":
    st.header("Base de Datos de Vehículos")
    if df_records.empty:
        st.info("No hay registros almacenados actualmente.")
    else:
        st.dataframe(df_records)
        
        st.write("### Buscar Registro por Placa")
        search_placa = st.text_input("Ingrese la placa del vehículo")
        if search_placa:
            filtered_df = df_records[df_records["Placa"].str.contains(search_placa, case=False, na=False)]
            st.dataframe(filtered_df)

import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import uuid

# Configuración visual
st.set_page_config(page_title="Expotécnica - Evaluación", page_icon="📝", layout="centered")

st.markdown("""
    <style>
    .main { padding: 1rem; }
    .stButton>button { width: 100%; background-color: #2E7D32; color: white; font-size: 18px; font-weight: bold; border-radius: 8px; padding: 0.6rem; }
    .project-card { background-color: #F4F6F8; padding: 12px; border-radius: 8px; margin-bottom: 15px; border-left: 5px solid #1976D2; }
    </style>
""", unsafe_allow_html=True)

st.title("📋 Evaluación Expotécnica")

# Conexión con Google Sheets y Google Apps Script
SPREADSHEET_ID = "1KWw1ybOAuxxBk4P3gVoqp90UXx2pBaa9ccAiiV8Rd-w"
URL_PROYECTOS = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=PROYECTOS"
URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbztdcK8cKx8PccUoH9ZtDS6hT1imOHturPpV3D2jfvAFIWkwrHLs0AYw6pVvHHGYLT_/exec"

# Cargar proyectos desde la solapa PROYECTOS
try:
    df_proyectos = pd.read_csv(URL_PROYECTOS)
    df_proyectos.columns = df_proyectos.columns.str.strip()
except Exception as e:
    st.error("Error al cargar la solapa PROYECTOS de Google Sheets.")
    st.stop()

col_evaluador = 'Evaluador' if 'Evaluador' in df_proyectos.columns else df_proyectos.columns[3]
col_id = 'ID_proyecto' if 'ID_proyecto' in df_proyectos.columns else df_proyectos.columns[0]
col_escuela = 'Escuela' if 'Escuela' in df_proyectos.columns else df_proyectos.columns[1]
col_proyecto = 'Proyecto' if 'Proyecto' in df_proyectos.columns else df_proyectos.columns[2]

# Selección de Evaluador
evaluadores_unicos = sorted(list(set([str(x).strip() for x in df_proyectos[col_evaluador].dropna().tolist() if str(x).strip()])))
evaluador_seleccionado = st.selectbox("👤 Selecciona tu Nombre (Evaluador):", ["-- Seleccionar --"] + evaluadores_unicos)

if evaluador_seleccionado != "-- Seleccionar --":
    df_filtrado = df_proyectos[df_proyectos[col_evaluador].astype(str).str.contains(evaluador_seleccionado, case=False, na=False)].copy()
    df_filtrado['Display'] = df_filtrado[col_id].astype(str) + " - " + df_filtrado[col_proyecto].astype(str) + " (" + df_filtrado[col_escuela].astype(str) + ")"
    proyectos_opciones = df_filtrado['Display'].tolist()
    
    st.info(f"Tienes **{len(proyectos_opciones)} proyectos** asignados.")
    proyecto_elegido = st.selectbox("📌 Selecciona el Proyecto a Evaluar:", ["-- Seleccionar Proyecto --"] + proyectos_opciones)
    
    if proyecto_elegido != "-- Seleccionar Proyecto --":
        row_proj = df_filtrado[df_filtrado['Display'] == proyecto_elegido].iloc[0]
        
        st.markdown(f"""
        <div class="project-card">
            <h4>{row_proj[col_proyecto]}</h4>
            <p><b>ID:</b> {row_proj[col_id]} | <b>Escuela:</b> {row_proj[col_escuela]}</p>
        </div>
        """, unsafe_allow_html=True)
            
        st.markdown("---")
        st.subheader("📝 Cargar Evaluación")
        
        with st.form("form_evaluacion"):
            c1 = st.slider("1. ¿El proyecto resuelve un problema claro y funciona correctamente?", 1, 5, 3)
            c2 = st.slider("2. ¿La propuesta presenta una idea novedosa o uso creativo de tecnología?", 1, 5, 3)
            c3 = st.slider("3. ¿El equipo explica con claridad y demuestra dominio técnico?", 1, 5, 3)
            c4 = st.slider("4. ¿El stand está prolijo, organizado y con apoyo visual/demostrativo?", 1, 5, 3)
            c5 = st.slider("5. ¿Adaptan la explicación para todo público?", 1, 5, 3)
            
            comentarios = st.text_area("💬 Comentarios / Observaciones:")
            destacado = st.checkbox("⭐ ¿Marcar como Proyecto Destacado?")
            
            enviar = st.form_submit_button("💾 Guardar Evaluación")
            
        if enviar:
            puntaje_total = c1 + c2 + c3 + c4 + c5
            porcentaje_logro = f"{(puntaje_total / 25.0) * 100:.1f}%"
            
            datos_eval = {
                "ID_Evaluacion": str(uuid.uuid4())[:8],
                "Fecha_Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "Evaluador": evaluador_seleccionado,
                "ID_Proyecto": str(row_proj[col_id]),
                "c1": c1, "c2": c2, "c3": c3, "c4": c4, "c5": c5,
                "Puntaje_Total": puntaje_total,
                "Porcentaje_Logro": porcentaje_logro,
                "Comentarios": comentarios,
                "Destacado": "⭐" if destacado else ""
            }
            
            with st.spinner("Guardando en Google Sheets..."):
                try:
                    headers = {"Content-Type": "application/json"}
                    res = requests.post(URL_APPS_SCRIPT, data=json.dumps(datos_eval), headers=headers, timeout=10)
                    
                    if "OK" in res.text:
                        st.success("🎉 ¡Evaluación guardada exitosamente en la solapa EVALUACIÓN!")
                        st.balloons()
                    else:
                        st.error(f"Error al enviar datos: {res.text}")
                except Exception as err:
                    st.error(f"Error de conexión: {err}")

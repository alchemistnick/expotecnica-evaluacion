import streamlit as st
import pandas as pd
from datetime import datetime
import uuid

# Configuración de página
st.set_page_config(page_title="Expotécnica - Evaluación", page_icon="📝", layout="centered")

st.markdown("""
    <style>
    .main { padding: 1rem; }
    .stButton>button { width: 100%; background-color: #2E7D32; color: white; font-size: 18px; font-weight: bold; border-radius: 8px; padding: 0.6rem; }
    .project-card { background-color: #F4F6F8; padding: 12px; border-radius: 8px; margin-bottom: 15px; border-left: 5px solid #1976D2; }
    </style>
""", unsafe_allow_html=True)

st.title("📋 Evaluación Expotécnica")
st.write("Selecciona un proyecto asignado y carga tu evaluación.")

# ID de tu planilla de Google Sheets
SPREADSHEET_ID = "1KWw1ybOAuxxBk4P3gVoqp90UXx2pBaa9ccAiiV8Rd-w"
URL_PROYECTOS = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=PROYECTOS"

# Cargar tabla PROYECTOS
try:
    df_proyectos = pd.read_csv(URL_PROYECTOS)
    # Limpiar nombres de columnas removiendo espacios extras
    df_proyectos.columns = df_proyectos.columns.str.strip()
except Exception as e:
    st.error("Error al conectar con la planilla de Google Sheets.")
    st.stop()

# Verificar columna de evaluador
col_evaluador = 'Evaluador' if 'Evaluador' in df_proyectos.columns else df_proyectos.columns[3]
col_id = 'ID_proyecto' if 'ID_proyecto' in df_proyectos.columns else df_proyectos.columns[0]
col_escuela = 'Escuela' if 'Escuela' in df_proyectos.columns else df_proyectos.columns[1]
col_proyecto = 'Proyecto' if 'Proyecto' in df_proyectos.columns else df_proyectos.columns[2]

# 1. Selección de Evaluador
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
        
        if 'Link al Proyecto' in row_proj and pd.notna(row_proj['Link al Proyecto']) and str(row_proj['Link al Proyecto']).startswith("http"):
            st.markdown(f"📄 [Abrir Documento/Link del Proyecto]({row_proj['Link al Proyecto']})")
        if 'Link al Video' in row_proj and pd.notna(row_proj['Link al Video']) and str(row_proj['Link al Video']).startswith("http"):
            st.markdown(f"🎥 [Ver Video del Proyecto]({row_proj['Link al Video']})")
            
        st.markdown("---")
        st.subheader("📝 Formulario de Calificación")
        
        with st.form("form_evaluacion"):
            c1 = st.slider("1. ¿El proyecto resuelve un problema claro y funciona correctamente?", 1, 5, 3)
            c2 = st.slider("2. ¿La propuesta presenta una idea novedosa o uso creativo de tecnología?", 1, 5, 3)
            c3 = st.slider("3. ¿El equipo explica con claridad y demuestra dominio técnico?", 1, 5, 3)
            c4 = st.slider("4. ¿El stand está prolijo, organizado y con apoyo visual/demostrativo?", 1, 5, 3)
            c5 = st.slider("5. ¿Adaptan la explicación para todo público?", 1, 5, 3)
            
            comentarios = st.text_area("💬 Comentarios / Observaciones:", placeholder="Escribe aquí tus comentarios del proyecto...")
            destacado = st.checkbox("⭐ ¿Marcar como Proyecto Destacado?")
            
            enviar = st.form_submit_button("💾 Confirmar Evaluación")
            
        if enviar:
            puntaje_total = c1 + c2 + c3 + c4 + c5
            porcentaje_logro = (puntaje_total / 25.0) * 100
            
            st.success(f"🎉 ¡Evaluación completada para el proyecto {row_proj[col_id]}!")
            st.info(f"**Puntaje Total:** {puntaje_total}/25 ({porcentaje_logro:.1f}%)")

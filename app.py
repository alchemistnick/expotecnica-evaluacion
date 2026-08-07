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

# Cargar tabla PROYECTOS mediante la API pública de CSV
try:
    df_proyectos = pd.read_csv(URL_PROYECTOS)
except Exception as e:
    st.error("Error al conectar con la planilla de Google Sheets. Asegúrate de que los permisos en la planilla estén en 'Cualquier persona con el enlace'.")
    st.stop()

# 1. Selección de Evaluador
evaluadores_unicos = sorted(list(set([str(x).strip() for x in df_proyectos['Evaluador'].dropna().tolist() if str(x).strip()])))
evaluador_seleccionado = st.selectbox("👤 Selecciona tu Nombre (Evaluador):", ["-- Seleccionar --"] + evaluadores_unicos)

if evaluador_seleccionado != "-- Seleccionar --":
    df_filtrado = df_proyectos[df_proyectos['Evaluador'].astype(str).str.contains(evaluador_seleccionado, case=False, na=False)].copy()
    
    df_filtrado['Display'] = df_filtrado['ID_proyecto'].astype(str) + " - " + df_filtrado['Proyecto'].astype(str) + " (" + df_filtrado['Escuela'].astype(str) + ")"
    proyectos_opciones = df_filtrado['Display'].tolist()
    
    st.info(f"Tienes **{len(proyectos_opciones)} proyectos** asignados.")
    
    proyecto_elegido = st.selectbox("📌 Selecciona el Proyecto a Evaluar:", ["-- Seleccionar Proyecto --"] + proyectos_opciones)
    
    if proyecto_elegido != "-- Seleccionar Proyecto --":
        row_proj = df_filtrado[df_filtrado['Display'] == proyecto_elegido].iloc[0]
        
        st.markdown(f"""
        <div class="project-card">
            <h4>{row_proj['Proyecto']}</h4>
            <p><b>ID:</b> {row_proj['ID_proyecto']} | <b>Escuela:</b> {row_proj['Escuela']}</p>
            <p><b>Estado previo:</b> {'✅ Ya Evaluado' if str(row_proj.get('Fué evaluado', '')).upper() == 'SI' else '⏳ Pendiente'}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if pd.notna(row_proj.get('Link al Proyecto')) and str(row_proj['Link al Proyecto']).startswith("http"):
            st.markdown(f"📄 [Abrir Documento/Link del Proyecto]({row_proj['Link al Proyecto']})")
        if pd.notna(row_proj.get('Link al Video')) and str(row_proj['Link al Video']).startswith("http"):
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
            
            st.success(f"🎉 ¡Evaluación calculada con éxito para el proyecto {row_proj['ID_proyecto']}!")
            st.info(f"**Puntaje Total:** {puntaje_total}/25 ({porcentaje_logro:.1f}%)")

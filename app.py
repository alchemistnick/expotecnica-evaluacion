import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid

# Configuración de página
st.set_page_config(page_title="Expotécnica - Evaluación", page_icon="📝", layout="centered")

# Estilos visuales optimizados para dispositivos móviles
st.markdown("""
    <style>
    .main {
        padding: 1rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #2E7D32;
        color: white;
        font-size: 18px;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.6rem;
    }
    .project-card {
        background-color: #F4F6F8;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 15px;
        border-left: 5px solid #1976D2;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📋 Evaluación Expotécnica")
st.write("Selecciona un proyecto asignado y carga tu evaluación.")

# Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Cargar tabla PROYECTOS
try:
    df_proyectos = conn.read(worksheet="PROYECTOS", ttl=5)
except Exception as e:
    st.error("Error al conectar con la planilla de Google Sheets.")
    st.stop()

# 1. Selección de Evaluador
evaluadores_unicos = sorted(list(set([str(x).strip() for x in df_proyectos['Evaluador'].dropna().tolist() if str(x).strip()])))
evaluador_seleccionado = st.selectbox("👤 Selecciona tu Nombre (Evaluador):", ["-- Seleccionar --"] + evaluadores_unicos)

if evaluador_seleccionado != "-- Seleccionar --":
    # Filtrar proyectos asignados a este evaluador
    df_filtrado = df_proyectos[df_proyectos['Evaluador'].astype(str).str.contains(evaluador_seleccionado, case=False, na=False)].copy()
    
    # Crear listado para el desplegable
    df_filtrado['Display'] = df_filtrado['ID_proyecto'].astype(str) + " - " + df_filtrado['Proyecto'].astype(str) + " (" + df_filtrado['Escuela'].astype(str) + ")"
    proyectos_opciones = df_filtrado['Display'].tolist()
    
    st.info(f"Tienes **{len(proyectos_opciones)} proyectos** asignados.")
    
    proyecto_elegido = st.selectbox("📌 Selecciona el Proyecto a Evaluar:", ["-- Seleccionar Proyecto --"] + proyectos_opciones)
    
    if proyecto_elegido != "-- Seleccionar Proyecto --":
        # Obtener fila seleccionada
        row_proj = df_filtrado[df_filtrado['Display'] == proyecto_elegido].iloc[0]
        
        # Mostrar tarjeta de detalles
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
            
            enviar = st.form_submit_button("💾 Guardar Evaluación")
            
        if enviar:
            puntaje_total = c1 + c2 + c3 + c4 + c5
            porcentaje_logro = (puntaje_total / 25.0) * 100
            
            nueva_eval = pd.DataFrame([{
                "ID_Evaluacion": str(uuid.uuid4())[:8],
                "Fecha_Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "Evaluador": evaluador_seleccionado,
                "ID_Proyecto": str(row_proj['ID_proyecto']),
                "¿El proyecto resuelve un problema claro y funciona correctamente según los objetivos planteados?": c1,
                "¿La propuesta presenta una idea novedosa, original o un uso creativo de los recursos/tecnología?": c2,
                "¿El equipo explica con claridad cómo desarrollaron el proyecto y demuestra dominio del tema y vocabulario técnico?": c3,
                "¿El stand se encuentra prolijo, bien organizado y utiliza apoyo visual o demostrativo atractivo?": c4,
                "¿Logran adaptar la explicación para que personas sin conocimientos técnicos o visitantes de distintos niveles entiendan la idea?": c5,
                "Puntaje_Total": puntaje_total,
                "Porcentaje_Logro": f"{porcentaje_logro:.1f}%",
                "Comentarios": comentarios,
                "Destacado": "⭐" if destacado else ""
            }])
            
            try:
                df_evals = conn.read(worksheet="EVALUACIÓN", ttl=0)
                df_actualizado = pd.concat([df_evals, nueva_eval], ignore_index=True)
                conn.update(worksheet="EVALUACIÓN", data=df_actualizado)
                
                # Actualizar flag 'Fué evaluado' en la pestaña PROYECTOS
                df_proyectos.loc[df_proyectos['ID_proyecto'] == row_proj['ID_proyecto'], 'Fué evaluado'] = 'Si'
                conn.update(worksheet="PROYECTOS", data=df_proyectos)
                
                st.success(f"🎉 ¡Evaluación guardada exitosamente en Google Sheets para el proyecto {row_proj['ID_proyecto']}!")
            except Exception as ex:
                st.error(f"Error al guardar en la base de datos: {ex}")

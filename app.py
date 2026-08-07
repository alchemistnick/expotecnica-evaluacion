import streamlit as st
import pandas as pd
import requests
import json
import urllib.parse
from datetime import datetime
import uuid
import os

# Configuración de página
st.set_page_config(
    page_title="Expotécnica 2026", 
    page_icon="🏆", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos CSS Personalizados
st.markdown("""
    <style>
    /* Estilos globales */
    .stApp {
        background-color: #F8F9FA;
    }
    
    /* Encabezado Principal */
    .header-container {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 20px;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    .header-container h1 {
        color: white !important;
        font-weight: 800 !important;
        font-size: 2rem !important;
        margin-bottom: 4px !important;
    }
    .header-container p {
        color: #E0E7FF;
        font-size: 0.95rem;
        margin: 0;
    }

    /* Pestañas (Tabs) estilizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #E2E8F0;
        padding: 6px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 16px;
        font-weight: 600;
        color: #475569;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #1E3A8A !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    /* Tarjeta de Proyecto Seleccionado */
    .project-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 18px 20px;
        border-left: 6px solid #2563EB;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        margin-top: 15px;
        margin-bottom: 20px;
    }
    .project-card h3 {
        margin: 0 0 6px 0 !important;
        color: #0F172A !important;
        font-size: 1.25rem !important;
    }
    .project-card p {
        margin: 4px 0 !important;
        color: #475569;
        font-size: 0.95rem;
    }
    .project-card a {
        color: #2563EB;
        font-weight: 600;
        text-decoration: none;
    }
    .project-card a:hover {
        text-decoration: underline;
    }

    /* Botón Principal */
    .stButton>button {
        background: linear-gradient(135deg, #16A34A 0%, #15803D 100%) !important;
        color: white !important;
        font-size: 17px !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(22, 163, 74, 0.25);
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 15px rgba(22, 163, 74, 0.35);
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado con Logo (si existe logo.png)
if os.path.exists("logo.png"):
    col_logo, col_header = st.columns([1, 3], vertical_alignment="center")
    with col_logo:
        st.image("logo.png", use_container_width=True)
    with col_header:
        st.markdown("""
            <div class="header-container" style="margin-bottom: 0;">
                <h1>📊 Expotécnica 2026</h1>
                <p>Sistema Digital de Evaluación y Ranking</p>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
else:
    st.markdown("""
        <div class="header-container">
            <h1>📊 Expotécnica 2026</h1>
            <p>Sistema Digital de Evaluación y Ranking de Proyectos</p>
        </div>
    """, unsafe_allow_html=True)

# Configuración de Google Sheets
SPREADSHEET_ID = "1KWw1ybOAuxxBk4P3gVoqp90UXx2pBaa9ccAiiV8Rd-w"
GID_EVALUACION = "" 

URL_PROYECTOS = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=PROYECTOS"
URL_RANKING = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=RANKING_OFICIAL"
URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbxhYfT5q-hnJsv70NAiBmAY_Dwvbl-4jjn0uRdYWn1akl_bvZxQ1O25RoEmkp95IGzW/exec"

# Carga de evaluaciones
def cargar_evaluaciones():
    urls_a_probar = []
    if GID_EVALUACION.strip():
        urls_a_probar.append(f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID_EVALUACION.strip()}")
        
    urls_a_probar.extend([
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=" + urllib.parse.quote("EVALUACIÓN"),
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=" + urllib.parse.quote("EVALUACIÓN "),
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=EVALUACION",
        f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=EVALUACION "
    ])
    
    for url in urls_a_probar:
        try:
            df = pd.read_csv(url)
            df.columns = df.columns.str.strip()
            cols_lower = [str(c).lower() for c in df.columns]
            if any(k in cols_lower for k in ['id_evaluacion', 'c1', 'puntaje_total', 'porcentaje_logro']):
                return df
        except:
            continue
            
    return pd.DataFrame(columns=["ID_Evaluacion", "Fecha_Hora", "Evaluador", "ID_Proyecto", "c1", "c2", "c3", "c4", "c5", "Puntaje_Total", "Porcentaje_Logro", "Comentarios", "Destacado"])

# Cargar catálogo de proyectos
try:
    df_proyectos = pd.read_csv(URL_PROYECTOS)
    df_proyectos.columns = df_proyectos.columns.str.strip()
except Exception as e:
    st.error("⚠️ Error de conexión al cargar la lista de proyectos.")
    st.stop()

col_evaluador = 'Evaluador' if 'Evaluador' in df_proyectos.columns else df_proyectos.columns[3]
col_id = 'ID_proyecto' if 'ID_proyecto' in df_proyectos.columns else df_proyectos.columns[0]
col_escuela = 'Escuela' if 'Escuela' in df_proyectos.columns else df_proyectos.columns[1]
col_proyecto = 'Proyecto' if 'Proyecto' in df_proyectos.columns else df_proyectos.columns[2]
col_url = next((c for c in df_proyectos.columns if any(k in c.lower() for k in ['url', 'link', 'enlace', 'drive', 'video'])), None)

# Pestañas principales
tab_evaluar, tab_ranking, tab_historial = st.tabs(["📝 Cargar Evaluación", "🏆 Ranking Oficial", "📋 Evaluaciones Cargadas"])

# --- TAB 1: EVALUAR ---
with tab_evaluar:
    evaluadores_unicos = sorted(list(set([str(x).strip() for x in df_proyectos[col_evaluador].dropna().tolist() if str(x).strip()])))
    evaluador_seleccionado = st.selectbox("👤 **Selecciona tu Nombre (Evaluador):**", ["-- Seleccionar --"] + evaluadores_unicos, key="sel_eval")

    if evaluador_seleccionado != "-- Seleccionar --":
        df_filtrado = df_proyectos[df_proyectos[col_evaluador].astype(str).str.contains(evaluador_seleccionado, case=False, na=False)].copy()
        df_filtrado['Display'] = df_filtrado[col_id].astype(str) + " - " + df_filtrado[col_proyecto].astype(str) + " (" + df_filtrado[col_escuela].astype(str) + ")"
        proyectos_opciones = df_filtrado['Display'].tolist()
        
        st.caption(f"📌 Tienes **{len(proyectos_opciones)} proyectos** asignados a tu nombre.")
        proyecto_elegido = st.selectbox("📌 **Selecciona el Proyecto a Evaluar:**", ["-- Seleccionar Proyecto --"] + proyectos_opciones, key="sel_proy")
        
        if proyecto_elegido != "-- Seleccionar Proyecto --":
            row_proj = df_filtrado[df_filtrado['Display'] == proyecto_elegido].iloc[0]
            
            url_val = str(row_proj[col_url]).strip() if col_url and pd.notna(row_proj[col_url]) else ""
            url_html = f'<p style="margin-top: 6px;">🔗 <b>Enlace:</b> <a href="{url_val}" target="_blank">{url_val}</a></p>' if url_val and url_val.lower().startswith('http') else ""
            
            st.markdown(f"""
            <div class="project-card">
                <h3>{row_proj[col_proyecto]}</h3>
                <p><b>ID:</b> <code>{row_proj[col_id]}</code> | <b>Escuela:</b> {row_proj[col_escuela]}</p>
                {url_html}
            </div>
            """, unsafe_allow_html=True)
                
            st.markdown("#### 📝 Rubro de Calificación")
            
            with st.form("form_evaluacion"):
                c1 = st.slider("1. ¿El proyecto resuelve un problema claro y funciona correctamente?", 1, 5, 3)
                c2 = st.slider("2. ¿La propuesta presenta una idea novedosa o uso creativo?", 1, 5, 3)
                c3 = st.slider("3. ¿El equipo explica con claridad y demuestra dominio técnico?", 1, 5, 3)
                c4 = st.slider("4. ¿El stand está prolijo, organizado y con apoyo demostrativo?", 1, 5, 3)
                c5 = st.slider("5. ¿Adaptan la explicación para todo público?", 1, 5, 3)
                
                st.markdown("---")
                comentarios = st.text_area("💬 Comentarios / Observaciones:", placeholder="Escribe aquí las fortalezas o recomendaciones del proyecto...")
                destacado = st.checkbox("⭐ **¿Marcar como Proyecto Destacado?**")
                
                enviar = st.form_submit_button("💾 Guardar Evaluación")
                
            if enviar:
                puntaje_total = c1 + c2 + c3 + c4 + c5
                porcentaje_logro = f"{(puntaje_total / 25.0) * 100:.1f}%"
                
                datos_eval = {
                    "accion": "crear",
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
                
                with st.spinner("Registrando evaluación en planilla..."):
                    try:
                        headers = {"Content-Type": "application/json"}
                        res = requests.post(URL_APPS_SCRIPT, data=json.dumps(datos_eval), headers=headers, timeout=12)
                        if "OK" in res.text:
                            st.success("🎉 ¡Evaluación registrada con éxito!")
                            st.balloons()
                        else:
                            st.error(f"Error al enviar datos: {res.text}")
                    except Exception as err:
                        st.error(f"Error de conexión: {err}")

# --- TAB 2: RANKING OFICIAL ---
with tab_ranking:
    st.markdown("### 🏆 Posiciones Oficiales")
    col_r1, col_r2 = st.columns([3, 1])
    with col_r2:
        if st.button("🔄 Actualizar", key="btn_rank_ref"):
            st.rerun()
        
    try:
        df_ranking = pd.read_csv(URL_RANKING)
        df_ranking.columns = df_ranking.columns.str.strip()
        
        if len(df_ranking) > 0:
            st.dataframe(
                df_ranking, 
                use_container_width=True, 
                hide_index=True,
                height=380
            )
        else:
            st.info("Aún no se han consolidado posiciones en el ranking.")
    except Exception as e:
        st.warning("El ranking se está calculando en segundo plano...")

# --- TAB 3: EVALUACIONES CARGADAS Y ADMIN ---
with tab_historial:
    st.markdown("### 📋 Historial de Evaluaciones")
    try:
        df_eval = cargar_evaluaciones()
        
        evaluadores_unicos = sorted(list(set([str(x).strip() for x in df_proyectos[col_evaluador].dropna().tolist() if str(x).strip()])))
        eval_usuario = st.selectbox("Filtrar por Evaluador:", ["-- Todos --"] + evaluadores_unicos, key="hist_eval")
        
        if len(df_eval) > 0:
            if eval_usuario != "-- Todos --":
                col_eval_name = next((c for c in df_eval.columns if 'evaluador' in c.lower()), df_eval.columns[2])
                df_mis_eval = df_eval[df_eval[col_eval_name].astype(str).str.contains(eval_usuario, case=False, na=False)]
            else:
                df_mis_eval = df_eval
                
            if len(df_mis_eval) > 0:
                # Columnas compactas incluyendo Destacado (⭐)
                cols_compactas = [c for c in ["Fecha_Hora", "Evaluador", "ID_Proyecto", "Puntaje_Total", "Porcentaje_Logro", "Destacado", "Comentarios"] if c in df_mis_eval.columns]
                df_compacto = df_mis_eval[cols_compactas] if len(cols_compactas) > 0 else df_mis_eval
                
                st.dataframe(
                    df_compacto, 
                    use_container_width=True, 
                    hide_index=True,
                    height=280
                )
            else:
                st.info(f"No hay registros asignados para {eval_usuario}.")
        else:
            st.info("Aún no hay evaluaciones registradas en la planilla.")
            
        # ZONA ADMINISTRADOR
        st.markdown("---")
        with st.expander("🔐 Panel de Administración (Borrar Registro)"):
            codigo_admin = st.text_input("Ingresa la clave ADMIN:", type="password", key="pwd_admin")
            
            if codigo_admin.strip() == "ADMIN":
                st.success("Acceso Administrador concedido.")
                
                if len(df_eval) > 0:
                    col_id_eval = df_eval.columns[0]
                    ids_disponibles = df_eval[col_id_eval].dropna().astype(str).tolist()
                    
                    if ids_disponibles:
                        id_a_borrar = st.selectbox("🗑️ ID_Evaluación a eliminar:", ["-- Seleccionar ID --"] + ids_disponibles)
                        
                        if id_a_borrar != "-- Seleccionar ID --":
                            if st.button("❌ Confirmar Eliminación", type="primary"):
                                payload_delete = {"accion": "eliminar", "ID_Evaluacion": id_a_borrar}
                                with st.spinner("Eliminando fila de la planilla..."):
                                    try:
                                        headers = {"Content-Type": "application/json"}
                                        res = requests.post(URL_APPS_SCRIPT, data=json.dumps(payload_delete), headers=headers, timeout=12)
                                        if "OK_ELIMINADO" in res.text:
                                            st.success(f"Evaluación '{id_a_borrar}' eliminada correctamente.")
                                            st.rerun()
                                        else:
                                            st.error(f"Error al eliminar: {res.text}")
                                    except Exception as err:
                                        st.error(f"Error de conexión: {err}")
            elif codigo_admin != "":
                st.error("Código incorrecto.")
                
    except Exception as e:
        st.warning("No se pudieron cargar las evaluaciones registradas.")

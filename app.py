import streamlit as st
import pandas as pd
import requests
import json
import urllib.parse
from datetime import datetime
import uuid
import os

# Configuración de la página
st.set_page_config(
    page_title="Expotécnica 2026", 
    page_icon="🏆", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos CSS Profesionales con Colores de Alto Contraste
st.markdown("""
    <style>
    /* Estilos globales */
    .stApp {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Forzar texto visible en etiquetas y párrafos comunes */
    label, p, span, h2, h3, h4, h5, h6, .stMarkdown, div[data-testid="stMarkdownContainer"] p {
        color: #0F172A !important;
    }

    /* Encabezado Principal Centrado */
    .header-container {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%);
        padding: 24px;
        border-radius: 12px;
        text-align: center !important;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
    }
    .header-container h1 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 1.8rem !important;
        letter-spacing: -0.02em;
        margin-bottom: 6px !important;
        text-align: center !important;
    }
    .header-container p {
        color: #E2E8F0 !important;
        font-size: 0.95rem;
        margin: 0;
        text-align: center !important;
    }

    /* Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #E2E8F0;
        padding: 4px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        font-size: 0.9rem;
        border: none !important;
    }
    .stTabs [data-baseweb="tab"] span {
        color: #475569 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .stTabs [aria-selected="true"] span {
        color: #1E3A8A !important;
        font-weight: 700 !important;
    }

    /* Tarjeta de Proyecto */
    .project-card {
        background-color: #FFFFFF;
        border-radius: 10px;
        padding: 18px 22px;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #2563EB;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        margin-top: 12px;
        margin-bottom: 20px;
    }
    .project-card h3 {
        margin: 0 0 8px 0 !important;
        color: #0F172A !important;
        font-size: 1.15rem !important;
        font-weight: 700;
    }
    .project-card .badge {
        display: inline-block;
        background-color: #F1F5F9;
        color: #1E293B !important;
        padding: 3px 8px;
        border-radius: 5px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 8px;
    }
    .project-card a {
        color: #2563EB !important;
        font-weight: 600;
        text-decoration: none;
    }
    .project-card a:hover {
        text-decoration: underline;
    }

    /* Componentes de Formulario */
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"] span {
        color: #0F172A !important;
    }
    .stTextInput input, .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }

    /* Sliders */
    div[data-testid="stSlider"] p {
        color: #0F172A !important;
        font-weight: 600 !important;
        font-size: 0.9rem;
    }

    /* Botones */
    .stButton>button {
        background: #15803D !important;
        color: #FFFFFF !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 0.65rem 1rem !important;
        border: none !important;
        box-shadow: 0 2px 6px rgba(21, 128, 61, 0.2);
        transition: background-color 0.15s ease-in-out;
    }
    .stButton>button:hover {
        background: #166534 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado Centrado
if os.path.exists("logo.png"):
    col_logo, col_header = st.columns([1, 4], vertical_alignment="center")
    with col_logo:
        st.image("logo.png", use_container_width=True)
    with col_header:
        st.markdown("""
            <div class="header-container" style="margin-bottom: 0;">
                <h1>Expotécnica 2026</h1>
                <p>Plataforma Oficial de Evaluación de Proyectos</p>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
else:
    st.markdown("""
        <div class="header-container">
            <h1>Expotécnica 2026</h1>
            <p>Plataforma Oficial de Evaluación de Proyectos</p>
        </div>
    """, unsafe_allow_html=True)

# Configuración de Google Sheets
SPREADSHEET_ID = "1KWw1ybOAuxxBk4P3gVoqp90UXx2pBaa9ccAiiV8Rd-w"
GID_EVALUACION = "" 

URL_PROYECTOS = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=PROYECTOS"
URL_RANKING = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=RANKING_OFICIAL"
URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbxhYfT5q-hnJsv70NAiBmAY_Dwvbl-4jjn0uRdYWn1akl_bvZxQ1O25RoEmkp95IGzW/exec"

# ==========================================
# FUNCIONES CON CACHÉ
# ==========================================

@st.cache_data(ttl=600)
def cargar_proyectos():
    df = pd.read_csv(URL_PROYECTOS)
    df.columns = df.columns.str.strip()
    return df

@st.cache_data(ttl=60)
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

@st.cache_data(ttl=60)
def cargar_ranking():
    df = pd.read_csv(URL_RANKING)
    df.columns = df.columns.str.strip()
    return df


try:
    df_proyectos = cargar_proyectos()
except Exception:
    st.error("Se produjo un error de conexión al cargar la lista de proyectos.")
    st.stop()

col_evaluador = 'Evaluador' if 'Evaluador' in df_proyectos.columns else df_proyectos.columns[3]
col_id = 'ID_proyecto' if 'ID_proyecto' in df_proyectos.columns else df_proyectos.columns[0]
col_escuela = 'Escuela' if 'Escuela' in df_proyectos.columns else df_proyectos.columns[1]
col_proyecto = 'Proyecto' if 'Proyecto' in df_proyectos.columns else df_proyectos.columns[2]
col_url = next((c for c in df_proyectos.columns if any(k in c.lower() for k in ['url', 'link', 'enlace', 'drive', 'video'])), None)

# Pestañas principales
tab_evaluar, tab_ranking, tab_historial = st.tabs(["Evaluación", "Ranking General", "Historial"])

# --- PESTAÑA 1: EVALUAR ---
with tab_evaluar:
    evaluadores_unicos = sorted(list(set([str(x).strip() for x in df_proyectos[col_evaluador].dropna().tolist() if str(x).strip()])))
    evaluador_seleccionado = st.selectbox("Evaluador asignado:", ["-- Seleccionar --"] + evaluadores_unicos, key="sel_eval")

    if evaluador_seleccionado != "-- Seleccionar --":
        df_filtrado = df_proyectos[df_proyectos[col_evaluador].astype(str).str.contains(evaluador_seleccionado, case=False, na=False)].copy()
        df_filtrado['Display'] = df_filtrado[col_id].astype(str) + " — " + df_filtrado[col_proyecto].astype(str) + " (" + df_filtrado[col_escuela].astype(str) + ")"
        proyectos_opciones = df_filtrado['Display'].tolist()
        
        st.caption(f"Posee {len(proyectos_opciones)} proyectos asignados.")
        proyecto_elegido = st.selectbox("Proyecto a evaluar:", ["-- Seleccionar Proyecto --"] + proyectos_opciones, key="sel_proy")
        
        if proyecto_elegido != "-- Seleccionar Proyecto --":
            row_proj = df_filtrado[df_filtrado['Display'] == proyecto_elegido].iloc[0]
            
            url_val = str(row_proj[col_url]).strip() if col_url and pd.notna(row_proj[col_url]) else ""
            url_html = f'<p style="margin-top: 8px; font-size: 0.9rem;">Enlace adjunto: <a href="{url_val}" target="_blank">{url_val}</a></p>' if url_val and url_val.lower().startswith('http') else ""
            
            st.markdown(f"""
            <div class="project-card">
                <h3>{row_proj[col_proyecto]}</h3>
                <div>
                    <span class="badge">ID: {row_proj[col_id]}</span>
                    <span class="badge">Escuela: {row_proj[col_escuela]}</span>
                </div>
                {url_html}
            </div>
            """, unsafe_allow_html=True)
                
            st.markdown("##### Criterios de Evaluación")
            
            with st.form("form_evaluacion"):
                c1 = st.slider("1. ¿El proyecto resuelve un problema claro y funciona correctamente?", 1, 5, 3)
                c2 = st.slider("2. ¿La propuesta presenta una idea novedosa o uso creativo de tecnología?", 1, 5, 3)
                c3 = st.slider("3. ¿El equipo explica con claridad y demuestra dominio técnico?", 1, 5, 3)
                c4 = st.slider("4. ¿El stand está prolijo, organizado y con apoyo demostrativo?", 1, 5, 3)
                c5 = st.slider("5. ¿Adaptan la explicación para todo público?", 1, 5, 3)
                
                st.markdown("---")
                comentarios = st.text_area("Observaciones técnicas y comentarios:", placeholder="Añada aquí observaciones adicionales sobre la presentación...")
                destacado = st.checkbox("Mención especial (Proyecto Destacado)")
                
                enviar = st.form_submit_button("Guardar Evaluación")
                
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
                    "Destacado": "Sí" if destacado else "No"
                }
                
                with st.spinner("Guardando registro..."):
                    try:
                        headers = {"Content-Type": "application/json"}
                        res = requests.post(URL_APPS_SCRIPT, data=json.dumps(datos_eval), headers=headers, timeout=15)
                        if "OK" in res.text:
                            st.cache_data.clear()
                            st.success("Evaluación guardada correctamente.")
                        else:
                            st.error(f"Error en la respuesta del servidor: {res.text}")
                    except Exception as err:
                        st.error(f"Error de conexión: {err}")

# --- PESTAÑA 2: RANKING ---
with tab_ranking:
    col_r1, col_r2 = st.columns([3, 1])
    with col_r1:
        st.markdown("##### Posiciones Consolidadas")
    with col_r2:
        if st.button("Actualizar", key="btn_rank_ref"):
            st.cache_data.clear()
            st.rerun()
        
    try:
        df_ranking = cargar_ranking()
        
        if len(df_ranking) > 0:
            st.dataframe(
                df_ranking, 
                use_container_width=True, 
                hide_index=True,
                height=380
            )
        else:
            st.info("No hay datos consolidados en la tabla de posiciones.")
    except Exception:
        st.warning("Cargando posiciones...")

# --- PESTAÑA 3: HISTORIAL Y ADMIN ---
with tab_historial:
    st.markdown("##### Consultar Registros")
    try:
        df_eval = cargar_evaluaciones()
        
        evaluadores_unicos = sorted(list(set([str(x).strip() for x in df_proyectos[col_evaluador].dropna().tolist() if str(x).strip()])))
        eval_usuario = st.selectbox("Filtrar por evaluador:", ["-- Todos --"] + evaluadores_unicos, key="hist_eval")
        
        if len(df_eval) > 0:
            if eval_usuario != "-- Todos --":
                col_eval_name = next((c for c in df_eval.columns if 'evaluador' in c.lower()), df_eval.columns[2])
                df_mis_eval = df_eval[df_eval[col_eval_name].astype(str).str.contains(eval_usuario, case=False, na=False)]
            else:
                df_mis_eval = df_eval
                
            if len(df_mis_eval) > 0:
                cols_compactas = [c for c in ["Fecha_Hora", "Evaluador", "ID_Proyecto", "Puntaje_Total", "Porcentaje_Logro", "Destacado", "Comentarios"] if c in df_mis_eval.columns]
                df_compacto = df_mis_eval[cols_compactas] if len(cols_compactas) > 0 else df_mis_eval
                
                st.dataframe(
                    df_compacto, 
                    use_container_width=True, 
                    hide_index=True,
                    height=280
                )
            else:
                st.info(f"Sin registros asignados para {eval_usuario}.")
        else:
            st.info("Aún no existen registros ingresados.")
            
        # ZONA ADMINISTRADOR
        st.markdown("---")
        with st.expander("Panel de Gestión (Eliminar registro)"):
            codigo_admin = st.text_input("Clave de administrador:", type="password", key="pwd_admin")
            
            if codigo_admin.strip() == "ADMIN":
                st.success("Acceso concedido.")
                
                if len(df_eval) > 0:
                    col_id_eval = df_eval.columns[0]
                    ids_disponibles = df_eval[col_id_eval].dropna().astype(str).tolist()
                    
                    if ids_disponibles:
                        id_a_borrar = st.selectbox("ID de Evaluación a eliminar:", ["-- Seleccionar ID --"] + ids_disponibles)
                        
                        if id_a_borrar != "-- Seleccionar ID --":
                            if st.button("Eliminar Registro", type="primary"):
                                payload_delete = {"accion": "eliminar", "ID_Evaluacion": id_a_borrar}
                                with st.spinner("Procesando eliminación..."):
                                    try:
                                        headers = {"Content-Type": "application/json"}
                                        res = requests.post(URL_APPS_SCRIPT, data=json.dumps(payload_delete), headers=headers, timeout=15)
                                        if "OK_ELIMINADO" in res.text:
                                            st.cache_data.clear()
                                            st.success(f"Registro '{id_a_borrar}' eliminado correctamente.")
                                            st.rerun()
                                        else:
                                            st.error(f"Error al procesar: {res.text}")
                                    except Exception as err:
                                        st.error(f"Error de conexión: {err}")
            elif codigo_admin != "":
                st.error("Clave no válida.")
                
    except Exception:
        st.warning("No fue posible obtener los registros guardados.")

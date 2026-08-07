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
    page_icon="⚙️", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Estilos CSS Personalizados
st.markdown("""
    <style>
    /* Fondo e interfaz general */
    .stApp {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }
    
    /* Forzar visibilidad de textos en pantalla */
    label, p, span, h2, h3, h4, h5, h6, .stMarkdown, div[data-testid="stMarkdownContainer"] p {
        color: #0F172A !important;
    }

    /* Encabezado Principal Centrado */
    .header-container {
        background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
        padding: 22px;
        border-radius: 16px;
        text-align: center !important;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    .header-container h1 {
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 2rem !important;
        margin-bottom: 4px !important;
        text-align: center !important;
    }
    .header-container p {
        color: #E0E7FF !important;
        font-size: 0.95rem;
        margin: 0;
        text-align: center !important;
    }

    /* Pestañas (Tabs) */
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
        border: none !important;
    }
    .stTabs [data-baseweb="tab"] span {
        color: #475569 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .stTabs [aria-selected="true"] span {
        color: #1E3A8A !important;
        font-weight: 700 !important;
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
    .project-card p, .project-card code {
        color: #334155 !important;
    }
    .project-card a {
        color: #2563EB !important;
        font-weight: 600;
        text-decoration: underline;
    }

    /* Formulario y Selectores */
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
    }

    /* Botón Guardar */
    .stButton>button {
        background: linear-gradient(135deg, #16A34A 0%, #15803D 100%) !important;
        color: #FFFFFF !important;
        font-size: 17px !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        padding: 0.75rem 1rem !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(22, 163, 74, 0.25);
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado Centrado
if os.path.exists("logo.png"):
    col_logo, col_header = st.columns([1, 3], vertical_alignment="center")
    with col_logo:
        st.image("logo.png", use_container_width=True)
    with col_header:
        st.markdown("""
            <div class="header-container" style="margin-bottom: 0;">
                <h1>⚙️ Expotécnica 2026</h1>
                <p>Sistema Digital de Evaluación y Ranking</p>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
else:
    st.markdown("""
        <div class="header-container">
            <h1>⚙️ Expotécnica 2026</h1>
            <p>Sistema Digital de Evaluación y Ranking de Proyectos</p>
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

@st.cache_data(ttl=30)
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
            if any(k in cols_lower for k in ['id_evaluacion', 'id_evaluación', 'c1', 'puntaje_total', 'porcentaje_logro']):
                return df
        except:
            continue
            
    return pd.DataFrame(columns=["ID_Evaluación", "Fecha_Hora", "Evaluador", "ID_Proyecto", "c1", "c2", "c3", "c4", "c5", "Puntaje_Total", "Porcentaje_Logro", "Comentarios", "Destacado"])

@st.cache_data(ttl=30)
def cargar_ranking():
    df = pd.read_csv(URL_RANKING)
    df.columns = df.columns.str.strip()
    return df


try:
    df_proyectos = cargar_proyectos()
except Exception:
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
    evaluador_seleccionado = st.selectbox("👤 Selecciona tu Nombre (Evaluador):", ["-- Seleccionar --"] + evaluadores_unicos, key="sel_eval")

    if evaluador_seleccionado != "-- Seleccionar --":
        df_filtrado = df_proyectos[df_proyectos[col_evaluador].astype(str).str.contains(evaluador_seleccionado, case=False, na=False)].copy()
        df_filtrado['Display'] = df_filtrado[col_id].astype(str) + " - " + df_filtrado[col_proyecto].astype(str) + " (" + df_filtrado[col_escuela].astype(str) + ")"
        proyectos_opciones = df_filtrado['Display'].tolist()
        
        st.caption(f"📌 Tienes **{len(proyectos_opciones)} proyectos** asignados a tu nombre.")
        proyecto_elegido = st.selectbox("📌 Selecciona el Proyecto a Evaluar:", ["-- Seleccionar Proyecto --"] + proyectos_opciones, key="sel_proy")
        
        if proyecto_elegido != "-- Seleccionar Proyecto --":
            row_proj = df_filtrado[df_filtrado['Display'] == proyecto_elegido].iloc[0]
            id_proy_actual = str(row_proj[col_id]).strip()
            
            url_val = str(row_proj[col_url]).strip() if col_url and pd.notna(row_proj[col_url]) else ""
            url_html = f'<p style="margin-top: 6px;">🔗 <b>Enlace al Proyecto:</b> <a href="{url_val}" target="_blank">{url_val}</a></p>' if url_val and url_val.lower().startswith('http') else ""
            
            st.markdown(f"""
            <div class="project-card">
                <h3>{row_proj[col_proyecto]}</h3>
                <p><b>ID:</b> <code>{row_proj[col_id]}</code> | <b>Escuela:</b> {row_proj[col_escuela]}</p>
                {url_html}
            </div>
            """, unsafe_allow_html=True)
            
            # Verificar si el proyecto ya fue evaluado
            df_eval_existentes = cargar_evaluaciones()
            evaluadores_previos = []
            
            if len(df_eval_existentes) > 0:
                col_id_p = next((c for c in df_eval_existentes.columns if 'proyecto' in c.lower()), df_eval_existentes.columns[3])
                col_eval_p = next((c for c in df_eval_existentes.columns if 'evaluador' in c.lower()), df_eval_existentes.columns[2])
                
                evals_mismo_proy = df_eval_existentes[df_eval_existentes[col_id_p].astype(str).str.strip().str.upper() == id_proy_actual.upper()]
                if len(evals_mismo_proy) > 0:
                    evaluadores_previos = evals_mismo_proy[col_eval_p].dropna().astype(str).str.strip().unique().tolist()

            permitir_evaluacion = True
            
            if evaluadores_previos:
                nombres_eval = ", ".join(evaluadores_previos)
                st.warning(f"⚠️ **Este proyecto ya fue evaluado por:** {nombres_eval}.")
                confirmacion = st.radio(
                    "¿Igualmente deseas registrar una nueva evaluación?", 
                    ["No", "Sí"], 
                    index=0, 
                    key="conf_re_eval"
                )
                if confirmacion == "No":
                    permitir_evaluacion = False
                    st.info("No se mostrará el formulario de evaluación para este proyecto.")

            if permitir_evaluacion:
                st.markdown("#### 📝 Rubro de Calificación")
                
                with st.form("form_evaluacion"):
                    c1 = st.slider("1. ¿El proyecto resuelve un problema claro y funciona correctamente?", 1, 5, 3)
                    c2 = st.slider("2. ¿La propuesta presenta una idea novedosa o uso creativo de tecnología?", 1, 5, 3)
                    c3 = st.slider("3. ¿El equipo explica con claridad y demuestra dominio técnico?", 1, 5, 3)
                    c4 = st.slider("4. ¿El stand está prolijo, organizado y con apoyo demostrativo?", 1, 5, 3)
                    c5 = st.slider("5. ¿Adaptan la explicación para todo público?", 1, 5, 3)
                    
                    st.markdown("---")
                    comentarios = st.text_area("💬 Comentarios / Observaciones:", placeholder="Escribe aquí las fortalezas o recomendaciones del proyecto...")
                    destacado = st.checkbox("⭐ ¿Marcar como Proyecto Destacado?")
                    
                    enviar = st.form_submit_button("💾 Guardar Evaluación")
                    
                if enviar:
                    puntaje_total = c1 + c2 + c3 + c4 + c5
                    porcentaje_logro = f"{(puntaje_total / 25.0) * 100:.1f}%"
                    id_eval_generado = str(uuid.uuid4())[:8]
                    
                    datos_eval = {
                        "accion": "crear",
                        "ID_Evaluación": id_eval_generado,
                        "ID_Evaluacion": id_eval_generado,
                        "Fecha_Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "Evaluador": evaluador_seleccionado,
                        "ID_Proyecto": str(row_proj[col_id]),
                        "c1": c1, "c2": c2, "c3": c3, "c4": c4, "c5": c5,
                        "Puntaje_Total": puntaje_total,
                        "Porcentaje_Logro": porcentaje_logro,
                        "Comentarios": comentarios,
                        "Destacado": "⭐" if destacado else ""
                    }
                    
                    with st.spinner("⚙️ Procesando y guardando evaluación..."):
                        try:
                            headers = {"Content-Type": "application/json"}
                            res = requests.post(URL_APPS_SCRIPT, data=json.dumps(datos_eval), headers=headers, timeout=15)
                            if "OK" in res.text:
                                st.cache_data.clear()
                                st.toast("⚙️ Evaluación registrada correctamente.", icon="⚙️")
                                st.success(f"⚙️ ¡Evaluación registrada con éxito! (ID: {id_eval_generado})")
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
            st.info("Aún no se han consolidado posiciones en el ranking.")
    except Exception:
        st.warning("⚙️ El ranking se está calculando en segundo plano...")

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
                cols_compactas = [c for c in df_mis_eval.columns if any(k in c.lower() for k in ['id_evalua', 'fecha', 'evaluador', 'id_proyecto', 'puntaje', 'porcentaje', 'destacado', 'comentario'])]
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
                    col_id_p = next((c for c in df_eval.columns if 'proyecto' in c.lower()), df_eval.columns[3])
                    col_eval_p = next((c for c in df_eval.columns if 'evaluador' in c.lower()), df_eval.columns[2])
                    
                    opciones_borrar = {}
                    for idx, r in df_eval.iterrows():
                        id_e = str(r[col_id_eval]).strip()
                        if id_e and id_e.lower() != 'nan':
                            label = f"ID: {id_e} | Proy: {r[col_id_p]} | Eval: {r[col_eval_p]}"
                            opciones_borrar[label] = id_e
                    
                    if opciones_borrar:
                        opcion_elegida = st.selectbox(
                            "🗑️ Selecciona la evaluación a eliminar:", 
                            ["-- Seleccionar Registro --"] + list(opciones_borrar.keys())
                        )
                        
                        if opcion_elegida != "-- Seleccionar Registro --":
                            id_a_borrar = opciones_borrar[opcion_elegida]
                            
                            if st.button("❌ Confirmar Eliminación", type="primary"):
                                payload_delete = {
                                    "accion": "eliminar", 
                                    "ID_Evaluacion": id_a_borrar,
                                    "ID_Evaluación": id_a_borrar
                                }
                                with st.spinner("⚙️ Eliminando fila de la planilla..."):
                                    try:
                                        headers = {"Content-Type": "application/json"}
                                        res = requests.post(URL_APPS_SCRIPT, data=json.dumps(payload_delete), headers=headers, timeout=15)
                                        if "OK_ELIMINADO" in res.text:
                                            st.cache_data.clear()
                                            st.toast("⚙️ Registro eliminado correctamente.", icon="⚙️")
                                            st.success(f"Evaluación '{id_a_borrar}' eliminada.")
                                            st.rerun()
                                        else:
                                            st.error(f"Error al eliminar: {res.text}")
                                    except Exception as err:
                                        st.error(f"Error de conexión: {err}")
            elif codigo_admin != "":
                st.error("Código incorrecto.")
                
    except Exception:
        st.warning("No se pudieron cargar las evaluaciones registradas.")

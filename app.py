import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import uuid

# Configuración visual
st.set_page_config(page_title="Expotécnica 2026", page_icon="📝", layout="centered")

st.markdown("""
    <style>
    .main { padding: 1rem; }
    .stButton>button { width: 100%; background-color: #2E7D32; color: white; font-size: 18px; font-weight: bold; border-radius: 8px; padding: 0.6rem; }
    .project-card { background-color: #F4F6F8; padding: 12px; border-radius: 8px; margin-bottom: 15px; border-left: 5px solid #1976D2; }
    .project-card a { color: #1976D2; font-weight: bold; text-decoration: underline; }
    </style>
""", unsafe_allow_html=True)

st.title("📋 Expotécnica 2026")

# Conexiones con Google Sheets
SPREADSHEET_ID = "1KWw1ybOAuxxBk4P3gVoqp90UXx2pBaa9ccAiiV8Rd-w"
URL_PROYECTOS = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=PROYECTOS"
URL_EVALUACIONES = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=EVALUACIÓN"
URL_RANKING = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=RANKING_OFICIAL"
URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbxhYfT5q-hnJsv70NAiBmAY_Dwvbl-4jjn0uRdYWn1akl_bvZxQ1O25RoEmkp95IGzW/exec"

# Cargar proyectos
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
col_url = next((c for c in df_proyectos.columns if any(k in c.lower() for k in ['url', 'link', 'enlace', 'drive', 'video'])), None)

# PESTAÑAS PRINCIPALES
tab_evaluar, tab_ranking, tab_historial = st.tabs(["📝 Cargar Evaluación", "🏆 Ranking Oficial", "📋 Evaluaciones Cargadas"])

# --- TAB 1: EVALUAR ---
with tab_evaluar:
    evaluadores_unicos = sorted(list(set([str(x).strip() for x in df_proyectos[col_evaluador].dropna().tolist() if str(x).strip()])))
    evaluador_seleccionado = st.selectbox("👤 Selecciona tu Nombre (Evaluador):", ["-- Seleccionar --"] + evaluadores_unicos, key="sel_eval")

    if evaluador_seleccionado != "-- Seleccionar --":
        df_filtrado = df_proyectos[df_proyectos[col_evaluador].astype(str).str.contains(evaluador_seleccionado, case=False, na=False)].copy()
        df_filtrado['Display'] = df_filtrado[col_id].astype(str) + " - " + df_filtrado[col_proyecto].astype(str) + " (" + df_filtrado[col_escuela].astype(str) + ")"
        proyectos_opciones = df_filtrado['Display'].tolist()
        
        st.info(f"Tienes **{len(proyectos_opciones)} proyectos** asignados.")
        proyecto_elegido = st.selectbox("📌 Selecciona el Proyecto a Evaluar:", ["-- Seleccionar Proyecto --"] + proyectos_opciones, key="sel_proy")
        
        if proyecto_elegido != "-- Seleccionar Proyecto --":
            row_proj = df_filtrado[df_filtrado['Display'] == proyecto_elegido].iloc[0]
            
            url_val = str(row_proj[col_url]).strip() if col_url and pd.notna(row_proj[col_url]) else ""
            url_html = f'<p style="margin-top: 8px;">🔗 <b>Enlace al Proyecto:</b> <a href="{url_val}" target="_blank">{url_val}</a></p>' if url_val and url_val.lower().startswith('http') else ""
            
            st.markdown(f"""
            <div class="project-card">
                <h4>{row_proj[col_proyecto]}</h4>
                <p><b>ID:</b> {row_proj[col_id]} | <b>Escuela:</b> {row_proj[col_escuela]}</p>
                {url_html}
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
                
                with st.spinner("Guardando y actualizando ranking..."):
                    try:
                        headers = {"Content-Type": "application/json"}
                        res = requests.post(URL_APPS_SCRIPT, data=json.dumps(datos_eval), headers=headers, timeout=12)
                        if "OK" in res.text:
                            st.success("🎉 ¡Evaluación guardada exitosamente y ranking actualizado!")
                            st.balloons()
                        else:
                            st.error(f"Error al enviar datos: {res.text}")
                    except Exception as err:
                        st.error(f"Error de conexión: {err}")

# --- TAB 2: RANKING OFICIAL ---
with tab_ranking:
    st.subheader("🏆 Ranking Oficial de Proyectos")
    if st.button("🔄 Actualizar Tabla de Ranking"):
        st.rerun()
        
    try:
        df_ranking = pd.read_csv(URL_RANKING)
        df_ranking.columns = df_ranking.columns.str.strip()
        if len(df_ranking) > 0:
            st.dataframe(df_ranking, use_container_width=True, hide_index=True)
        else:
            st.info("Aún no se han generado posiciones en el ranking.")
    except Exception as e:
        st.warning("El ranking oficial aún se está procesando o la solapa está vacía.")

# --- TAB 3: EVALUACIONES CARGADAS Y ADMIN ---
with tab_historial:
    st.subheader("📋 Consultar Evaluaciones")
    try:
        df_eval = pd.read_csv(URL_EVALUACIONES)
        df_eval.columns = df_eval.columns.str.strip()
        
        eval_usuario = st.selectbox("Selecciona un Evaluador para filtrar:", ["-- Seleccionar --"] + evaluadores_unicos, key="hist_eval")
        if eval_usuario != "-- Seleccionar --":
            col_eval_name = next((c for c in df_eval.columns if 'evaluador' in c.lower()), df_eval.columns[2])
            df_mis_eval = df_eval[df_eval[col_eval_name].astype(str).str.contains(eval_usuario, case=False, na=False)]
            
            if len(df_mis_eval) > 0:
                st.write(f"Registros de **{eval_usuario}** ({len(df_mis_eval)}):")
                st.dataframe(df_mis_eval, use_container_width=True, hide_index=True)
            else:
                st.info(f"No hay registros asignados a {eval_usuario}.")
                
        st.markdown("---")
        st.subheader("🔐 Zona de Administración")
        codigo_admin = st.text_input("Ingresa la clave ADMIN para eliminar registros:", type="password")
        
        if codigo_admin.strip() == "ADMIN":
            st.success("Acceso Administrador concedido.")
            st.dataframe(df_eval, use_container_width=True, hide_index=True)
            
            col_id_eval = df_eval.columns[0]
            ids_disponibles = df_eval[col_id_eval].dropna().astype(str).tolist()
            
            if ids_disponibles:
                id_a_borrar = st.selectbox("🗑️ Selecciona el ID_Evaluación a borrar:", ["-- Seleccionar ID --"] + ids_disponibles)
                
                if id_a_borrar != "-- Seleccionar ID --":
                    if st.button("❌ Confirmar Eliminación en Excel", type="primary"):
                        payload_delete = {"accion": "eliminar", "ID_Evaluacion": id_a_borrar}
                        with st.spinner("Eliminando fila en Google Sheets..."):
                            try:
                                headers = {"Content-Type": "application/json"}
                                res = requests.post(URL_APPS_SCRIPT, data=json.dumps(payload_delete), headers=headers, timeout=12)
                                if "OK_ELIMINADO" in res.text:
                                    st.success(f"🎉 Evaluación ID '{id_a_borrar}' eliminada del Excel.")
                                    st.rerun()
                                else:
                                    st.error(f"Error al eliminar: {res.text}")
                            except Exception as err:
                                st.error(f"Error de conexión: {err}")
        elif codigo_admin != "":
            st.error("Código incorrecto.")
            
    except Exception as e:
        st.warning("No se pudieron cargar las evaluaciones registradas.")

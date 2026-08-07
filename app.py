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
    .project-card a { color: #1976D2; font-weight: bold; text-decoration: underline; }
    </style>
""", unsafe_allow_html=True)

st.title("📋 Evaluación Expotécnica")

# Conexión con Google Sheets y Google Apps Script
SPREADSHEET_ID = "1KWw1ybOAuxxBk4P3gVoqp90UXx2pBaa9ccAiiV8Rd-w"
URL_PROYECTOS = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=PROYECTOS"
URL_EVALUACIONES = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet=EVALUACIÓN"
URL_APPS_SCRIPT = "https://script.google.com/macros/s/AKfycbzNSmDLQmrfRK-BRAB-ujmp2WEqbmCnz2f4EPDOLL2AS12XM0-GTQxki7QjOoyGm1Z0/exec"

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

# Buscar columna para la URL / Link / Enlace
col_url = next((c for c in df_proyectos.columns if any(k in c.lower() for k in ['url', 'link', 'enlace', 'drive', 'video'])), None)

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
        
        # Extraer enlace si existe en la fila
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

    # --- SECCIÓN: VER Y ADMINISTRAR EVALUACIONES CARGADAS ---
    st.markdown("---")
    with st.expander("📋 Ver Evaluaciones Ya Cargadas"):
        try:
            df_eval = pd.read_csv(URL_EVALUACIONES)
            df_eval.columns = df_eval.columns.str.strip()
            
            # Filtrar por el evaluador seleccionado
            col_eval_name = next((c for c in df_eval.columns if 'evaluador' in c.lower()), df_eval.columns[2])
            df_mis_eval = df_eval[df_eval[col_eval_name].astype(str).str.contains(evaluador_seleccionado, case=False, na=False)]
            
            if len(df_mis_eval) > 0:
                st.write(f"Has registrado **{len(df_mis_eval)} evaluaciones**:")
                st.dataframe(df_mis_eval, use_container_width=True)
            else:
                st.info("Aún no has registrado ninguna evaluación.")
                
            # --- MODO ADMINISTRADOR (CLAVE "ADMIN") ---
            st.markdown("---")
            st.subheader("🔐 Zona de Administración")
            codigo_admin = st.text_input("Ingresa el código ADMIN para gestionar o borrar registros:", type="password")
            
            if codigo_admin.strip() == "ADMIN":
                st.success("Acceso Administrador concedido.")
                st.write("### Carga completa de la solapa EVALUACIÓN:")
                st.dataframe(df_eval, use_container_width=True)
                
                col_id_eval = df_eval.columns[0] # ID_Evaluacion
                ids_disponibles = df_eval[col_id_eval].dropna().astype(str).tolist()
                
                if ids_disponibles:
                    id_a_borrar = st.selectbox("🗑️ Selecciona el ID_Evaluación a eliminar:", ["-- Seleccionar ID --"] + ids_disponibles)
                    
                    if id_a_borrar != "-- Seleccionar ID --":
                        if st.button("❌ Confirmar Eliminación en Excel", type="primary"):
                            payload_delete = {
                                "accion": "eliminar",
                                "ID_Evaluacion": id_a_borrar
                            }
                            with st.spinner("Eliminando fila en Google Sheets..."):
                                try:
                                    headers = {"Content-Type": "application/json"}
                                    res = requests.post(URL_APPS_SCRIPT, data=json.dumps(payload_delete), headers=headers, timeout=10)
                                    if "OK_ELIMINADO" in res.text:
                                        st.success(f"🎉 Evaluación ID '{id_a_borrar}' eliminada correctamente del Excel.")
                                        st.rerun()
                                    else:
                                        st.error(f"Error al eliminar: {res.text}")
                                except Exception as err:
                                    st.error(f"Error de conexión: {err}")
            elif codigo_admin != "":
                st.error("Código incorrecto.")
                
        except Exception as e:
            st.warning("No se pudieron cargar las evaluaciones registradas o la tabla aún está vacía.")

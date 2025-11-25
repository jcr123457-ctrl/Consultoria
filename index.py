import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib
# Configurar matplotlib para que no use interfaz gráfica
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from datetime import datetime
from fpdf import FPDF
import io
import tempfile
import os
import time
import json
import base64

# --- Configuración de Página ---
st.set_page_config(page_title="Consultoría Pro", page_icon="💎", layout="wide")

# --- Constantes y Persistencia ---
DB_FILE = "financial_db.json"

def load_data():
    """Carga la base de datos desde un archivo JSON local."""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for record in data:
                    if 'PDF_Bytes' in record and record['PDF_Bytes']:
                        record['PDF_Bytes'] = base64.b64decode(record['PDF_Bytes'])
                return data
        except Exception as e:
            st.error(f"Error cargando base de datos: {e}")
            return []
    return []

def save_data(data):
    """Guarda la base de datos en un archivo JSON local."""
    try:
        data_to_save = []
        for record in data:
            new_record = record.copy()
            if 'PDF_Bytes' in new_record and isinstance(new_record['PDF_Bytes'], bytes):
                new_record['PDF_Bytes'] = base64.b64encode(new_record['PDF_Bytes']).decode('utf-8')
            data_to_save.append(new_record)
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=4)
    except Exception as e:
        st.error(f"Error guardando datos: {e}")

# --- Inicialización de Estado ---
if 'transacciones' not in st.session_state:
    st.session_state.transacciones = []
if 'deudas' not in st.session_state:
    st.session_state.deudas = []
if 'historial_db' not in st.session_state:
    st.session_state.historial_db = load_data()

# Inicialización de seguridad para evitar AttributeError
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Datos Cliente
if 'cliente' not in st.session_state:
    st.session_state.cliente = ""
if 'ocupacion' not in st.session_state:
    st.session_state.ocupacion = ""
if 'telefono' not in st.session_state:
    st.session_state.telefono = ""
if 'email' not in st.session_state:
    st.session_state.email = ""
if 'edad' not in st.session_state:
    st.session_state.edad = 18
if 'sexo' not in st.session_state:
    st.session_state.sexo = "No especificar"

if 'editando_id' not in st.session_state:
    st.session_state.editando_id = None

# --- DEFINICIÓN DE PALETA DE COLORES (TEMA CLARO APPLE PRO) ---
# Fondos
bg_color = "#F5F5F7" # Gris Sistema Apple (Fondo)
card_bg = "#FFFFFF"  # Blanco Puro (Tarjetas)
input_bg = "#FFFFFF"
input_border = "transparent" 

# Textos
text_color = "#1D1D1F" # Casi Negro
input_text = "#000000"

# Colores Financieros
color_ingreso = "#007AFF" # Azul Apple
color_gasto = "#5AC8FA"   # Cyan/Azul Claro Apple
color_balance = "#007AFF"
color_proyeccion = "#0040DD" # Azul Oscuro para Proyecciones

shadow_style = "0 8px 24px rgba(0, 0, 0, 0.05)"

# --- INYECCIÓN CSS (Estilo Apple Pro 2.0 - Corregido y Reforzado) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Estilo Global de la App */
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
        font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }}
    
    /* Tarjetas Apple */
    .metric-card, div[data-testid="stExpander"] {{
        background-color: {card_bg} !important;
        border-radius: 20px !important;
        padding: 24px;
        box-shadow: {shadow_style};
        border: none !important;
        color: {text_color} !important;
        transition: transform 0.2s ease;
    }}
    
    /* Inputs */
    div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="select"] {{
        background-color: {input_bg} !important;
        border: none !important;
        border-radius: 12px !important;
        color: {input_text} !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }}
    
    input, textarea, select, div[data-baseweb="select"] div {{
        color: {input_text} !important;
        font-weight: 500 !important;
        font-size: 16px !important; 
    }}

    /* Encabezados */
    h1, h2, h3, h4, h5, h6 {{
        color: {text_color} !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }}
    p, label, .stMarkdown {{
        color: {text_color} !important;
    }}

    /* --- BOTONES (FIX: Forzar Azul en Botones Primarios) --- */
    
    /* Botones normales */
    .stButton button {{
        border-radius: 30px !important;
        font-weight: 600;
        border: none;
        padding: 0.6rem 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: all 0.2s;
    }}

    /* Selector MUY específico para el botón Primario (Agregar/Actualizar) */
    button[kind="primary"], 
    button[kind="primaryFormSubmit"],
    div[data-testid="stForm"] button[kind="primary"] {{
        background-color: #007AFF !important; /* Azul Apple */
        color: white !important;
        border: 1px solid #007AFF !important;
    }}
    
    button[kind="primary"]:hover,
    button[kind="primaryFormSubmit"]:hover {{
        background-color: #0051A8 !important; /* Azul más oscuro al pasar el mouse */
        border-color: #0051A8 !important;
        transform: scale(1.02);
    }}
    
    /* Botones secundarios (Cancelar, Eliminar, etc.) */
    button[kind="secondary"] {{
        background-color: white !important;
        color: {text_color} !important;
        border: 1px solid #E5E5EA !important;
    }}

    /* --- LIMPIEZA DE PESTAÑAS --- */
    div[data-baseweb="tab-list"] {{
        gap: 20px;
        border-bottom: none !important; 
        padding-bottom: 10px;
    }}
    div[data-baseweb="tab-highlight"] {{
        display: none !important; 
    }}
    
    /* Estilo Pestañas */
    button[data-baseweb="tab"] {{
        background-color: {card_bg} !important;
        color: {text_color} !important;
        border-radius: 15px !important;
        font-weight: 600;
        border: none !important;
        box-shadow: {shadow_style};
        opacity: 0.7;
        transition: all 0.2s;
        margin: 0 2px;
    }}
    
    button[data-baseweb="tab"][aria-selected="true"] {{
        opacity: 1;
        transform: scale(1.03);
        color: {color_ingreso} !important; 
        box-shadow: 0 6px 20px rgba(0,122,255, 0.25);
    }}

    @media (min-width: 1024px) {{
        button[data-baseweb="tab"] {{
            font-size: 18px !important;
            padding: 15px 40px !important;
            min-width: 160px;
        }}
    }}
    
    /* --- BOTONES DE SELECCIÓN (RADIO) CORREGIDOS Y VISIBLES --- */
    /* Contenedor general */
    div[role="radiogroup"] {{
        background: transparent !important;
        box-shadow: none !important;
        gap: 15px !important;
        display: flex !important;
        border: none !important;
    }}
    
    /* Estilo base de cada opción (Ingreso/Gasto) */
    div[role="radiogroup"] label {{
        background-color: white !important;
        border: 1px solid #E5E5EA !important;
        border-radius: 16px !important;
        padding: 15px !important;
        text-align: center !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        transition: all 0.2s ease !important;
        flex: 1; /* Ocupar espacio igual */
        margin: 0 !important;
        display: flex;
        justify-content: center;
        align-items: center;
        cursor: pointer;
    }}
    
    /* Asegurar que el texto se vea (Color Negro por defecto) */
    div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {{
        color: #1D1D1F !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        margin: 0 !important;
    }}
    
    /* Ocultar el círculo por defecto de Streamlit */
    div[role="radiogroup"] label div:first-child {{
        display: none !important;
    }}

    /* --- ESTADOS SELECCIONADOS (Con Texto Blanco) --- */
    
    /* Cuando INGRESO (primer hijo) está seleccionado */
    div[role="radiogroup"] label:first-child:has(input:checked) {{
        background: linear-gradient(135deg, #007AFF 0%, #0051A8 100%) !important;
        border: none !important;
        box-shadow: 0 8px 20px rgba(0, 122, 255, 0.4) !important;
        transform: translateY(-2px);
    }}
    /* Texto blanco para Ingreso seleccionado */
    div[role="radiogroup"] label:first-child:has(input:checked) div[data-testid="stMarkdownContainer"] p {{
        color: white !important;
    }}

    /* Cuando GASTO (segundo hijo) está seleccionado */
    div[role="radiogroup"] label:nth-child(2):has(input:checked) {{
        background: linear-gradient(135deg, #5AC8FA 0%, #2D9CDB 100%) !important;
        border: none !important;
        box-shadow: 0 8px 20px rgba(90, 200, 250, 0.4) !important;
        transform: translateY(-2px);
    }}
    /* Texto blanco para Gasto seleccionado */
    div[role="radiogroup"] label:nth-child(2):has(input:checked) div[data-testid="stMarkdownContainer"] p {{
        color: white !important;
    }}

    </style>
""", unsafe_allow_html=True)

# --- Funciones Auxiliares ---

def format_money(amount):
    return f"${amount:,.2f}"

def format_years(meses):
    years = meses / 12
    if meses < 12:
        return f"{meses} Meses"
    elif meses % 12 == 0:
        return f"{int(years)} Años"
    else:
        return f"{meses} Meses ({years:.1f} Años)"

def get_balance():
    if not st.session_state.transacciones:
        return 0, 0, 0
    df = pd.DataFrame(st.session_state.transacciones)
    if df.empty:
        return 0, 0, 0
    
    ingresos = df[df['tipo'] == 'Ingreso']['monto'].sum()
    gastos = df[df['tipo'] == 'Gasto']['monto'].sum()
    return ingresos, gastos, ingresos - gastos

def clear_form_data():
    st.session_state.cliente = ""
    st.session_state.ocupacion = ""
    st.session_state.telefono = ""
    st.session_state.email = ""
    st.session_state.edad = 18
    st.session_state.sexo = "No especificar"
    st.session_state.transacciones = []
    st.session_state.deudas = []
    st.session_state.editando_id = None

# --- Lógica Excel ---
def generate_complex_excel(data):
    output = io.BytesIO()
    df_all = pd.DataFrame(data)
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if not df_all.empty:
            df_unique_clients = df_all.sort_values('id').groupby('Cliente').last().reset_index()
            cols_resumen = ['Cliente', 'Ocupacion', 'Telefono', 'Email', 'Edad', 'Sexo']
            cols_resumen = [c for c in cols_resumen if c in df_unique_clients.columns]
            df_resumen = df_unique_clients[cols_resumen]
            df_resumen.to_excel(writer, sheet_name='Resumen Clientes', index=False)
            worksheet = writer.sheets['Resumen Clientes']
            for idx, col in enumerate(df_resumen.columns):
                worksheet.column_dimensions[chr(65 + idx)].width = 20
        unique_clients = df_all['Cliente'].unique()
        for client_name in unique_clients:
            client_data = df_all[df_all['Cliente'] == client_name]
            sheet_name = str(client_name)[:30].replace(":", "").replace("/", "").replace("?", "").replace("*", "")
            if not sheet_name: sheet_name = "Cliente"
            last_record = client_data.iloc[-1]
            personal_info = {
                'Dato': ['Cliente', 'Ocupación', 'Teléfono', 'Email', 'Edad', 'Sexo'],
                'Valor': [last_record.get('Cliente', ''), last_record.get('Ocupacion', ''), last_record.get('Telefono', ''), last_record.get('Email', ''), last_record.get('Edad', ''), last_record.get('Sexo', '')]
            }
            df_personal = pd.DataFrame(personal_info)
            financial_cols = ['Periodo', 'Mes', 'Año', 'Ingresos', 'Egresos', 'Balance']
            if 'Ahorro_Proyectado' in client_data.columns:
                financial_cols.append('Ahorro_Proyectado')
            valid_cols = [c for c in financial_cols if c in client_data.columns]
            df_financial = client_data[valid_cols].copy()
            df_personal.to_excel(writer, sheet_name=sheet_name, startrow=1, startcol=1, index=False)
            start_row_financial = len(df_personal) + 4
            writer.sheets[sheet_name].cell(row=start_row_financial, column=2).value = "Historial Financiero"
            df_financial.to_excel(writer, sheet_name=sheet_name, startrow=start_row_financial, startcol=1, index=False)
    return output.getvalue()

# --- Lógica PDF ---
class PDFReport(FPDF):
    def header(self):
        self.set_fill_color(0, 122, 255) # Azul Apple
        self.rect(0, 0, 210, 25, 'F')
        self.set_font('Arial', 'B', 18)
        self.set_text_color(255, 255, 255)
        self.set_y(8)
        self.cell(0, 10, 'Reporte Financiero Profesional', 0, 0, 'C')
        self.ln(25) 
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')
    def chapter_title(self, label, color_rgb):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(color_rgb[0], color_rgb[1], color_rgb[2])
        self.set_text_color(255, 255, 255)
        self.cell(0, 8, f"  {label}", 0, 1, 'L', 1)
        self.ln(4)
        self.set_text_color(0, 0, 0)

def create_pro_pdf(report_type, extra_data=None):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    cliente_nombre = extra_data.get('cliente_snap') if extra_data and 'cliente_snap' in extra_data else st.session_state.cliente
    ocupacion_nombre = extra_data.get('ocupacion_snap') if extra_data and 'ocupacion_snap' in extra_data else st.session_state.ocupacion
    fecha_reporte = extra_data.get('fecha_snap') if extra_data and 'fecha_snap' in extra_data else datetime.now().strftime('%d/%m/%Y')
    
    pdf.set_fill_color(242, 242, 247)
    pdf.rect(10, 30, 190, 25, 'F')
    pdf.set_y(32)
    pdf.set_x(15)
    pdf.set_font("Arial", 'B', 10)
    pdf.set_text_color(28, 28, 30)
    pdf.cell(90, 6, f"CLIENTE: {cliente_nombre.upper() or 'NO REGISTRADO'}", 0, 0)
    pdf.cell(90, 6, f"FECHA: {fecha_reporte}", 0, 1, 'R')
    pdf.set_x(15)
    pdf.cell(90, 6, f"OCUPACIÓN: {ocupacion_nombre.upper() or 'N/A'}", 0, 1)
    pdf.ln(12)

    if extra_data and 'ingresos_snap' in extra_data:
        ingresos = extra_data['ingresos_snap']
        gastos = extra_data['gastos_snap']
        balance = extra_data['balance_snap']
        transacciones_data = [] 
    else:
        ingresos, gastos, balance = get_balance()
        transacciones_data = st.session_state.transacciones

    if report_type == "analisis":
        y_start = pdf.get_y()
        def draw_kpi(x, title, amount, color_top, bg_color):
            pdf.set_fill_color(bg_color[0], bg_color[1], bg_color[2])
            pdf.rect(x, y_start, 60, 20, 'F')
            pdf.set_fill_color(color_top[0], color_top[1], color_top[2])
            pdf.rect(x, y_start, 60, 1, 'F')
            pdf.set_xy(x, y_start + 4)
            pdf.set_font("Arial", 'B', 8)
            pdf.set_text_color(color_top[0], color_top[1], color_top[2])
            pdf.cell(60, 4, title, 0, 2, 'C')
            pdf.set_font("Arial", 'B', 12)
            pdf.set_text_color(28, 28, 30)
            pdf.cell(60, 6, amount, 0, 0, 'C')

        draw_kpi(12, "TOTAL INGRESOS", format_money(ingresos), (0, 122, 255), (230, 242, 255))
        draw_kpi(75, "TOTAL EGRESOS", format_money(gastos), (90, 200, 250), (230, 250, 255))
        draw_kpi(138, "BALANCE FINAL", format_money(balance), (0, 122, 255), (242, 242, 247))
        pdf.ln(28)

        if ingresos > 0 or gastos > 0:
            fig, ax = plt.subplots(figsize=(7, 4))
            labels = ['Ingresos', 'Egresos']
            sizes = [ingresos, gastos]
            colors = ['#007AFF', '#5AC8FA']
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, textprops=dict(color="#1C1C1E", fontsize=10, weight='bold'), pctdistance=0.85)
            centre_circle = plt.Circle((0,0),0.65,fc='white')
            fig.gca().add_artist(centre_circle)
            plt.text(0, 0, "Balance", ha='center', va='bottom', fontsize=10, color='gray')
            plt.text(0, 0, f"\n{format_money(balance)}", ha='center', va='center', fontsize=12, fontweight='bold', color='#007AFF')
            ax.axis('equal')
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                plt.savefig(tmpfile.name, format='png', bbox_inches='tight', dpi=150, transparent=True)
                x_img = (210 - 120) / 2
                pdf.image(tmpfile.name, x=x_img, w=120)
                tmp_path = tmpfile.name
            plt.close(fig)
            os.remove(tmp_path)
        pdf.ln(5)

        if transacciones_data:
            df = pd.DataFrame(transacciones_data)
            def header_tabla(titulo, r, g, b):
                pdf.set_font('Arial', 'B', 11)
                pdf.set_fill_color(r, g, b)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(190, 8, f"  {titulo}", 0, 1, 'L', 1)
            def fila_tabla(concepto, monto, fill=False):
                pdf.set_fill_color(242, 242, 247)
                pdf.set_text_color(28, 28, 30)
                pdf.set_font('Arial', '', 10)
                pdf.cell(140, 7, f"  {concepto}", 'B', 0, 'L', fill)
                pdf.set_font('Arial', 'B', 10)
                pdf.cell(50, 7, f"{format_money(monto)}  ", 'B', 1, 'R', fill)

            if not df.empty:
                ingresos_list = df[df['tipo'] == 'Ingreso']
                if not ingresos_list.empty:
                    header_tabla("DETALLE DE INGRESOS", 0, 122, 255)
                    for idx, row in ingresos_list.iterrows():
                        fila_tabla(row['concepto'], row['monto'], idx % 2 != 0)
                    pdf.ln(5)
                gastos_list = df[df['tipo'] == 'Gasto']
                if not gastos_list.empty:
                    header_tabla("DETALLE DE EGRESOS", 90, 200, 250)
                    for idx, row in gastos_list.iterrows():
                        fila_tabla(row['concepto'], row['monto'], idx % 2 != 0)
    elif report_type == "proyeccion":
        pdf.chapter_title("PROYECCIÓN DE AHORRO", (0, 64, 221))
        ahorro = extra_data.get('ahorro', 0)
        meses = extra_data.get('meses', 0)
        total = extra_data.get('total', 0)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 8, f"Ahorro Mensual Base: {format_money(ahorro)}", ln=True)
        pdf.cell(0, 8, f"Tiempo Estimado: {format_years(meses)}", ln=True)
        pdf.ln(2)
        pdf.set_fill_color(230, 242, 255)
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(0, 64, 221)
        pdf.cell(0, 12, f"  Meta Total: {format_money(total)}", 0, 1, 'L', 1)
        pdf.ln(5)
        pdf.set_fill_color(0, 64, 221)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(95, 8, "Periodo", 0, 0, 'C', 1)
        pdf.cell(95, 8, "Capital Acumulado", 0, 1, 'C', 1)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", size=10)
        for i in range(1, meses + 1):
             if i == meses or i % 6 == 0: 
                fill = i % 12 == 0
                pdf.set_fill_color(242, 242, 247)
                pdf.cell(95, 7, f"Mes {i} ({format_years(i)})", 'B', 0, 'C', fill)
                pdf.cell(95, 7, format_money(ahorro * i), 'B', 1, 'C', fill)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- Layout Principal ---

st.title("Consultoría 2.0")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["➕ Registros", "📈 Análisis", "📝 Deudas", "🧮 Proyecciones", "🗄️ Base de Datos"])

# --- TAB 1: REGISTROS ---
with tab1:
    with st.container():
        st.markdown("#### 👤 Perfil del Cliente")
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.cliente = st.text_input("Nombre Completo", value=st.session_state.cliente, placeholder="Ej. Juan Pérez")
        with c2:
            st.session_state.ocupacion = st.text_input("Ocupación", value=st.session_state.ocupacion, placeholder="Ej. Arquitecto")

        with st.expander("🔒 Datos Privados"):
            st.markdown("<div class='private-data'>Estos datos <b>NO</b> aparecerán en los reportes PDF.</div>", unsafe_allow_html=True)
            pc1, pc2, pc3, pc4 = st.columns(4)
            with pc1:
                st.session_state.telefono = st.text_input("Teléfono", value=st.session_state.telefono)
            with pc2:
                st.session_state.email = st.text_input("Correo", value=st.session_state.email)
            with pc3:
                st.session_state.edad = st.number_input("Edad", min_value=1, max_value=120, value=st.session_state.edad, step=1)
            with pc4:
                st.session_state.sexo = st.selectbox("Sexo", ["Masculino", "Femenino", "No especificar"], index=["Masculino", "Femenino", "No especificar"].index(st.session_state.sexo))

        ingresos, gastos, balance = get_balance()
        
        balance_color = color_ingreso if balance >= 0 else "#FF3B30"
        
        st.markdown(f"""
        <div style="margin-top:10px; padding:20px; background-color:{card_bg}; border-radius:20px; text-align:right; box-shadow:{shadow_style}; border: 1px solid {input_border};">
            <span style='color:{text_color}; font-size:0.9em; text-transform:uppercase; letter-spacing:1px; font-weight:600;'>Balance Total</span><br>
            <span style='color:{balance_color}; font-weight:800; font-size:2.5em;'>{format_money(balance)}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    col_left, col_right = st.columns([4, 3])
    
    with col_left:
        # Lógica de Edición
        if st.session_state.editando_id:
            tx_edit = next((t for t in st.session_state.transacciones if t['id'] == st.session_state.editando_id), None)
            if tx_edit:
                header_text = '✏️ Editando Movimiento'
                default_type_idx = 0 if tx_edit['tipo'] == "Ingreso" else 1
                default_monto = tx_edit['monto']
                default_concepto = tx_edit['concepto']
            else:
                st.session_state.editando_id = None
                st.rerun()
        else:
            header_text = '✨ Nuevo Movimiento'
            default_type_idx = 0
            default_monto = None
            default_concepto = ""
            
        st.markdown(f"**{header_text}**")
        
        with st.form(key="registro_form", clear_on_submit=True):
            fc_tipo, fc_monto = st.columns([1, 1])
            with fc_tipo:
                # Radio Buttons personalizados
                tipos = ["Ingreso", "Gasto"]
                if st.session_state.editando_id and tx_edit:
                    idx = tipos.index(tx_edit['tipo'])
                else:
                    idx = 0
                tipo_sel = st.radio("Tipo", tipos, index=idx, horizontal=True, label_visibility="collapsed")
                
            with fc_monto:
                val_monto = tx_edit['monto'] if (st.session_state.editando_id and tx_edit) else None
                monto = st.number_input("Monto", min_value=0.0, step=100.0, value=val_monto, label_visibility="collapsed", placeholder="$0.00")

            val_concepto = tx_edit['concepto'] if (st.session_state.editando_id and tx_edit) else ""
            concepto = st.text_input("Concepto", value=val_concepto, placeholder="Ej. Nómina, Renta...", label_visibility="collapsed")
            
            fb1, fb2 = st.columns([1, 2])
            with fb1:
                btn_label = "Actualizar" if st.session_state.editando_id else "Agregar"
                submit_btn = st.form_submit_button(btn_label, type="primary", use_container_width=True)
            with fb2:
                if st.session_state.editando_id:
                     if st.form_submit_button("Cancelar"):
                         st.session_state.editando_id = None
                         st.rerun()

            if submit_btn:
                if concepto and monto is not None and monto > 0:
                    if st.session_state.editando_id:
                        for t in st.session_state.transacciones:
                            if t['id'] == st.session_state.editando_id:
                                t.update({'concepto': concepto, 'monto': monto, 'tipo': tipo_sel})
                        st.session_state.editando_id = None
                        st.success("¡Actualizado!")
                        st.rerun()
                    else:
                        st.session_state.transacciones.append({
                            "id": int(datetime.now().timestamp() * 1000),
                            "fecha": datetime.now().strftime("%Y-%m-%d"),
                            "concepto": concepto,
                            "monto": monto,
                            "tipo": tipo_sel
                        })
                        st.success("¡Agregado!")
                        st.rerun()

        st.markdown("### 📋 Movimientos")
        if not st.session_state.transacciones:
            st.info("Sin registros.")
        else:
            for t in reversed(st.session_state.transacciones):
                # CORRECCIÓN: Usar el borde definido sin depender de dark_mode que fue eliminado
                c_stripe = color_ingreso if t['tipo'] == "Ingreso" else color_gasto
                row_bg = "#FFFFFF"

                with st.container():
                    st.markdown(f"""
                    <div style="
                        background-color:{row_bg}; 
                        border-left: 6px solid {c_stripe}; 
                        padding: 16px; 
                        border-radius: 12px; 
                        margin-bottom: 12px; 
                        box-shadow: {shadow_style};
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    ">
                        <div>
                            <div style="font-weight:600; font-size:1.1em; color:{text_color}">{t['concepto']}</div>
                            <div style="color:{c_stripe}; font-weight:bold; font-size:0.9em">{t['tipo']}</div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-weight:bold; font-size:1.2em; color:{text_color}">{format_money(t['monto'])}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_edit, col_del, col_void = st.columns([1, 1, 3])
                    with col_edit:
                        if st.button("✏️ Editar", key=f"edit_{t['id']}", use_container_width=True):
                            st.session_state.editando_id = t['id']
                            st.rerun()
                    with col_del:
                        if st.button("🗑️ Borrar", key=f"del_{t['id']}", use_container_width=True):
                            st.session_state.transacciones = [x for x in st.session_state.transacciones if x['id'] != t['id']]
                            if st.session_state.editando_id == t['id']:
                                st.session_state.editando_id = None
                            st.rerun()

    with col_right:
        st.markdown("**Distribución**")
        if ingresos > 0 or gastos > 0:
            fig = px.pie(names=['Ingresos', 'Egresos'], values=[ingresos, gastos], 
                         color=['Ingresos', 'Egresos'],
                         color_discrete_map={'Ingresos': color_ingreso, 'Egresos': color_gasto},
                         hole=0.6)
            
            fig.update_layout(
                showlegend=False, 
                margin=dict(t=0,b=0,l=0,r=0), 
                height=250, 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                font=dict(color=text_color)
            )
            fig.add_annotation(
                text=format_money(balance), 
                x=0.5, y=0.5, 
                font_size=16, 
                showarrow=False, 
                font_weight="bold", 
                font=dict(color=text_color)
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.caption("Agrega datos para ver la gráfica.")

# --- TAB 2: ANÁLISIS ---
with tab2:
    ingresos, gastos, balance = get_balance()
    
    col_k1, col_k2, col_k3 = st.columns(3)
    col_k1.markdown(f"""<div class="metric-card" style="border-top: 5px solid {color_ingreso};"><div style="color:{color_ingreso}; font-weight:bold;">INGRESOS</div><div style="font-size:1.5rem; font-weight:bold;">{format_money(ingresos)}</div></div>""", unsafe_allow_html=True)
    col_k2.markdown(f"""<div class="metric-card" style="border-top: 5px solid {color_gasto};"><div style="color:{color_gasto}; font-weight:bold;">EGRESOS</div><div style="font-size:1.5rem; font-weight:bold;">{format_money(gastos)}</div></div>""", unsafe_allow_html=True)
    col_k3.markdown(f"""<div class="metric-card" style="border-top: 5px solid {color_balance};"><div style="color:{text_color}; font-weight:bold;">BALANCE</div><div style="font-size:1.5rem; font-weight:bold;">{format_money(balance)}</div></div>""", unsafe_allow_html=True)
    
    st.write("")
    if st.session_state.transacciones:
        c_chart, c_details = st.columns([1, 1])
        with c_chart:
            st.subheader("Visualización")
            fig_analisis = px.pie(names=['Ingresos', 'Egresos'], values=[ingresos, gastos], 
                                  color=['Ingresos', 'Egresos'], 
                                  color_discrete_map={'Ingresos': color_ingreso, 'Egresos': color_gasto}, 
                                  hole=0.5)
            
            fig_analisis.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                font=dict(color=text_color)
            )
            st.plotly_chart(fig_analisis, use_container_width=True)
        with c_details:
            st.subheader("Detalles")
            tab_in, tab_out = st.tabs(["Ingresos", "Egresos"])
            df = pd.DataFrame(st.session_state.transacciones)
            with tab_in:
                st.markdown(f"<h4 style='color:{color_ingreso}'>Viendo: INGRESOS</h4>", unsafe_allow_html=True)
                st.dataframe(df[df['tipo']=='Ingreso'][['concepto', 'monto']], use_container_width=True, hide_index=True)
            with tab_out:
                st.markdown(f"<h4 style='color:{color_gasto}'>Viendo: EGRESOS</h4>", unsafe_allow_html=True)
                st.dataframe(df[df['tipo']=='Gasto'][['concepto', 'monto']], use_container_width=True, hide_index=True)
        st.markdown("---")
        col_space, col_btn = st.columns([3, 1])
        with col_btn:
            pdf_bytes = create_pro_pdf("analisis")
            st.download_button("📄 Descargar PDF Pro", pdf_bytes, f"Reporte_{st.session_state.cliente}.pdf", "application/pdf", type="primary", use_container_width=True)

# --- TAB 3: DEUDAS ---
with tab3:
    st.markdown("### 📝 Control de Deudas")
    with st.container():
        dc1, dc2, dc3, dc4 = st.columns([3, 2, 2, 1])
        with dc1: n_acreedor = st.text_input("Acreedor", placeholder="Banco...", label_visibility="collapsed")
        with dc2: n_monto = st.number_input("Monto Deuda", min_value=0.0, label_visibility="collapsed")
        with dc3: n_tasa = st.number_input("Interés %", min_value=0.0, label_visibility="collapsed")
        with dc4:
            if st.button("➕", use_container_width=True):
                if n_acreedor and n_monto:
                    st.session_state.deudas.append({"id": int(datetime.now().timestamp()*1000), "acreedor": n_acreedor, "monto": n_monto, "tasa": n_tasa})
                    st.rerun()
    if st.session_state.deudas:
        st.write("")
        for d in st.session_state.deudas:
            st.markdown(f"""<div style="background:{card_bg}; padding:15px; border-radius:15px; border:1px solid {input_border}; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center; color:{text_color}; box-shadow:{shadow_style};"><div><div style="font-weight:bold;">{d['acreedor']}</div><div style="font-size:0.8rem; color:{color_gasto};">Tasa: {d['tasa']}%</div></div><div style="font-weight:bold; color:{color_gasto};">{format_money(d['monto'])}</div></div>""", unsafe_allow_html=True)
            if st.button("Eliminar", key=f"dd_{d['id']}"):
                st.session_state.deudas = [x for x in st.session_state.deudas if x['id'] != d['id']]
                st.rerun()

# --- TAB 4: PROYECCIONES ---
with tab4:
    st.markdown("### 🧮 Calculadora de Ahorro")
    col_calc, col_graph = st.columns([1, 2])
    with col_calc:
        ahorro_mes = st.number_input("Ahorro Mensual ($)", min_value=0.0, value=None, step=100.0, placeholder="0.00")
        meses_input = st.slider("Periodo (Meses)", 1, 60, 12)
        st.caption(f"📅 Equivalente a: **{format_years(meses_input)}**")
        
        ahorro_val = ahorro_mes if ahorro_mes is not None else 0.0
        total_proy = ahorro_val * meses_input
        
        st.markdown(f"""<div style="background: linear-gradient(135deg, {color_proyeccion} 0%, #007AFF 100%); padding:25px; border-radius:20px; color:white; text-align:center; margin-top:20px; box-shadow:{shadow_style};"><div style="font-size:0.9rem; opacity:0.9; letter-spacing:1px;">CAPITAL ACUMULADO</div><div style="font-size:2.2rem; font-weight:800;">{format_money(total_proy)}</div><div style="font-size:0.9rem;">en {format_years(meses_input)}</div></div>""", unsafe_allow_html=True)
        st.write("")
        pdf_proj = create_pro_pdf("proyeccion", {"ahorro": ahorro_val, "meses": meses_input, "total": total_proy})
        st.download_button("⬇️ PDF Proyección", pdf_proj, "Proyeccion_Ahorro.pdf", "application/pdf", use_container_width=True)
    with col_graph:
        if ahorro_val > 0:
            data_p = [{"Mes": m, "Total": ahorro_val * m} for m in range(1, meses_input + 1)]
            df_p = pd.DataFrame(data_p)
            
            # --- PROJECTION: DARK BLUE ---
            fig_p = px.area(df_p, x="Mes", y="Total", title="Crecimiento del Capital", color_discrete_sequence=[color_proyeccion])
            
            fig_p.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                font=dict(color=text_color)
            )
            st.plotly_chart(fig_p, use_container_width=True)

# --- TAB 5: BASE DE DATOS ---
with tab5:
    st.header("🗄️ Historial y Clientes")
    
    with st.container():
        st.markdown("#### 💾 Guardar Corte de Mes")
        current_ing, current_gas, current_bal = get_balance()
        
        if not st.session_state.cliente:
             st.warning("⚠️ Debes ingresar un nombre de cliente en la pestaña 'Registros' antes de guardar.")
        else:
             col_db1, col_db2, col_db3 = st.columns([2, 2, 1])
             with col_db1:
                 mes_cierre = st.selectbox("Mes de Corte", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"], index=datetime.now().month - 1)
             with col_db2:
                 anio_cierre = st.number_input("Año", min_value=2020, max_value=2030, value=datetime.now().year, step=1)
             with col_db3:
                 st.write("")
                 st.write("")
                 if st.button("Guardar Historial", type="primary", use_container_width=True):
                     pdf_actual_bytes = create_pro_pdf("analisis")
                     ahorro_actual = ahorro_mes if 'ahorro_mes' in locals() and ahorro_mes else 0.0
                     
                     nuevo_registro = {
                         "id": int(datetime.now().timestamp() * 1000),
                         "Cliente": st.session_state.cliente,
                         "Ocupacion": st.session_state.ocupacion,
                         "Telefono": st.session_state.telefono,
                         "Email": st.session_state.email,
                         "Edad": st.session_state.edad,
                         "Sexo": st.session_state.sexo,
                         "Fecha": datetime.now().strftime("%Y-%m-%d"),
                         "Periodo": f"{mes_cierre} {anio_cierre}",
                         "Mes": mes_cierre,
                         "Año": anio_cierre,
                         "Ingresos": current_ing,
                         "Egresos": current_gas,
                         "Balance": current_bal,
                         "Ahorro_Proyectado": float(ahorro_actual),
                         "PDF_Bytes": pdf_actual_bytes
                     }
                     st.session_state.historial_db.append(nuevo_registro)
                     
                     save_data(st.session_state.historial_db)
                     
                     st.success(f"✅ Historial guardado para {st.session_state.cliente}. Campos reiniciados.")
                     clear_form_data()
                     time.sleep(1)
                     st.rerun()

    st.markdown("---")
    
    if st.session_state.historial_db:
        excel_bytes = generate_complex_excel(st.session_state.historial_db)
            
        st.download_button(
            label="📊 Descargar Excel Completo",
            data=excel_bytes,
            file_name="Base_Datos_Clientes_Completa.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="secondary"
        )
    
    st.markdown("---")
    
    st.subheader("👥 Clientes Registrados")
    if st.session_state.historial_db:
        df_full = pd.DataFrame(st.session_state.historial_db)
        lista_clientes = df_full['Cliente'].unique()
        for nombre_cliente in lista_clientes:
            with st.expander(f"👤 {nombre_cliente}"):
                
                col_title, col_del_client = st.columns([4, 1])
                with col_del_client:
                    if st.button("⛔ Eliminar Cliente", key=f"del_client_{nombre_cliente}"):
                        st.session_state.historial_db = [rec for rec in st.session_state.historial_db if rec['Cliente'] != nombre_cliente]
                        save_data(st.session_state.historial_db)
                        st.success(f"Cliente {nombre_cliente} eliminado.")
                        time.sleep(1)
                        st.rerun()
                        
                registros_cliente = df_full[df_full['Cliente'] == nombre_cliente]
                if not registros_cliente.empty:
                    ultimo_reg = registros_cliente.iloc[-1]
                    
                    st.markdown("##### ✏️ Datos Personales")
                    
                    key_edit = f"edit_mode_{nombre_cliente}"
                    if key_edit not in st.session_state:
                        st.session_state[key_edit] = False

                    if not st.session_state[key_edit]:
                        c_dato1, c_dato2, c_dato3, c_dato4 = st.columns(4)
                        c_dato1.markdown(f"**Ocupación:** {ultimo_reg.get('Ocupacion', 'N/A')}")
                        c_dato2.markdown(f"**Tel:** {ultimo_reg.get('Telefono', 'N/A')}")
                        c_dato3.markdown(f"**Email:** {ultimo_reg.get('Email', 'N/A')}")
                        c_dato4.markdown(f"**Edad:** {ultimo_reg.get('Edad', 'N/A')} años")
                        
                        if st.button("✏️ Editar Datos Personales", key=f"btn_edit_{nombre_cliente}"):
                            st.session_state[key_edit] = True
                            st.rerun()
                    else:
                        with st.form(key=f"form_edit_{nombre_cliente}"):
                            c_e1, c_e2 = st.columns(2)
                            new_ocupacion = c_e1.text_input("Ocupación", value=ultimo_reg.get('Ocupacion', ''))
                            new_telefono = c_e2.text_input("Teléfono", value=ultimo_reg.get('Telefono', ''))
                            
                            c_e3, c_e4, c_e5 = st.columns(3)
                            new_email = c_e3.text_input("Email", value=ultimo_reg.get('Email', ''))
                            new_edad = c_e4.number_input("Edad", min_value=1, max_value=120, value=int(ultimo_reg.get('Edad', 18)), step=1)
                            
                            idx_sexo = 0
                            opciones_sexo = ["Masculino", "Femenino", "No especificar"]
                            if ultimo_reg.get('Sexo') in opciones_sexo:
                                idx_sexo = opciones_sexo.index(ultimo_reg.get('Sexo'))
                            new_sexo = c_e5.selectbox("Sexo", opciones_sexo, index=idx_sexo)

                            if st.form_submit_button("💾 Guardar Cambios"):
                                for rec in st.session_state.historial_db:
                                    if rec['Cliente'] == nombre_cliente:
                                        rec['Ocupacion'] = new_ocupacion
                                        rec['Telefono'] = new_telefono
                                        rec['Email'] = new_email
                                        rec['Edad'] = new_edad
                                        rec['Sexo'] = new_sexo
                                
                                save_data(st.session_state.historial_db)
                                st.session_state[key_edit] = False
                                st.success("Datos actualizados correctamente.")
                                st.rerun()

                    st.markdown("##### 📅 Meses Registrados")
                    # CORRECCIÓN: Usar input_border definido anteriormente
                    for idx, row in registros_cliente.iterrows():
                        col_info, col_dl = st.columns([4, 1])
                        with col_info:
                            st.markdown(f"""<div style="background-color:{card_bg}; padding:12px; border-radius:12px; border:1px solid {input_border}; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; color:{text_color}; box-shadow:{shadow_style};"><strong>{row['Periodo']}</strong> — <span style="color:{color_ingreso}">Ing: {format_money(row['Ingresos'])}</span> | <span style="color:{color_gasto}">Gas: {format_money(row['Egresos'])}</span></div>""", unsafe_allow_html=True)
                        with col_dl:
                            st.download_button("📄 PDF", row['PDF_Bytes'], f"Reporte_{row['Cliente']}_{row['Periodo']}.pdf", "application/pdf", key=f"btn_dl_{row['id']}")
    else:
        st.info("No hay clientes en la base de datos.")

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Ruta de la carpeta de tickets
TICKETS_FOLDER = './tickets/'
SCREENSHOTS_FOLDER='screenshots'
def load_tickets_from_folder(folder_path):
    """Cargar todos los archivos JSON de la carpeta de tickets."""
    tickets = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            with open(os.path.join(folder_path, filename), 'r') as file:
                ticket_data = json.load(file)
                tickets.append(ticket_data)
    return tickets

def process_ticket_data(tickets):
    """Procesar los datos de los tickets para crear un DataFrame o lista."""
    data = []
    for ticket in tickets:
        info_error_truncated = ', '.join(ticket['info_error'][:3]) + '...' if len(ticket['info_error']) > 3 else ', '.join(ticket['info_error'])
        info = '🔴 High' if 'Error' in ticket['info_error'] else '🟢 Low'
        user_email = ticket.get('log_data', {}).get('error_logs', {}).get('user_email', 'unknown@example.com')
        ticket_short_id = ticket['ticket_id'][-5:]  # Últimos 5 caracteres del ticket_id
        
        # Estado del ticket basado en la variable send y required_vars
        if ticket['send'] and not ticket['required_vars']:
            status = 'Closed'
            ia_response = 'Respondido por IA'
            tag_colors = ['#0acf83']  # Verde - Completado por IA
        elif ticket['send'] and ticket['required_vars']:
            status = 'Open'
            ia_response = 'Esperando Respuesta'
            tag_colors = ['#f2c94c']  # Amarillo - Esperando respuesta
        else:
            status = 'Open'
            ia_response = 'Acción humana requerida'
            tag_colors = ['#f44336']  # Rojo - Requiere intervención humana

        data.append({
            'ticket_id': ticket['ticket_id'],
            'ticket_short_id': ticket_short_id,  # Agregar el ID corto
            'info': info,
            'origin': ticket.get('origin', 'Unknown'),
            'messages': len(ticket.get('info_error', [])),
            'last_message': info_error_truncated,  # Truncar el último mensaje
            'user': user_email,  # Mostrar el correo electrónico del ticket
            'status': status,
            'ia_response': ia_response,
            'tag_colors': tag_colors,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")  # Puedes cambiarlo si tienes fecha en el JSON
        })
    return pd.DataFrame(data)

def main():
    st.set_page_config(page_title="MonitorAI", page_icon="🤖", layout="wide")
    
    # Inicializar session state para manejar la navegación
    if 'current_view' not in st.session_state:
        st.session_state.current_view = 'list'
    if 'selected_ticket' not in st.session_state:
        st.session_state.selected_ticket = None

    st.markdown("""
        <h1 style='font-size: 24px; margin-bottom: 20px;'>MonitorAI</h1>
    """, unsafe_allow_html=True)

    if st.session_state.current_view == 'list':
        show_ticket_list()
    else:
        show_ticket_detail()

def show_ticket_list():
    # Cargar los tickets desde la carpeta una sola vez
    tickets = load_tickets_from_folder(TICKETS_FOLDER)
    df = process_ticket_data(tickets)

    # Barra de búsqueda con un key único basado en la vista y un sufijo adicional
    search_term = st.text_input("🔍 Buscar tickets...", key=f"search_input_{st.session_state.current_view}_list")

    # Filtrar el DataFrame basado en el término de búsqueda
    if search_term:
        df = df[df.apply(lambda row: search_term.lower() in row.astype(str).str.lower().to_list(), axis=1)]

    # Encabezado de la tabla
    st.markdown("""
        <div style='font-weight: bold; padding: 10px; display: flex; justify-content: space-between;'>
            <div style='width: 10%;'>Acciones</div>
            <div style='width: 10%;'>ID</div>
            <div style='width: 10%;'>Origen</div>
            <div style='width: 10%;'>Mensajes</div>
            <div style='width: 25%;'>Último Mensaje</div>
            <div style='width: 10%;'>Correo Electrónico</div>
            <div style='width: 10%;'>Estado</div>
            <div style='width: 15%;'>IA / Acción</div>
        </div>
    """, unsafe_allow_html=True)

    # Mostrar tickets con estilo de columnas
    for idx, row in df.iterrows():
        ticket_id = row['ticket_id']  # Obtener el ID del ticket
        cols = st.columns([1, 1, 1, 1, 2.5, 1, 1, 1.5])  # Ajustar las proporciones según el diseño

        with cols[0]:
            # Usar una combinación de idx y ticket_id para crear un key único
            if st.button(f"Ver detalles", key=f"details_{idx}_{ticket_id}", help="Ver detalles del ticket"):
                # Convertir el ticket seleccionado de vuelta a un diccionario original
                st.session_state.current_view = 'detail'
                st.session_state.selected_ticket = tickets[idx]  # Usar el ticket original como dict
                st.rerun()
        
        with cols[1]:
            st.write(row['ticket_short_id'])
        
        with cols[2]:
            if row['origin'].lower() == 'widget':
                st.markdown('<img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ3ls7pJrg5g4j8gDw-tKm__k9j5Fcc6Z3jtg&s" alt="widget icon" style="width:25px;">', unsafe_allow_html=True)
            else:
                st.write(row['origin'])
        
        with cols[3]:
            st.write(f"💬 {row['messages']}")

        with cols[4]:
            st.write(f"**{row['last_message'][:40]}...**" if len(row['last_message']) > 40 else f"**{row['last_message']}**")
        
        with cols[5]:
            st.write(row['user'])
        
        with cols[6]:
            status_color = 'green' if row['status'] == 'Closed' else 'red'
            st.markdown(f"<div style='color: {status_color}; font-weight: bold;'>{row['status']}</div>", unsafe_allow_html=True)
        
        with cols[7]:
            tags_html = ''.join([f'<span style="background-color: {color}; padding: 4px 8px; border-radius: 10px; color: white; margin-right: 5px;">{row["ia_response"]}</span>'
                                for color in row['tag_colors']])
            st.markdown(tags_html, unsafe_allow_html=True)

def show_ticket_detail():
    ticket = st.session_state.selected_ticket
    ticket_id = ticket['ticket_id']
    
    # Dividir la página en dos columnas
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        st.markdown(f"### Detalles del ticket: {ticket_id}")
        
        # Mostrar el historial de mensajes
        st.markdown("#### Historial de Chat")
        
        # Usar .get para evitar KeyError si 'send' no existe
        if ticket.get('send', False):
            # Mensaje inicial desde Suggested Answer si fue enviado
            st.markdown(f"**Cliente:** {ticket.get('Suggested_Answer', '')}")
        
        # Mostrar input para enviar un mensaje con un key único basado en ticket_id
        if ticket.get('send', False):
            response_input = st.text_area("Respuesta sugerida", height=100, key=f"response_input_{ticket_id}_send")
        else:
            # Si el mensaje no fue enviado, mostrar el Suggested Answer en el campo
            response_input = st.text_area("Respuesta sugerida", value=ticket.get('Suggested_Answer', ''), height=100, key=f"response_input_{ticket_id}")
        
        st.button("Enviar respuesta")

        # Mostrar la captura de pantalla si existe, siempre
        screenshot_path = os.path.join(SCREENSHOTS_FOLDER, f"screenshot_{ticket_id}.png")
        if os.path.exists(screenshot_path):
            st.markdown("**Captura de pantalla:**")
            st.image(screenshot_path, caption=f"Screenshot del Ticket {ticket_id}")
        else:
            st.markdown("*No hay captura de pantalla disponible.*")

    with right_col:
        # Mostrar información adicional
        
        # Mostrar Información del error
        st.markdown("### Información del error")
        for error in ticket.get('info_error', []):
            st.markdown(f"- {error}")
        
        # Mostrar APIs útiles (dentro de api_requirement_json)
        st.markdown("### APIs útiles")
        api_requirement = ticket.get('api_requirement_json', {})
        apis_to_call = api_requirement.get('apis_to_call', [])
        if apis_to_call:
            for api in apis_to_call:
                st.markdown(f"- **URL:** {api['url']}")
                st.markdown(f"  **Método:** {api['method']}")
                if api.get('required_vars', []):
                    st.markdown(f"  **Variables requeridas:** {', '.join(api.get('required_vars', []))}")
                else:
                    st.markdown("  **Variables requeridas:** No se requieren variables adicionales.")
        else:
            st.markdown("No hay APIs útiles disponibles.")
        
        # Mostrar Variables requeridas directamente (si existieran)
        st.markdown("### Variables requeridas")
        required_vars = ticket.get('required_vars', [])
        if required_vars:
            for var in required_vars:
                st.markdown(f"- {var}")
        else:
            st.markdown("No se requieren variables adicionales.")
        
        # Mostrar Logs de errores
        if 'log_data' in ticket and 'error_logs' in ticket['log_data']:
            error_logs = ticket['log_data']['error_logs']
            st.markdown(f"**Correo del usuario:** {error_logs.get('user_email', 'No disponible')}")
            st.markdown(f"**Error en consola:** {error_logs.get('console_logs', 'No disponible')}")
            
            if 'network_logs' in error_logs:
                st.markdown("#### Logs de red")
                for log in error_logs['network_logs']:
                    st.markdown(f"- **Request**: {log['request']}")
                    st.markdown(f"- **Response**: {log['response']}")
        else:
            st.markdown("No hay información de logs disponible.")
        
        # Botón para volver a la lista de tickets
        if st.button("← Volver a la lista"):
            st.session_state.current_view = 'list'
            st.session_state.selected_ticket = None
            st.rerun()

if __name__ == "__main__":
    main()

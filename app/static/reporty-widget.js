(function () {
    let chatWindow, chatBody, submitBtn;
    let consoleLogs = [];  // Almacenamos los logs de consola
    let networkLogs = [];  // Almacenamos los logs de la red
    let screenshotData;     // Almacenamos la captura de pantalla

    // Función para cargar html2canvas dinámicamente si no está disponible
    function loadHtml2Canvas(callback) {
        if (typeof html2canvas !== 'undefined') {
            // Si html2canvas ya está cargado, ejecutamos el callback
            callback();
        } else {
            console.log("Cargando html2canvas...");
            const script = document.createElement('script');
            script.src = "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js";
            script.onload = () => {
                console.log("html2canvas cargado exitosamente.");
                callback();
            };
            script.onerror = () => {
                console.error("No se pudo cargar html2canvas.");
            };
            document.head.appendChild(script);  // Añadir el script al head
        }
    }

    // Función para capturar los logs de consola
    function captureConsoleLogs() {
        const originalConsoleError = console.error;
        console.error = function (...args) {
            consoleLogs.push(args.join(' '));  // Guardamos los logs
            originalConsoleError.apply(console, args);
        };
    }

    // Función para esperar un determinado tiempo (en milisegundos)
    function delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Función para capturar la captura de pantalla
    async function captureScreenshot() {
        try {
            window.scrollTo(0, 0);  // Asegura que todo esté visible
            await delay(500);  // Espera para asegurar que todo se renderice correctamente
            
            // Ajusta la posición y visibilidad del modal swal, si está presente
            const modalContainer = document.querySelector('.swal2-container');
            if (modalContainer) {
                modalContainer.style.position = 'relative';
                modalContainer.style.zIndex = '9999';
            }
            
            // Ajusta la posición y visibilidad del toast, si está presente
            const toastContainer = document.querySelector('.swal2-toast');
            if (toastContainer) {
                toastContainer.style.position = 'relative';
                toastContainer.style.zIndex = '9999';
            }
    
            // Captura la pantalla
            const canvas = await html2canvas(document.body, {
                useCORS: true,
                allowTaint: false,
                logging: true,
                windowWidth: document.documentElement.scrollWidth,
                windowHeight: document.documentElement.scrollHeight,
                scrollX: 0,
                scrollY: 0
            });
    
            console.log("Captura de pantalla exitosa");
            screenshotData = canvas.toDataURL();  // Guarda la captura en base64
            return screenshotData;
        } catch (error) {
            console.error("Error al capturar la pantalla:", error.message || error);
            return null;
        }
    }
    

    // Función para capturar errores de la red
    function monitorNetworkRequests() {
        const originalFetch = window.fetch;
        window.fetch = async function (...args) {
            const url = args[0];
            const options = args[1] || {};
            const method = options.method || 'GET';

            const requestDetails = `${method} ${url}`;
            let requestBody = options.body || null;

            try {
                const response = await originalFetch.apply(this, args);
                const responseClone = response.clone();  // Clonar para no interferir con el flujo original

                const responseText = await responseClone.text();  // Obtener el texto de la respuesta
                const status = responseClone.status;

                // Si la respuesta no es OK (ejemplo: 404, 500, etc.), capturamos el estado
                networkLogs.push({
                    request: requestDetails,
                    body: requestBody,
                    status: status,  // Aquí capturamos el código de estado aunque no sea exitoso
                    response: responseText
                });

                if (!response.ok) {
                    console.error('Error de API detectado (fetch):', status);
                    showErrorWidget();  // Mostrar el widget una sola vez en caso de error
                }

                return response;
            } catch (error) {
                // En caso de error en la red, como fallos de conexión
                console.error('Error en fetch:', error);
                networkLogs.push({
                    request: requestDetails,
                    body: requestBody,
                    status: 'failed',  // Marcamos como "failed" en caso de error de red
                    response: error.message
                });
                showErrorWidget();  // Mostrar el widget en caso de error
                throw error;
            }
        };
    }

    // Función para mostrar el widget de error (solo se abrirá una vez)
    let errorWidgetShown = false;  // Variable para evitar mostrar el widget dos veces

    async function showErrorWidget() {
        if (errorWidgetShown) return;  // Si el widget ya se mostró, no hacer nada
        errorWidgetShown = true;  // Marcamos el widget como mostrado

        console.log('Intentando abrir el widget de error...');
        screenshotData = await captureScreenshot();  // Captura la pantalla
        if (!screenshotData) {
            console.error("No se pudo capturar la pantalla, el widget se abrirá de todos modos.");
        }
        chatWindow.style.display = 'flex';  // Mostrar el widget
        chatBody.innerHTML = `
            <p>Ups, parece que ha habido un error, ¿desea reportar este error al equipo de Customer Success?</p>
            <input type="email" id="userEmail" placeholder="Tu correo" style="width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 4px;" />
        `;
        submitBtn.textContent = 'Enviar Reporte';
    }

    // Inicializar el widget cuando el DOM esté listo
    document.addEventListener("DOMContentLoaded", function () {
        console.log('Inicializando el widget...');
        
        // Crea el botón de la burbuja del chat
        const chatBubble = document.createElement('div');
        chatBubble.style.position = 'fixed';
        chatBubble.style.top = '20px';
        chatBubble.style.right = '20px';
        chatBubble.style.width = '60px';
        chatBubble.style.height = '60px';
        chatBubble.style.backgroundColor = '#0083ff';
        chatBubble.style.borderRadius = '50%';
        chatBubble.style.display = 'flex';
        chatBubble.style.alignItems = 'center';
        chatBubble.style.justifyContent = 'center';
        chatBubble.style.color = '#fff';
        chatBubble.style.fontSize = '24px';
        chatBubble.style.cursor = 'pointer';
        chatBubble.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
        chatBubble.textContent = '💬';

        // Crea la ventana del chat
         chatWindow = document.createElement('div');
        chatWindow.style.position = 'fixed';
        chatWindow.style.top = '90px';
        chatWindow.style.right = '20px';
        chatWindow.style.width = '320px';
        chatWindow.style.height = 'auto';
        chatWindow.style.backgroundColor = '#fff';
        chatWindow.style.border = '1px solid #e2e2e2';
        chatWindow.style.borderRadius = '10px';
        chatWindow.style.display = 'none';
        chatWindow.style.flexDirection = 'column';
        chatWindow.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.1)';

        // Header del chat
        const chatHeader = document.createElement('div');
        chatHeader.style.backgroundColor = '#007bff';
        chatHeader.style.color = 'white';
        chatHeader.style.padding = '10px';
        chatHeader.style.textAlign = 'center';
        chatHeader.textContent = 'Report an Issue';

        // Cuerpo del chat (mensaje de error)
        chatBody = document.createElement('div');
        chatBody.style.flexGrow = '1';
        chatBody.style.padding = '10px';

        // Footer del chat con botón de envío
        const chatFooter = document.createElement('div');
        chatFooter.style.padding = '10px';
        chatFooter.style.borderTop = '1px solid #ddd';
        submitBtn = document.createElement('button');
        submitBtn.textContent = 'Enviar Reporte';
        submitBtn.style.backgroundColor = '#007bff';
        submitBtn.style.color = 'white';
        submitBtn.style.padding = '8px';
        submitBtn.style.border = 'none';
        submitBtn.style.borderRadius = '4px';
        submitBtn.style.cursor = 'pointer';

        chatFooter.appendChild(submitBtn);

        // Agregar los elementos al DOM
        chatWindow.appendChild(chatHeader);
        chatWindow.appendChild(chatBody);
        chatWindow.appendChild(chatFooter);
        document.body.appendChild(chatBubble);
        document.body.appendChild(chatWindow);

        // Mostrar/ocultar la ventana del chat al hacer clic en la burbuja
        chatBubble.addEventListener('click', () => {
            console.log('Burbujita de chat clickeada.');
            chatWindow.style.display = chatWindow.style.display === 'none' ? 'flex' : 'none';
        });

        // Enviar reporte de error al backend
        submitBtn.addEventListener('click', async () => {
            const userEmail = document.getElementById('userEmail').value;
            console.log('Enviando reporte de error con correo:', userEmail);

            const response = await fetch('http://localhost:8000/api/log_error', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: 'Se ha reportado un error desde la página',
                    user_email: userEmail,
                    console_logs: consoleLogs.join('\n'),
                    network_logs: networkLogs,  // Añadimos los logs de la red
                    screenshot: screenshotData  // Enviamos la captura de pantalla
                })
            });

            if (response.ok) {
                alert('Reporte enviado correctamente');
                chatWindow.style.display = 'none';
            } else {
                alert('No se pudo enviar el reporte');
            }
        });

        // Cargar html2canvas dinámicamente antes de capturar la pantalla
        loadHtml2Canvas(() => {
            // Capturar los logs de consola y monitorear la red
            captureConsoleLogs();
            monitorNetworkRequests();  // Capturar las solicitudes de red
        });
    });
})();

import tkinter as tk
from tkinter import messagebox
from pynput.mouse import Controller, Button
from pynput.keyboard import Controller as KeyboardController, Key # Importamos 'Key' para usar Enter
import threading
import time
import sys

# --- Constantes y Configuración ---
WINDOW_TITLE = "🐦 WOODY Autoclicker"
WHITE_BG_COLOR = "#ffffff"  # Fondo Blanco
BUTTON_BG_COLOR = "#dc3545"  # Rojo (Fondo de todos los botones)
ACCENT_COLOR = "#007bff"    # Azul (Para mensajes de estado)
FONT_STYLE = ("Arial", 10, "bold")
DELAY_BEFORE_START = 3
CLICK_INTERVAL_SECONDS = 0.03 
MESSAGE_TO_TYPE = "Hola soy un bot 🤖 de Neuros 😎 que sirve a su dios ⚡"

class WoodyAutoclicker:
    def __init__(self, master):
        self.master = master
        master.title(WINDOW_TITLE)
        master.geometry("400x530") # Aumentamos el tamaño para el nuevo botón
        master.resizable(False, False)
        master.config(bg=WHITE_BG_COLOR) # Establecer fondo blanco

        # Inicialización de variables
        self.mouse = Controller()
        self.keyboard = KeyboardController() # Inicializamos el controlador de teclado
        self.target_x = None
        self.target_y = None
        self.is_running = False
        self.stop_requested = False 
        self.clicks_performed = 0
        self.current_click_limit = 0 # Para saber qué tarea está corriendo
        
        # Estilo común de botones (letras blancas, fondo rojo consistente)
        BUTTON_STYLES = {
            "fg": "white",                  # Color de fuente normal (Blanco)
            "bg": BUTTON_BG_COLOR,          # Fondo Rojo
            "disabledforeground": "white",  # Color de fuente cuando está deshabilitado
            "activeforeground": "white",    # Color de fuente cuando se pulsa
            "activebackground": "#b02a37",  # Tono de rojo más oscuro al pulsar
            "relief": tk.FLAT,
            "font": FONT_STYLE,
            "highlightthickness": 0,        
        }

        # Estilo de etiquetas (letras negras, fondo blanco)
        LABEL_STYLES = {
            "fg": "black", # Color de fuente Negro
            "bg": WHITE_BG_COLOR,
        }

        # --- Título Principal ---
        self.title_label = tk.Label(
            master,
            text="🐦 WOODY",
            font=("Arial", 24, "bold"),
            **LABEL_STYLES
        )
        self.title_label.pack(pady=(20, 0))

        self.subtitle_label = tk.Label(
            master,
            text="Autoclicker",
            font=("Arial", 14),
            **LABEL_STYLES
        )
        self.subtitle_label.pack(pady=(0, 15))


        # 1. Indicador de estado/coordenadas
        self.status_label = tk.Label(
            master,
            text="Estado: Esperando coordenadas...",
            font=("Arial", 11),
            **LABEL_STYLES
        )
        self.status_label.pack(pady=5)
        
        # 1b. Etiqueta de progreso 
        self.progress_label = tk.Label(
            master,
            text=f"Intervalo: {CLICK_INTERVAL_SECONDS}s por click",
            font=("Arial", 10),
            **LABEL_STYLES
        )
        self.progress_label.pack(pady=5)


        # 2. Botón de Selección de Área
        self.select_button = tk.Button(
            master,
            text="📌 Seleccionar Área (3s)",
            command=self.start_selection_thread,
            **BUTTON_STYLES
        )
        self.select_button.pack(pady=8, padx=20, fill=tk.X)
        
        # 3a. Botón de Iniciar 1000 Clicks
        self.start_1000_button = tk.Button(
            master,
            text="🚀 Iniciar 1000 Clicks",
            command=lambda: self.start_clicks_thread(1000),
            state=tk.DISABLED,
            **BUTTON_STYLES
        )
        self.start_1000_button.pack(pady=(10, 5), padx=20, fill=tk.X)

        # 3b. Botón de Iniciar 5000 Clicks
        self.start_5000_button = tk.Button(
            master,
            text="⚡️ Iniciar 5000 Clicks",
            command=lambda: self.start_clicks_thread(5000),
            state=tk.DISABLED,
            **BUTTON_STYLES
        )
        self.start_5000_button.pack(pady=(5, 10), padx=20, fill=tk.X)
        
        # 3c. Botón de Escribir Mensaje
        self.typing_button = tk.Button(
            master,
            text="✍️ Escribir Mensaje",
            command=self.start_typing_thread,
            state=tk.DISABLED,
            **BUTTON_STYLES
        )
        self.typing_button.pack(pady=(5, 10), padx=20, fill=tk.X)


        # 4. Botón de Detener
        self.stop_button = tk.Button(
            master,
            text="🛑 Detener Clicks",
            command=self.stop_clicks,
            state=tk.DISABLED,
            **BUTTON_STYLES
        )
        self.stop_button.pack(pady=8, padx=20, fill=tk.X)
        
        # 5. Botón de Salir
        self.exit_button = tk.Button(
            master,
            text="Salir",
            command=master.quit,
            **BUTTON_STYLES
        )
        self.exit_button.pack(pady=8, padx=20, fill=tk.X)


    # --- Lógica de Hilos y Captura de Coordenadas ---

    def start_selection_thread(self):
        """Inicia un hilo para la cuenta regresiva y la captura de coordenadas."""
        if self.is_running:
            return

        self.status_label.config(text="Estado: ⏳ 3 segundos para posicionar el ratón...", fg=ACCENT_COLOR)
        self._disable_all_buttons()
        self.is_running = True

        threading.Thread(target=self.capture_coordinates_after_delay, daemon=True).start()

    def capture_coordinates_after_delay(self):
        """Espera 3 segundos y luego captura las coordenadas del ratón."""
        
        # Muestra una cuenta regresiva simple en la etiqueta
        for i in range(DELAY_BEFORE_START, 0, -1):
            # Usamos master.after para actualizar la UI desde el hilo
            self.master.after(1000 * (DELAY_BEFORE_START - i), 
                              lambda i=i: self.status_label.config(text=f"Estado: ⏳ Captura en {i} segundos...", fg=ACCENT_COLOR))
            time.sleep(1) 

        time.sleep(1) 
        
        try:
            x, y = self.mouse.position
            self.target_x = x
            self.target_y = y
            self.master.after(0, self.update_status_after_selection)
        except Exception as e:
            self.master.after(0, lambda: self._handle_mac_permissions_error(e))

    def update_status_after_selection(self):
        """Actualiza la interfaz después de que la selección haya terminado."""
        self.is_running = False
        self._enable_all_buttons()
        
        if self.target_x is not None:
            self.status_label.config(
                text=f"✅ Coordenadas capturadas: ({self.target_x}, {self.target_y})",
                fg=BUTTON_BG_COLOR # Usamos rojo para el éxito
            )
            # Habilita todos los botones de acción (clics y escritura)
            self.start_1000_button.config(state=tk.NORMAL)
            self.start_5000_button.config(state=tk.NORMAL)
            self.typing_button.config(state=tk.NORMAL)
            self.progress_label.config(text=f"Listo para iniciar clics o escribir.")
        else:
            self.status_label.config(text="❌ Error al capturar coordenadas.", fg=BUTTON_BG_COLOR)
            self.progress_label.config(text=f"Intervalo: {CLICK_INTERVAL_SECONDS}s por click")
        
    # --- Lógica de Auto Clicks ---

    def start_clicks_thread(self, click_limit):
        """Inicia un hilo para la ráfaga de clicks y activa el botón de Detener."""
        if self.is_running or self.target_x is None:
            return
        
        # Establece el límite de clics para esta ejecución
        self.current_click_limit = click_limit
        
        # Reiniciar variables de control
        self.stop_requested = False
        self.clicks_performed = 0

        self.status_label.config(text=f"Estado: ⚙️ Realizando {click_limit} clicks...", fg=ACCENT_COLOR)
        self._disable_all_buttons(allow_stop=True) # Permite que solo Detener esté activo
        self.is_running = True
        
        threading.Thread(target=self.perform_clicks, daemon=True).start()

    def stop_clicks(self):
        """Establece el flag para detener el proceso de clicks."""
        if self.is_running:
            self.stop_requested = True
            self.status_label.config(text="Estado: 🔴 Detención solicitada...", fg=BUTTON_BG_COLOR)
            self.stop_button.config(state=tk.DISABLED)

    def perform_clicks(self):
        """Mueve el ratón y realiza los clicks con pausa, revisando el flag de detención."""
        
        try:
            # Mueve el ratón una sola vez antes de empezar
            self.mouse.position = (self.target_x, self.target_y)

            for i in range(1, self.current_click_limit + 1):
                if self.stop_requested:
                    break # Sale del bucle si se solicita la detención

                self.clicks_performed = i
                
                # Actualiza la etiqueta de progreso en el hilo principal
                self.master.after(0, 
                                  lambda i=i: self.progress_label.config(text=f"Click {i} de {self.current_click_limit} | Faltan {self.current_click_limit - i}"))
                
                self.mouse.click(Button.left)
                
                # PAUSA DE 0.03 SEGUNDOS
                time.sleep(CLICK_INTERVAL_SECONDS) 

            self.master.after(0, self.finish_clicks)
        except Exception as e:
            self.master.after(0, lambda: self._handle_mac_permissions_error(e))

    # --- Lógica de Auto Escritura ---

    def start_typing_thread(self):
        """Inicia un hilo para la automatización de escritura."""
        if self.is_running or self.target_x is None:
            return
        
        self.status_label.config(text="Estado: ✍️ Escribiendo mensaje...", fg=ACCENT_COLOR)
        self.progress_label.config(text=f"Mensaje: '{MESSAGE_TO_TYPE[:30]}...'")
        self._disable_all_buttons() 
        self.is_running = True
        
        threading.Thread(target=self.perform_typing, daemon=True).start()

    def perform_typing(self):
        """Mueve el ratón, hace clic y escribe el mensaje, luego presiona Enter."""
        try:
            # 1. Mueve el ratón y hace clic para activar el campo de texto
            self.mouse.position = (self.target_x, self.target_y)
            time.sleep(0.1) # Breve pausa para que el cursor se mueva
            self.mouse.click(Button.left)
            time.sleep(0.1) # Breve pausa para asegurar que el campo está activo

            # 2. Escribe el mensaje
            self.keyboard.type(MESSAGE_TO_TYPE)
            time.sleep(0.1) 
            
            # 3. PULSA LA TECLA ENTER
            self.keyboard.press(Key.enter)
            self.keyboard.release(Key.enter)
            time.sleep(0.5) # Pausa final para que la acción se complete

            self.master.after(0, self.finish_typing)
        except Exception as e:
            self.master.after(0, lambda: self._handle_mac_permissions_error(e))

    def finish_typing(self):
        """Muestra el popup de finalización de escritura y restaura el estado."""
        self.is_running = False
        self._enable_all_buttons()
        
        msg = f"El mensaje ha sido escrito y enviado (pulsando Enter) en las coordenadas ({self.target_x}, {self.target_y}):\n\n{MESSAGE_TO_TYPE}"
        self.status_label.config(text="✅ Tarea de escritura finalizada.", fg=BUTTON_BG_COLOR)
        self.progress_label.config(text=f"Listo para iniciar clics o escribir.")

        messagebox.showinfo("Woody - Escritura Finalizada", msg)


    # --- Finalización y Utilidad ---

    def finish_clicks(self):
        """Muestra el popup de finalización de clics y restaura el estado."""
        
        self.is_running = False
        self._enable_all_buttons()
        
        if self.clicks_performed == self.current_click_limit:
            # Tarea completada
            msg = f"La ráfaga de {self.current_click_limit} clicks izquierdos ha finalizado COMPLETAMENTE en las coordenadas ({self.target_x}, {self.target_y})."
            self.status_label.config(text=f"✅ Tarea finalizada ({self.clicks_performed} clicks).", fg=BUTTON_BG_COLOR)
        else:
            # Tarea detenida
            msg = f"La ráfaga de clicks ({self.current_click_limit}) fue DETENIDA por el usuario después de realizar {self.clicks_performed} clics."
            self.status_label.config(text=f"⚠️ Tarea detenida ({self.clicks_performed} clicks).", fg=ACCENT_COLOR)
        
        self.progress_label.config(text=f"Total: {self.clicks_performed} clicks realizados. Último límite: {self.current_click_limit}")

        # Muestra el mensaje de finalización con el conteo actualizado
        messagebox.showinfo("Woody - Finalizado", msg)
        
    # --- Métodos de utilidad ---

    def _disable_all_buttons(self, allow_stop=False):
        self.select_button.config(state=tk.DISABLED)
        self.start_1000_button.config(state=tk.DISABLED)
        self.start_5000_button.config(state=tk.DISABLED)
        self.typing_button.config(state=tk.DISABLED)
        self.exit_button.config(state=tk.DISABLED)
        # Habilita el botón de detener solo si el proceso está en curso
        self.stop_button.config(state=tk.NORMAL if allow_stop else tk.DISABLED)

    def _enable_all_buttons(self):
        self.select_button.config(state=tk.NORMAL)
        self.exit_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED) # Siempre deshabilitado fuera del proceso de clics
        # Los botones de acción solo se habilitan si hay coordenadas capturadas
        if self.target_x is not None:
            self.start_1000_button.config(state=tk.NORMAL)
            self.start_5000_button.config(state=tk.NORMAL)
            self.typing_button.config(state=tk.NORMAL)

    def _handle_mac_permissions_error(self, error):
        """Maneja errores específicos de pynput en macOS."""
        self.is_running = False
        self._enable_all_buttons()
        self.status_label.config(text="❌ ERROR de Permisos de macOS.", fg=BUTTON_BG_COLOR)
        self.progress_label.config(text=f"Intervalo: {CLICK_INTERVAL_SECONDS}s por click")

        if "You must grant permission for the application to control your input devices" in str(error) or sys.platform == "darwin":
            messagebox.showerror(
                "❌ ERROR: Permisos de macOS",
                "¡ATENCIÓN! El sistema operativo macOS está bloqueando el control del ratón/teclado.\n\n"
                "NECESITAS hacer lo siguiente:\n"
                "1. Ir a Preferencias del Sistema > Seguridad y Privacidad > Privacidad.\n"
                "2. Seleccionar 'Accesibilidad'.\n"
                "3. Agregar la aplicación de Python (o la terminal que ejecuta el script) a la lista de aplicaciones permitidas.\n"
                "4. Reiniciar la aplicación de Woody."
            )
        else:
            messagebox.showerror("Error", f"Ocurrió un error inesperado al usar el ratón/teclado: {e}")


# --- Ejecución Principal ---
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = WoodyAutoclicker(root)
        root.mainloop()
    except ImportError:
        messagebox.showerror(
            "Error de Dependencia",
            "La librería 'pynput' es necesaria para esta aplicación.\n"
            "Instálala con: pip install pynput"
        )
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error inesperado al iniciar la aplicación: {e}")

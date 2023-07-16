"""
One of the rare files that was written by me and me only (not GPT-4) :D
"""

from nicegui import ui, app
from nicegui.events import KeyEventArguments
from chatbox import ChatBox

class KeyDownHandler:
    def __init__(self):
        self.keys = {}

    def on_key_down(self, key, action):
        self.keys[key] = {
            "ui": ui.button(key).style("padding: 5px 10px").style("margin: 0px"),
            "action": action,
        }

    def handle_keys(self, e: KeyEventArguments):
        pass


chatbox = ChatBox()
chatbox._debug_echo = True
key_down_handler = KeyDownHandler()


with ui.row():
    # First column: video stream and robot status
    with ui.column():
        # Video stream row
        with ui.card().tight().style("width: 900px"):
            image = ui.image('http://10.0.0.140:8000/stream.mjpg')

    # Second column: manual controls and chat with AI
    with ui.column().style("width: 500px"):
        with ui.tabs().classes('w-full') as tabs:
            chat_with_ai = ui.tab('Chat with AI')
            manual_controls = ui.tab('Manual Controls')
        
        with ui.tab_panels(tabs, value=manual_controls).classes('w-full no-wrap max-w-3xl'):
            with ui.tab_panel(chat_with_ai):
                chatbox.create_chatbox()
            with ui.tab_panel(manual_controls):
                # Sliders for everything
                def add_slider_row(name, min, max, value):
                    with ui.row().classes("w-full no-wrap max-w-3xl"):
                        with ui.column().classes("w-1/6"):
                            ui.label(name).classes("w-full")
                        with ui.column().classes("w-5/6"):
                            with ui.row().classes("w-full no-wrap max-w-3xl"):
                                with ui.column().classes("w-[90%]"):
                                    slider = ui.slider(min=min, max=max, value=value).classes("w-full")
                                with ui.column().classes("w-[10%]"):
                                    ui.label().bind_text_from(slider, 'value')
                    return slider
            
                with ui.row().classes("w-full no-wrap max-w-3xl"):
                    with ui.column().classes("w-2/3").style("gap: 7px"):
                        add_slider_row("Roll", -20, 20, 0)
                        add_slider_row("Pitch", -20, 20, 0)
                        add_slider_row("Yaw", -20, 20, 0)
                        add_slider_row("Head", 50, 180, 90)
                    with ui.column().classes("w-1/3").style("gap: 0px"):
                        ui.joystick(color='blue', size=50,
                                    on_move=lambda e: coordinates.set_text(f"{e.x:.3f}, {e.y:.3f}"),
                                    on_end=lambda _: coordinates.set_text('0, 0'))
                        coordinates = ui.label('0, 0')

                ui.separator().style("margin-top: 15px; margin-bottom: 15px")

                with ui.column().classes("w-full no-wrap max-w-3xl").style("gap: 7px"):
                    add_slider_row("Speed", 2, 10, 7)
                    add_slider_row("Horizon", -20, 20, 0)
                    add_slider_row("Height", -20, 20, 0)

                ui.separator().style("margin-top: 15px; margin-bottom: 15px")

                with ui.row().classes('justify-between'): # Add 'justify-between' to distribute space between columns
                    # WASD+QE+R controls
                    with ui.column():
                        with ui.grid(columns=4).style("gap: 7px"):
                            # Row 1
                            key_down_handler.on_key_down('Q', lambda: None)
                            key_down_handler.on_key_down('W', lambda: None)
                            key_down_handler.on_key_down('E', lambda: None)
                            key_down_handler.on_key_down('R', lambda: None)
                            # Row 2
                            key_down_handler.on_key_down('A', lambda: None)
                            key_down_handler.on_key_down('S', lambda: None)
                            key_down_handler.on_key_down('D', lambda: None)
                        ui.markdown("**WASD** - move, **R** - reset,\n\n**QE** - step left/right")

                    # Second row: YUIHJK controls
                    with ui.column():
                        with ui.grid(columns=4).style("gap: 7px"):
                            # Row 1
                            key_down_handler.on_key_down('Y', lambda: None)
                            key_down_handler.on_key_down('U', lambda: None)
                            key_down_handler.on_key_down('I', lambda: None)
                            key_down_handler.on_key_down('O', lambda: None)
                            # Row 2
                            key_down_handler.on_key_down('H', lambda: None)
                            key_down_handler.on_key_down('J', lambda: None)
                            key_down_handler.on_key_down('K', lambda: None)
                            key_down_handler.on_key_down('L', lambda: None)
                        ui.markdown("**JL** - roll, **UO** - yaw,\n\n**IK** - pitch, **YH** - head")

keyboard = ui.keyboard(on_key=key_down_handler.handle_keys)
keyboard.active = True



app.add_static_files("/images", "../images")
ui.run()
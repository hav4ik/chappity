#!/usr/bin/env python3
from datetime import datetime
from typing import List, Tuple
from uuid import uuid4
from nicegui import Client, ui, app


class ChatBox:
    def __init__(self):
        self.messages: List[Tuple[str, str, str, str]] = []
        self.user_id = "user"
        self.robot_id = "robot"
        self.avatar_robot = f'/images/chappity.jpeg'
        self._debug_echo = False

    @ui.refreshable
    async def chat_messages(self, own_id: str) -> None:
        for user_id, avatar, text, stamp in self.messages:
            ui.chat_message(text=text, stamp=stamp, avatar=avatar, sent=own_id == user_id)
        # Scroll to bottom of chat messages
        await ui.run_javascript('''
            var element = document.getElementsByClassName("scroll")[0];
            var isScrolledToBottom = element.scrollHeight - element.clientHeight <= element.scrollTop + 1;
            if (!isScrolledToBottom) {
                element.scrollTop = element.scrollHeight - element.clientHeight;
            }''', respond=False)
        
    def send_robot_text(self, text: str) -> None:
        stamp = datetime.utcnow().strftime('%X')
        self.messages.append((self.robot_id, self.avatar_robot, text, stamp))
        self.chat_messages.refresh()

    def create_chatbox(self):
        def send_user() -> None:
            stamp = datetime.utcnow().strftime('%X')
            self.messages.append((self.user_id, None, text.value, stamp))
            if self._debug_echo:
                self.messages.append((self.robot_id, self.avatar_robot, text.value, stamp))
            text.value = ''
            self.chat_messages.refresh()

        anchor_style = r'a:link, a:visited {color: inherit !important; text-decoration: none; font-weight: 500}'
        scrollbar_style = r'''
            .scroll::-webkit-scrollbar {
                width: 10px;
            }
            .scroll::-webkit-scrollbar-track {
                background: #f1f1f1;
            }
            .scroll::-webkit-scrollbar-thumb {
                background: #888;
            }
            .scroll::-webkit-scrollbar-thumb:hover {
                background: #555;
            }
            .scroll {
                overflow-y: scroll;
                padding-right: 20px;  # add right padding to the element
            }
            '''
        ui.add_head_html(f'<style>{anchor_style} {scrollbar_style}</style>')

        chatbox_card = ui.card().classes('w-full max-w-3xl mx-auto my-6')
        with chatbox_card:
            # client.connected()  # chat_messages(...) uses run_javascript which is only possible after connecting
            with ui.row().classes('w-full no-wrap h-[500px] scroll'):  # change class to "scroll"
                with ui.column().classes('w-full items-stretch'):  # here we add 'w-full'
                    self.chat_messages(self.user_id)
            with ui.row().classes('w-full no-wrap items-center'):
                #with ui.avatar(): # .on('click', lambda: ui.open(main)):
                #    ui.image(avatar)
                text = ui.input(placeholder='Talk with Chappity').on('keydown.enter', send_user) \
                    .props('rounded outlined input-class=mx-3').classes('flex-grow')
        return chatbox_card


if __name__ in {'__main__', '__mp_main__'}:
    app.add_static_files("/images", "../images")
    chatbox = ChatBox()
    chatbox._debug_echo = True
    chatbox_card = chatbox.create_chatbox()
    ui.run()
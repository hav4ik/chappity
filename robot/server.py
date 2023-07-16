"""
This module implements a websocket server that can be used to send messages to a client.
The code is written almost fully by GPT-4 (I only made few modifications). Full link to the chat here:
https://chat.openai.com/share/22827538-60fd-45d7-919c-079f22290891
"""


import asyncio
import websockets
from threading import Thread
import logging
import pprint


class Server:
    def __init__(self, on_message=None, port=8765, fully_async_mode=True):
        """
        :param on_message: A function that takes in a message and a connection and is called when a message is received
        :param port: The port to run the server on
        :param fully_async_mode: If True, on_message will be called in a new thread. If False, on_message will be called
            in the same thread as the server.
        """
        self.server = None
        self.thread = None
        self.connections = set()
        self.on_message = on_message
        self.port = port
        self.fully_async_mode = fully_async_mode
        logging.basicConfig(level=logging.INFO)

    async def handler(self, websocket, path):
        logging.info(f"Client connected: {websocket.remote_address}")
        self.connections.add(websocket)
        try:
            while True:
                try:
                    message = await websocket.recv()
                    if self.on_message:
                        if self.fully_async_mode:
                            asyncio.create_task(self.on_message(message, websocket))
                        else:
                            await self.on_message(message, websocket)
                except (websockets.exceptions.ConnectionClosedOK, websockets.exceptions.ConnectionClosedError) as e:
                    print(f"Connection closed: {e}")
                    break
                except websockets.exceptions.PayloadTooBig:
                    print("Received message too large. Closing connection.")
                    await websocket.close(code=1009)
                    break
                except websockets.exceptions.InvalidMessage:
                    print("Received invalid message. Closing connection.")
                    await websocket.close(code=1007)
                    break
        finally:
            self.connections.remove(websocket)
            logging.info(f"Client disconnected: {websocket.remote_address}")
            logging.info("Current connections:")
            logging.info(pprint.pformat([str(sock.remote_address) for sock in self.connections]))

    def send_message(self, message):
        for connection in self.connections:
            asyncio.run(connection.send(message))

    def send_message_to(self, message, connection):
        asyncio.run(connection.send(message))

    def start(self):
        self.thread = Thread(target=self.run)
        self.thread.start()

    def run(self):
        asyncio.run(self.start_server())

    async def start_server(self):
        async with websockets.serve(self.handler, 'localhost', self.port):
            await asyncio.Future()  # runs forever

    def stop(self):
        if self.server:
            self.server.close()
            asyncio.run(self.server.wait_closed())


# Example usage
if __name__ == "__main__":
    async def on_message(message, connection):
        print(f"Server received: {message}; Echoing back to client!")
        await connection.send(message)

    server = Server(on_message=on_message)
    server.start()

    try:
        while True:
            message = input("Enter message to send: ")
            server.send_message(message)
    except KeyboardInterrupt:
        server.stop()

"""
Client for connecting to the server. The client will attempt to reconnect to the server if the connection is lost.
This code is written almost fully by GPT-4 (I only made a few modifications). Full link to the chat here:
https://chat.openai.com/share/22827538-60fd-45d7-919c-079f22290891
"""

import asyncio
import websockets
from threading import Thread
import time
import logging


class Client:
    def __init__(self, on_message=None, max_retries=-1, retry_interval=5, server_ip="localhost", server_port=8765):
        """
        :param on_message: A function that takes in a message and a connection and is called when a message is received
        :param max_retries: The maximum number of times to retry connecting to the server. -1 means infinite retries.
        :param retry_interval: The number of seconds to wait between retries.
        :param server_ip: The IP address of the server to connect to.
        :param server_port: The port of the server to connect to.
        """
        self.client = None
        self.thread = None
        self.websocket = None
        self.on_message = on_message
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self.server_ip = server_ip
        self.server_port = server_port
        logging.basicConfig(level=logging.INFO)

    async def handler(self):
        retry_count = 0
        while self.max_retries < 0 or retry_count < self.max_retries:
            try:
                self.websocket = await websockets.connect(f'ws://{self.server_ip}:{self.server_port}')
                logging.info(f"Connected to server at ws://{self.server_ip}:{self.server_port}")
                while True:
                    response = await self.websocket.recv()
                    if self.on_message:
                        self.on_message(response, self)
            except (websockets.exceptions.ConnectionClosedOK, websockets.exceptions.ConnectionClosedError) as e:
                print(f"Connection closed: {e}")
                self.websocket = None
            except websockets.exceptions.PayloadTooBig:
                print("Received message too large. Disconnecting.")
                await self.websocket.close()
                self.websocket = None
                break
            except websockets.exceptions.InvalidMessage:
                print("Received invalid message. Disconnecting.")
                await self.websocket.close()
                self.websocket = None
                break
            except OSError:
                print("Failed to connect. Retrying...")
                retry_count += 1
                time.sleep(self.retry_interval)

    def start(self):
        self.thread = Thread(target=self.run)
        self.thread.start()

    def run(self):
        asyncio.run(self.handler())

    def send_message(self, message):
        if self.websocket:
            asyncio.run(self.websocket.send(message))

    def stop(self):
        if self.client:
            self.client.close()
            asyncio.run(self.client.wait_closed())


# Example usage
if __name__ == "__main__":
    def on_message(message, client):
        print(f"Client received: {message}")

    client = Client(on_message)
    client.start()

    try:
        while True:
            message = input("Enter message to send: ")
            client.send_message(message)
    except KeyboardInterrupt:
        client.stop()

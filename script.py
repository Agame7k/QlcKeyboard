import asyncio
import websockets
from pynput import keyboard
# This script listens for key presses and sends messages to QLC+ when a key is pressed
async def set_widget_value(websocket, widget_id, value):
    message = f"{widget_id}|{value}"
    await websocket.send(message)
    response = await websocket.recv()
    print(f"Response from QLC+: {response}")

async def main():
    host = "192.168.1.157:9999/qlcplusWS"  # Update with your QLC+ host
    # Update with your widget IDs
    widget_id_R = "25"
    widget_id_space = "26"
    widget_id_Q = "27"
    widget_id_U = "29"
    #value is typically 255 for buttons but can be different for other widgets
    value = 255

    key_queue = asyncio.Queue()
    pressed_keys = set()
    # check if the key is pressed and if it is not already pressed, add it to the set and send the message
    def on_press(key):
        try:
            if key.char == 'r' and 'r' not in pressed_keys:
                pressed_keys.add('r')
                asyncio.run_coroutine_threadsafe(key_queue.put((widget_id_R, value)), loop)
            if key.char == 'q' and 'q' not in pressed_keys:
                pressed_keys.add('q')
                asyncio.run_coroutine_threadsafe(key_queue.put((widget_id_Q, value)), loop)
            if key.char == 'u' and 'u' not in pressed_keys:
                pressed_keys.add('u')
                asyncio.run_coroutine_threadsafe(key_queue.put((widget_id_U, value)), loop)
        except AttributeError:
            if key == keyboard.Key.space and keyboard.Key.space not in pressed_keys:
                pressed_keys.add(keyboard.Key.space)
                asyncio.run_coroutine_threadsafe(key_queue.put((widget_id_space, value)), loop)
    # check if the key is released and if it is in the set, remove it from the set
    def on_release(key):
        try:
            if key.char == 'r':
                pressed_keys.discard('r')
            if key.char == 'q':
                pressed_keys.discard('q')
            if key.char == 'u':
                pressed_keys.discard('u')
        except AttributeError:
            if key == keyboard.Key.space:
                pressed_keys.discard(keyboard.Key.space)
    # start the listener
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    # connect to the websocket and send the message
    while True:
        try:
            async with websockets.connect(f"ws://{host}") as websocket:
                while True:
                    widget_id, value = await key_queue.get()
                    await set_widget_value(websocket, widget_id, value)
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed with error: {e}. Reconnecting...")
            await asyncio.sleep(5)  # Wait before reconnecting
        except Exception as e:
            print(f"Unexpected error: {e}. Reconnecting...")
            await asyncio.sleep(5)  # Wait before reconnecting

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
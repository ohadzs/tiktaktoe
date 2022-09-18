
from pynput import keyboard
import time
import threading
import concurrent.futures


def on_press(key):
    if key == keyboard.Key.space:
        print(key)
        print(type(key))
        print(f'pressing')


def on_release(key):
    return False


def sleep(seconds):
    time.sleep(seconds)
    return 'done'


# Collect events until released
with concurrent.futures.ThreadPoolExecutor() as executor:
    with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        print('hi')
        future = executor.submit(sleep, 5)
        return_value = future.result()
        print(return_value)


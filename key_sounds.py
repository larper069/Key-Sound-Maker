#!/usr/bin/env python3
import os
import sys

# Force Pygame to connect to PipeWire/PulseAudio
os.environ["SDL_AUDIODRIVER"] = "pulse"

import pygame
from pynput import keyboard

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Initialize Pygame audio mixer
try:
    pygame.mixer.quit()
except Exception:
    pass

pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.mixer.set_num_channels(16)

# Helper function to safely load sound files with fallback
def load_sound(filename, fallback_sound=None):
    path = os.path.join(SCRIPT_DIR, filename)
    if os.path.exists(path):
        try:
            snd = pygame.mixer.Sound(path)
            snd.set_volume(1.0)
            print(f"Loaded: {filename}")
            return snd
        except Exception as e:
            print(f"Failed loading {filename}: {e}")

    if fallback_sound:
        print(f"Fallback for {filename} -> using default click sound")
        return fallback_sound
    return None

# Load base default sound first
default_sound = load_sound("click.wav")
if not default_sound:
    print("ERROR: click.wav is missing! Please place click.wav in key folder")
    sys.exit(1)

# Load specialized sounds (or fallback to click.wav if missing)
space_sound = load_sound("space.wav", fallback_sound=default_sound)
enter_sound = load_sound("enter.wav", fallback_sound=default_sound)
mod_sound   = load_sound("mod.wav", fallback_sound=default_sound)
num_sound   = load_sound("num.wav", fallback_sound=default_sound)

# Grouping special keys
ENTER_KEYS = {keyboard.Key.enter, keyboard.Key.backspace, keyboard.Key.tab, keyboard.Key.delete}
MODIFIER_KEYS = {
    keyboard.Key.shift, keyboard.Key.shift_r,
    keyboard.Key.ctrl, keyboard.Key.ctrl_r,
    keyboard.Key.alt, keyboard.Key.alt_r,
    keyboard.Key.cmd, keyboard.Key.cmd_r
}

pressed_keys = set()

def get_sound_for_key(key):
    # 1. Spacebar
    if key == keyboard.Key.space:
        return space_sound

    # 2. Big keys (Enter, Backspace, Tab, Delete)
    if key in ENTER_KEYS:
        return enter_sound

    # 3. Modifier keys (Shift, Ctrl, Alt, Meta)
    if key in MODIFIER_KEYS:
        return mod_sound

    # 4. Numbers & Symbols
    if hasattr(key, 'char') and key.char is not None:
        if key.char.isdigit() or not key.char.isalnum():
            return num_sound

    # 5. Default letters (A-Z)
    return default_sound

def on_press(key):
    if key in pressed_keys:
        return
    pressed_keys.add(key)

    sound_to_play = get_sound_for_key(key)
    sound_to_play.play()

def on_release(key):
    if key in pressed_keys:
        pressed_keys.remove(key)

print("\nKey sound daemon running with multi-key sound groups! Press Ctrl+C to stop.")

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    try:
        listener.join()
    except KeyboardInterrupt:
        print("\nExiting key sound daemon.")

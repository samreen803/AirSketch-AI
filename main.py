import os
import time
import math
import copy
import json
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import cv2
import mediapipe as mp
from PIL import Image, ImageDraw, ImageTk


APP_TITLE = "AirSketch AI - Virtual Painter"
SAVE_DIR = "Saved_Drawings"
os.makedirs(SAVE_DIR, exist_ok=True)

PALETTE = [
    ("Red", "#ff2020"),
    ("Blue", "#2878ff"),
    ("Green", "#12a84a"),
    ("Yellow", "#ffd92e"),
    ("Black", "#161616"),
    ("Orange", "#ff8c24"),
    ("Purple", "#a64dff"),
    ("White", "#ffffff"),
]

SHAPES = ["Freehand", "Line", "Rectangle", "Circle", "Triangle", "Star", "Arrow"]


class AirSketchApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1650x950")
        self.root.minsize(1100, 700)
        self.root.configure(bg="#eaf4ff")

        self.color_name = "Red"
        self.color = "#ff2020"
        self.shape = "Freehand"
        self.eraser = False
        self.fill_shapes = False
        self.brush_size = tk.IntVar(value=8)

        self.strokes = []
        self.redo_stack = []
        self.current_stroke = None
        self.shape_start = None
        self.preview_item = None

        self.gesture_text = tk.StringVar(value="Camera: opening...")
        self.camera = None
        self.hands = None
        self.camera_running = False
        self.voice_busy = False

        self.last_action = 0.0
        self.action_delay = 0.8
        self.smoothed_pointer = None
        self.pointer_last_time = 0.0

        # Second hand controls canvas pan and zoom.
        self.view_scale = 1.0
        self.view_pan_x = 0.0
        self.view_pan_y = 0.0
        self.control_hand_anchor = None

        # Lesson recording and replay.
        self.lesson_events = []
        self.record_lesson = True
        self.replaying = False
        self.replay_after_id = None
        self.replay_index = 0
        self.pre_replay_strokes = None

        # User-configurable gesture shortcuts.
        self.shortcut_path = os.path.join(SAVE_DIR, "gesture_shortcuts.json")
        self.gesture_shortcuts = self.load_gesture_shortcuts()
        self.shortcut_candidate = None
        self.shortcut_candidate_since = 0.0
        self.shortcut_fired = False
        self.shortcut_cooldown_until = 0.0

        self.build_ui()
        self.bind_keys()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(200, self.start_camera)

    def build_ui(self):
        top = tk.Frame(
            self.root,
            bg="#f7fbff",
            height=132,
            highlightbackground="#d6e7f7",
            highlightthickness=1
        )
        top.pack(side="top", fill="x", padx=4, pady=(4, 2))
        top.pack_propagate(False)

        brand = tk.Frame(top, bg="#f7fbff")
        brand.pack(side="left", padx=(14, 12), pady=16)

        tk.Label(
            brand,
            text="AirSketch AI",
            bg="#f7fbff",
            fg="#102d4b",
            font=("Arial", 21, "bold")
        ).pack(anchor="w")

        tk.Label(
            brand,
            text="Gesture Drawing",
            bg="#f7fbff",
            fg="#60758b",
            font=("Arial", 10)
        ).pack(anchor="w")

        tk.Frame(top, bg="#c3d5e7", width=2).pack(
            side="left", fill="y", pady=16, padx=4
        )

        self.color_buttons = {}
        palette_frame = tk.Frame(top, bg="#f7fbff")
        palette_frame.pack(side="left", padx=8, pady=12)

        for name, color in PALETTE:
            cell = tk.Frame(palette_frame, bg="#f7fbff")
            cell.pack(side="left", padx=3)

            button = tk.Button(
                cell,
                text="",
                bg=color,
                activebackground=color,
                width=3,
                height=1,
                relief="solid",
                bd=1,
                highlightthickness=2,
                highlightbackground="#dce8f2",
                command=lambda n=name, c=color: self.select_color(n, c)
            )
            button.pack(ipadx=3, ipady=9)

            tk.Label(
                cell,
                text=name,
                bg="#f7fbff",
                fg="#18324c",
                font=("Arial", 8)
            ).pack(pady=(3, 0))

            self.color_buttons[name] = button

        tk.Frame(top, bg="#c3d5e7", width=2).pack(
            side="left", fill="y", pady=16, padx=5
        )

        actions = tk.Frame(top, bg="#f7fbff")
        actions.pack(side="left", fill="both", expand=True, padx=4, pady=14)

        def make_action(label, color, command, fg="white"):
            button = tk.Button(
                actions,
                text=label,
                command=command,
                bg=color,
                fg=fg,
                activebackground=color,
                activeforeground=fg,
                font=("Arial", 9, "bold"),
                relief="flat",
                bd=0,
                width=8,
                height=3,
                cursor="hand2"
            )
            button.pack(side="left", fill="y", padx=2)
            return button

        self.brush_button = make_action(
            "BRUSH", "#087ff0", self.use_brush
        )
        self.eraser_button = make_action(
            "ERASER", "#e4eef7", self.use_eraser, "#18324c"
        )
        make_action("SAVE", "#0ba85a", self.save_drawing)
        make_action("CLEAR", "#f2313b", self.clear_canvas)
        make_action("UNDO", "#ff8b00", self.undo)
        make_action("VOICE", "#087ff0", self.start_voice_command)

        # Lesson and shortcut controls are in the top toolbar so they stay visible.
        self.record_button = make_action(
            "REC: ON", "#0ba85a", self.toggle_recording
        )
        self.replay_button = make_action(
            "REPLAY", "#ff8b00", self.start_replay
        )
        self.shortcut_button = make_action(
            "GESTURES", "#60758b", self.open_shortcut_settings
        )

        body = tk.Frame(self.root, bg="#eaf4ff")
        body.pack(fill="both", expand=True, padx=4)

        sidebar = tk.Frame(
            body,
            bg="#f5faff",
            width=220,
            highlightbackground="#d6e7f7",
            highlightthickness=1
        )
        sidebar.pack(side="left", fill="y", padx=(0, 4), pady=2)
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="Brush Size",
            bg="#f5faff",
            fg="#18324c",
            font=("Arial", 13, "bold")
        ).pack(anchor="w", padx=16, pady=(18, 4))

        tk.Scale(
            sidebar,
            from_=2,
            to=35,
            orient="horizontal",
            variable=self.brush_size,
            bg="#f5faff",
            fg="#18324c",
            activebackground="#087ff0",
            troughcolor="#cbd9e7",
            highlightthickness=0,
            bd=0
        ).pack(fill="x", padx=14)

        tk.Frame(sidebar, bg="#cdddea", height=1).pack(
            fill="x", padx=16, pady=12
        )

        tk.Label(
            sidebar,
            text="Shapes",
            bg="#f5faff",
            fg="#18324c",
            font=("Arial", 13, "bold")
        ).pack(anchor="w", padx=16, pady=(0, 8))

        self.shape_buttons = {}
        for shape in SHAPES:
            button = tk.Button(
                sidebar,
                text=shape,
                anchor="w",
                padx=14,
                command=lambda s=shape: self.select_shape(s),
                bg="#eaf1f7",
                fg="#18324c",
                activebackground="#087ff0",
                activeforeground="white",
                font=("Arial", 11),
                relief="flat",
                bd=0,
                height=1,
                cursor="hand2"
            )
            button.pack(fill="x", padx=14, pady=2)
            self.shape_buttons[shape] = button

        tk.Frame(sidebar, bg="#cdddea", height=1).pack(
            fill="x", padx=16, pady=10
        )

        fill_row = tk.Frame(sidebar, bg="#f5faff")
        fill_row.pack(fill="x", padx=16, pady=4)

        tk.Label(
            fill_row,
            text="Fill Shapes",
            bg="#f5faff",
            fg="#18324c",
            font=("Arial", 11, "bold")
        ).pack(side="left")

        self.fill_button = tk.Button(
            fill_row,
            text="OFF",
            command=self.toggle_fill,
            bg="#d8e3ee",
            fg="#18324c",
            activebackground="#087ff0",
            relief="flat",
            width=6,
            cursor="hand2"
        )
        self.fill_button.pack(side="right")

        tk.Label(
            sidebar,
            text="Shape Color",
            bg="#f5faff",
            fg="#18324c",
            font=("Arial", 11, "bold")
        ).pack(anchor="w", padx=16, pady=(14, 5))

        self.selected_color_preview = tk.Label(
            sidebar,
            text="",
            bg=self.color,
            height=2,
            relief="solid",
            bd=1
        )
        self.selected_color_preview.pack(fill="x", padx=14)

        stage = tk.Frame(
            body,
            bg="white",
            highlightbackground="#d6e7f7",
            highlightthickness=1
        )
        stage.pack(side="left", fill="both", expand=True, pady=2)

        self.canvas = tk.Canvas(
            stage,
            bg="white",
            highlightthickness=0,
            cursor="crosshair"
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.mouse_down)
        self.canvas.bind("<B1-Motion>", self.mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.mouse_up)
        self.canvas.bind("<Configure>", lambda event: self.redraw())

        self.camera_label = tk.Label(
            stage,
            text="LIVE CAMERA - Starting...",
            bg="#eef3f8",
            fg="#18324c",
            font=("Arial", 9),
            anchor="center",
            relief="solid",
            bd=1
        )
        self.camera_label.place(
            relx=0.99, rely=0.18, anchor="ne",
            width=440, height=330
        )
        self.camera_label.lift()

        tk.Label(
            stage,
            textvariable=self.gesture_text,
            bg="#eaf4ff",
            fg="#18324c",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=6
        ).place(relx=0.01, rely=0.02, anchor="nw")

        tk.Label(
            stage,
            text="Press V = Voice Command     Press Q = Exit",
            bg="#fff3c4",
            fg="#18324c",
            font=("Arial", 11, "bold"),
            padx=14,
            pady=10,
            relief="solid",
            bd=1
        ).place(relx=0.99, rely=0.09, anchor="ne")

        footer = tk.Frame(
            self.root,
            bg="#dceeff",
            height=48,
            highlightbackground="#c7e0f8",
            highlightthickness=1
        )
        footer.pack(side="bottom", fill="x", padx=4, pady=(2, 4))
        footer.pack_propagate(False)

        tk.Label(
            footer,
            text="1 Hand = Draw   |   2nd Hand = Pan / Zoom",
            bg="#dceeff",
            fg="#18324c",
            font=("Arial", 11, "bold")
        ).pack(side="left", padx=18)

        tk.Label(
            footer,
            text="Hand Tracking   Gesture Drawing   Shapes   Voice Commands",
            bg="#dceeff",
            fg="#176e50",
            font=("Arial", 10, "bold")
        ).pack(side="right", padx=18)

        self.select_color("Red", "#ff2020")
        self.select_shape("Freehand")

    def bind_keys(self):
        self.root.bind("<KeyPress-q>", lambda event: self.close())
        self.root.bind("<KeyPress-Q>", lambda event: self.close())
        self.root.bind("<KeyPress-s>", lambda event: self.save_drawing())
        self.root.bind("<KeyPress-S>", lambda event: self.save_drawing())
        self.root.bind("<KeyPress-c>", lambda event: self.clear_canvas())
        self.root.bind("<KeyPress-C>", lambda event: self.clear_canvas())
        self.root.bind("<KeyPress-z>", lambda event: self.undo())
        self.root.bind("<KeyPress-y>", lambda event: self.redo())
        self.root.bind("<KeyPress-e>", lambda event: self.use_eraser())
        self.root.bind("<KeyPress-b>", lambda event: self.use_brush())
        self.root.bind("<KeyPress-v>", lambda event: self.start_voice_command())
        self.root.bind("<KeyPress-V>", lambda event: self.start_voice_command())

    # Gesture shortcut settings

    def load_gesture_shortcuts(self):
        defaults = {
            "Thumbs Up": "Save",
            "Fist": "No Action",
            "Open Palm": "No Action",
            "Pinch": "No Action"
        }
        try:
            with open(self.shortcut_path, "r", encoding="utf-8") as file:
                defaults.update(json.load(file))
        except (OSError, ValueError, AttributeError):
            pass
        return defaults

    def open_shortcut_settings(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Gesture Shortcuts")
        dialog.configure(bg="#f5faff")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="Choose an action for each gesture",
            bg="#f5faff",
            fg="#18324c",
            font=("Arial", 12, "bold")
        ).pack(padx=18, pady=(16, 10), anchor="w")

        actions = [
            "No Action", "Save", "Undo", "Redo", "Brush", "Eraser",
            "Toggle Fill", "Replay Lesson", "Toggle Recording"
        ]
        variables = {}

        for gesture in ("Thumbs Up", "Fist", "Open Palm", "Pinch"):
            row = tk.Frame(dialog, bg="#f5faff")
            row.pack(fill="x", padx=18, pady=4)

            tk.Label(
                row,
                text=gesture,
                width=14,
                anchor="w",
                bg="#f5faff",
                fg="#18324c"
            ).pack(side="left")

            variable = tk.StringVar(
                value=self.gesture_shortcuts.get(gesture, "No Action")
            )
            tk.OptionMenu(row, variable, *actions).pack(side="right")
            variables[gesture] = variable

        def save_settings():
            self.gesture_shortcuts = {
                gesture: variable.get()
                for gesture, variable in variables.items()
            }
            try:
                with open(self.shortcut_path, "w", encoding="utf-8") as file:
                    json.dump(self.gesture_shortcuts, file, indent=2)
                self.gesture_text.set("Gesture shortcuts saved")
            except OSError as error:
                messagebox.showerror(
                    "Could not save",
                    f"Shortcut settings could not be saved:\n{error}"
                )
            dialog.destroy()

        tk.Button(
            dialog,
            text="Save Shortcuts",
            command=save_settings,
            bg="#087ff0",
            fg="white",
            relief="flat",
            padx=12,
            pady=6
        ).pack(pady=14)

    def classify_custom_gesture(self, hand):
        landmarks = hand.landmark
        index_up, middle_up, ring_up, pinky_up = self.fingers_up(hand)

        thumb_up = landmarks[4].y < landmarks[3].y - 0.02
        thumb_index_distance = math.hypot(
            landmarks[4].x - landmarks[8].x,
            landmarks[4].y - landmarks[8].y
        )

        fingers = (index_up, middle_up, ring_up, pinky_up)

        if thumb_up and not any(fingers):
            return "Thumbs Up"
        if not any(fingers):
            return "Fist"
        if (
            thumb_index_distance < 0.055
            and index_up
            and not middle_up
            and not ring_up
            and not pinky_up
        ):
            return "Pinch"
        if index_up and middle_up and ring_up and pinky_up:
            return "Open Palm"
        return None

    def handle_custom_shortcut(self, hand):
        gesture = self.classify_custom_gesture(hand)
        now = time.monotonic()

        if gesture is None:
            self.shortcut_candidate = None
            self.shortcut_candidate_since = 0.0
            self.shortcut_fired = False
            return False

        if gesture != self.shortcut_candidate:
            self.shortcut_candidate = gesture
            self.shortcut_candidate_since = now
            self.shortcut_fired = False
            return True

        if (
            not self.shortcut_fired
            and now - self.shortcut_candidate_since >= 0.7
            and now >= self.shortcut_cooldown_until
        ):
            action = self.gesture_shortcuts.get(gesture, "No Action")
            self.execute_shortcut_action(action)
            self.shortcut_fired = True
            self.shortcut_cooldown_until = now + 1.2

        return True

    def execute_shortcut_action(self, action):
        actions = {
            "Save": self.save_drawing,
            "Undo": self.undo,
            "Redo": self.redo,
            "Brush": self.use_brush,
            "Eraser": self.use_eraser,
            "Toggle Fill": self.toggle_fill,
            "Replay Lesson": self.start_replay,
            "Toggle Recording": self.toggle_recording
        }

        if action in actions:
            self.gesture_text.set(f"Gesture shortcut: {action}")
            actions[action]()

    # Lesson recording and replay

    def record_lesson_event(self, action):
        if self.record_lesson and not self.replaying:
            self.lesson_events.append({
                "time": time.monotonic(),
                "action": action,
                "strokes": copy.deepcopy(self.strokes)
            })
            if len(self.lesson_events) > 250:
                self.lesson_events.pop(0)

    def toggle_recording(self):
        self.record_lesson = not self.record_lesson

        if self.record_lesson:
            self.lesson_events.clear()
            self.record_button.config(text="REC: ON", bg="#0ba85a")
            self.record_lesson_event("Recording started")
            self.gesture_text.set("Lesson recording started")
        else:
            self.record_button.config(text="REC: OFF", bg="#65758b")
            self.gesture_text.set("Lesson recording paused")

    def start_replay(self):
        if self.replaying:
            self.stop_replay()
            return

        if not self.lesson_events:
            self.gesture_text.set("No lesson strokes recorded yet")
            return

        self.pre_replay_strokes = copy.deepcopy(self.strokes)
        self.replaying = True
        self.replay_index = 0
        self.replay_button.config(text="STOP")
        self.gesture_text.set("Replaying lesson...")
        self.strokes = []
        self.redraw()
        self.play_next_lesson_event()

    def play_next_lesson_event(self):
        if not self.replaying:
            return

        if self.replay_index >= len(self.lesson_events):
            self.stop_replay(restore=True)
            return

        event = self.lesson_events[self.replay_index]
        self.strokes = copy.deepcopy(event["strokes"])
        self.redraw()
        self.replay_index += 1

        if self.replay_index < len(self.lesson_events):
            current_time = event["time"]
            next_time = self.lesson_events[self.replay_index]["time"]
            delay = int(max(70, min(700, (next_time - current_time) * 400)))
        else:
            delay = 250

        self.replay_after_id = self.root.after(
            delay, self.play_next_lesson_event
        )

    def stop_replay(self, restore=True):
        if self.replay_after_id is not None:
            try:
                self.root.after_cancel(self.replay_after_id)
            except tk.TclError:
                pass
            self.replay_after_id = None

        self.replaying = False

        if restore and self.pre_replay_strokes is not None:
            self.strokes = self.pre_replay_strokes

        self.pre_replay_strokes = None
        self.replay_button.config(text="REPLAY", bg="#ff8b00")
        self.redraw()
        self.gesture_text.set("Lesson replay finished")

    # Voice commands

    def start_voice_command(self):
        if self.voice_busy:
            return

        self.voice_busy = True
        self.gesture_text.set("Voice: listening...")
        threading.Thread(
            target=self._listen_for_voice_command,
            daemon=True
        ).start()

    def _listen_for_voice_command(self):
        try:
            import speech_recognition as sr

            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.4)
                audio = recognizer.listen(
                    source, timeout=4, phrase_time_limit=5
                )

            phrase = recognizer.recognize_google(
                audio, language="en-IN"
            )
            self.root.after(
                0, lambda: self._apply_voice_command(phrase)
            )
        except Exception as error:
            message = str(error)
            self.root.after(
                0, lambda: self._voice_error(message)
            )

    def _voice_error(self, message):
        self.voice_busy = False

        if "speech_recognition" in message or "No module named" in message:
            self.gesture_text.set(
                "Voice: install SpeechRecognition and PyAudio"
            )
        elif "pyaudio" in message.lower():
            self.gesture_text.set("Voice: microphone needs PyAudio")
        elif "WaitTimeoutError" in message:
            self.gesture_text.set("Voice: no speech heard")
        else:
            self.gesture_text.set("Voice: could not hear command")

    def _apply_voice_command(self, phrase):
        self.voice_busy = False
        command = phrase.lower().strip()

        colors = {
            "red": ("Red", "#ff2020"),
            "blue": ("Blue", "#2878ff"),
            "green": ("Green", "#12a84a"),
            "yellow": ("Yellow", "#ffd92e"),
            "black": ("Black", "#161616"),
            "orange": ("Orange", "#ff8c24"),
            "purple": ("Purple", "#a64dff"),
            "white": ("White", "#ffffff")
        }

        for word, (name, color) in colors.items():
            if word in command:
                self.select_color(name, color)
                self.gesture_text.set(f"Voice: {name}")
                return

        for shape in SHAPES:
            if shape.lower() in command:
                self.select_shape(shape)
                self.gesture_text.set(f"Voice: {shape}")
                return

        if "eraser" in command:
            self.use_eraser()
        elif "brush" in command:
            self.use_brush()
        elif "save" in command:
            self.save_drawing()
        elif "clear" in command:
            self.clear_canvas()
        elif "undo" in command:
            self.undo()
        elif "redo" in command:
            self.redo()
        elif "fill" in command:
            self.toggle_fill()
        elif "exit" in command or "quit" in command:
            self.close()
            return
        else:
            self.gesture_text.set(
                f"Voice: heard '{phrase}', command not recognized"
            )
            return

        self.gesture_text.set(f"Voice: {phrase}")

    # Drawing tools

    def select_color(self, name, color):
        self.color_name = name
        self.color = color
        self.eraser = False
        self.selected_color_preview.config(bg=color)

        for button_name, button in self.color_buttons.items():
            button.config(
                relief="solid",
                bd=3 if button_name == name else 1
            )

        self.update_tools()

    def select_shape(self, shape):
        self.shape = shape

        for name, button in self.shape_buttons.items():
            button.config(
                bg="#087ff0" if name == shape else "#eaf1f7",
                fg="white" if name == shape else "#18324c"
            )

        self.shape_start = None
        self.preview_item = None
        self.redraw()

    def use_brush(self):
        self.eraser = False
        self.update_tools()

    def use_eraser(self):
        self.eraser = True
        self.update_tools()

    def update_tools(self):
        self.brush_button.config(
            bg="#087ff0" if not self.eraser else "#e4eef7",
            fg="white" if not self.eraser else "#18324c"
        )
        self.eraser_button.config(
            bg="#087ff0" if self.eraser else "#e4eef7",
            fg="white" if self.eraser else "#18324c"
        )

    def toggle_fill(self):
        self.fill_shapes = not self.fill_shapes
        self.fill_button.config(
            text="ON" if self.fill_shapes else "OFF",
            bg="#087ff0" if self.fill_shapes else "#d8e3ee",
            fg="white" if self.fill_shapes else "#18324c"
        )

    def get_style(self):
        return {
            "color": "white" if self.eraser else self.color,
            "width": 30 if self.eraser else self.brush_size.get(),
            "fill": (
                self.color
                if self.fill_shapes and not self.eraser
                else ""
            )
        }

    def make_shape(self, start, end):
        x1, y1 = start
        x2, y2 = end

        item = {
            "kind": self.shape.lower(),
            "coords": (x1, y1, x2, y2),
            **self.get_style()
        }

        if self.shape in ("Triangle", "Star", "Arrow"):
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            rx = max(5, abs(x2 - x1) / 2)
            ry = max(5, abs(y2 - y1) / 2)

            if self.shape == "Triangle":
                points = [(cx, y1), (x2, y2), (x1, y2)]

            elif self.shape == "Star":
                points = []
                for i in range(10):
                    angle = -math.pi / 2 + i * math.pi / 5
                    radius = 1 if i % 2 == 0 else 0.42
                    points.append((
                        cx + math.cos(angle) * rx * radius,
                        cy + math.sin(angle) * ry * radius
                    ))

            else:
                dx = x2 - x1
                dy = y2 - y1
                length = max(1, math.hypot(dx, dy))
                ux, uy = dx / length, dy / length
                px, py = -uy, ux
                head = min(25, max(12, length * 0.25))
                bx, by = x2 - ux * head, y2 - uy * head
                points = [
                    (x1 + px * 2, y1 + py * 2),
                    (bx + px * 2, by + py * 2),
                    (bx + px * 8, by + py * 8),
                    (x2, y2),
                    (bx - px * 8, by - py * 8),
                    (bx - px * 2, by - py * 2),
                    (x1 - px * 2, y1 - py * 2)
                ]

            item["points"] = points

        return item

    def canvas_to_world(self, x, y):
        scale = max(0.01, self.view_scale)
        return (
            (x - self.view_pan_x) / scale,
            (y - self.view_pan_y) / scale
        )

    def world_to_canvas(self, x, y):
        return (
            x * self.view_scale + self.view_pan_x,
            y * self.view_scale + self.view_pan_y
        )

    def draw_item(self, item, tag="drawing"):
        kind = item["kind"]
        color = item["color"]
        width = max(1, item["width"] * self.view_scale)
        fill = item.get("fill", "")

        if kind == "freehand":
            points = [
                self.world_to_canvas(x, y)
                for x, y in item["points"]
            ]

            if len(points) == 1:
                x, y = points[0]
                self.canvas.create_oval(
                    x - width / 2, y - width / 2,
                    x + width / 2, y + width / 2,
                    fill=color, outline=color, tags=tag
                )
            elif len(points) > 1:
                flat = [value for point in points for value in point]
                self.canvas.create_line(
                    *flat,
                    fill=color,
                    width=width,
                    capstyle=tk.ROUND,
                    joinstyle=tk.ROUND,
                    smooth=True,
                    tags=tag
                )

        elif kind in ("line", "rectangle", "circle"):
            x1, y1, x2, y2 = item["coords"]
            x1, y1 = self.world_to_canvas(x1, y1)
            x2, y2 = self.world_to_canvas(x2, y2)
            coords = (x1, y1, x2, y2)

            if kind == "line":
                self.canvas.create_line(
                    *coords, fill=color, width=width, tags=tag
                )
            elif kind == "rectangle":
                self.canvas.create_rectangle(
                    *coords, outline=color, width=width,
                    fill=fill, tags=tag
                )
            else:
                self.canvas.create_oval(
                    *coords, outline=color, width=width,
                    fill=fill, tags=tag
                )

        elif kind in ("triangle", "star", "arrow"):
            points = [
                self.world_to_canvas(x, y)
                for x, y in item["points"]
            ]
            flat = [value for point in points for value in point]
            self.canvas.create_polygon(
                *flat, outline=color, fill=fill, width=width, tags=tag
            )

    def redraw(self):
        self.canvas.delete("drawing")
        self.canvas.delete("preview")

        for item in self.strokes:
            self.draw_item(item)

        if self.preview_item:
            self.draw_item(self.preview_item, "preview")

    def mouse_down(self, event):
        if self.replaying:
            return

        point = self.canvas_to_world(event.x, event.y)

        if self.shape == "Freehand":
            self.current_stroke = {
                "kind": "freehand",
                "points": [point],
                **self.get_style()
            }
            self.strokes.append(self.current_stroke)
            self.redo_stack.clear()
        else:
            self.shape_start = point
            self.preview_item = self.make_shape(point, point)

        self.redraw()

    def mouse_move(self, event):
        if self.replaying:
            return

        point = self.canvas_to_world(event.x, event.y)

        if self.current_stroke:
            self.current_stroke["points"].append(point)
        elif self.shape_start:
            self.preview_item = self.make_shape(self.shape_start, point)

        self.redraw()

    def mouse_up(self, event):
        if self.replaying:
            return

        point = self.canvas_to_world(event.x, event.y)

        if self.current_stroke:
            self.current_stroke = None
            self.record_lesson_event("Freehand stroke")
        elif self.shape_start:
            self.strokes.append(self.make_shape(self.shape_start, point))
            self.redo_stack.clear()
            self.record_lesson_event(f"Draw {self.shape}")
            self.shape_start = None
            self.preview_item = None

        self.redraw()

    @staticmethod
    def fingers_up(hand):
        landmarks = hand.landmark
        return (
            landmarks[8].y < landmarks[6].y,
            landmarks[12].y < landmarks[10].y,
            landmarks[16].y < landmarks[14].y,
            landmarks[20].y < landmarks[18].y
        )

    def start_camera(self):
        self.gesture_text.set("Camera: opening...")
        self.camera = None

        for camera_index in (0, 1, 2):
            if os.name == "nt":
                camera = cv2.VideoCapture(
                    camera_index, cv2.CAP_DSHOW
                )
            else:
                camera = cv2.VideoCapture(camera_index)

            if camera.isOpened():
                success, _ = camera.read()
                if success:
                    self.camera = camera
                    break

            camera.release()

        if self.camera is None:
            self.camera_label.config(text="Camera unavailable")
            self.gesture_text.set(
                "Camera not found - check camera permission"
            )
            return

        try:
            self.hands = mp.solutions.hands.Hands(
                static_image_mode=False,
                max_num_hands=2,
                model_complexity=0,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        except Exception as error:
            self.camera_label.config(text="Hand detector unavailable")
            self.gesture_text.set(f"Hand detector error: {error}")
            self.camera.release()
            self.camera = None
            return

        self.camera_running = True
        self.gesture_text.set("Camera ready - show your hand")
        self.camera_loop()

    def camera_loop(self):
        if not self.camera_running:
            return

        success, frame = self.camera.read()
        if not success:
            self.gesture_text.set("Camera frame unavailable")
            self.root.after(30, self.camera_loop)
            return

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)
        detected_hands = result.multi_hand_landmarks or []

        if detected_hands:
            for hand in detected_hands:
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand, mp.solutions.hands.HAND_CONNECTIONS
                )

            if len(detected_hands) >= 2:
                self.handle_two_hand_control(detected_hands[1])
            else:
                self.control_hand_anchor = None

            self.handle_gesture(detected_hands[0])

            if len(detected_hands) >= 2:
                self.gesture_text.set(
                    "Two hands: first draws, second pans/zooms"
                )
        else:
            self.gesture_text.set(
                "Hand not detected - show palm to camera"
            )
            self.control_hand_anchor = None
            self.shortcut_candidate = None
            self.shortcut_candidate_since = 0.0
            self.shortcut_fired = False

            if self.current_stroke is not None:
                self.current_stroke = None
                self.record_lesson_event("Freehand stroke")

            self.shape_start = None
            self.preview_item = None
            self.smoothed_pointer = None
            self.pointer_last_time = 0.0

        preview = cv2.resize(frame, (510, 350))
        preview = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
        photo = ImageTk.PhotoImage(Image.fromarray(preview))
        self.camera_label.config(image=photo, text="")
        self.camera_label.image = photo

        self.redraw()
        self.root.after(15, self.camera_loop)

    def handle_two_hand_control(self, hand):
        landmarks = hand.landmark
        canvas_left = self.canvas.winfo_rootx() - self.root.winfo_rootx()
        canvas_top = self.canvas.winfo_rooty() - self.root.winfo_rooty()
        canvas_width = max(1, self.canvas.winfo_width())
        canvas_height = max(1, self.canvas.winfo_height())

        palm_x = (landmarks[0].x + landmarks[9].x) * 0.5
        palm_y = (landmarks[0].y + landmarks[9].y) * 0.5
        center_x = palm_x * self.root.winfo_width() - canvas_left
        center_y = palm_y * self.root.winfo_height() - canvas_top

        finger_spread = math.hypot(
            landmarks[4].x - landmarks[8].x,
            landmarks[4].y - landmarks[8].y
        )

        if self.control_hand_anchor is None:
            self.control_hand_anchor = (
                center_x,
                center_y,
                max(0.04, finger_spread),
                self.view_scale,
                self.view_pan_x,
                self.view_pan_y
            )
            return

        (
            anchor_x, anchor_y, anchor_spread,
            start_scale, start_pan_x, start_pan_y
        ) = self.control_hand_anchor

        zoom_ratio = max(
            0.65, min(1.65, finger_spread / anchor_spread)
        )
        self.view_scale = max(
            0.5, min(2.5, start_scale * zoom_ratio)
        )
        self.view_pan_x = start_pan_x + center_x - anchor_x
        self.view_pan_y = start_pan_y + center_y - anchor_y

        self.view_pan_x = max(
            -canvas_width * 0.8,
            min(canvas_width * 0.8, self.view_pan_x)
        )
        self.view_pan_y = max(
            -canvas_height * 0.8,
            min(canvas_height * 0.8, self.view_pan_y)
        )
        self.redraw()

    def smooth_pointer(self, x, y):
        now = time.monotonic()

        if self.smoothed_pointer is None:
            self.smoothed_pointer = (float(x), float(y))
            self.pointer_last_time = now
            return int(x), int(y)

        old_x, old_y = self.smoothed_pointer
        dt = max(0.001, now - self.pointer_last_time)
        distance = math.hypot(x - old_x, y - old_y)

        if distance < 2.5:
            self.pointer_last_time = now
            return round(old_x), round(old_y)

        speed = distance / dt
        alpha = 1.0 - math.exp(-dt / 0.075)
        alpha = min(
            0.78, max(0.16, alpha + min(0.42, speed / 1800))
        )

        new_x = old_x + alpha * (x - old_x)
        new_y = old_y + alpha * (y - old_y)
        self.smoothed_pointer = (new_x, new_y)
        self.pointer_last_time = now
        return round(new_x), round(new_y)

    def handle_gesture(self, hand):
        if self.replaying:
            return

        if self.handle_custom_shortcut(hand):
            if self.current_stroke is not None:
                self.current_stroke = None
                self.record_lesson_event("Freehand stroke")
            self.shape_start = None
            self.preview_item = None
            return

        landmarks = hand.landmark
        index_up, middle_up, ring_up, pinky_up = self.fingers_up(hand)

        raw_x = int(landmarks[8].x * self.root.winfo_width())
        raw_y = int(landmarks[8].y * self.root.winfo_height())
        screen_x, screen_y = self.smooth_pointer(raw_x, raw_y)
        now = time.time()

        # Two fingers point at the palette to select a color.
        if index_up and middle_up and not ring_up and not pinky_up:
            self.gesture_text.set("Gesture: 2 fingers - select color")

            if self.current_stroke is not None:
                self.current_stroke = None
                self.record_lesson_event("Freehand stroke")

            self.shape_start = None
            self.preview_item = None

            if now - self.last_action > self.action_delay:
                for name, button in self.color_buttons.items():
                    left = button.winfo_rootx() - self.root.winfo_rootx()
                    top = button.winfo_rooty() - self.root.winfo_rooty()
                    right = left + button.winfo_width()
                    bottom = top + button.winfo_height()

                    if (
                        left <= screen_x <= right
                        and top <= screen_y <= bottom
                    ):
                        self.select_color(name, dict(PALETTE)[name])
                        self.last_action = now
                        break

        # One raised index finger draws.
        elif (
            index_up and not middle_up and not ring_up and not pinky_up
        ):
            self.gesture_text.set("Gesture: 1 finger - draw")

            canvas_left = self.canvas.winfo_rootx() - self.root.winfo_rootx()
            canvas_top = self.canvas.winfo_rooty() - self.root.winfo_rooty()
            view_x = screen_x - canvas_left
            view_y = screen_y - canvas_top
            canvas_x, canvas_y = self.canvas_to_world(view_x, view_y)

            if (
                0 <= view_x < self.canvas.winfo_width()
                and 0 <= view_y < self.canvas.winfo_height()
            ):
                point = (canvas_x, canvas_y)

                if self.shape == "Freehand":
                    if self.current_stroke is None:
                        self.current_stroke = {
                            "kind": "freehand",
                            "points": [point],
                            **self.get_style()
                        }
                        self.strokes.append(self.current_stroke)
                        self.redo_stack.clear()
                    else:
                        self.current_stroke["points"].append(point)
                else:
                    if self.shape_start is None:
                        self.shape_start = point
                    self.preview_item = self.make_shape(
                        self.shape_start, point
                    )
            else:
                if self.current_stroke is not None:
                    self.current_stroke = None
                    self.record_lesson_event("Freehand stroke")
                self.shape_start = None
                self.preview_item = None

        # Relaxed hand finishes a stroke or shape.
        else:
            self.gesture_text.set("Gesture: hand relaxed")
            self.smoothed_pointer = None
            self.pointer_last_time = 0.0

            if self.current_stroke is not None:
                self.current_stroke = None
                self.record_lesson_event("Freehand stroke")

            if self.shape_start is not None and self.preview_item is not None:
                self.strokes.append(self.preview_item)
                self.redo_stack.clear()
                self.record_lesson_event(f"Draw {self.shape}")

            self.shape_start = None
            self.preview_item = None

    def save_drawing(self):
        path = filedialog.asksaveasfilename(
            initialdir=SAVE_DIR,
            initialfile=f"airs_ketch_{int(time.time())}.png",
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")]
        )
        if not path:
            return

        width = max(1, self.canvas.winfo_width())
        height = max(1, self.canvas.winfo_height())
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)

        for item in self.strokes:
            kind = item["kind"]
            color = item["color"]
            line_width = max(1, int(item["width"]))
            fill = item.get("fill") or None

            if kind == "freehand":
                points = item["points"]
                if len(points) == 1:
                    x, y = points[0]
                    draw.ellipse(
                        (
                            x - line_width / 2,
                            y - line_width / 2,
                            x + line_width / 2,
                            y + line_width / 2
                        ),
                        fill=color
                    )
                elif len(points) > 1:
                    draw.line(
                        points,
                        fill=color,
                        width=line_width,
                        joint="curve"
                    )
            elif kind == "line":
                draw.line(
                    item["coords"],
                    fill=color,
                    width=line_width
                )
            elif kind == "rectangle":
                draw.rectangle(
                    item["coords"],
                    outline=color,
                    fill=fill,
                    width=line_width
                )
            elif kind == "circle":
                draw.ellipse(
                    item["coords"],
                    outline=color,
                    fill=fill,
                    width=line_width
                )
            else:
                points = item["points"]
                draw.polygon(points, outline=color, fill=fill)
                if not fill:
                    draw.line(
                        points + [points[0]],
                        fill=color,
                        width=line_width
                    )

        image.save(path)
        messagebox.showinfo("Saved", f"Drawing saved:\n{path}")

    def clear_canvas(self):
        if self.replaying:
            self.stop_replay(restore=True)

        self.strokes.clear()
        self.redo_stack.clear()
        self.current_stroke = None
        self.shape_start = None
        self.preview_item = None
        self.record_lesson_event("Clear canvas")
        self.redraw()

    def undo(self):
        if self.replaying:
            self.stop_replay(restore=True)

        if self.strokes:
            self.redo_stack.append(self.strokes.pop())
            self.record_lesson_event("Undo")
            self.redraw()

    def redo(self):
        if self.replaying:
            self.stop_replay(restore=True)

        if self.redo_stack:
            self.strokes.append(self.redo_stack.pop())
            self.record_lesson_event("Redo")
            self.redraw()

    def close(self):
        self.camera_running = False

        if self.replaying:
            self.stop_replay(restore=False)

        try:
            if self.camera is not None:
                self.camera.release()
            if self.hands is not None:
                self.hands.close()
        except Exception:
            pass

        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AirSketchApp(root)
    root.mainloop()
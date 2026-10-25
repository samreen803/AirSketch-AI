import tkinter as tk
from tkinter import messagebox
import subprocess
import sys


# COLORS
BG_COLOR = "#0F172A"
CARD_COLOR = "#1E293B"
PRIMARY_COLOR = "#6366F1"
PRIMARY_HOVER = "#818CF8"
SECONDARY_COLOR = "#14B8A6"
SECONDARY_HOVER = "#2DD4BF"
DANGER_COLOR = "#EF4444"
DANGER_HOVER = "#F87171"
TEXT_COLOR = "#FFFFFF"
SUBTEXT_COLOR = "#CBD5E1"


def start_drawing():
    root.destroy()
    subprocess.Popen([sys.executable, "main.py"])


def how_to_use():
    guide = tk.Toplevel(root)
    guide.title("AirSketch AI - How to Use")
    guide.configure(bg=BG_COLOR)
    guide.attributes("-fullscreen", True)
    guide.bind("<Escape>", lambda event: guide.destroy())

    title = tk.Label(
        guide,
        text="How to Use AirSketch AI",
        font=("Arial", 30, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    )
    title.pack(pady=(24, 16))

    # Scrollable instructions so they remain visible on smaller screens.
    content = tk.Frame(guide, bg=BG_COLOR)
    content.pack(fill="both", expand=True, padx=70, pady=8)

    guide_canvas = tk.Canvas(
        content,
        bg=BG_COLOR,
        highlightthickness=0
    )
    scrollbar = tk.Scrollbar(
        content,
        orient="vertical",
        command=guide_canvas.yview
    )
    guide_canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    guide_canvas.pack(side="left", fill="both", expand=True)

    card = tk.Frame(guide_canvas, bg=CARD_COLOR, padx=40, pady=24)
    card_window = guide_canvas.create_window(
        (0, 0),
        window=card,
        anchor="nw"
    )

    def update_scroll_region(event=None):
        guide_canvas.configure(scrollregion=guide_canvas.bbox("all"))
        guide_canvas.itemconfigure(
            card_window,
            width=guide_canvas.winfo_width()
        )

    card.bind("<Configure>", update_scroll_region)
    guide_canvas.bind("<Configure>", update_scroll_region)

    instructions = [
        ("START", [
            "1. Dashboard par Start Drawing dabakar drawing app kholo.",
            "2. Camera ke saamne apna haath poora dikhayein. Roshni achhi rakhein.",
            "3. Status mein hand detected dikhne ke baad gestures use karein."
        ]),
        ("DRAWING CONTROLS", [
            "4. Ek ungli utha kar canvas par draw karein.",
            "5. Do ungliyon se top color palette par point karke color chunein.",
            "6. Sidebar se Freehand, Line, Rectangle, Circle, Triangle, Star ya Arrow chunein.",
            "7. Brush size, eraser aur Fill Shapes controls use karein.",
            "8. Save button ya S dabakar drawing save karein.",
            "9. Clear button ya C se canvas saaf karein.",
            "10. Undo ke liye Z aur Redo ke liye Y dabayein.",
            "11. Q dabakar drawing app band karein."
        ]),
        ("LESSON REPLAY", [
            "12. Toolbar mein REC: ON dikh raha ho to recording chalu hai.",
            "13. REC: OFF ho to REC button dabakar recording chalu karein.",
            "14. Recording ON rehte hue kuch draw karein.",
            "15. REPLAY dabakar apni recorded drawing dobara dekhein.",
            "16. Replay rokne ke liye REPLAY/STOP button dabayein."
        ]),
        ("TWO-HAND CANVAS CONTROL", [
            "17. Camera ke saamne dono haath dikhayein.",
            "18. Pehli detect hui hand se draw karein.",
            "19. Doosri hand ko move karke canvas pan karein.",
            "20. Doosri hand ke thumb aur index finger ko paas ya door karke zoom karein."
        ]),
        ("CUSTOM GESTURE SHORTCUTS", [
            "21. GESTURES button dabakar Gesture Shortcuts window kholein.",
            "22. Gesture ke saamne dropdown se action chunein.",
            "23. Save Shortcuts dabana zaroori hai, tabhi selection save hota hai.",
            "24. Chuna hua gesture camera ke saamne lagbhag 1 second hold karein.",
            "25. Default shortcut: Thumbs Up se Save. Baaki gestures No Action hain."
        ]),
        ("VOICE COMMANDS & CAMERA HELP", [
            "26. Voice Command ke liye V dabayein; app English command sunta hai.",
            "27. Agar Hand not detected aaye to haath camera ke saamne poora dikhayein.",
            "28. Camera lens ko dhakne wali cheezein hataayein aur lighting badhayein."
        ])
    ]

    for section_title, lines in instructions:
        tk.Label(
            card,
            text=section_title,
            font=("Arial", 15, "bold"),
            bg=CARD_COLOR,
            fg=PRIMARY_HOVER,
            anchor="w"
        ).pack(fill="x", pady=(8, 3))

        for line in lines:
            tk.Label(
                card,
                text=line,
                font=("Arial", 13),
                bg=CARD_COLOR,
                fg=SUBTEXT_COLOR,
                anchor="w",
                justify="left",
                wraplength=1000
            ).pack(fill="x", pady=3)

    # Mouse wheel scrolling on Windows
    def on_mousewheel(event):
        guide_canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    guide_canvas.bind_all("<MouseWheel>", on_mousewheel)

    def close_guide():
        guide_canvas.unbind_all("<MouseWheel>")
        guide.destroy()

    close_button = tk.Button(
        guide,
        text="← Back",
        font=("Arial", 15, "bold"),
        bg=PRIMARY_COLOR,
        fg=TEXT_COLOR,
        activebackground=PRIMARY_HOVER,
        activeforeground=TEXT_COLOR,
        relief="flat",
        width=15,
        height=2,
        command=close_guide
    )
    close_button.pack(pady=14)


def about_project():
    about = tk.Toplevel(root)
    about.title("About AirSketch AI")
    about.configure(bg=BG_COLOR)
    about.attributes("-fullscreen", True)
    about.bind("<Escape>", lambda event: about.destroy())

    title = tk.Label(
        about,
        text="About AirSketch AI",
        font=("Arial", 32, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR
    )
    title.pack(pady=45)

    card = tk.Frame(about, bg=CARD_COLOR, padx=50, pady=30)
    card.pack(padx=100, pady=10)

    tk.Label(
        card,
        text="AirSketch AI",
        font=("Arial", 26, "bold"),
        bg=CARD_COLOR,
        fg=PRIMARY_HOVER
    ).pack(pady=10)

    description = (
        "An intelligent gesture-based virtual drawing "
        "and shape drawing system."
    )

    tk.Label(
        card,
        text=description,
        font=("Arial", 18),
        bg=CARD_COLOR,
        fg=SUBTEXT_COLOR,
        wraplength=850
    ).pack(pady=15)

    features = (
        "✓ Hand tracking and gesture drawing\n"
        "✓ Color selection and drawing tools\n"
        "✓ Voice commands\n"
        "✓ Lesson recording and replay\n"
        "✓ Two-hand canvas pan and zoom\n"
        "✓ Custom gesture shortcuts\n"
        "✓ Shape drawing, fill, undo and redo\n"
        "✓ Save drawing as an image"
    )

    tk.Label(
        card,
        text=features,
        font=("Arial", 16),
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        justify="left"
    ).pack(pady=16)

    tk.Button(
        about,
        text="← Back",
        font=("Arial", 15, "bold"),
        bg=PRIMARY_COLOR,
        fg=TEXT_COLOR,
        activebackground=PRIMARY_HOVER,
        activeforeground=TEXT_COLOR,
        relief="flat",
        width=15,
        height=2,
        command=about.destroy
    ).pack(pady=25)


def logout():
    answer = messagebox.askyesno(
        "Logout",
        "Are you sure you want to logout?"
    )

    if answer:
        root.destroy()
        subprocess.Popen([sys.executable, "login.py"])


def add_hover(button, normal_color, hover_color):
    def on_enter(event):
        button.config(bg=hover_color)

    def on_leave(event):
        button.config(bg=normal_color)

    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)


# MAIN DASHBOARD
root = tk.Tk()
root.title("AirSketch AI - Dashboard")
root.attributes("-fullscreen", True)
root.configure(bg=BG_COLOR)


def exit_fullscreen(event=None):
    root.attributes("-fullscreen", False)


root.bind("<Escape>", exit_fullscreen)


# HEADER
header = tk.Frame(root, bg=BG_COLOR)
header.pack(fill="x", pady=(35, 0))

tk.Label(
    header,
    text="AirSketch AI",
    font=("Arial", 42, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR
).pack()

tk.Label(
    header,
    text="Intelligent Gesture-Based Virtual Drawing",
    font=("Arial", 17),
    bg=BG_COLOR,
    fg=SUBTEXT_COLOR
).pack(pady=8)


# WELCOME
tk.Label(
    root,
    text="Welcome to your creative workspace",
    font=("Arial", 20, "bold"),
    bg=BG_COLOR,
    fg=SECONDARY_COLOR
).pack(pady=(35, 20))


# BUTTON CARD
button_card = tk.Frame(root, bg=CARD_COLOR, padx=70, pady=30)
button_card.pack()


draw_button = tk.Button(
    button_card,
    text="🎨  Start Drawing",
    font=("Arial", 18, "bold"),
    bg=PRIMARY_COLOR,
    fg=TEXT_COLOR,
    activebackground=PRIMARY_HOVER,
    activeforeground=TEXT_COLOR,
    relief="flat",
    bd=0,
    width=25,
    height=2,
    cursor="hand2",
    command=start_drawing
)
draw_button.pack(pady=10)
add_hover(draw_button, PRIMARY_COLOR, PRIMARY_HOVER)


guide_button = tk.Button(
    button_card,
    text="📖  How to Use",
    font=("Arial", 18, "bold"),
    bg=SECONDARY_COLOR,
    fg=TEXT_COLOR,
    activebackground=SECONDARY_HOVER,
    activeforeground=TEXT_COLOR,
    relief="flat",
    bd=0,
    width=25,
    height=2,
    cursor="hand2",
    command=how_to_use
)
guide_button.pack(pady=10)
add_hover(guide_button, SECONDARY_COLOR, SECONDARY_HOVER)


about_button = tk.Button(
    button_card,
    text="ℹ  About Project",
    font=("Arial", 18, "bold"),
    bg="#334155",
    fg=TEXT_COLOR,
    activebackground="#475569",
    activeforeground=TEXT_COLOR,
    relief="flat",
    bd=0,
    width=25,
    height=2,
    cursor="hand2",
    command=about_project
)
about_button.pack(pady=10)
add_hover(about_button, "#334155", "#475569")


logout_button = tk.Button(
    button_card,
    text="🚪  Logout",
    font=("Arial", 18, "bold"),
    bg=DANGER_COLOR,
    fg=TEXT_COLOR,
    activebackground=DANGER_HOVER,
    activeforeground=TEXT_COLOR,
    relief="flat",
    bd=0,
    width=25,
    height=2,
    cursor="hand2",
    command=logout
)
logout_button.pack(pady=10)
add_hover(logout_button, DANGER_COLOR, DANGER_HOVER)


# FOOTER
tk.Label(
    root,
    text="Gesture • Voice • Drawing • Lesson Replay • Two-Hand Control",
    font=("Arial", 12),
    bg=BG_COLOR,
    fg=SUBTEXT_COLOR
).pack(side="bottom", pady=25)


root.mainloop()
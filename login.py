import tkinter as tk
from tkinter import messagebox
from database import create_table, register_user, login_user
import subprocess
import sys



# DATABASE


create_table()



# COLORS


BG = "#080B18"
CARD = "#12182B"
INPUT = "#202A42"

WHITE = "#FFFFFF"
LIGHT = "#D9DDF0"
MUTED = "#8993AE"

PURPLE = "#7657FF"
PURPLE_HOVER = "#6545F0"

CYAN = "#21D4C5"
CYAN_HOVER = "#18BCAF"

PINK = "#E85DFF"
RED = "#FF5B6E"


# MAIN WINDOW


root = tk.Tk()

root.title("AirSketch AI")
root.geometry("1250x720")
root.minsize(1000, 600)

root.configure(bg=BG)

# CENTER WINDOW


def center_window(window, width, height):

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(
        f"{width}x{height}+{x}+{y}"
    )


center_window(root, 1250, 720)


# HOVER EFFECT


def add_hover(button, normal_color, hover_color):

    button.bind(
        "<Enter>",
        lambda event: button.config(
            bg=hover_color
        )
    )

    button.bind(
        "<Leave>",
        lambda event: button.config(
            bg=normal_color
        )
    )


# OPEN DASHBOARD


def open_dashboard():

    try:

        subprocess.Popen(
            [sys.executable, "dashboard.py"]
        )

    except Exception as error:

        messagebox.showerror(
            "Error",
            "Dashboard could not be opened.\n\n"
            + str(error)
        )


# LOGIN


def login():

    username = username_entry.get().strip()
    password = password_entry.get()

    if username == "" or password == "":

        messagebox.showwarning(
            "Missing Information",
            "Please enter username and password."
        )

        return

    success = login_user(
        username,
        password
    )

    if success:

        messagebox.showinfo(
            "Login Successful",
            "Welcome to AirSketch AI!"
        )

        root.destroy()

        open_dashboard()

    else:

        messagebox.showerror(
            "Login Failed",
            "Invalid username or password."
        )

# PASSWORD SHOW / HIDE


password_visible = False


def toggle_password():

    global password_visible

    if password_visible:

        password_entry.config(
            show="*"
        )

        show_button.config(
            text="SHOW"
        )

        password_visible = False

    else:

        password_entry.config(
            show=""
        )

        show_button.config(
            text="HIDE"
        )

        password_visible = True


# REGISTER WINDOW


def open_register():

    register_window = tk.Toplevel(root)

    register_window.title(
        "AirSketch AI - Create Account"
    )

    register_window.configure(
        bg=BG
    )

    register_window.resizable(
        False,
        False
    )

    center_window(
        register_window,
        500,
        600
    )


 
    # HEADER


    tk.Label(
        register_window,
        text="AirSketch AI",
        font=("Arial", 28, "bold"),
        fg=WHITE,
        bg=BG
    ).pack(
        pady=(35, 5)
    )


    tk.Label(
        register_window,
        text="Create Account",
        font=("Arial", 13),
        fg=CYAN,
        bg=BG
    ).pack(
        pady=(0, 25)
    )


    # REGISTER CARD


    card = tk.Frame(
        register_window,
        bg=CARD,
        padx=35,
        pady=30
    )

    card.pack(
        padx=35,
        fill="both",
        expand=True
    )


    # Username

    tk.Label(
        card,
        text="Username",
        font=("Arial", 11, "bold"),
        fg=LIGHT,
        bg=CARD
    ).pack(
        anchor="w"
    )


    reg_username = tk.Entry(
        card,
        font=("Arial", 12),
        bg=INPUT,
        fg=WHITE,
        insertbackground=WHITE,
        relief="flat"
    )

    reg_username.pack(
        fill="x",
        ipady=12,
        pady=(7, 18)
    )


    # Password

    tk.Label(
        card,
        text="Password",
        font=("Arial", 11, "bold"),
        fg=LIGHT,
        bg=CARD
    ).pack(
        anchor="w"
    )


    reg_password = tk.Entry(
        card,
        font=("Arial", 12),
        bg=INPUT,
        fg=WHITE,
        insertbackground=WHITE,
        show="*",
        relief="flat"
    )

    reg_password.pack(
        fill="x",
        ipady=12,
        pady=(7, 18)
    )


    # Confirm Password

    tk.Label(
        card,
        text="Confirm Password",
        font=("Arial", 11, "bold"),
        fg=LIGHT,
        bg=CARD
    ).pack(
        anchor="w"
    )


    reg_confirm = tk.Entry(
        card,
        font=("Arial", 12),
        bg=INPUT,
        fg=WHITE,
        insertbackground=WHITE,
        show="*",
        relief="flat"
    )

    reg_confirm.pack(
        fill="x",
        ipady=12,
        pady=(7, 25)
    )


    # REGISTER FUNCTION
   
    def register():

        username = reg_username.get().strip()
        password = reg_password.get()
        confirm = reg_confirm.get()

        if username == "" or password == "":

            messagebox.showwarning(
                "Missing Information",
                "Please enter username and password.",
                parent=register_window
            )

            return


        if password != confirm:

            messagebox.showerror(
                "Password Error",
                "Passwords do not match.",
                parent=register_window
            )

            return


        success = register_user(
            username,
            password
        )


        if success:

            messagebox.showinfo(
                "Success",
                "Registration successful!",
                parent=register_window
            )

            register_window.destroy()

        else:

            messagebox.showerror(
                "Error",
                "Username already exists.",
                parent=register_window
            )


    # CREATE ACCOUNT BUTTON


    create_button = tk.Button(
        card,
        text="CREATE ACCOUNT",
        font=("Arial", 12, "bold"),
        bg=CYAN,
        fg=WHITE,
        activebackground=CYAN_HOVER,
        activeforeground=WHITE,
        relief="flat",
        borderwidth=0,
        cursor="hand2",
        command=register
    )

    create_button.pack(
        fill="x",
        ipady=12
    )

    add_hover(
        create_button,
        CYAN,
        CYAN_HOVER
    )


# BACKGROUND CANVAS


background = tk.Canvas(
    root,
    bg=BG,
    highlightthickness=0
)

background.place(
    x=0,
    y=0,
    relwidth=1,
    relheight=1
)


# DECORATIVE AURORA CIRCLES


background.create_oval(
    -250,
    -250,
    350,
    350,
    fill="#17153A",
    outline=""
)

background.create_oval(
    900,
    -220,
    1450,
    330,
    fill="#21163C",
    outline=""
)

background.create_oval(
    850,
    500,
    1400,
    1050,
    fill="#101E3D",
    outline=""
)

background.create_oval(
    -250,
    500,
    300,
    1050,
    fill="#101D38",
    outline=""
)


# CENTER CONTENT


content = tk.Frame(
    root,
    bg=BG
)

content.place(
    relx=0.5,
    rely=0.5,
    anchor="center"
)



# LOGO / TITLE


tk.Label(
    content,
    text="✦",
    font=("Arial", 30),
    fg=CYAN,
    bg=BG
).pack(
    pady=(0, 3)
)


tk.Label(
    content,
    text="AirSketch AI",
    font=("Arial", 40, "bold"),
    fg=WHITE,
    bg=BG
).pack()


tk.Label(
    content,
    text="LOGIN",
    font=("Arial", 10, "bold"),
    fg=CYAN,
    bg=BG
).pack(
    pady=(3, 25)
)


# =========================================================
# LOGIN CARD
# =========================================================

login_card = tk.Frame(
    content,
    bg=CARD,
    width=450,
    height=390
)

login_card.pack(
    padx=10
)

login_card.pack_propagate(False)



# CARD TITLE


tk.Label(
    login_card,
    text="Welcome Back",
    font=("Arial", 24, "bold"),
    fg=WHITE,
    bg=CARD
).pack(
    pady=(30, 5)
)


tk.Label(
    login_card,
    text="Enter your account details",
    font=("Arial", 10),
    fg=MUTED,
    bg=CARD
).pack(
    pady=(0, 25)
)


# USERNAME


tk.Label(
    login_card,
    text="USERNAME",
    font=("Arial", 9, "bold"),
    fg=LIGHT,
    bg=CARD
).pack(
    anchor="w",
    padx=45
)


username_entry = tk.Entry(
    login_card,
    font=("Arial", 12),
    bg=INPUT,
    fg=WHITE,
    insertbackground=WHITE,
    relief="flat"
)

username_entry.pack(
    fill="x",
    padx=45,
    ipady=11,
    pady=(6, 17)
)


# PASSWORD


tk.Label(
    login_card,
    text="PASSWORD",
    font=("Arial", 9, "bold"),
    fg=LIGHT,
    bg=CARD
).pack(
    anchor="w",
    padx=45
)


password_frame = tk.Frame(
    login_card,
    bg=INPUT
)

password_frame.pack(
    fill="x",
    padx=45,
    pady=(6, 22)
)


password_entry = tk.Entry(
    password_frame,
    font=("Arial", 12),
    bg=INPUT,
    fg=WHITE,
    insertbackground=WHITE,
    show="*",
    relief="flat"
)

password_entry.pack(
    side="left",
    fill="x",
    expand=True,
    ipady=11,
    padx=(10, 0)
)


show_button = tk.Button(
    password_frame,
    text="SHOW",
    font=("Arial", 8, "bold"),
    bg=INPUT,
    fg=CYAN,
    activebackground=INPUT,
    activeforeground=CYAN,
    relief="flat",
    borderwidth=0,
    cursor="hand2",
    command=toggle_password
)

show_button.pack(
    side="right",
    padx=10
)


# LOGIN BUTTON


login_button = tk.Button(
    login_card,
    text="LOGIN  →",
    font=("Arial", 12, "bold"),
    bg=PURPLE,
    fg=WHITE,
    activebackground=PURPLE_HOVER,
    activeforeground=WHITE,
    relief="flat",
    borderwidth=0,
    cursor="hand2",
    command=login
)

login_button.pack(
    fill="x",
    padx=45,
    ipady=12
)

add_hover(
    login_button,
    PURPLE,
    PURPLE_HOVER
)



# CREATE ACCOUNT


register_button = tk.Button(
    login_card,
    text="CREATE NEW ACCOUNT",
    font=("Arial", 9, "bold"),
    bg=CARD,
    fg=CYAN,
    activebackground=CARD,
    activeforeground=CYAN_HOVER,
    relief="flat",
    borderwidth=0,
    cursor="hand2",
    command=open_register
)

register_button.pack(
    pady=(14, 4)
)



# EXIT


exit_button = tk.Button(
    login_card,
    text="Exit",
    font=("Arial", 9),
    bg=CARD,
    fg=MUTED,
    activebackground=CARD,
    activeforeground=RED,
    relief="flat",
    borderwidth=0,
    cursor="hand2",
    command=root.destroy
)

exit_button.pack()



# ENTER KEY = LOGIN


root.bind(
    "<Return>",
    lambda event: login()
)



# START APPLICATION


root.mainloop()
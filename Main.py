import tkinter as tk
from tkinter import messagebox
import pickle
import os
from cryptography.fernet import Fernet, InvalidToken
import binascii

def center_window(size, window):
    """Centers the window on the screen."""
    window_width = size[0]
    window_height = size[1]
    window_x = int((window.winfo_screenwidth() / 2) - (window_width / 2))
    window_y = int((window.winfo_screenheight() / 2) - (window_height / 2))

    window_geometry = f'{window_width}x{window_height}+{window_x}+{window_y}'
    window.geometry(window_geometry)
    return

# Generate a key for encryption
def generate_key():
    return Fernet.generate_key()

# Save the key to a file
def save_key(key, key_file='secret.key'):
    with open(key_file, 'wb') as keyfile:
        keyfile.write(key)

# Load the key from a file
def load_key(key_file='secret.key'):
    with open(key_file, 'rb') as keyfile:
        return keyfile.read()

# Encrypt data
def encrypt_data(data, key):
    fernet = Fernet(key)
    return fernet.encrypt(pickle.dumps(data))

# Decrypt data
def decrypt_data(data, key):
    fernet = Fernet(key)
    return pickle.loads(fernet.decrypt(data))

# Initialize main window
root = tk.Tk()
root.title("Hoyo Games Daily Check-in Receiver")

# Set the custom icon
icon_path = 'image.png'
if os.path.exists(icon_path):
    root.iconphoto(True, tk.PhotoImage(file=icon_path))

# Define window size and center it
size = (400, 300)  # Width x Height for the Tk root
center_window(size, root)
root.resizable(False, False)  # Disable window resizing

# File to store login data
login_data_file = 'login_data.pkl'
key_file = 'secret.key'

# Generate and save the key if it does not exist
if not os.path.exists(key_file):
    save_key(generate_key(), key_file)

# Load the encryption key
key = load_key(key_file)

def load_login_data():
    """Loads saved login data from file, if it exists."""
    if os.path.exists(login_data_file):
        try:
            with open(login_data_file, 'rb') as f:
                encrypted_data = f.read()
                return decrypt_data(encrypted_data, key)
        except (InvalidToken, pickle.UnpicklingError, binascii.Error) as e:
            # Handle decryption errors by removing corrupted data file
            print(f"Error loading login data: {e}")
            os.remove(login_data_file)
    return {"username": "", "password": "", "games": {"HI3": False, "HSR": False, "GI": False, "ZZZ": False}, "remember_me": False}

def save_login_data(username, password, game_selections, remember_me):
    """Saves login data to file."""
    data = {"username": username, "password": password, "games": game_selections, "remember_me": remember_me}
    encrypted_data = encrypt_data(data, key)
    with open(login_data_file, 'wb') as f:
        f.write(encrypted_data)

def save_remember_me():
    """Saves the 'remember me' state and current selections if 'remember me' is enabled."""
    if chk_remember_var.get():
        save_login_data(txt_username.get(), txt_password.get(), {
            "HI3": chk_hi3_var.get(),
            "HSR": chk_hsr_var.get(),
            "GI": chk_gi_var.get(),
            "ZZZ": chk_zzz_var.get()
        }, True)
    else:
        # Clear saved data if 'remember me' is disabled
        if os.path.exists(login_data_file):
            os.remove(login_data_file)

def save_games():
    """Saves the state of the game checkboxes only if 'remember me' is enabled."""
    if chk_remember_var.get():
        save_login_data(txt_username.get(), txt_password.get(), {
            "HI3": chk_hi3_var.get(),
            "HSR": chk_hsr_var.get(),
            "GI": chk_gi_var.get(),
            "ZZZ": chk_zzz_var.get()
        }, True)

# Load saved login data
login_data = load_login_data()

# Username label and entry
lbl_username = tk.Label(root, text="Username")
lbl_username.grid(column=0, row=0, padx=5, pady=5, sticky='E')
txt_username = tk.Entry(root, width=20)
txt_username.grid(column=1, row=0, padx=5, pady=5, columnspan=3, sticky='W')
txt_username.insert(0, login_data["username"])

# Password label and entry
lbl_password = tk.Label(root, text="Password")
lbl_password.grid(column=0, row=1, padx=5, pady=5, sticky='E')
txt_password = tk.Entry(root, width=20, show='*')
txt_password.grid(column=1, row=1, padx=5, pady=5, columnspan=3, sticky='W')
txt_password.insert(0, login_data["password"])

# Label for game selection checkboxes
lbl_games = tk.Label(root, text="Select games to check-in:")
lbl_games.grid(column=0, row=2, pady=10, padx=5, sticky='W')

# Create frame for checkboxes to manage their layout
frame = tk.Frame(root)
frame.grid(column=0, row=3, columnspan=4)

# Game selection checkboxes
chk_hi3_var = tk.BooleanVar(value=login_data["games"]["HI3"])
chk_hsr_var = tk.BooleanVar(value=login_data["games"]["HSR"])
chk_gi_var = tk.BooleanVar(value=login_data["games"]["GI"])
chk_zzz_var = tk.BooleanVar(value=login_data["games"]["ZZZ"])

chk_hi3 = tk.Checkbutton(frame, text="HI3", variable=chk_hi3_var, command=save_games)
chk_hi3.grid(column=0, row=0, padx=10)

chk_hsr = tk.Checkbutton(frame, text="HSR", variable=chk_hsr_var, command=save_games)
chk_hsr.grid(column=1, row=0, padx=10)

chk_gi = tk.Checkbutton(frame, text="GI", variable=chk_gi_var, command=save_games)
chk_gi.grid(column=2, row=0, padx=10)

chk_zzz = tk.Checkbutton(frame, text="ZZZ", variable=chk_zzz_var, command=save_games)
chk_zzz.grid(column=3, row=0, padx=10)

# Label to display the result of user action
lbl_result = tk.Label(root, text="")
lbl_result.grid(column=0, row=5, columnspan=4, pady=10)

# 'Remember me' checkbox variable
chk_remember_var = tk.BooleanVar(value=login_data["remember_me"])

def clicked():
    """Handles the click event of the main button."""
    username = txt_username.get()
    password = txt_password.get()
    selected_games = {
        "HI3": chk_hi3_var.get(),
        "HSR": chk_hsr_var.get(),
        "GI": chk_gi_var.get(),
        "ZZZ": chk_zzz_var.get()
    }

    selected_game_names = [game for game, selected in selected_games.items() if selected]

    res = f"Username: {username}\nPassword: {password}\nSelected games: {', '.join(selected_game_names)}"
    lbl_result.configure(text=res)

    if chk_remember_var.get():
        save_login_data(username, password, selected_games, chk_remember_var.get())
    else:
        if os.path.exists(login_data_file):
            os.remove(login_data_file)

# Main button widget
btn = tk.Button(root, text="Click me", fg="red", command=clicked)
btn.grid(column=1, row=6, pady=10)

# Create menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Add 'Remember me' option to the menu
options_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Options", menu=options_menu)
options_menu.add_checkbutton(label="Remember me", variable=chk_remember_var, command=save_remember_me)

# Run the main loop
root.mainloop()

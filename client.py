import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, filedialog, messagebox
from database import register_user, verify_user
import os
from pygame import mixer
from plyer import notification
from config import HOST, PORT  # Import from config

# Initialize pygame mixer
mixer.init()

# Path to the notification sound file
NOTIFICATION_SOUND = "notification.mp3"


class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # Hide the window until connection is confirmed
        self.is_muted = False

        self.username = self.authenticate_user()
        if not self.username:
            return

        # Connect to server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((HOST, PORT))

        self.client.send(f"{self.username}:{self.password}".encode())

        response = self.client.recv(1024).decode()

        if response == "SERVER_FULL":
            messagebox.showerror("Error", "Server is full! Try again later.")
            self.client.close()
            self.root.destroy()
            return
        elif response == "LOGIN_FAILED":
            messagebox.showerror("Error", "Invalid credentials!")
            self.client.close()
            self.root.destroy()
            return
        elif response == "LOGIN_SUCCESS":
            messagebox.showinfo(
                "Success", "Successfully connected to the server!")
        else:
            messagebox.showerror("Error", "Unexpected server response!")
            self.client.close()
            self.root.destroy()
            return

        # Connection successful—show the Tkinter window
        self.root.deiconify()

        # UI Setup
        self.text_area = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, state='disabled', height=20, width=90)
        self.text_area.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        self.entry = tk.Entry(root, width=40)
        self.entry.grid(row=1, column=0, padx=10, pady=10)

        self.send_button = tk.Button(
            root, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=3, pady=3)

        self.file_button = tk.Button(
            root, text="Send File", command=self.send_file)
        self.file_button.grid(row=1, column=2, padx=3, pady=3)

        self.mute_button = tk.Button(
            root, text="🔊 Mute", command=self.toggle_mute)
        self.mute_button.grid(row=1, column=3, padx=3, pady=3)

        # Start listening for messages
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def authenticate_user(self):
        """Handles user authentication via login or registration."""
        while True:
            choice = simpledialog.askstring(
                "Authentication", "Login (L) or Register (R)?").strip().lower()
            if choice not in ['l', 'r']:
                messagebox.showerror("Error", "Invalid choice! Enter L or R.")
                continue

            username = simpledialog.askstring(
                "Username", "Enter your username:")
            password = simpledialog.askstring(
                "Password", "Enter your password:", show='*')

            if not username or not password:
                messagebox.showerror(
                    "Error", "Username and password cannot be empty!")
                continue

            if choice == 'r':
                success = register_user(username, password)
                if success:
                    messagebox.showinfo(
                        "Success", "Registration successful! You can now log in.")
                else:
                    messagebox.showerror("Error", "Username already exists!")
            elif choice == 'l':
                if verify_user(username, password):
                    messagebox.showinfo("Success", "Login successful!")
                    self.password = password
                    return username
                else:
                    messagebox.showerror(
                        "Error", "Invalid username or password!")

    def send_message(self):
        """Sends a message to the server."""
        message = self.entry.get()
        if message:
            self.client.send(message.encode())
            self.entry.delete(0, tk.END)

    def send_file(self):
        """Handles sending a file to the server."""
        file_path = filedialog.askopenfilename(title="Select a file")
        if not file_path:
            return

        filename = os.path.basename(file_path)
        filesize = os.path.getsize(file_path)

        try:
            # Notify server about the file transfer
            self.client.send(f"FILE_TRANSFER:{filename}:{filesize}".encode())

            with open(file_path, "rb") as file:
                while chunk := file.read(4096):
                    self.client.send(chunk)

            messagebox.showinfo(
                "Success", f"File '{filename}' sent successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send file: {e}")

    def receive_messages(self):
        """Receives messages from the server and updates the UI."""
        while True:
            try:
                message = self.client.recv(1024).decode()
                if not message:
                    break

                self.show_notification("New Message", message)

                self.text_area.config(state=tk.NORMAL)
                self.text_area.insert(tk.END, message + "\n")
                self.text_area.config(state=tk.DISABLED)
                self.text_area.yview(tk.END)
            except:
                break

    def show_notification(self, title, message):
        """Displays a system notification and plays a sound."""
        self.play_sound()
        try:
            notification.notify(title=title, message=message, timeout=3)
        except Exception as e:
            print("Notification Error:", e)

    def toggle_mute(self):
        """Toggles notification sound on/off."""
        self.is_muted = not self.is_muted
        self.mute_button.config(text="🔇 Unmute" if self.is_muted else "🔊 Mute")

    def play_sound(self):
        """Plays a sound alert when a new message arrives."""
        if not self.is_muted and os.path.exists(NOTIFICATION_SOUND):
            mixer.music.load(NOTIFICATION_SOUND)
            mixer.music.play()


root = tk.Tk()
app = ChatClient(root)
root.mainloop()

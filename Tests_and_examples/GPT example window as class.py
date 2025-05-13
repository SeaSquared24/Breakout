import tkinter as tk


class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("My Tkinter Window")
        self.root.geometry("400x300")

        self.label = tk.Label(self.root, text="Hello, Tkinter!")
        self.label.pack(pady=20)


# Create the main window and run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()

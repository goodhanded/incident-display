import tkinter as tk

root = tk.Tk()
root.title("Place Geometry Test")

# Give the window a size so 'place' has an area to work with
root.geometry("600x400")

root.configure(bg="black")

label = tk.Label(
    root,
    text="Hello from place()!",
    font=("Helvetica", 32, "bold"),
    fg="white",
    bg="black"
)

# Place the label in the center of the root
label.place(relx=0.5, rely=0.5, anchor="center")

root.mainloop()
#!/usr/bin/env python3

import tkinter as tk
from incidents.IncidentDisplay import IncidentDisplay

def main():
  def on_escape(event):
      root.quit()  # or root.destroy()
  root = tk.Tk()
  root.bind("<Escape>", on_escape)
  root.config(cursor="none")
  root.overrideredirect(True)
  root.attributes("-fullscreen", True)
  IncidentDisplay(root)
  root.mainloop()

if __name__ == "__main__":
  main()
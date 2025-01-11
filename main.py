#!/usr/bin/env python3
import tkinter as tk
from display import IncidentDisplay
from rewards import *
from data import fetch_data
from config import Config
from environment import determine_environment

def configure(root):
  root.config(cursor="none")
  root.overrideredirect(True)
  root.attributes("-fullscreen", True)
  root.geometry("1920x1080")
  root.configure(background="black")
  root.columnconfigure(0, weight=1)
  root.rowconfigure(0, weight=1)
  root.bind("<Escape>", lambda event: root.quit())

def main():
  root = tk.Tk()
  environment = determine_environment()
  config = Config(environment)
  configure(root)
  IncidentDisplay(root, config)
  root.mainloop()

if __name__ == "__main__":
  main()
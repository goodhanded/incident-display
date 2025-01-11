import tkinter as tk
from tkinter import N, W, E, S
from rewards import *
from quotes import IntegrityQuotes
from data import fetch_data
import datetime

BG_COLOR = "black"
SECONDARY_COLOR = "white"
PRIMARY_FONT_FAMILY = "Helvetica"

def pluralize(word, count):
  return word + "s" if count != 1 else word

class IncidentPanel:
  def __init__(self, root, name, primary_color):
    self.root = root
    self.root.configure(bg=BG_COLOR)

    self.name_label = tk.Label(self.root, text=name, fg=primary_color, bg=BG_COLOR, font=(PRIMARY_FONT_FAMILY, 96))
    self.progress_label = tk.Label(self.root, text="...", fg=SECONDARY_COLOR, bg=BG_COLOR, font=(PRIMARY_FONT_FAMILY, 48))
    self.reward_label = tk.Label(self.root, text="", fg=primary_color, bg=BG_COLOR, font=(PRIMARY_FONT_FAMILY, 24))
    self.minor_rewards_label = tk.Label(self.root, text="", fg=SECONDARY_COLOR, bg=BG_COLOR, font=(PRIMARY_FONT_FAMILY, 18))

    self.name_label.pack(pady=(50, 0))
    self.progress_label.pack(pady=50)
    self.reward_label.pack()
    self.minor_rewards_label.pack(pady=50)

  def update(self, progress, rewards):

    if progress == 0:
      self.progress_label.config(text="Today is a\nDay of Integrity")
    else:
      self.progress_label.config(text=f"{progress} Days\nof Integrity!")

    todays_reward = rewards.todays_reward(progress)
    next_reward = rewards.next_unearned_reward(progress)
    earned_rewards = rewards.earned_rewards(progress)

    if todays_reward:
      self.reward_label.config(text=f"Today's Reward:\n{todays_reward.description}!")
    elif next_reward:
      days_remaining = next_reward.days_remaining(progress)
      self.reward_label.config(text=f"{days_remaining} more {pluralize('day', days_remaining)} for\n{next_reward.description}!")
      earned_rewards_text = "\n".join([f" - {reward.days_remaining(progress)} {pluralize('day', reward.days_remaining(progress))} for {reward.description}" for reward in earned_rewards])
      self.minor_rewards_label.config(text=earned_rewards_text)

class DualPanelGridWithQuote:
  def __init__(self, root):
    grid = tk.Frame(root, bg=BG_COLOR)

    grid.grid(column=0, row=0, sticky=(N, W, E, S))
    grid.rowconfigure(0, weight=2)
    grid.rowconfigure(1, weight=0)
    grid.rowconfigure(2, weight=3)
    grid.columnconfigure(0, weight=2)
    grid.columnconfigure(1, weight=0)
    grid.columnconfigure(2, weight=1)
    grid.columnconfigure(3, weight=1)
    grid.columnconfigure(4, weight=0)
    grid.columnconfigure(5, weight=2)

    self.left_panel = tk.Frame(grid, bg=BG_COLOR)
    self.right_panel = tk.Frame(grid, bg=BG_COLOR)
    self.bottom_panel = tk.Frame(grid, bg=BG_COLOR)

    self.left_panel.grid(column=1, row=1)
    self.right_panel.grid(column=4, row=1)
    self.bottom_panel.grid(column=1, row=2, columnspan=4, sticky=(N, W, E, S))

class QuotePanel:
  def __init__(self, root, config):
    self.root = root
    self.interval = config.quote_interval
    self.label = tk.Label(root, text="", fg=SECONDARY_COLOR, bg=BG_COLOR, font=("Times", 20, "italic"), wraplength=1000)
    self.label.place(relx=0.5, rely=0.5, anchor="center", y=-50)
    self.quotes = IntegrityQuotes(config.quote_file)
    self.selected_quote = self.quotes.get()
    self.cycle()

  def update(self):
    self.label.config(text=self.selected_quote)
  
  def cycle(self):
    self.selected_quote = self.quotes.get()
    self.update()
    self.root.after(self.interval, self.cycle)

class IncidentDisplay:
  def __init__(self, root, config):
    self.root = root
    self.config = config

    grid = DualPanelGridWithQuote(root)

    self.aaron_panel = IncidentPanel(grid.left_panel, "Aaron", "steel blue")
    self.michael_panel = IncidentPanel(grid.right_panel, "Michael", "coral")
    self.quote_panel = QuotePanel(grid.bottom_panel, config)
    self.last_update_label = tk.Label(root, text="", font=(PRIMARY_FONT_FAMILY, 12), fg=SECONDARY_COLOR, bg=BG_COLOR)
    self.last_update_label.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor='se')

    self.cycle()

  def update(self):
    try:
      a_progress, m_progress, a_rewards, m_rewards = fetch_data(self.config)
      self.aaron_panel.update(a_progress, a_rewards)
      self.michael_panel.update(m_progress, m_rewards)
      self.last_update_label.config(text=f"Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", fg=SECONDARY_COLOR)
    except Exception as e:
      self.last_update_label.config(text=f"Error fetching data: {e}", fg="red")

  def cycle(self):
    self.update()
    self.root.after(self.config.poll_interval, self.cycle)

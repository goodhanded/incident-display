#!/usr/bin/env python3

import os
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import tkinter as tk
import platform

from dotenv import load_dotenv

EXAMPLE_TEXT = "Build Trust! No lying, cheating, stealing, or sneaking."

# 1) Determine script's directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 2) Determine the environment (dev or pi)
ENV = os.getenv('ENV')
if not ENV:
    if platform.system() == 'Darwin':  # macOS
        ENV = 'dev'
    elif platform.system() == 'Linux':
        ENV = 'pi'
    else:
        ENV = 'dev'

# 3) Build a full path to your .env file in the script directory
env_file = os.path.join(SCRIPT_DIR, f'.env.{ENV}')

# 4) Load the .env file from that path
if os.path.exists(env_file):
    load_dotenv(env_file)
else:
    raise FileNotFoundError(f"The environment file {env_file} does not exist.")

# Fetch environment variables
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
SPREADSHEET_KEY = os.getenv('SPREADSHEET_KEY')
POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', 3600))  # default to 3600 if not set

if not SERVICE_ACCOUNT_FILE or not SPREADSHEET_KEY:
    raise EnvironmentError("SERVICE_ACCOUNT_FILE and SPREADSHEET_KEY must be set in the environment variables.")

def pluralize(word, count):
    """
    Returns the plural form of a word based on the count.
    """
    return word + "s" if count != 1 else word

def get_sheets_client():
  """
  Creates and returns an authenticated gspread client
  using the service account credentials.
  """
  scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
  ]
  creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
  client = gspread.authorize(creds)
  return client

def extract_milestones(sheet):
    """
    Extracts the milestone data from the specified sheet.
    Returns a list of (threshold, reward) tuples.
    """
    # Fetch milestones (threshold, reward)
    # Assuming the first row is a header, skip it
    milestone_data = sheet.get_all_values()
    if len(milestone_data) > 0:
        milestone_data = milestone_data[1:]
    milestones = []
    for row in milestone_data:
        if len(row) >= 2 and row[0] and row[1]:
            try:
                threshold = int(row[0].strip())
                reward = row[1].strip()
                milestones.append((threshold, reward))
            except ValueError:
                # skip rows that don't have an integer threshold
                pass

    return milestones

def fetch_data():
    """
    Fetches the most recent incident date and milestone data from the spreadsheet.
    Returns:
        (last_incident_date, milestones)
        - last_incident_date: A datetime.date object for the most recent incident
        - milestones: A list of (threshold, reward) tuples
    """
    client = get_sheets_client()

    aaron_rewards_sheet = client.open_by_key(SPREADSHEET_KEY).worksheet('Aaron Rewards')
    michael_rewards_sheet = client.open_by_key(SPREADSHEET_KEY).worksheet('Michael Rewards')

    aaron_rewards = extract_milestones(aaron_rewards_sheet)
    michael_rewards = extract_milestones(michael_rewards_sheet)

    aaron_incidents = client.open_by_key(SPREADSHEET_KEY).worksheet('Aaron')
    michael_incidents = client.open_by_key(SPREADSHEET_KEY).worksheet('Michael')

    aaron_last_incident_date = find_last_incident_date(aaron_incidents)
    michael_last_incident_date = find_last_incident_date(michael_incidents)

    return aaron_last_incident_date, michael_last_incident_date, aaron_rewards, michael_rewards

def find_last_incident_date(sheet):
    # Find the most recent incident date
    # Assuming the first row is a header, skip it
    records = sheet.col_values(1)  # All values in column A
    # Remove the header
    if len(records) > 0:
        records = records[1:]
    # Remove any empty strings
    records = [row for row in records if row.strip() != '']

    # Parse dates and collect valid ones
    parsed_dates = []
    for row in records:
        try:
            # Attempt to parse the date
            parsed_date = datetime.datetime.strptime(row.strip(), "%Y-%m-%d").date()
            parsed_dates.append(parsed_date)
        except ValueError:
            # If parsing fails, skip the row (could be a malformed date or unexpected text)
            continue

    if not parsed_dates:
        # Default to some fallback if no valid incidents are recorded
        return datetime.date(2000, 1, 1)

    # Pick the most recent date
    return max(parsed_dates)

def get_days_since(last_incident_date):
  """
  Computes the number of days since the last incident based on today's date.
  """
  today = datetime.date.today()
  delta = today - last_incident_date
  return delta.days

class MilestoneStats:
    def __init__(self, days_since, milestones):
        self.days_since = days_since
        self.milestones = milestones

        # Compute next occurrence for each milestone
        self.todays_reward = None
        self.next_reward = None
        self.next_minor_milestones = []

        next_major_milestone = (999, 999, None)
        next_milestones = []
        for threshold, reward in milestones:

            if threshold == 0:
                continue  # Avoid division by zero

            # Check if this milestone is the next major one
            if days_since < threshold and threshold < next_major_milestone[0]:
                next_major_milestone = (threshold, threshold - days_since, reward)

            if days_since > 0 and days_since % threshold == 0:
                # Exactly on the milestone day
                days_to_next = 0
            else:
                # Compute the next multiple beyond today
                multiplier = (days_since // threshold) + 1
                next_threshold = threshold * multiplier
                days_to_next = next_threshold - days_since
            
            next_milestones.append((threshold, days_to_next, reward))

            # Keep track of minor milestones (milestones that have been passed once already)
            if threshold < days_since:
                self.next_minor_milestones.append((days_to_next, reward))


        # Gather all that are due today (days_to_next == 0)
        same_day_candidates = [m for m in next_milestones if m[1] == 0]
        if same_day_candidates:
            # Pick the one with the highest threshold
            last_same_day = max(same_day_candidates, key=lambda x: x[0])
            self.todays_reward = (last_same_day[1], last_same_day[2])

        # If there's a next major milestone, use that
        if next_major_milestone[2]:
            self.next_reward = (next_major_milestone[1], next_major_milestone[2])

        # otherwise, use the minor milestone with the minimum days_to_next
        elif self.next_minor_milestones:
            self.next_reward = min(self.next_minor_milestones, key=lambda x: x[0])

class IncidentPanel:
    def __init__(self, root, name, color):
        self.root = root
        self.name = name

        self.name_label = tk.Label(self.root, text=name, font=("Helvetica", 96), fg=color, bg="black")
        self.name_label.pack(pady=0)

        self.progress_label = tk.Label(self.root, text="...", font=("Helvetica", 48), fg="white", bg="black")
        self.progress_label.pack(pady=50)

        self.reward_label = tk.Label(self.root, text="...", font=("Helvetica", 24), fg=color, bg="black")
        self.reward_label.pack(pady=0)

        self.minor_rewards_label = tk.Label(self.root, text="", font=("Helvetica", 18), fg="white", bg="black")
        self.minor_rewards_label.pack(pady=10)

    def update(self, days_since, milestones):
        milestone_stats = MilestoneStats(days_since, milestones)
        minor_reward_text = ""

        # Update Progress Label
        if days_since == 0:
            progress_text = "Today is a\nDay of Integrity"
        else:
            progress_text = f"{days_since} {pluralize('Day', days_since)} of Integrity!"
    
        self.progress_label.config(text=progress_text)

        # Update Reward Labels
        if milestone_stats.todays_reward:
            reward_text = f"Today's reward:\n{milestone_stats.todays_reward[1]}!"
        else:
            reward_text = f"{milestone_stats.next_reward[0]} more {pluralize('day', milestone_stats.next_reward[0])} for\n{milestone_stats.next_reward[1]}!"
            for days_to_next, reward in milestone_stats.next_minor_milestones:
                minor_reward_text += f"\n - {days_to_next} {pluralize('day', days_to_next)}: {reward}"

        self.reward_label.config(text=reward_text)
        self.minor_rewards_label.config(text=minor_reward_text)
class IncidentDisplay:
  def __init__(self, root):
    self.root = root
    self.root.title("Days Since Last Incident")
    #self.root.geometry("1024x768")
    # wide screen
    self.root.geometry("1920x1080")
    self.root.configure(bg="black")

    # Create a container frame to manage positioning
    self.container = tk.Frame(self.root, bg="black")
    self.container.pack(fill="both", expand=True)

    # Top spacer expands vertically
    top_spacer = tk.Frame(self.container, bg="black", height=100)
    top_spacer.pack(side="top", fill="both", expand=True)

    # Main content
    content_frame = tk.Frame(self.container, bg="black")
    content_frame.pack(side="top")

    # Left column
    left_frame = tk.Frame(content_frame, bg="black")
    left_frame.pack(side="left", fill="both", expand=True)
    self.aaron_panel = IncidentPanel(left_frame, "Aaron", "goldenrod")

    # Center spacer fixed width
    center_spacer = tk.Frame(content_frame, bg="black", width=300)
    center_spacer.pack(side="left", fill="both")

    # Right column
    right_frame = tk.Frame(content_frame, bg="black")
    right_frame.pack(side="right", fill="both", expand=True)
    self.michael_panel = IncidentPanel(right_frame, "Michael", "tomato")

    # Bottom spacer expands vertically
    bottom_spacer = tk.Frame(self.container, bg="black")
    bottom_spacer.pack(side="top", fill="both", expand=True)

    self.example_label = tk.Label(bottom_spacer, text=EXAMPLE_TEXT, font=("Helvetica", 18), fg="white", bg="black")
    self.example_label.pack(pady=50)

    # Start polling in the background
    self.update_display()


  def update_display(self):
    """
    Poll the spreadsheet, update the display labels, and schedule the next poll.
    """
    try:
        aaron_last_incident_date, michael_incident_date, aaron_rewards, michael_rewards = fetch_data()

        days_since_aaron_incident = get_days_since(aaron_last_incident_date)
        days_since_michael_incident = get_days_since(michael_incident_date)

        self.aaron_panel.update(days_since_aaron_incident, aaron_rewards)
        self.michael_panel.update(days_since_michael_incident, michael_rewards)

        self.example_label.config(text=EXAMPLE_TEXT)

    except Exception as e:
        # If something goes wrong (e.g., connectivity issue, etc.)
        self.example_label.config(text=f"Error fetching data: {e}")

    # Schedule next update after POLL_INTERVAL (in ms -> * 1000)
    self.root.after(POLL_INTERVAL * 1000, self.update_display)



def main():
  def on_escape(event):
      root.quit()  # or root.destroy()
  root = tk.Tk()
  root.bind("<Escape>", on_escape)
  root.config(cursor="none")
  root.overrideredirect(True)
  root.attributes("-fullscreen", True)
  display = IncidentDisplay(root)
  root.mainloop()


if __name__ == "__main__":
  main()
#!/usr/bin/env python3

import os
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import tkinter as tk
import platform

from dotenv import load_dotenv

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


def fetch_data():
    """
    Fetches the most recent incident date and milestone data from the spreadsheet.
    Returns:
        (last_incident_date, milestones)
        - last_incident_date: A datetime.date object for the most recent incident
        - milestones: A list of (threshold, reward) tuples
    """
    client = get_sheets_client()
    sheet_incidents = client.open_by_key(SPREADSHEET_KEY).get_worksheet(0)
    sheet_milestones = client.open_by_key(SPREADSHEET_KEY).get_worksheet(1)

    # 1) Find the most recent incident date
    # Assuming the first row is a header, skip it
    incident_records = sheet_incidents.col_values(1)  # All values in column A
    # Remove the header
    if len(incident_records) > 0:
        incident_records = incident_records[1:]
    # Remove any empty strings
    incident_records = [row for row in incident_records if row.strip() != '']

    # Parse dates and collect valid ones
    parsed_dates = []
    for row in incident_records:
        try:
            # Attempt to parse the date
            parsed_date = datetime.datetime.strptime(row.strip(), "%Y-%m-%d").date()
            parsed_dates.append(parsed_date)
        except ValueError:
            # If parsing fails, skip the row (could be a malformed date or unexpected text)
            continue

    if not parsed_dates:
        # Default to some fallback if no valid incidents are recorded
        last_incident_date = datetime.date(2000, 1, 1)
    else:
        # Pick the most recent date
        last_incident_date = max(parsed_dates)

    # 2) Fetch milestones (threshold, reward)
    # Assuming the first row is a header, skip it
    milestone_data = sheet_milestones.get_all_values()
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

    return last_incident_date, milestones


def get_days_since(last_incident_date):
  """
  Computes the number of days since the last incident based on today's date.
  """
  today = datetime.date.today()
  delta = today - last_incident_date
  return delta.days



def find_next_milestone(days_since, milestones):
    """
    Given the current days_since count and a list of (threshold, reward),
    returns (days_to_next, reward).

    Behavior:
    1. If any milestones are exactly due today (days_to_next == 0),
       return the last one in the original 'milestones' order.
    2. Otherwise, return the last one in the original 'milestones' order
       among those with the minimal positive days_to_next.

    Repeating milestones are supported by computing the next multiple
    of each threshold.
    """

    # 1) Compute next occurrence for each milestone
    next_milestones = []

    for threshold, reward in milestones:
        if threshold == 0:
            continue  # Avoid division by zero

        if days_since > 0 and days_since % threshold == 0:
            # Exactly on the milestone day
            days_to_next = 0
        else:
            # Compute the next multiple beyond today
            multiplier = (days_since // threshold) + 1
            next_threshold = threshold * multiplier
            days_to_next = next_threshold - days_since
        
        next_milestones.append((threshold, days_to_next, reward))

    # 2) If no milestones exist, return (None, None)
    if not next_milestones:
        return None, None

    # 3) Gather all that are due today (days_to_next == 0)
    same_day_candidates = [m for m in next_milestones if m[1] == 0]
    if same_day_candidates:
        # Pick the last one in original list order => the last in same_day_candidates
        last_same_day = same_day_candidates[-1]
        return (last_same_day[1], last_same_day[2])

    # 4) No milestones are due today, so find the minimal positive days_to_next
    min_days = min(m[1] for m in next_milestones)
    # 5) Collect all that match this minimal days_to_next
    candidates = [m for m in next_milestones if m[1] == min_days]

    # 6) Return the last candidate among the ties
    last_candidate = candidates[-1]
    return (last_candidate[1], last_candidate[2])

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
    top_spacer = tk.Frame(self.container, bg="black")
    top_spacer.pack(side="top", fill="both", expand=True)

    # Main content
    content_frame = tk.Frame(self.container, bg="black")
    content_frame.pack(side="top")

    self.label_num_days = tk.Label(content_frame, text="Loading...", font=("Helvetica", 128), fg="white", bg="black")
    self.label_num_days.pack(pady=0)

    self.label_examples = tk.Label(content_frame, text="", font=("Helvetica", 28), fg="white", bg="black")
    self.label_examples.pack(pady=0)

    self.label_next_reward = tk.Label(content_frame, text="", font=("Helvetica", 48), fg="yellow", bg="black")
    self.label_next_reward.pack(pady=50)

    # Bottom spacer expands vertically
    bottom_spacer = tk.Frame(self.container, bg="black")
    bottom_spacer.pack(side="top", fill="both", expand=True)

    # Start polling in the background
    self.update_display()
  

  def update_display(self):
    """
    Poll the spreadsheet, update the display labels, and schedule the next poll.
    """
    try:
      last_incident_date, milestones = fetch_data()
      days_since = get_days_since(last_incident_date)
      num_days_text = f"{days_since} {pluralize('Day', days_since)} of Integrity"
      self.label_num_days.config(text=num_days_text)
      examples = "(no lying, cheating, stealing, or sneaking)"
      self.label_examples.config(text=examples)

      days_to_next, next_reward = find_next_milestone(days_since, milestones)
      if next_reward:
        if days_to_next == 0:
          reward_text = f"Today's reward: {next_reward}!"
        else:
          reward_text = f"{days_to_next} more {pluralize('day', days_to_next)} for {next_reward}!"
      else:
        reward_text = "All rewards reached! Keep it going!"
      self.label_next_reward.config(text=reward_text)

    except Exception as e:
      # If something goes wrong (e.g., connectivity issue, etc.)
      self.label_examples.config(text="Error fetching data")
      self.label_next_reward.config(text=str(e))

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
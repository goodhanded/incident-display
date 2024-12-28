import os
import tkinter as tk
import datetime
from incidents.IncidentPanel import IncidentPanel
from incidents.IntegrityQuotes import IntegrityQuotes
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import platform

# 1) Determine script's directory
#SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Get script directory from parent directory
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', 3600))  # default to 3600 if not set
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
SPREADSHEET_KEY = os.getenv('SPREADSHEET_KEY')
QUOTE_TEXT = "Build Trust! No lying, cheating, stealing, or sneaking."

if not SERVICE_ACCOUNT_FILE or not SPREADSHEET_KEY:
  raise EnvironmentError("SERVICE_ACCOUNT_FILE and SPREADSHEET_KEY must be set in the environment variables.")

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

def get_days_since(last_incident_date):
  """
  Computes the number of days since the last incident based on today's date.
  """
  today = datetime.date.today()
  delta = today - last_incident_date
  return delta.days

class IncidentDisplay:
  def __init__(self, root):
    self.root = root
    self.root.title("Days Since Last Incident")
    self.integrity_quotes = IntegrityQuotes()
    self.selected_quote = self.integrity_quotes.get_quote()

    # wide screen
    self.root.geometry("1920x1080")
    self.root.configure(bg="black")

    # Keep track of last update time
    self.last_update = datetime.datetime.now()

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

    self.quote_label = tk.Label(bottom_spacer, text=QUOTE_TEXT, font=("Times", 20, "italic"), fg="white", bg="black", wraplength=800)
    self.quote_label.pack(pady=50)
    
    # Position the last_update_label in the absolute bottom right of the window
    self.last_update_label = tk.Label(self.root, text="", font=("Helvetica", 12), fg="white", bg="black")
    self.last_update_label.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor='se')

    # Start polling in the background
    self.cycle_quote()
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

      self.refresh_quote_label()

      # Update last update time
      self.last_update = datetime.datetime.now()
      #self.last_update_label.config(text=f"Last updated: {self.last_update.strftime('%Y-%m-%d %H:%M')}")
      # Display the last update time in a more human-friendly format
      self.last_update_label.config(text=f"Last updated: {self.last_update.strftime('%Y-%m-%d %I:%M %p')}")

    except Exception as e:
      # If something goes wrong (e.g., connectivity issue, etc.)
      self.quote_label.config(text=f"Error fetching data: {e}")

    # Schedule next update after POLL_INTERVAL (in ms -> * 1000)
    self.root.after(POLL_INTERVAL * 1000, self.update_display)

  def cycle_quote(self):
    """
    Update the quote label with a new quote every 10 minutes.
    """
    self.selected_quote = self.integrity_quotes.get_quote()
    self.refresh_quote_label()
    self.root.after(60000, self.cycle_quote)

  def refresh_quote_label(self):
    """
    Refresh the quote label with a new quote.
    """
    self.quote_label.config(text=f'"{self.selected_quote.quote}"\n\n~ {self.selected_quote.author} ~')
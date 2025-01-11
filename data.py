import gspread, datetime
from oauth2client.service_account import ServiceAccountCredentials
from rewards import *
from config import Config

def get_sheets_client(service_account_file):
  """
  Creates and returns an authenticated gspread client
  using the service account credentials.
  """
  scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
  ]
  creds = ServiceAccountCredentials.from_json_keyfile_name(service_account_file, scope)
  client = gspread.authorize(creds)
  return client

def extract_rewards(sheet):
  # Assuming the first row is a header, skip it
  reward_data = sheet.get_all_values()
  if len(reward_data) > 0:
    reward_data = reward_data[1:]
  rewards = []
  for row in reward_data:
    if len(row) >= 2 and row[0] and row[1]:
      try:
        threshold = int(row[0].strip())
        description = row[1].strip()
        rewards.append(Reward(threshold, description))
      except ValueError:
        # skip rows that don't have an integer threshold
        pass

  return RewardCollection(rewards)

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
  today = datetime.date.today()
  delta = today - last_incident_date
  return delta.days

def fetch_data(config: Config):

  client = get_sheets_client(config.service_account_file)

  aaron_rewards_sheet = client.open_by_key(config.spreadsheet_key).worksheet('Aaron Rewards')
  michael_rewards_sheet = client.open_by_key(config.spreadsheet_key).worksheet('Michael Rewards')

  aaron_rewards = extract_rewards(aaron_rewards_sheet)
  michael_rewards = extract_rewards(michael_rewards_sheet)

  aaron_incidents = client.open_by_key(config.spreadsheet_key).worksheet('Aaron')
  michael_incidents = client.open_by_key(config.spreadsheet_key).worksheet('Michael')

  aaron_last_incident_date = find_last_incident_date(aaron_incidents)
  michael_last_incident_date = find_last_incident_date(michael_incidents)

  return \
    get_days_since(aaron_last_incident_date), \
    get_days_since(michael_last_incident_date), \
    aaron_rewards, \
    michael_rewards

import os
from dotenv import load_dotenv

class Config:
  def __init__(self, env):

    # Get script directory from current directory
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

    # Build a full path to your .env file in the script directory
    env_file = os.path.join(SCRIPT_DIR, f'.env.{env}')

    # Load the .env file from that path
    if os.path.exists(env_file):
      load_dotenv(env_file)
    else:
      raise FileNotFoundError(f"The environment file {env_file} does not exist.")    
    
    # Load the environment variables
    self.service_account_file = os.getenv('SERVICE_ACCOUNT_FILE')
    self.spreadsheet_key = os.getenv('SPREADSHEET_KEY')

    if not self.service_account_file or not self.spreadsheet_key:
      raise EnvironmentError("SERVICE_ACCOUNT_FILE and SPREADSHEET_KEY must be set in the environment variables.")

    self.poll_interval = int(os.getenv('POLL_INTERVAL', 30)) * 1000
    self.quote_interval = int(os.getenv('QUOTE_INTERVAL', 60)) * 1000
    self.quote_file = os.getenv('QUOTE_FILE', 'quotes.yml')
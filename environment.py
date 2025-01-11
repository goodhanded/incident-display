import platform, os

def determine_environment():
  # Determine the environment (dev or pi)
  ENV = os.getenv('ENV')
  if not ENV:
    if platform.system() == 'Darwin':  # macOS
      ENV = 'dev'
    elif platform.system() == 'Linux':
      ENV = 'pi'
    else:
      ENV = 'dev'

  return ENV
import random, yaml

class IntegrityQuotes:
	def __init__(self, file_name):
		self.quotes = []

		# load quotes	from yaml file
		with open(file_name, 'r') as file:
			data = yaml.load(file, Loader=yaml.FullLoader)
			self.quotes = data['quotes']
	
	def get(self):
		return random.choice(self.quotes)
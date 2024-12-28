import random

class Quote:
	def __init__(self, quote, author):
		self.quote = quote
		self.author = author

class IntegrityQuotes:
	def __init__(self):
		self.quotes = [
			("As I have said, the first thing is to be honest with yourself. You can never have an impact on society if you have not changed yourself. Great peacemakers are all people of integrity, of honesty, but humility.", "Nelson Mandela"),
			("Moral authority comes from following universal and timeless principles like honesty, integrity, treating people with respect.", "Stephen Covey"),
			("Have the courage to say no. Have the courage to face the truth. Do the right thing because it is right. These are the magic keys to living your life with integrity.", "W. Clement Stone"),
			("Leading with integrity and empathy requires vision and a connection to your deepest self.", "Karla McLaren"),
			("Develop your character so that you are a person of integrity.", "Peter Cain"),
			("It takes courage to create a meaningful life of integrity. It also requires good company. And practice.", "Shelly Francis"),
			("With many overhead schemes for the world's salvation, everything rests back on integrity and driving power in personal character.", "Harry Emerson Fosdick"),
			("Supporting the truth, even when it is unpopular, shows the capacity for honesty and integrity.", "Steve Brunkhorst"),
			("Our deeds determine us, as much as we determine our deeds.", "George Eliot"),
			("There are three constants in life . . . change, choice and principles.", "Stephen Covey"),
			("The development and contributing factors to good character is the continual process of understanding the components and actions of love. It is these components that provide the guidance for compassion, integrity, behaviors and actions that transcend living only for self.", "Byron R. Pulsifer"),
			("Creating a culture of integrity and accountability not only improves effectiveness, it also generates a respectful, enjoyable and life-giving setting in which to work.", "Tom Hanson"),
			("Customer retention may be best supported by operational integrity. After all, when you think about your personal relationships as well as your business relationships, you tend to stick with the folks that are really good at showing they sincerely care about you, and doing what they say they're going to do. It boils down to trust.", "L. Hunsaker"),
			("As you experience changes and breakthroughs, know that integrity, honesty and truth are the highest vibrating energies to guide you forward. Everything else will fall away.", "Molly McCord"),
			("Six essential qualities that are the key to success: Sincerity, personal integrity, humility, courtesy, wisdom, charity.", "Dr. William Menninger"),
			("The qualities of a great man are vision, integrity, courage, understanding, the power of articulation, and profundity of character.", "Dwight Eisenhower"),
			("Think P.I.G. - that's my motto. P stands for Persistence, I stands for Integrity, and G stands for Guts. These are the ingredients for a successful business and a successful life.", "Linda Chandler"),
			("Honor your commitments with integrity.", "Les Brown"),
			("It's easy to have principles when you're rich. The important thing is to have principles when you're poor.", "Ray Kroc"),
			("Trust, family and integrity are always going to be at the core of my leadership plan.", "Kristina Diviny-MacBury"),
			("One of your most prized possessions is integrity; if this is you, then you should never compromise it.", "Byron Pulsifer"),
			("To give real service you must add something which cannot be bought or measured with money, and that is sincerity and integrity.", "Donald A. Adams"),
			("I've learned that people will forget what you said, people will forget what you did, but people will never forget how you made them feel.", "Maya Angelou"),
			("There is no investment you can make which will pay you so well as the effort to scatter sunshine and good cheer through your establishment.", "Orison Swett Marden"),
			("Power really is a test of character. In the hands of a person of integrity, it is of tremendous benefit; in the hands of a tyrant, it causes terrible destruction.", "John Maxwell"),
			("I don't know a more dignified and effective workforce than one operating from a position of worth, integrity, and confidence, as well as one that excels in language of appreciation.", "Tan Sri Francis Yeoh"),
			("You could consider Wednesday as a day of the week to inspire yourself and others to accomplish all that needs to be done by the end of the week.", "Kate Summers"),
			("Some things are kind of obvious when it comes to leadership. You have to be a great communicator, have very high integrity and have tremendous perseverance and stamina.", "Suresh Basandra"),
			("Make living your life with absolute integrity and kindness your first priority.", "Richard Carlson"),
			("Integrity is the seed for achievement. It is the principle that never fails.", "Earl Nightingale"),
			("Here's a truth: principled leaders solve moral problems. They have the courage to act rightly. They consistently demonstrate principled conduct under pressure.", "Gus Lee"),
			("We must adjust to changing times and still hold to unchanging principles.", "Jimmy Carter"),
			("Live so that when your children think of fairness, caring, and integrity, they think of you.", "H. Jackson Brown, Jr."),
			("Speak with integrity. Say only what you mean. Avoid using the word to speak against yourself or to gossip about others. Use the power of your word in the direction of truth and love.", "Miguel Angel Ruiz"),
			("The support of truth takes integrity.", "Byron Pulsifer"),
			("People with integrity do what they say they are going to do. Others have excuses.", "Dr. Laura Schlessinger"),
			("The foundation stones for a balanced success are honesty, character, integrity, faith, love and loyalty.", "Zig Ziglar"),
			("The first law of leadership is that your foundation is built through integrity, character, and trust.", "Brian Cagneey"),
			("Becoming a leader is synonymous with becoming yourself. It is precisely that simple and it is also that difficult.", "Warren Bennis"),
			("The wind might cause a kite to rise, but what keeps it up there is the fact that somebody on the ground has a steady hand. You have to hold steady to your values - your integrity. It's your anchor. You let go of that... well, it isn't long before your kite comes crashing down.", "Mark Victor Hansen and Robert G. Allen"),
			("Admitting one's own faults is the first step to changing them, and it is a demonstration of true bravery and integrity.", "Philip Johnson"),
			("For those who find themselves more concerned with how much money they can accumulate for the sake of wealth alone, who find themselves stuck like glue to materialistic possessions that mean more than their personal integrity or their contribution to their fellow human beings, these traps have jaws of steel.", "Catherine Pulsifer"),
		]
	
	def get_quote(self):
		return Quote(*random.choice(self.quotes))
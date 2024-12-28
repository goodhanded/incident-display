import tkinter as tk
from incidents.MilestoneStats import MilestoneStats

def pluralize(word, count):
    """
    Returns the plural form of a word based on the count.
    """
    return word + "s" if count != 1 else word

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
class Reward:
  def __init__(self, threshold: int, description: str):
    self.threshold = threshold
    self.description = description

  def days_remaining(self, progress: int):
    # return self.threshold - progress
    # these rewards are recurring, so calculate days until next iteration
    return self.threshold - (progress % self.threshold)

class RewardCollection:
  def __init__(self, rewards):
    self.rewards = rewards

  def todays_reward(self, progress: int):
    if progress == 0:
      return None

    candidates = [reward for reward in self.rewards if progress % reward.threshold == 0]
    
    if len(candidates) == 0:
      return None

    return max(candidates, key=lambda reward: reward.threshold) # return the reward with the highest threshold

  def next_unearned_reward(self, progress):
    candidates = [reward for reward in self.rewards if progress < reward.threshold]
    if len(candidates) == 0:
      return None
    return min(candidates, key=lambda reward: reward.threshold) # return the next unearned reward with the lowest threshold

  def earned_rewards(self, progress):
    return [reward for reward in self.rewards if progress > reward.threshold] # return all rewards that have been earned before today
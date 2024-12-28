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
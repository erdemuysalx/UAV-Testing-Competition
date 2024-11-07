import random
import math
from typing import List
from aerialist.px4.drone_test import DroneTest
from aerialist.px4.obstacle import Obstacle
from testcase import TestCase


class AdvancedRandomGenerator(object):
    min_size = Obstacle.Size(2, 2, 15)
    max_size = Obstacle.Size(20, 20, 25)
    min_position = Obstacle.Position(5, 5, 0, 0)
    max_position = Obstacle.Position(50, 50, 0, 90)

    min_distance = 1
    zones = {
        'start': {
            'zone_min_position': Obstacle.Position(-20, 5, 0, 0),
            'zone_max_position': Obstacle.Position(5, 20, 0, 90)}, 
        'mid': {
            'zone_min_position': Obstacle.Position(-20, 20, 0, 0),
            'zone_max_position': Obstacle.Position(5, 35, 0, 90)},
        'end': {
            'zone_min_position': Obstacle.Position(-20, 35, 0, 0),
            'zone_max_position': Obstacle.Position(5, 50, 0, 90)}}


    def __init__(self, case_study_file: str) -> None:
        self.case_study = DroneTest.from_yaml(case_study_file)

    def generate(self, budget: int) -> List[TestCase]:
        test_cases = []
        for i in range(budget):      
            # Randomly select number of obstacles
            num_obs = random.randint(1, 3)
            # Randomly select zones for the obstacles
            selected_zones = random.sample(list(self.zones.keys()), num_obs)
            obstacles = []
            # Create obstacles for each selected zone
            for zone in selected_zones:
                # Define a mock obstacle (replace this with actual obstacle creation if needed)
                size = Obstacle.Size(
                    l=random.uniform(self.min_size.l, self.max_size.l),
                    w=random.uniform(self.min_size.w, self.max_size.w),
                    h=random.uniform(self.min_size.h, self.max_size.h),
                )
                # Try to find a non-overlapping position for the obstacle
                for attempt in range(5):  # Limit the number of attempts to avoid infinite loops
                    position = Obstacle.Position(
                        x=random.uniform(self.zones[zone]['zone_min_position'].x, self.zones[zone]['zone_max_position'].x),
                        y=random.uniform(self.zones[zone]['zone_min_position'].y, self.zones[zone]['zone_max_position'].y),
                        z=0,  # obstacles should always be place on the ground
                        r=random.uniform(self.zones[zone]['zone_min_position'].r, self.zones[zone]['zone_max_position'].r),
                    )
                    if not self.is_overlapping(position, obstacles):
                        obstacle = Obstacle(size, position)
                        obstacles.append(obstacle)
                        break
                    else:
                        print("Could not place obstacle without overlap, skipping this one.")
                
            test = TestCase(self.case_study, obstacles)
            try:
                test.execute()
                distances = test.get_distances()
                print(f"minimum_distance:{min(distances)}")
                test.plot()
                test_cases.append(test)
            except Exception as e:
                print("Exception during test execution, skipping the test")
                print(e)

        ### You should only return the test cases
        ### that are needed for evaluation (failing or challenging ones)
        return test_cases

    def is_overlapping(self, position, obstacles):
        """
        Check if the position overlaps with any existing obstacles.
        """
        for obs in obstacles:
            dist = math.sqrt((obs.position.x - position.x) ** 2 + (obs.position.y - position.y) ** 2)
            if dist < self.min_distance:
                return True
        return False

if __name__ == "__main__":
    generator = AdvancedRandomGenerator("case_studies/mission1.yaml")
    generator.generate(3)

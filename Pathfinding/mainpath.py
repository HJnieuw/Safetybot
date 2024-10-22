import bandit as bd
import agent as agent

import numpy as np


def define_epsilon():
    # Initialize the environment and epsilon values
    env = bd.CustomBanditzones()
    epsilon_values = [1.0, 0.5, 0.1, 0.05, 0.01]

    # Create an instance of EpsilonGreedyOptimizer
    optimizer = agent.EpsilonGreedyOptimizer(env, epsilon_values, n_steps=1000)

    # Run the simulation
    optimizer.run_simulation()

    # Get the best epsilon value
    best_epsilon = optimizer.get_best_epsilon()
    print(f"\nBest epsilon value: {best_epsilon}")
    return best_epsilon

def calc_schedule():
    env = bd.CustomBanditzones()
    epsilon_values = best_epsilon
    calc_schedule = agent.EpsilonGreedyOptimizer(env, epsilon_values, n_steps=50)
    calc_schedule.run_simulation()
    schedule = agent.
    
    


define_epsilon()
calc_schedule()
import bandit as bd
import agent as agent
import numpy as np

def define_epsilon():
    # Initialize the environment and epsilon values
    env = bd.CustomBanditzones()
    epsilon_values = [0.5, 0.4, 0.3, 0.2, 0.1]

    # Create an instance of EpsilonGreedyOptimizer
    optimizer = agent.EpsilonGreedyBandit(env, epsilon_values, n_steps=1000)

    # Run the simulation
    optimizer.run_simulation()

    # Get the best epsilon value
    best_epsilon = optimizer.get_best_epsilon()
    print(f"\nBest epsilon value: {best_epsilon}")
    return best_epsilon

def calc_schedule(epsilon):
    env = bd.CustomBanditzones()
    epsilon_values = [epsilon]
    calc_schedule_optimizer = agent.EpsilonGreedyBandit(env, epsilon_values, n_steps=100)
    calc_schedule_optimizer.run_simulation()

# Get the best epsilon value from define_epsilon
epsilon = define_epsilon()

# Pass the best epsilon value to calc_schedule
calc_schedule(epsilon)
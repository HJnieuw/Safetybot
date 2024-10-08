import numpy as np
import bandit as bd

# Select an environment to use
env = bd.BanditTwoArmedHighHighFixed()

# Define a list of fixed epsilon values
epsilon_values = [1.0, 0.5, 0.1, 0.05, 0.01]

# Number of steps per simulation
n_steps = 1000

# Run simulations for each epsilon value
for epsilon in epsilon_values:
    # Reset environment and tracking variables for each epsilon
    observation = env.reset()
    total_reward = 0
    mean_reward = np.zeros(len(env.p_dist))
    action_counts = np.zeros(len(env.p_dist))
    
    print(f"\nRunning simulation with epsilon = {epsilon}")

    for step in range(n_steps):
        
        if np.random.rand() < epsilon:
            # Explore: choose a random action
            action = np.random.randint(len(mean_reward))
        else:
            # Exploit: choose the action with the highest estimate
            max_reward_estimate = np.max(mean_reward)
            best_actions = np.where(mean_reward == max_reward_estimate)[0]
            action = np.random.choice(best_actions)
        
        # Take a step in the environment
        observation, reward, done, info = env.step(action)
        
        # Update counts and mean reward estimate for chosen action
        action_counts[action] += 1
        mean_reward[action] += (reward - mean_reward[action]) / action_counts[action]
        
        # Accumulate total reward
        total_reward += reward

    # Summary of results for the current epsilon
    print(f"Total reward after {n_steps} steps with epsilon {epsilon}: {total_reward}")

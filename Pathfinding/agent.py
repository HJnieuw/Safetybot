import numpy as np
import bandit as bd
import matplotlib.pyplot as plt

class EpsilonGreedyOptimizer:
    def __init__(self, env, epsilon_values, n_steps=1000):
        self.env = env
        self.epsilon_values = epsilon_values
        self.n_steps = n_steps
        self.step_rewards = {epsilon: np.zeros(n_steps) for epsilon in epsilon_values}
        self.final_avg_rewards = {}

    def run_simulation(self):
        #Runs the epsilon-greedy simulation for each epsilon value.

        for epsilon in self.epsilon_values:

            # Reset environment and tracking variables for each epsilon
            observation = self.env.reset()
            total_reward = 0
            mean_reward = np.zeros(len(self.env.p_dist))
            action_counts = np.zeros(len(self.env.p_dist))
            print(f"\nRunning simulation with epsilon = {epsilon}")

            for step in range(self.n_steps):
                if np.random.rand() < epsilon:
                    # Explore: choose a random action
                    action = np.random.randint(len(mean_reward))
                else:
                    # Exploit: choose the action with the highest estimate
                    max_reward_estimate = np.max(mean_reward)
                    best_actions = np.where(mean_reward == max_reward_estimate)[0]
                    action = np.random.choice(best_actions)

                # Take a step in the environment
                observation, reward, done, info = self.env.step(action)

                # Update counts and mean reward estimate for chosen action
                action_counts[action] += 1
                mean_reward[action] += (reward - mean_reward[action]) / action_counts[action]

                # Accumulate total reward
                total_reward += reward

                # Store the cumulative reward at this step
                self.step_rewards[epsilon][step] = total_reward

            # Calculate the final average reward for this epsilon
            self.final_avg_rewards[epsilon] = self.step_rewards[epsilon][-1] / self.n_steps

    def get_best_epsilon(self):
        # Returns the epsilon value with the highest final average reward.
        if not self.final_avg_rewards:
            raise ValueError("Simulation has not been run yet. Call run_simulation() first.")
        best_epsilon = max(self.final_avg_rewards, key=self.final_avg_rewards.get)
        return best_epsilon
    

# If this script is being run directly, execute the following code:
if __name__ == "__main__":
    # Initialize the environment and epsilon values
    env = bd.CustomBanditzones()
    epsilon_values = [1.0, 0.5, 0.1, 0.05, 0.01]

    # Create an instance of EpsilonGreedyOptimizer
    optimizer = EpsilonGreedyOptimizer(env, epsilon_values, n_steps=1000)

    # Run the simulation
    optimizer.run_simulation()

    # Get the best epsilon value
    best_epsilon = optimizer.get_best_epsilon()
    print(f"\nBest epsilon value: {best_epsilon}")

    # Plotting the average rewards over time for each epsilon value
    plt.figure(figsize=(10, 8))

    for epsilon in epsilon_values:
        # Compute average reward per step at each step
        average_rewards = optimizer.step_rewards[epsilon] / (np.arange(optimizer.n_steps) + 1)
        plt.plot(np.arange(optimizer.n_steps), average_rewards, label=f"Epsilon = {epsilon}")

    plt.title('Average Reward vs Steps for different Epsilon values')
    plt.xlabel('Steps')
    plt.ylabel('Average Reward')
    plt.legend()
    plt.grid(True)
    plt.show()

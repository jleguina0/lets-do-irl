import gym
import pylab
import numpy as np

import maxent

n_states = 400 # position - 20, velocity - 20
n_actions = 3
one_feature = 20 # number of state per one feature
q_table = np.zeros((n_states, n_actions)) # (400, 3)
feature_matrix = np.eye((n_states)) # (400, 400)

gamma = 0.99
q_learning_rate = 0.03
epochs = 10
theta_learning_rate = 0.01

np.random.seed(400)

def idx_demo(env, one_feature):
    env_low = env.observation_space.low     
    env_high = env.observation_space.high   
    env_distance = (env_high - env_low) / one_feature  

    raw_demo = np.load(file="expert_demo/expert_demo.npy")
    demonstrations = np.zeros((len(raw_demo), len(raw_demo[0]), 3))

    for x in range(len(raw_demo)):
        for y in range(len(raw_demo[0])):
            position_idx = int((raw_demo[x][y][0] - env_low[0]) / env_distance[0])
            velocity_idx = int((raw_demo[x][y][1] - env_low[1]) / env_distance[1])
            state_idx = position_idx + velocity_idx * one_feature

            demonstrations[x][y][0] = state_idx
            demonstrations[x][y][1] = raw_demo[x][y][2] 
            
    return demonstrations

def idx_state(env, state):
    env_low = env.observation_space.low
    env_high = env.observation_space.high 
    env_distance = (env_high - env_low) / one_feature 
    position_idx = int((state[0] - env_low[0]) / env_distance[0])
    velocity_idx = int((state[1] - env_low[1]) / env_distance[1])
    state_idx = position_idx + velocity_idx * one_feature
    return state_idx

def update_q_table(state, action, reward, next_state):
    q_1 = q_table[state][action]
    q_2 = reward + gamma * max(q_table[next_state])
    q_table[state][action] += q_learning_rate * (q_2 - q_1)

def get_q_table():
    return q_table


def main():
    env = gym.make('MountainCar-v0')
    demonstrations = idx_demo(env, one_feature)

    episodes, scores = [], []

    for episode in range(30000):
        state = env.reset()
        score = 0

        if episode == 1000:
            irl_rewards = maxent.maxent_irl(feature_matrix, n_actions, epochs,
                                            theta_learning_rate, demonstrations)
                
        while True:
            state_idx = idx_state(env, state)
            action = np.argmax(q_table[state_idx])
            next_state, reward, done, _ = env.step(action)
            
            next_state_idx = idx_state(env, next_state)
            if episode >= 1000:
                irl_reward = irl_rewards[state_idx]
                update_q_table(state_idx, action, irl_reward, next_state_idx)
            else:
                update_q_table(state_idx, action, reward, next_state_idx)
            
            score += reward
            state = next_state
            
            if done:
                scores.append(score)
                episodes.append(episode)
                break

        if episode % 1000 == 0:
            score_avg = np.mean(scores)
            print('{} episode score is {:.2f}'.format(episode, score_avg))
            pylab.plot(episodes, scores, 'b')
            pylab.savefig(learning_curve_file_name)
            pylab.savefig("./learning_curves/maxent_eps_30000.png")
            np.save("./results/maxent_q_table", arr=q_table)

if __name__ == '__main__':
    main()
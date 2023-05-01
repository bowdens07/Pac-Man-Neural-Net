from stable_baselines3.common.env_checker import check_env

from Game import PacManGame

env = PacManGame(lockFrameRate=True,drawGhostPaths=False,pacManLives=0,startUpTime=0,allowReplays=False, pelletTimeLimit=True, renderGraphics=True)
# It will check your custom environment and output additional warnings if needed
check_env(env)



episodes = 5
for episode in range(episodes):
    obs = env.reset()
    done = False
    while not done:
        random_action = env.action_space.sample()
        print("action",random_action)
        obs,reward,done,info = env.step(random_action)
        print('reward',reward)

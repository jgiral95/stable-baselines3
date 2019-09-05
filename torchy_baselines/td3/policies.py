import torch as th
import torch.nn as nn

from torchy_baselines.common.policies import BasePolicy


class Actor(nn.Module):
    def __init__(self, state_dim, action_dim, net_arch=None):
        super(Actor, self).__init__()

        if net_arch is None:
            net_arch = [400, 300]

        self.actor_net = nn.Sequential(
            nn.Linear(state_dim, net_arch[0]),
            nn.ReLU(),
            nn.Linear(net_arch[0], net_arch[1]),
            nn.ReLU(),
            nn.Linear(net_arch[1], action_dim),
            nn.Tanh(),
        )

    def forward(self, x):
        return self.actor_net(x)


class Critic(nn.Module):
    def __init__(self, state_dim, action_dim, net_arch=None):
        super(Critic, self).__init__()

        if net_arch is None:
            net_arch = [400, 300]

        self.q1_net = nn.Sequential(
            nn.Linear(state_dim + action_dim, net_arch[0]),
            nn.ReLU(),
            nn.Linear(net_arch[0], net_arch[1]),
            nn.ReLU(),
            nn.Linear(net_arch[1], 1),
        )

        self.q2_net = nn.Sequential(
            nn.Linear(state_dim + action_dim, net_arch[0]),
            nn.ReLU(),
            nn.Linear(net_arch[0], net_arch[1]),
            nn.ReLU(),
            nn.Linear(net_arch[1], 1),
        )

    def forward(self, obs, action):
        qvalue_input = th.cat([obs, action], dim=1)
        return self.q1_net(qvalue_input), self.q2_net(qvalue_input)

    def q1_forward(self, obs, action):
        return self.q1_net( th.cat([obs, action], dim=1))


class TD3Policy(BasePolicy):
    def __init__(self, observation_space, action_space,
                 learning_rate=1e-3, net_arch=None, device='cpu'):
        super(TD3Policy, self).__init__(observation_space, action_space, device)
        self.state_dim = self.observation_space.shape[0]
        self.action_dim = self.action_space.shape[0]
        self.net_arch = net_arch
        self._build(learning_rate)

    def _build(self, learning_rate):
        self.actor = self.make_actor()
        self.actor_target = self.make_actor()
        self.actor_target.load_state_dict(self.actor.state_dict())
        self.actor.optimizer = th.optim.Adam(self.actor.parameters(), lr=learning_rate)

        self.critic = self.make_critic()
        self.critic_target = self.make_critic()
        self.critic_target.load_state_dict(self.critic.state_dict())
        self.critic.optimizer = th.optim.Adam(self.critic.parameters(), lr=learning_rate)

    def make_actor(self):
        return Actor(self.state_dim, self.action_dim, self.net_arch).to(self.device)

    def make_critic(self):
        return Critic(self.state_dim, self.action_dim, self.net_arch).to(self.device)

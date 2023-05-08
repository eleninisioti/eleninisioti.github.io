class Agent:

    def __init__(self, init_strategy, location, radius, idx, nagents):
        self.strategy = init_strategy
        # self.color = self.colors[self.strategy_transition]
        self.color = ""
        self.location = location
        self.neighbors = self.find_neighbors(radius)
        self.idx = idx
        self.game_log = [0 for _ in range(nagents)]

    def find_neighbors(self, radius):
        neighb_locations = []
        for xdis in range(-radius, radius + 1):
            for ydis in range(-radius, radius + 1):
                new_neighb = [self.location[0] + xdis, self.location[1] + ydis]

                neighb_locations.append(new_neighb)
        self.neighbors = neighb_locations
        # neighb_locations.remove(self.location)
        return neighb_locations

    def play(self):
        "Returns 1 for cooperate and 0 for defect"
        return self.strategy


import random
import copy


class Tournament:

    def __init__(self, args):
        "Initialize tournament object."
        self.benefit = args.benefit
        self.grid_length = args.grid_length
        self.game = args.game
        self.radius = args.radius

        self.create_agents(args.init_coop, args.grid_length)
        self.payoffs = self.create_payoffs()
        self.well_mixed = args.well_mixed
        self.counter = 0

        self.rounds = args.rounds
        self.inter_per_round = args.inter_per_round

    def create_agents(self, init_coop, grid_length):
        # randomly sample location of initial cooperators
        self.agents = []
        self.nagents = self.grid_length * self.grid_length
        num_coop = int(np.floor(self.nagents * init_coop))

        # put agents in random positions in the grid
        agent_positions = random.sample(list(range(self.grid_length * self.grid_length)), self.nagents)
        coop_indexes = random.sample(agent_positions, num_coop)

        if init_coop == 0.999:
            coop_indexes = list(range(self.nagents))
            x = y = np.ceil(int(self.grid_length / 2))

            coop_indexes.remove(x + y * self.grid_length)
        for index, i in enumerate(agent_positions):
            location = [i % grid_length, i // grid_length]
            init_strategy = (i in coop_indexes)

            agent = Agent(nagents=self.nagents, idx=index, location=location, init_strategy=init_strategy,
                          radius=self.radius)
            self.agents.append(agent)

    def create_payoffs(self):
        if self.game == "PD":
            # payoffs = {'R': self.benefit - self.cost, 'P': 0, 'T': self.benefit, 'S': -self.cost}
            payoffs = {'R': 1, 'P': 0, 'T': self.benefit, 'S': 0}
        elif self.game == "Snow":
            # payoffs = {'R': self.benefit - self.cost / 2, 'P': 0, 'T': self.benefit, 'S': self.benefit - self.cost}
            payoffs = {'R': 1, 'P': 0, 'T': self.benefit, 'S': 2 - self.benefit}
        return payoffs

    def actions_to_outcome(self, action_a, action_b):
        """Converts the binary strategies to the outcome of the game. Possible outcomes are R (reward), S (sucker),
    T (traitor?), P (punishment)"""
        if action_a and action_b:
            return 'R'
        elif not action_a and not action_b:
            return 'P'
        elif action_a and not action_b:
            return 'S'
        else:
            return 'T'

    def compete(self):
        for central_agent in self.agents:
            central_agent.value = 0

            if self.well_mixed:
                neighbors = random.sample(self.agents, self.inter_per_round)
            else:
                neighbor_locs = central_agent.neighbors
                neighbors = []
                for neighbor_loc in neighbor_locs:
                    # out = [el % self.grid_length for el in neighbor_loc]
                    out = [1 if el >= 0 and el < self.grid_length else 0 for el in neighbor_loc]
                    if 0 not in out:
                        for agent in self.agents:
                            if agent.location == neighbor_loc:
                                neighbors.append(agent)

            for neighbor in neighbors:
                # print("new battle")

                # print(central_agent.idx, neighbor.idx)
                action_a = central_agent.play()

                # find neighbor based on his location
                action_b = neighbor.play()
                # neighbor.game_log[central_agent.idx] += 1
                central_agent.game_log[neighbor.idx] += 1
                outcome = self.actions_to_outcome(action_a, action_b)
                payoff = self.payoffs[outcome]
                central_agent.value += payoff

        prev_agents = copy.deepcopy(self.agents)
        for idx, central_agent in enumerate(prev_agents):

            max_value = central_agent.value
            winner_strat = central_agent.strategy
            # if not central_agent.strategy:
            #   print(central_agent.value)
            if self.well_mixed:
                neighbors = random.sample(self.agents, 8)
            else:
                neighbor_locs = central_agent.neighbors
                neighbors = []
                for neighbor_loc in neighbor_locs:
                    # folding
                    out = [el % self.grid_length for el in neighbor_loc]
                    # out = [1 if el > 0 and el < self.grid_length else 0 for el in neighbor_loc]
                    for agent in prev_agents:
                        if agent.location == neighbor_loc:
                            neighbors.append(agent)
            for neighbor in neighbors:

                if neighbor.value > max_value:
                    max_value = neighbor.value
                    winner_strat = neighbor.strategy
                    # print("changing agent ",central_agent.idx, central_agent.location, neighbor.location )

            self.agents[idx].transition = self.encode_transition(central_agent.strategy,
                                                                 winner_strat)
            self.agents[idx].strategy = winner_strat

    def play_round(self):
        # move agents according to day/night

        self.compete()
        # for agent in self.agents:
        #   agent.transition = self.encode_transition( agent.strategy, agent.strategy)
        #

        # self.agents = copy.deepcopy(prev_agents)
        log = self.collect_log()
        return log

    def encode_transition(self, prev_strat, current_strat):
        if prev_strat and current_strat:
            return 0
        elif not prev_strat and not current_strat:
            return 1
        elif not prev_strat and current_strat:
            return 2
        else:
            return 3

    def collect_log(self):
        log = {}
        width = self.grid_length
        strat_transitions = np.ones(shape=(width, width)) * 4
        for agent in self.agents:
            loc = agent.location
            strat_trans = agent.transition
            strat_transitions[loc[0], loc[1]] = strat_trans
        log["strat_transitions"] = strat_transitions

        return log

    def pop_log(self):
        log = {}
        coop_perc = np.sum([1 for agent in self.agents if agent.strategy]) / len(self.agents)
        log["coop_perc"] = coop_perc
        return log


import os
import numpy as np
import matplotlib.pyplot as plt

import asyncio


# async def plot_grid(strat_transitions, round, project):


# 0: C->C, 1: D->D, 2: D -> C, 4: C-> D
# from IPython.display import display

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


import matplotlib.pyplot as plt
import numpy as np
import time


# async def showPlots():
#
#     for step in range(20):
#
#         fig, ax = plt.subplots()
#         year_1 = [2016, 2017, 2018, 2019, 2020, 2021]
#         population_1 = np.random.randint(20,size=6)
#         plt.plot(year_1, population_1, marker='o', linestyle='--', color='g', label='Country 1')
#         plt.xlabel('Year')
#         plt.ylabel('Population (M)')
#         plt.title('Year vs Population')
#         plt.legend(loc='lower right')
#         display(fig, target="graph-area", append=False)
#         await asyncio.sleep(1)
#
#         plt.clf()
#
# asyncio.ensure_future(showPlots())


async def play_tournament(*args, **kwargs):
    config = {"project": "temp",
              "game": "PD",
              "grid_length": 30,
              "radius": 1,
              "benefit": float(benefit.value),
              "inter_per_round": 1,
              "init_coop": float(perc_coop.value),
              "rounds": int(num_rounds.value),
              "trials": 1}

    config = dotdict(config)

    tournament = Tournament(config)
    for round in range(config.rounds):
        log_round = tournament.play_round()

        strat_transitions = log_round["strat_transitions"]

        colors = {0: np.array([0, 0, 255]), 1: np.array([255, 0, 0]), 2: np.array([0, 255, 0]), 3:
            np.array([255, 255, 0]), 4: np.array([128, 128, 128])}
        data_3d = np.ndarray(shape=(strat_transitions.shape[0],
                                    strat_transitions.shape[1], 3), dtype=int)
        for i in range(0, strat_transitions.shape[0]):
            for j in range(0, strat_transitions.shape[1]):
                data_3d[i][j] = colors[strat_transitions[i][j].T]

        figure = plt.figure()
        axes = figure.add_subplot(111)
        axes.imshow(data_3d,
                    origin="lower")

        plt.title("Round " + str(round))
        plt.xlabel("$x$")
        plt.ylabel("$y$")
        display(figure, target="graph-area", append=False)

        plt.clf()
        await asyncio.sleep(0.05)




benefit = Element("benefit")
perc_coop = Element("perc_coop")
num_rounds = Element("num_rounds")
op = Element("output")

async def run_chaotic():
    config = {"project": "temp",
              "game": "PD",
              "grid_length": 30,
              "radius": 1,
              "benefit": 1.95,
              "inter_per_round": 1,
              "init_coop": 0.999,
              "rounds": 100,
              "trials": 1}

    config = dotdict(config)

    tournament = Tournament(config)
    for round in range(config.rounds):
        log_round = tournament.play_round()

        strat_transitions = log_round["strat_transitions"]

        colors = {0: np.array([0, 0, 255]), 1: np.array([255, 0, 0]), 2: np.array([0, 255, 0]), 3:
            np.array([255, 255, 0]), 4: np.array([128, 128, 128])}
        data_3d = np.ndarray(shape=(strat_transitions.shape[0],
                                    strat_transitions.shape[1], 3), dtype=int)
        for i in range(0, strat_transitions.shape[0]):
            for j in range(0, strat_transitions.shape[1]):
                data_3d[i][j] = colors[strat_transitions[i][j].T]

        figure = plt.figure()
        axes = figure.add_subplot(111)
        axes.imshow(data_3d,
                    origin="lower")

        plt.title("Round " + str(round))
        plt.xlabel("$x$")
        plt.ylabel("$y$")
        display(figure, target="graph-area", append=False)

        plt.clf()
        await asyncio.sleep(0.05)
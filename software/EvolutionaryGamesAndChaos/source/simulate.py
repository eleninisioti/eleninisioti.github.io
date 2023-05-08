import argparse
from tournament import *
import os
from visualize import plot_grid, plot_bifurcation, plot_mixed, plot_coop_evol
import pickle

import yaml

colors = {0: "blue", 1: "red", 2: "green", 3: "yellow"}


# 0: C->C, 1: D->D, 2: D -> C, 4: C-> D


def main(args):
    # initialize project's subdirs
    if not os.path.exists("../projects/" + args.project + "/plots/grids"):
        os.makedirs("../projects/" + args.project + "/plots/grids")

    for trial in range(args.trials):
        if not os.path.exists("../projects/" + args.project + "/plots/trial_" + str(trial)):
            os.makedirs("../projects/" + args.project + "/plots/trial_" + str(trial))

    log_perf = {"coop_perc": []}

    if args.bifurcation:
        benefit_values = np.linspace(1, 2.5, 10)
        fixed_points = [[] for _ in range(len(benefit_values))]

        for trial in range(args.trials):
            # fixed_points.append([])
            log_perf["coop_perc"].append([])

            for b_idx, benefit in enumerate(benefit_values):

                args.benefit = benefit
                tournament = Tournament(args)
                for round in range(args.rounds):
                    log_round = tournament.play_round()
                    if not os.path.exists("../projects/" + args.project + "/b_" + str(benefit) + "/trial_" + str(
                            trial) + "/plots/grids"):
                        os.makedirs("../projects/" + args.project + "/b_" + str(benefit) + "/trial_" + str(
                            trial) + "/plots/grids")
                    plot_grid(strat_transitions=log_round["strat_transitions"],
                              round=round, project=args.project + "/b_" + str(benefit) + "/trial_" + str(trial))

                    # consider that the last 10 rounds have converged
                    # gather performance metrics
                    pop_log = tournament.pop_log()
                    if round == (args.rounds - 1):
                        fixed_points[b_idx].append(pop_log["coop_perc"])

                    log_perf["coop_perc"][trial].append(pop_log["coop_perc"])
            # plot_coop_evol(args.project, log_perf["coop_perc"][trial], trial, night=args.night_duration, trial=trial)

        log_perf["fixed_points"] = fixed_points
        plot_bifurcation(args.project, benefit_values, fixed_points)


    else:
        if not os.path.exists("../projects/" + args.project + "/plots/grids"):
            os.makedirs("../projects/" + args.project + "/plots/grids")
        tournament = Tournament(args)
        logs = []
        for round in range(args.rounds):
            log_round = tournament.play_round()
            plot_grid(strat_transitions=log_round["strat_transitions"], round=round, project=args.project)
            logs.append(log_round)
            pop_log = tournament.pop_log()
            log_perf["coop_perc"].append(pop_log["coop_perc"])

    # ----- final saving for project ------
    with open("../projects/" + args.project + '/config.yml', 'w') as outfile:
        yaml.dump(args, outfile)
    with open('../projects/' + args.project + '/log.pickle', 'wb') as pfile:
        pickle.dump(log_perf, pfile, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--project',
                        help='Name of current project',
                        type=str,
                        default="temp")

    parser.add_argument('--game',
                        help='Name of game. Choose between PD and Snow',
                        type=str,
                        default="PD")

    parser.add_argument('--grid_length',
                        help='Length of grid in tiles ',
                        type=int,
                        default=50)

    parser.add_argument('--radius',
                        help='Neighborhood radius ',
                        type=int,
                        default=1)

    parser.add_argument('--benefit',
                        help='Benefit of cooperation.',
                        type=float,
                        default=1.9)

    parser.add_argument('--inter_per_round',
                        help='Interactions per round.',
                        type=int,
                        default=8)

    parser.add_argument('--init_coop',
                        help='Initial percentage of cooperators.',
                        type=float,
                        default=0.999)

    parser.add_argument('--rounds',
                        help='Number of evolutionary rounds.',
                        type=int,
                        default=1000)

    parser.add_argument('--trials',
                        help='Number of independent trials.',
                        type=int,
                        default=1)

    parser.add_argument('--well_mixed',
                        help='Number of evolutionary rounds.',
                        default=False,
                        action="store_true")

    parser.add_argument('--bifurcation',
                        help='Whether a bifurcation plot will be made.',
                        default=False,
                        action="store_true")

    args = parser.parse_args()
    main(args)

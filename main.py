import csv
import os
from pprint import pprint
from typing import List, Dict

from hand import Hand

LOG_FILE_PATH = "logs"

def get_all_log_files(dir_path: str) -> List[str]:
    log_files: List[str] = []
    for file_path in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, file_path)):
            log_files.append(os.path.join(dir_path, file_path))
    return log_files

def load_hands(file_path: str, name_map: Dict[str, str], all_players: List[str]) -> List[Hand]:
    hands: List[Hand] = []
    hand_txt: List[List[str]] = []

    raw_data = []
    with open(file_path, 'r') as log_file:
        reader = csv.reader(log_file)
        for row in reader:
            raw_data.append(row)

    in_hand = False
    for row in reversed(raw_data):
        if row[0].startswith("-- starting hand"):
            in_hand = True
            continue
        if row[0].startswith("-- ending hand"):
            in_hand = False
            hand_txt = preprocess_hand_txt(hand_txt, name_map)
            new_hand = Hand(hand_txt)
            if new_hand.valid:
                hands.append(new_hand)
            hand_txt = []
            continue
        if in_hand is True:
            hand_txt.append(row)

    return hands

def calculate_vpip(hands: List[Hand], user_list: List[str],
        min_player: int = 2, max_player: int = 10) -> Dict[str, float]:
    # TODO: add more general user handling
    total_hands = dict(zip(user_list, [0.0] * len(user_list)))
    vpip_hands = dict(zip(user_list, [0.0] * len(user_list)))
    vpip = dict(zip(user_list, [0.0] * len(user_list)))
    for hand in hands:
        if len(hand.players) < min_player or len(hand.players) > max_player:
            continue
        for player in hand.players:
            total_hands[player] += 1

        played_this_hand = dict(zip(user_list, [False] * len(user_list)))
        for action in hand.all_actions:
            if action.action in ["bet", "call", "raise"]:
                played_this_hand[action.player] = True
        for user in user_list:
            if played_this_hand[user] is True:
                vpip_hands[user] += 1

    for user in user_list:
        vpip[user] = vpip_hands[user] / total_hands[user]

    return vpip

def calculate_pfr(hands: List[Hand], user_list: List[str],
        min_player: int = 2, max_player: int = 10) -> Dict[str, float]:
    # TODO: add more general user handling
    total_hands = dict(zip(user_list, [0.0] * len(user_list)))
    pfr_hands = dict(zip(user_list, [0.0] * len(user_list)))
    pfr = dict(zip(user_list, [0.0] * len(user_list)))
    for hand in hands:
        if len(hand.players) < min_player or len(hand.players) > max_player:
            continue
        for player in hand.players:
            total_hands[player] += 1

        pfr_this_hand = dict(zip(user_list, [False] * len(user_list)))
        for action in hand.preflop_actions:
            if action.action == "raise":
                pfr_this_hand[action.player] = True
        for user in user_list:
            if pfr_this_hand[user] is True:
                pfr_hands[user] += 1

    for user in user_list:
        pfr[user] = pfr_hands[user] / total_hands[user]

    return pfr


def preprocess_hand_txt(hand_txt: List[List[str]], name_map: Dict[str, str]) -> List[List[str]]:
    for item in hand_txt:
        action, _, _ = item

        # make sure all users are known
        if action.startswith("The player "): # this is when a new player joins the game
            screen_name = action.split("The player ")[1].split("@")[0][1:-1] # magic string processing
            if screen_name not in name_map:
                print(f"Unknown user {screen_name}. Stopping analysis.")
                exit()

        # replace different screen names with the unique name of each player
        for screen_name, unique_name in name_map.items():
            action = action.replace(screen_name, unique_name)
        item[0] = action
    return hand_txt

def create_user_map(file_path):
    import json
    name_map: Dict[str, str] = {}
    all_players: List[str] = []
    with open(file_path) as user_file:
        name_dict = json.load(user_file)
        for unique_name, screen_names in name_dict.items():
            all_players.append(unique_name)
            for screen_name in screen_names:
                name_map[screen_name] = unique_name
        return name_map, all_players

def plot_vpip_pfr(vpip: Dict[str, float], pfr: Dict[str, float]) -> None:
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    import numpy as np
    import random

    #colors = list(mcolors.XKCD_COLORS.keys())
    #colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'tab:orange', 'tab:brown', 'tab:pink', 'tab:grey', 'tab:red']
    colors = ['black', 'grey', 'lightgrey', 'red', 'darkred', 'tomato', 'yellow', 'green', 'yellowgreen', 'lime', 'gold', 'blue', 'blueviolet', 'cornflowerblue', 'pink', 'cyan', 'orange', 'olive', 'fuchsia']
    random.shuffle(colors)

    fig, ax = plt.subplots()
    n_users = len(vpip)

    for idx, name in enumerate(vpip.keys()):
        v = vpip[name]
        p = pfr[name]

        ax.scatter(v, p, c = colors[idx], label = name, s = 80)

    font = {'family':'serif','color':'black','size':12}
    ax.legend()

    ax.set_xlabel("VPIP", fontdict = font)
    ax.set_ylabel("PFR", fontdict = font)

    ax.grid(True)

    plt.show()

def get_args():
    import argparse

    parser = argparse.ArgumentParser(
        description = "Parser for poker analysis.",
        formatter_class = argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--min-player",
        type = int,
        default = 2,
        help = "Minimum number of players to consider for analysis."
    )
    parser.add_argument(
        "--max-player",
        type = int,
        default = 10,
        help = "Maximum number of players to consider for analysis."
    )
    args = parser.parse_args()

    return args

def main():
    args = get_args()
    name_map, all_players = create_user_map("user_names.json")
    log_files = get_all_log_files(LOG_FILE_PATH)

    all_hands: List[Hand] = []
    for file_path in log_files:
        hands = load_hands(file_path, name_map, all_players)
        all_hands.extend(hands)

    vpip = calculate_vpip(all_hands, all_players, min_player = args.min_player, max_player = args.max_player)
    pfr = calculate_pfr(all_hands, all_players, min_player = args.min_player, max_player = args.max_player)

    plot_vpip_pfr(vpip, pfr)
    

if __name__ == "__main__":
    main()

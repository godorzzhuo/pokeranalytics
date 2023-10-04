import csv
import os
from pprint import pprint
from typing import List, Dict

LOG_FILE_PATH = "logs"

def get_all_log_files(dir_path: str) -> List[str]:
    log_files: List[str] = []
    for file_path in os.listdir(dir_path):
        if os.path.isfile(os.path.join(dir_path, file_path)):
            log_files.append(os.path.join(dir_path, file_path))
    return log_files

def load_hands(file_path: str) -> List[List[List[str]]]:
    hands: List[List[List[str]]] = []
    hand: List[List[str]] = []

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
            hands.append(hand)
            hand = []
            continue
        if in_hand is True:
            hand.append(row)

    return hands

def calculate_vpip(hands: List[List[List[str]]], user_list: List[str]) -> Dict[str, float]:
    # TODO: add more general user handling
    total_hands = dict(zip(user_list, [0.0] * len(user_list)))
    vpip_hands = dict(zip(user_list, [0.0] * len(user_list)))
    vpip = dict(zip(user_list, [0.0] * len(user_list)))
    for hand in hands:
        played_this_hand = dict(zip(user_list, [False] * len(user_list)))
        for item in hand:
            action, _, _ = item
            if "Player stacks" in action:
                for user in user_list:
                    if user in action:
                        total_hands[user] += 1
                continue
            if "bets" in action or "calls" in action or "raises" in action:
                for user in user_list:
                    if user in action:
                        played_this_hand[user] = True
        for user in user_list:
            if played_this_hand[user] is True:
                vpip_hands[user] += 1

    for user in user_list:
        vpip[user] = vpip_hands[user] / total_hands[user]

    return vpip

def calculate_pfr(hands: List[List[List[str]]], user_list: List[str]) -> Dict[str, float]:
    # TODO: add more general user handling
    total_hands = dict(zip(user_list, [0.0] * len(user_list)))
    pfr_hands = dict(zip(user_list, [0.0] * len(user_list)))
    pfr = dict(zip(user_list, [0.0] * len(user_list)))
    for hand in hands:
        pfr_this_hand = dict(zip(user_list, [False] * len(user_list)))
        for item in hand:
            action, _, _ = item
            if "Player stacks" in action:
                for user in user_list:
                    if user in action:
                        total_hands[user] += 1
                continue

            # only consider action before flop
            if "Flop" in action:
                break

            if "raises" in action:
                for user in user_list:
                    if user in action:
                        pfr_this_hand[user] = True
        for user in user_list:
            if pfr_this_hand[user] is True:
                pfr_hands[user] += 1

    for user in user_list:
        pfr[user] = pfr_hands[user] / total_hands[user]

    return pfr


def preprocess(hands: List[List[List[str]]], name_map: Dict[str, str]) -> List[List[List[str]]]:
    for hand in hands:
        for item in hand:
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
    return hands

def create_user_map(file_path):
    import json
    name_map: Dict[str, str] = {}
    all_users: List[str] = []
    with open(file_path) as user_file:
        name_dict = json.load(user_file)
        for unique_name, screen_names in name_dict.items():
            all_users.append(unique_name)
            for screen_name in screen_names:
                name_map[screen_name] = unique_name
        return name_map, all_users

def main():
    name_map, all_users = create_user_map("user_names.json")
    log_files = get_all_log_files(LOG_FILE_PATH)

    all_hands = []
    for file_path in log_files:
        hands = load_hands(file_path)
        hands = preprocess(hands, name_map)
        all_hands.extend(hands)

    vpip = calculate_vpip(all_hands, all_users)
    pfr = calculate_pfr(all_hands, all_users)

    pprint(vpip)
    pprint(pfr)
    

if __name__ == "__main__":
    main()

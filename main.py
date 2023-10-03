import csv
import os
from typing import List

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

def calculate_vpip(hands: List[List[List[str]]]) -> None:
    # TODO: add more general user handling
    user_list = ["Zhuo", "ming", "Mj", "Rish", "Jorge2", "Army"]
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
            if "bets" in action or "calls" in action:
                for user in user_list:
                    if user in action:
                        played_this_hand[user] = True
        for user in user_list:
            if played_this_hand[user] is True:
                vpip_hands[user] += 1

    for user in user_list:
        vpip[user] = vpip_hands[user] / total_hands[user]

    print(vpip)

def main():
    log_files = get_all_log_files(LOG_FILE_PATH)

    for file_path in log_files:
        hands = load_hands(file_path)

        calculate_vpip(hands)
    

if __name__ == "__main__":
    main()

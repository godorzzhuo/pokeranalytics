from typing import List, Optional

class Action:
    def __init__(self, s: str):
        self._player = s.split(" @")[0][1:]
        self._action = s.split(" @")[1].split('"')[1].split(" ")[1][:-1]

    def __str__(self):
        return f"Player: {self.player}, Action: {self.action}"

    @property
    def player(self):
        return self._player

    @property
    def action(self):
        return self._action

class Hand:
    def __init__(self, hands_txt):
        self._clean_up(hands_txt)

        self.valid = True
        self.hand_time, self.players = self._setup_hand(hands_txt[:3])

        self._preflop_actions: List[Actions] = []
        self._flop_actions: List[Actions] = []
        self._turn_actions: List[Actions] = []
        self._river_actions: List[Actions] = []

        self.flop_board: Optional[str] = None
        self.turn_board: Optional[str] = None
        self.river_board: Optional[str] = None

        self._create_actions(hands_txt[3:])

    @property
    def preflop_actions(self):
        return self._preflop_actions

    @property
    def flop_actions(self):
        return self._flop_actions

    @property
    def turn_actions(self):
        return self._turn_actions

    @property
    def river_actions(self):
        return self._river_actions

    @property
    def all_actions(self) -> List[Action]:
        return self._preflop_actions + self._flop_actions + self._turn_actions + self._river_actions

    def _clean_up(self, hands_txt: List[List[str]]) -> None:
        for item in reversed(hands_txt):
            action, _, _ = item
            if "joined" in action or "requested" in action or \
                    "approved" in action or "forced" in action:
                hands_txt.remove(item)

    def _setup_hand(self, items):
        # check the format is correct
        assert len(items) == 3
        assert "Player stacks" in items[0][0]        
        if "small blind" not in items[1][0]:
            self.valid = False
            return "", []
        assert "small blind" in items[1][0]        
        assert "big blind" in items[2][0]        

        # get all player names
        player_info = items[0][0]
        player_info_split = player_info.split("@")
        players: List[str] = []
        for sub_str in player_info_split[:-1]:
            player = sub_str.rsplit('"')[-1][:-1]
            players.append(player)

        # adjust player position based on small/big blind
        # after this adjustmen, the 0th player is button, the 1st/2nd player are small/big blind
        small_blind = items[1][0].split(" @")[0][1:]
        big_blind = items[2][0].split(" @")[0][1:]
        for idx, player in enumerate(players):
            if small_blind == player:
                players = players[idx:] + players[:idx]
                break
        assert players[1] == big_blind
        players = [players[-1]] + players[:-1]

        # get hand time
        hand_time = items[0][1]

        return hand_time, players

    def _create_actions(self, items):
        actions = self.preflop_actions
        for item in items:
            action_txt, _, _ = item
            if "Uncalled bet" in action_txt or "collected" in action_txt:
                break

            # TODO: may need to handle run it twice case later
            if "run it twice" in action_txt:
                break

            if action_txt.startswith("Flop"):
                self.flop_board = action_txt.split("Flop:  ")[-1]
                actions = self.flop_actions
                continue

            if action_txt.startswith("Turn"):
                self.flop_board = action_txt.split("Turn: ")[-1]
                actions = self.turn_actions
                continue

            if action_txt.startswith("River"):
                self.flop_board = action_txt.split("River: ")[-1]
                actions = self.river_actions
                continue

            action = Action(action_txt)
            actions.append(action)

if __name__ == "__main__":
    example_hand_txt = [
        ['Player stacks: #1 "George @ ZuSkGJ10Lh" (114.14) | #4 "Mo @ C2SGJZ5XJ6" (172.60) | #8 "Connor @ UZnSnRINEa" (221.00)', '2023-10-03T05:12:09.521Z', '169630992952101'], 
        ['"Mo @ C2SGJZ5XJ6" posts a small blind of 0.50', '2023-10-03T05:12:09.521Z', '169630992952105'],
        ['"Connor @ UZnSnRINEa" posts a big blind of 1.00', '2023-10-03T05:12:09.521Z', '169630992952106'],
        ['"George @ ZuSkGJ10Lh" folds', '2023-10-03T05:12:10.778Z', '169630993077800'],
        ['"Mo @ C2SGJZ5XJ6" raises to 2.50', '2023-10-03T05:12:12.972Z', '169630993297200'],
        ['"Connor @ UZnSnRINEa" calls 2.50', '2023-10-03T05:12:14.307Z', '169630993430700'],
        ['Flop:  [K♦, 10♠, 10♦]', '2023-10-03T05:12:15.136Z', '169630993513600'],
        ['"Mo @ C2SGJZ5XJ6" bets 2.50', '2023-10-03T05:12:19.964Z', '169630993996400'],
        ['"Connor @ UZnSnRINEa" calls 2.50', '2023-10-03T05:12:21.282Z', '169630994128200'],
        ['Turn: K♦, 10♠, 10♦ [5♠]', '2023-10-03T05:12:22.141Z', '169630994214100'],
        ['"Mo @ C2SGJZ5XJ6" bets 5.00', '2023-10-03T05:12:27.351Z', '169630994735100'],
        ['"Connor @ UZnSnRINEa" folds', '2023-10-03T05:12:41.573Z', '169630996157300'],
        ['Uncalled bet of 5.00 returned to "Mo @ C2SGJZ5XJ6"', '2023-10-03T05:12:42.404Z', '169630996240400'],
        ['"Mo @ C2SGJZ5XJ6" collected 10.00 from pot', '2023-10-03T05:12:42.404Z', '169630996240401']
    ]

    hand = Hand(example_hand_txt)
    print("# Preflop:")
    for action in hand.preflop_actions:
        print(action)
    print("# Flop:")
    for action in hand.flop_actions:
        print(action)
    print("# Turn:")
    for action in hand.turn_actions:
        print(action)
    print("# River:")
    for action in hand.river_actions:
        print(action)

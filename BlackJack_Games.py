import random


class Card(object):
    """一张牌"""

    def __init__(self, suite, face):
        self._suite = suite  # 扑克的花色
        self._face = face  # 扑克的数字

    @property
    def face(self):
        return self._face

    @property
    def suite(self):
        return self._suite

    def __str__(self):
        if self._face == 1:
            face_str = 'A'
        elif self._face == 11:
            face_str = 'J'
        elif self._face == 12:
            face_str = 'Q'
        elif self._face == 13:
            face_str = 'K'
        else:
            face_str = str(self._face)
        return '%s%s' % (self._suite, face_str)

    def __repr__(self):
        return self.__str__()


class Poker(object):
    """一副牌"""

    def __init__(self):
        self._cards = [Card(suite, face)
                       for suite in '♠♥♣♦'
                       for face in range(1, 14)]  # 一套牌
        self._current = 0  # 当前第一张牌在牌堆中的位置

    @property
    def cards(self):
        return self._cards

    def shuffle(self):
        """洗牌(随机乱序)"""
        self._current = 0
        random.shuffle(self._cards)

    @property
    def next(self):
        """发牌"""
        card = self._cards[self._current]
        self._current += 1
        return card

    @property
    def has_next(self):
        """还有没有牌"""
        return self._current < len(self._cards)


class Player(object):
    """玩家"""

    def __init__(self, name, chips):
        self._name = name
        self._cards_on_hand = []
        self._points = 0  # 手牌分数
        self._chips = chips  # 筹码

    @property
    def name(self):
        return self._name

    @property
    def cards_on_hand(self):
        return self._cards_on_hand

    @property
    def points(self):
        return self._points

    @property
    def chips(self):
        return self._chips

    @chips.setter
    def chips(self, variation):  # 计算筹码
        self._chips += variation

    @points.setter  # 改变目前手牌分数
    def points(self, points):
        self._points = points

    def cards_clear(self):
        self.cards_on_hand.clear()

    def get(self, card):
        """摸牌"""
        self._cards_on_hand.append(card)  # 这里的card其实是接收发牌函数的返回值

    def __str__(self):
        return f"{self._name}玩家，您的手牌为：{self._cards_on_hand}， \
            剩余筹码为：{self._chips}"


def card_point_calculate(cards):
    """
    计算分数并返回  temp_points = 22 代表出现BJ， temp_points = 0 为爆牌  
    其余情况为手牌分数

    :param cards: 输入玩家手牌
    :rtype : int
    """
    temp_points = 0
    flag = 0  # flag表征手牌里有无‘A’
    for card in cards:
        if card.face == 1:
            flag = 1

    for card in cards:
        if card.face >= 10:
            point = 10
            temp_points += point
        else:
            point = card.face
            temp_points += point

    if flag:
        temp_points += 10
        if temp_points == 21 and len(cards) == 2:
            temp_points = 22  # 22代表Black Jack
            return temp_points
        
        if temp_points > 21:
            temp_points -= 10  # 如果点数> 21，则将A算作1点，即总点数 - 10

    if temp_points > 21:
        return 0
    else:
        return temp_points


def chips_calculate(
            banker, players: list, winner_condition: list, players_chips: list):
    """
    赌注计算函数

    :param banker: 庄家的实例对象
    :param players: 闲家的实例对象
    :param winner_condition: 闲家对庄家的赔率表
    :param players_chips: 闲家的赌注
    :return: 返回庄家赢下的钱
    """
    # winner_condition 存储每个玩家对于庄家的胜利情况 1为胜 -1为输  ±1.5为出现BJ时的情况
    banker_win_chips = 0.0
    for player in players:
        player_index = players.index(player)
        players_chips[player_index] *= winner_condition[player_index]
        player.chips = players_chips[player_index]
        banker_win_chips += -players_chips[player_index]  # 庄家的输赢情况和闲家相反
    banker.chips = banker_win_chips
    return banker_win_chips


def winner_calculate(banker, players):
    """
    结算函数  此函数已自动考虑BJ情况，无需在外部进行操作

    :param banker: 庄家
    :param players: 闲家
    :return: 各个闲家对庄家的赔率表
    """
    winner_condition = []
    for player in players:
        if player.points > banker.points and player.points == 22:
            winner_condition.append(1.5)
        elif player.points > banker.points:
            winner_condition.append(1)
        elif banker.points > player.points and banker.points == 22:
            winner_condition.append(-1.5)
        else:
            winner_condition.append(-1)
    return winner_condition


def player_round(player, poker):
    """
    闲家回合进行函数

    :param player: 玩家的实例对象
    :param poker:   将牌传入
    :return: 0 为爆牌  2 为不爆牌且停牌   3 为加倍赌注成功
    """
    player.points = card_point_calculate(player.cards_on_hand)
    if player.points < 21:
        print(f"{player.name}玩家，您手牌分数为：{player.points}")
        player_choice = int(input(f"请您选择: 1.继续要牌 2.停牌 3.加倍赌注"))
        if player_choice == 1:
            player.get(poker.next)
            player.points = card_point_calculate(player.cards_on_hand)
            while player.points != 0:
                print(f"{player.name}玩家，您手牌分数为：{player.points}", end='  ')
                player_choice = int(input(f"请您选择: 1.继续要牌 2.停牌"))
                if player_choice == 1:
                    player.get(poker.next)
                    player.points = card_point_calculate(player.cards_on_hand)
                else:
                    print(f"{player.name}玩家，您选择停牌，手牌分数为：{player.points}")
                    return 2
            print(f"{player.name}玩家，很遗憾，您爆牌了")       # 未在循环内停牌即为爆牌
            return 0
        elif player_choice == 2:
            print(f"{player.name}玩家，您选择停牌，手牌分数为：{player.points}")
            return 2
        elif player_choice == 3:
            player.get(poker.next)
            player.points = card_point_calculate(player.cards_on_hand)
            if player.points == 0:
                print(f"{player.name}玩家，很遗憾，您爆牌了")
                return 0
            else:
                print(f"{player.name}玩家，您加倍赌注成功，手牌分数为：{player.points}")
                return 3
    elif player.points == 22:
        print(f"{player.name}玩家，恭喜您！手牌为Black Jack，您将获得1.5倍赌注奖励！")
        return 2
    elif player.points == 0:
        print(f"{player.name}玩家，很遗憾，您爆牌了")
        return 0


def banker_round(banker, poker):
    """
    庄家回合进行函数

    :param banker: 庄家的实例对象
    :param poker: 传入的牌
    :return: 0 庄家爆牌  1 成功停牌   2 庄家 BJ
    """
    banker.points = card_point_calculate(banker.cards_on_hand)
    if banker.points < 17:
        while banker.points < 17 and banker.points != 0:
            print(f"{banker.name}庄家，您手牌分数为：{banker.points}，需继续要牌")
            banker.get(poker.next)
            banker.points = card_point_calculate(banker.cards_on_hand)
        if banker.points == 0:
            print(f"{banker.name}庄家，您已爆牌")
            return 0
        else:
            print(f"{banker.name}庄家，您手牌分数为：{banker.points}，已停牌")
            return 1
    elif banker.points >= 17:
        print(f"{banker.name}庄家，您手牌分数为：{banker.points}，已停牌")
        return 1
    elif banker.points == 22:
        print(f"恭喜{banker.name}庄家！手牌为Black Jack，将获得1.5倍赌注奖励！")
        return 2


def main():
    game_flag = 1
    game_round = 0
    a_set_poker = Poker()  # 创建一副牌

    info_list = input("请输入庄家姓名，以及初始筹码：（以空格分隔）").split()
    banker = Player(info_list[0], float(info_list[1]))  # 创建一个庄家

    player_number = int(input("请输入玩家人数："))
    players = []  # 存放每个玩家对象的列表

    player_chips = [0.0] * player_number  # 存放玩家下注筹码情况
    winner_condition = []  # 存放玩家输赢情况

    for i in range(1, player_number + 1):  # 创建一群玩家
        info_list = input(f"请输入第{i}位玩家姓名，以及初始筹码：（以空格分隔）").split()
        player = Player(info_list[0], float(info_list[1]))
        players.append(player)

    while game_flag:
        game_round += 1
        print(f"--------------------第{game_round}回合--------------------")
        a_set_poker.shuffle()
        banker.points = 0
        banker.cards_clear()    # 清空手牌
        for player in players:
            player.points = 0  # 清空每个人的手牌分数
            player.cards_clear()    # 清空手牌
        for i in range(0, player_number):
            player_chips[i] = 0.0

        print('\n')

        print(f"------------------------请闲家下注-------------------------")
        for i in range(1, player_number + 1):
            player_chips[i-1] = float(input(f"请{players[i - 1].name}玩家下注:(最小1注)"))
        for i in range(1, player_number + 1):
            print(f"{players[i-1].name}玩家下注:{player_chips[i-1]}", end='    ')
        print('\n')

        print(f"-------------------------现在发牌-------------------------")
        banker.get(a_set_poker.next)
        banker.get(a_set_poker.next)
        for player in players:
            player.get(a_set_poker.next)
            player.get(a_set_poker.next)
        print("\n")
        print(f"{banker.name}庄家的第一张手牌为{banker.cards_on_hand[0]}", end='    ')
        for player in players:
            print(f"{player.name}玩家的手牌为\
{player.cards_on_hand[0]}{player.cards_on_hand[1]}", end='    ')
        print("\n")

        print(f"-------------------------闲家回合-------------------------")
        for player in players:
            round_flag = player_round(player, a_set_poker)
            if round_flag == 3:
                player_chips[players.index(player)] *= 2
        print('\n')

        print(f"-------------------------庄家回合-------------------------")
        banker_round(banker, a_set_poker)
        print('\n')

        print(f"-------------------------结算回合-------------------------")
        print(f"{banker.name}庄家手牌为：", end='')
        for card in banker.cards_on_hand:               # 展示庄家手牌
            print(f"{card}", end='  ')
        print('\n')

        for player in players:                      # 展示闲家手牌
            print(f"{player.name}玩家手牌为：", end='')
            for card in player.cards_on_hand:
                print(f"{card}", end='  ')
            print('\n')

        winner_condition = winner_calculate(banker, players)
        banker_win_chips = chips_calculate(banker, players, winner_condition, player_chips)
        print(f"各闲家赢下的赌注:")
        for i in range(0, player_number):
            print(f"{players[i].name}玩家：{player_chips[i]}", end='   ')
        print('\n')
        print(f"{banker.name}庄家赢下的赌注：{banker_win_chips}")
        print('\n')

        print(f"{banker.name}庄家剩余筹码：{banker.chips}", end='   ')
        for player in players:
            print(f"{player.name}玩家剩余筹码：{player.chips}", end='   ')
        print('\n')

        game_flag = int(input("请输入是否继续游戏：0.停止 1.继续 "))
        if not game_flag:
            print('感谢您游玩本游戏！')


if __name__ == '__main__':
    main()

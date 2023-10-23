import numpy as np
import eval7


def calc_equity(deck, hero_cards, table_cards, iters=100000):
    """
    Parameters:
        deck(list of str): all other cards, not including cards that are on the table and hero cards
        hero_cards(list of str): cards that belong to the hero
        table_cards(list of str): cards that are on the table
        iters(int): the amount that the table generates
    Returns:

    """
    deck = [eval7.Card(card) for card in deck]
    table_cards = [eval7.Card(card) for card in table_cards]
    hero_cards = [eval7.Card(card) for card in hero_cards]
    max_table_cards = 5
    win_count = 0
    for _ in range(iters):
        np.random.shuffle(deck)
        num_remaining = max_table_cards - len(table_cards)
        # Draw the remaining community cards and two hole cards for the opponent.
        draw = deck[:num_remaining+2]
        opp_hole, remaining_comm = draw[:2], draw[2:]
        player_hand = hero_cards + table_cards + remaining_comm
        opp_hand = opp_hole + table_cards + remaining_comm
        player_strength = eval7.evaluate(player_hand)
        opp_strength = eval7.evaluate(opp_hand)

        if player_strength > opp_strength:
            win_count += 1

    win_prob = (win_count / iters) * 100
    return round(win_prob, 2)


def remove_cards(hero_cards, table_cards):
    """
    Parameters:
        hero_cards(list of str): cards that belong to the hero
        table_cards(list of str): cards that are on the table
    Returns:
        all_cards(list of str): all other cards, not including cards that are on the table and hero cards
    """
    all_cards = ['2c', '2d', '2h', '2s', '3c', '3d', '3h', '3s', '4c', '4d', '4h', '4s', '5c', '5d', '5h', '5s',
                 '6c', '6d', '6h', '6s', '7c', '7d', '7h', '7s', '8c', '8d', '8h', '8s', '9c', '9d', '9h', '9s',
                 'Tc', 'Td', 'Th', 'Ts', 'Jc', 'Jd', 'Jh', 'Js', 'Qc', 'Qd', 'Qh', 'Qs', 'Kc', 'Kd', 'Kh', 'Ks',
                 'Ac', 'Ad', 'Ah', 'As']
    for card in hero_cards+table_cards:
        all_cards.remove(card)
    return all_cards


def simple_strategy(pot, equity):
    pot = int(pot)
    if equity < 50:
        if 0 < equity < 20:
            action = 'fold'
            optimal_bet_amount = None
            analysis = 'extremely weak hand'
        else:
            action = 'bet'
            optimal_bet_amount = pot * 1 / 6  # pot * equity / (100 - 2 * equity)
            analysis = 'weak hand'
    else:
        action = 'bet'
        if 50 <= equity < 65:
            optimal_bet_amount = 1 / 3 * pot
            analysis = 'strong hand'
        else:
            optimal_bet_amount = pot
            analysis = 'extremely strong hand'

    if optimal_bet_amount is not None:
        optimal_bet_amount = int(optimal_bet_amount)
        if optimal_bet_amount < 100:
            optimal_bet_amount = 100

    return action, optimal_bet_amount, analysis

from django.shortcuts import render
import requests
from collections import Counter
import operator

def get_list_of_cards():
    URL = 'http://netrunnerdb.com/api/cards/'
    cardlist = requests.get(URL).json()
    cards = {}
    for item in list(cardlist):
        cards[item['code']] = item['title']
    return cards 

def get_deck(deck_id):
    URL = 'http://netrunnerdb.com/api/decklist/' + deck_id
    deck_info = requests.get(URL).json()
    deck_cards = []
    for key, value in deck_info['cards'].items():
        if value == 1:
            deck_cards.append(key)
        elif value > 1:
            for x in range(0, value):
                deck_cards.append(key)
        else:
            deck_cards = ['We\'re sorry, an error occured']
    return deck_cards

def compare_decklist(old_deck, new_deck):
    diff_old_to_new = Counter(old_deck) - Counter(new_deck)
    diff_new_to_old = Counter(new_deck) - Counter(old_deck)
    diff_new_to_old.update({key : -1 * value for key, value in diff_old_to_new.items()})
    return dict(diff_new_to_old)

def attach_names(diff_list, all_cards):
    named_cards = {}
    for key, value in diff_list.items():
        card_name = all_cards[key]
        named_cards[card_name] = value
    return named_cards

def cards_changed(named_cards, negative=False):
    if negative:
        named_cards = {key : value for key, value in named_cards.items() if value < 0}
        return sorted(named_cards.items(), key=lambda x: (x[1], x[0]))
    else:
        named_cards = {key : value for key, value in named_cards.items() if value > 0}
        return sorted(named_cards.items(), key=lambda x: (x[1], x[0]))

def deck_list(request):
    old_deck = get_deck('25994')
    new_deck = get_deck('17417')
    diff_lists = compare_decklist(old_deck, new_deck)
    named_cards = attach_names(diff_lists, get_list_of_cards())
    return render(request, 'netdeckmanager/deck_list.html', 
        {'drop_list' : cards_changed(named_cards, negative=True),
        'add_list' : cards_changed(named_cards, negative=False) })

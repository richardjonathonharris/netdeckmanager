from django.shortcuts import render, HttpResponse
import requests
from collections import Counter
import operator
from django.core.exceptions import *
import re

def index(request):
    return render(request, 'netdeckmanager/forms.html')

def search_for_deck(request):
    if request.method == 'POST':
        deck1_request = request.POST.get('deck1', None)
        deck2_request = request.POST.get('deck2', None)
        refresh = request.POST.get('new_deck', None)
        if refresh is not None:
            return render(request, 'netdeckmanager/forms.html')
        else:
            deck_info, counter = {}, 0
            try:
                for deck in [deck1_request, deck2_request]:
                    string_key = re.search('decklist/([0-9]+)/', deck)
                    deck_key = string_key.group(1)
                    deck_info[counter] = deck_key
                    counter += 1
                old_deck = get_deck(deck_info[0])
                new_deck = get_deck(deck_info[1])
                diff_lists = compare_decklist(old_deck, new_deck)
                named_cards = attach_names(diff_lists, get_list_of_cards())
                return render(request, 'netdeckmanager/deck_list.html',
                        {'drop_list' : cards_changed(named_cards, negative=True),
                         'add_list' : cards_changed(named_cards, negative=False) })
            except:
                 return HttpResponse('Keys were not correct')
    else:
        return HttpResponse('Else clause fired')

def get_list_of_cards():
    URL = 'http://netrunnerdb.com/api/cards/'
    cardlist = requests.get(URL).json()
    cards = {}
    for item in list(cardlist):
        imagesrc = 'http://netrunnerdb.com' + item['imagesrc'].replace('\/', '/')
        url = item['url'].replace('\/', '/')
        cards[item['code']] = {'title':  item['title'], 'imagesrc' : imagesrc, 'url' : url}
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
        card_name = all_cards[key]['title']
        named_cards[card_name] = {'value' : value, 'imagesrc' : all_cards[key]['imagesrc'], 'url' : all_cards[key]['url']}
    return named_cards

def cards_changed(named_cards, negative=False):
    if negative:
        named_cards = {key : value for key, value in named_cards.items() if value['value'] < 0}
        return sorted(named_cards.items(), key=lambda x: (x[1]['value'], x[0]))
    else:
        named_cards = {key : value for key, value in named_cards.items() if value['value'] > 0}
        return sorted(named_cards.items(), key=lambda x: (x[1]['value'], x[0]))

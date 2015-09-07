from django.shortcuts import render

def deck_list(request):
    return render(request, 'netdeckmanager/deck_list.html', {})

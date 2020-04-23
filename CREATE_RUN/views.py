from django.shortcuts import render
from zeep import Client
import random

# Create your views here.
def view_home(request):
    return render(request, 'CREATE_RUN/home.html', {})


def view_page(request):
    print("")

    return render(request, 'CREATE_RUN/page.html', {})


def view_stanovisko(request):
    if request.POST:
        print(request.POST)


        beh = {
            "id": random.randint(1, 10),
            "name": request.POST['name'],
            "stafeta": True if request.POST.get('typ') == '0' else False,
            "datum_konania": request.POST['termin'],
            "kapacita": int(request.POST.get('kapacita')) if request.POST.get('kapacita') else 0,
            "podporny_tim": True if request.POST.get('podporny_tim') else False,
            "prihlaseni": 0,
            "zakladna_cena_behu": 0
        }

        stanovisko_names = request.POST.getlist('stanovisko_name')
        obcerstvenia = request.POST.getlist('obcerstvenie')

        print(beh)





    client = Client('http://pis.predmety.fiit.stuba.sk/pis/ws/GeoServices/Cities?WSDL')
    result_cities = client.service.getAll()

    stanice = []
    for item in result_cities:
        stanice.append({
            'nazov': item['name'],
            'zem_dlzka': item['coord_lon'],
            'zem_sirka': item['coord_lat'],
            'vyska': 100
        })

    client = Client('http://pis.predmety.fiit.stuba.sk/pis/ws/GeoServices/Peaks?WSDL')
    result_peaks = client.service.searchByName("")

    for item in result_peaks:
        stanice.append({
            'nazov': item['name'],
            'zem_dlzka': item['coord_lon'],
            'zem_sirka': item['coord_lat'],
            'vyska': item['height']
        })

    entry = {
        'items': stanice
    }

    return render(request, 'CREATE_RUN/stanovisko.html', {'entry': entry})

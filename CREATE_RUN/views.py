from django.shortcuts import render
from zeep import Client


# Create your views here.

def view_page(request):
    return render(request, 'CREATE_RUN/page.html', {})


def view_stanovisko(request):
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

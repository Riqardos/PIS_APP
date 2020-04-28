from django.shortcuts import render
from zeep import Client
import random
import datetime


# Create your views here.
def view_home(request):
    return render(request, 'CREATE_RUN/home.html', {})


vsetky_behy = []

global_stanice = []
global_dict_stanice = {}


def view_page(request):

    client_behy = Client('http://pis.predmety.fiit.stuba.sk/pis/ws/Students/Team041Beh?WSDL')
    behy = client_behy.service.getAll()

    output = {
        'behy': behy
    }

    return render(request, 'CREATE_RUN/page.html', {'output': output})

def view_page_success(request):
    global global_stanice
    global global_dict_stanice
    global vsetky_behy
    if not (global_stanice):
        global_stanice, global_dict_stanice = ziskaj_stanice()

    if request.POST:
        print(request.POST)

        beh = {
            "id": random.randint(1, 10),
            "name": request.POST['name'],
            "stafeta": True if request.POST.get('typ') == '0' else False,
            "datum_konania": datetime.datetime.strptime(request.POST['termin'], '%Y-%m-%dT%H:%M'),
            "kapacita": int(request.POST.get('kapacita')) if request.POST.get('kapacita') else 0,
            "podporny_tim": True if request.POST.get('podporny_tim') == 'on' else False,
            "prihlaseni": 0,
        }

        stanovisko_names = request.POST.getlist('stanovisko_name')
        obcerstvenia = request.POST.getlist('cena_obcerstvenie')
        ceny_pomoc = request.POST.getlist('cena_pomoc')
        ceny_pacer = request.POST.getlist('cena_pacer')
        porady = request.POST.getlist('porada')
        odovzdania = request.POST.getlist('odovzdanie')
        limity = request.POST.getlist('limit')
        ceny_preprava = request.POST.getlist('cena_preprava')

        stanoviska = []

        if not beh['stafeta']:
            odovzdania = ['' for i in range(len(stanovisko_names))]

        for index, stanovisko in enumerate(stanovisko_names):
            zem_dlzka, zem_sirka, prevysenie = global_dict_stanice[stanovisko]
            stanica = {
                "id": index,
                "id_beh": beh['id'],
                "name": stanovisko,
                "poradie": index + 1,
                "lekar": True if ceny_pomoc[index] else False,
                "cena_lekara": float(ceny_pomoc[index]) if ceny_pomoc[index] else float(0),
                "pacer": True if ceny_pacer[index] else False,
                "cena_pacera": float(ceny_pacer[index]) if ceny_pacer[index] else float(0),
                "obcerstvenie": True if obcerstvenia[index] else False,
                "cena_obcerstvenia": float(obcerstvenia[index]) if obcerstvenia[index] else float(0),
                "timova_porada": True if porady[index] == 'True' else False,
                "odovzdanie_stafety": True if odovzdania[index] == 'True' else False,
                "casovy_limit_dosiahnutia": int(limity[index]) if limity[index] else 0,
                "prevysenie": prevysenie,
                "zem_sirka": zem_sirka,
                "zem_dlzka": zem_dlzka
            }
            stanoviska.append(stanica)

        stanoviska = vypocitaj_vzdialenosti(stanoviska)

        zakladna_cena = vypocitaj_cenu(stanoviska)

        beh['zakladna_cena'] = zakladna_cena

        print(stanoviska)
        print(beh)
        print(zakladna_cena)

        vloz_do_db(beh, stanoviska)

        return render(request, 'CREATE_RUN/page_success.html', {'beh': beh, 'stanoviska': stanoviska})

def view_stanovisko(request):
    global global_stanice
    global global_dict_stanice

    if not (global_stanice):
        global_stanice, global_dict_stanice = ziskaj_stanice()

    entry = {
        'items': global_stanice
    }

    return render(request, 'CREATE_RUN/stanovisko.html', {'entry': entry})


def vypocitaj_vzdialenosti(stanoviska):
    #     stanoviska = [
    #  ...
    #     {"zem_sirka":12, "zem_dlzka":12},
    #     {"zem_sirka":432, "zem_dlzka":23}
    # ...
    #     ]

    client_distance = Client('http://pis.predmety.fiit.stuba.sk/pis/ws/GeoServices/Locations?WSDL')

    for index, stanovisko in enumerate(stanoviska):

        if index == 0:
            stanovisko['vzdialenost_predchadzajuceho_stanoviska'] = 0
            continue
        else:
            prev_zem_sirka = stanoviska[index - 1]['zem_sirka']
            prev_zem_dlzka = stanoviska[index - 1]['zem_dlzka']

            aktual_zem_sirka = stanovisko['zem_sirka']
            aktual_zem_dlzka = stanovisko['zem_dlzka']
            vzdialenost = client_distance.service.distanceByGPS(prev_zem_sirka, prev_zem_dlzka, aktual_zem_sirka,
                                                                aktual_zem_dlzka)

            stanovisko['vzdialenost_predchadzajuceho_stanoviska'] = vzdialenost

    return stanoviska


def ziskaj_stanice():
    stanice = []
    dict_stanice = {}
    client = Client('http://pis.predmety.fiit.stuba.sk/pis/ws/GeoServices/Cities?WSDL')
    result_cities = client.service.getAll()
    #
    for item in result_cities:
        nazov = item['name'].replace("'", " ")
        stanice.append({
            'nazov': nazov,
            'zem_dlzka': item['coord_lon'],
            'zem_sirka': item['coord_lat'],
            'vyska': 100
        })
        dict_stanice[nazov] = (item['coord_lon'], item['coord_lat'], 100)

    client = Client('http://pis.predmety.fiit.stuba.sk/pis/ws/GeoServices/Peaks?WSDL')
    result_peaks = client.service.searchByName("")

    for item in result_peaks:
        nazov = item['name'].replace("'", " ")
        stanice.append({
            'nazov': nazov,
            'zem_dlzka': item['coord_lon'],
            'zem_sirka': item['coord_lat'],
            'vyska': item['height']
        })

        dict_stanice[nazov] = (item['coord_lon'], item['coord_lat'], item['height'])

    return stanice, dict_stanice


def vypocitaj_cenu(stanice):
    cena = 0
    for stanica in stanice:
        cena += stanica['cena_lekara']
        cena += stanica['cena_pacera']
        cena += stanica['cena_obcerstvenia']
    return cena


def vloz_do_db(beh, stanoviska):
    beh_insert = Client('http://pis.predmety.fiit.stuba.sk/pis/ws/Students/Team041Beh?WSDL')
    stanovisko_insert = Client('http://pis.predmety.fiit.stuba.sk/pis/ws/Students/Team041Stanovisko?WSDL')

    response = beh_insert.service.insert('041', 'D1QFEP', beh)
    print(response)
    for stanovisko in stanoviska:
        stanovisko['id_beh'] = response
        stanovisko_insert.service.insert('041', 'D1QFEP', stanovisko)
        print(response)

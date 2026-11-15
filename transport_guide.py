"""Curated modal guidance, not an availability, ticketing or fare service.

Each mode describes a practical path to investigate. Booking links open the
provider's official homepage or search and never claim a specific service runs.
Reviewed against provider pages on 15 November 2026. Operator availability and
sailing seasons must always be rechecked for chosen travel dates.
"""
from math import radians, sin, cos, asin, sqrt
from urllib.parse import urlencode

FLIGHT_URLS = [
    {'name': 'AirAsia MOVE – search flights', 'url': 'https://www.airasia.com/flights/'},
    {'name': 'Malaysia Airlines – search flights', 'url': 'https://www.malaysiaairlines.com/my/en/home.html'},
]
BUS_URLS = [
    {'name': 'Easybook – search coach tickets', 'url': 'https://www.easybook.com/en-my'},
    {'name': 'BusOnlineTicket – search coaches', 'url': 'https://www.busonlineticket.com/'},
]
KTM = [{'name': 'KTMB KITS – railway tickets / times', 'url': 'https://online.ktmb.com.my/'}]
GRAB = [{'name': 'Grab Malaysia – book a ride in the app', 'url': 'https://www.grab.com/my/transport/'}]
FERRIES = {
    'Langkawi': {'gateway': 'Kuala Perlis or Kuala Kedah passenger jetty', 'url': 'https://www.langkawiferryline.com/', 'name': 'Langkawi Ferry Line'},
    'Tioman Island': {'gateway': 'Mersing or Tanjung Gemok (Teluk Gading) jetty', 'url': 'https://www.mim.com.my/', 'name': 'Bluewater Express Tioman ferry'},
    'Perhentian Islands': {'gateway': 'Kuala Besut jetty', 'url': 'https://www.perhentiantrans.com/', 'name': 'Perhentian Trans boat transfers'},
}
EAST_MALAYSIA = {'Kota Kinabalu', 'Kuching'}
ISLANDS = set(FERRIES)
AIRPORT_DESTINATIONS = {'Kuala Lumpur', 'Penang', 'Langkawi', 'Johor Bahru', 'Kota Kinabalu', 'Kuching'}
WEST_RAIL = {'Kuala Lumpur', 'Ipoh', 'Penang', 'Johor Bahru'}
KL_LOCAL = {'Kuala Lumpur', 'Batu Caves', 'Putrajaya'}
RURAL_RAIL = {'Taman Negara'}  # Jerantut station + onward transfer


def map_directions(start, end, mode='driving'):
    return 'https://www.google.com/maps/dir/?' + urlencode({
        'api': '1', 'origin': start + ', Malaysia',
        'destination': end + ', Malaysia', 'travelmode': mode})


def distance(a, b):
    try:
        lat1, lon1, lat2, lon2 = map(float, [a['latitude'], a['longitude'], b['latitude'], b['longitude']])
    except (TypeError, ValueError, KeyError):
        return None
    rad = radians
    x = sin(rad(lat2 - lat1)/2)**2 + cos(rad(lat1))*cos(rad(lat2))*sin(rad(lon2-lon1)/2)**2
    return round(12742 * asin(min(1.0, sqrt(x))))


def make(mode, title, description, legs, providers, priority=50, note='Availability and connections must be checked for your travel date.'):
    return dict(mode=mode, title=title, description=description, legs=legs,
                providers=providers, priority=priority, note=note,
                availability='Check with provider – not live')


def options_for(origin, destination):
    """Return carefully qualified travel possibilities for 15 curated destinations.

    'Available' means a mode is relevant to investigate, not that a direct
    departure or seat exists between these points. Never manufacture schedules.
    """
    a, b = origin['name'], destination['name']
    if a == b:
        return []
    approx = distance(origin, destination)
    same_mainland = a not in (ISLANDS | EAST_MALAYSIA) and b not in (ISLANDS | EAST_MALAYSIA)
    east = a in EAST_MALAYSIA or b in EAST_MALAYSIA
    island = a in ISLANDS or b in ISLANDS
    result = []

    if a in AIRPORT_DESTINATIONS and b in AIRPORT_DESTINATIONS and (east or island or approx is None or approx >= 240):
        result.append(make('flight', 'Flight · direct or connecting',
            'Search airport-to-airport flights. The operator will confirm whether a direct flight exists or a connection is needed.',
            [f'Check flights serving {a} and {b}', 'Allow for airport transfers at both ends'],
            FLIGHT_URLS, 10))
    elif east or ('Langkawi' in {a, b} and (a not in ISLANDS or b not in ISLANDS)) or ('Perhentian Islands' in {a,b} and ({a,b} & AIRPORT_DESTINATIONS)):
        result.append(make('flight', 'Flight + onward transfer',
            'A flight to/from a suitable gateway airport may be practical (for example, Kota Bharu for the Perhentian Islands). A separate road or ferry transfer is likely; this is not a flight directly to the island.',
            ['Find an airport serving your origin and destination region', 'Arrange road, ferry or local transport for the remaining leg'],
            FLIGHT_URLS, 12))

    if same_mainland:
        result.append(make('car', 'Self-drive / private car',
            'Driving is a point-to-point option on the peninsula. Compare road routes, tolls and realistic journey times on Maps.',
            [f'Drive from {a} to {b}'],
            [{'name':'Google Maps – driving directions', 'url':map_directions(a,b)}], 30))
        if approx is None or approx <= 220:
            result.append(make('cab', 'Taxi or Grab · check coverage',
                'Try an app-based ride or private taxi. Long intercity trips may not be offered and fares depend on pickup area.',
                [f'Enter {a} as pickup and {b} as destination in the app'], GRAB, 25))
        if approx is None or approx >= 25 or (a in KL_LOCAL and b in KL_LOCAL):
            result.append(make('bus', 'Coach / bus · check service',
                'Search intercity coaches or local buses. Some routes require a transfer at a major terminal.',
                ['Search the nearest terminals in both areas', 'Confirm departures, operator and last-mile transfer'],
                BUS_URLS + [{'name':'Google Maps – public transit', 'url':map_directions(a,b,'transit')}], 20))
        if a in KL_LOCAL and b in KL_LOCAL:
            result.append(make('train', 'Urban rail + local transfer',
                'Look up local rail services. KTM Komuter serves Batu Caves, while Putrajaya is served by separate MRT / KLIA Transit links; connections may be needed.',
                ['Find suitable stations and interchanges', 'Check rail lines and service hours'],
                KTM + [{'name':'Google Maps – rail/transit directions','url':map_directions(a,b,'transit')}], 15))
        elif a in WEST_RAIL and b in WEST_RAIL:
            result.append(make('train', 'KTM ETS / intercity + transfers',
                'Check KTM rail services. For Penang, use Butterworth station and connect across to the island. A train may not cover the full route.',
                ['Search the appropriate KTM departure and arrival stations', 'Add a local transfer where necessary'],
                KTM, 16))
        elif ((a in WEST_RAIL and b in {'Batu Caves', 'Melaka'}) or (b in WEST_RAIL and a in {'Batu Caves','Melaka'})):
            result.append(make('train', 'Train + onward local transport',
                'Check rail stations near your route. Melaka requires an onward transfer from the rail corridor; Batu Caves connects via KTM Komuter.',
                ['Check KTM service and connections','Continue by local bus or taxi'], KTM, 19))
        elif 'Taman Negara' in {a, b} and ({a,b} & WEST_RAIL):
            result.append(make('train','Rail towards Jerantut + road transfer',
                'Some itineraries can use rail towards Jerantut, then local transfers to Kuala Tahan / Taman Negara. This is not a direct train to the park.',
                ['Check KTMB services to Jerantut','Arrange onward road/river access depending on accommodation'], KTM, 32))
    elif east and (a in EAST_MALAYSIA and b in EAST_MALAYSIA):
        result.append(make('car', 'Road trip / private transfer',
            'Sabah and Sarawak are connected by roads, but overland journeys can be long and may involve cross-border formalities through Brunei. Check route requirements.',
            ['Review route, timing, documentation and border requirements'],
            [{'name':'Google Maps – suggested road route','url':map_directions(a,b)}], 50))
        result.append(make('bus','Coach / overland connection · verify',
            'Investigate whether a coach connection is operating on your dates; do not assume a direct bus.',
            ['Check bus operators and permitted border crossings'],BUS_URLS,55))

    for island_name in (a,b):
        if island_name not in FERRIES: continue
        p=FERRIES[island_name]
        result.append(make('ferry', 'Ferry / speedboat + transfer',
            f'{island_name} is reached by a water crossing from {p["gateway"]}. Unless you start at the jetty, arrange another leg first. There is no implied direct island-to-island ferry.',
            [f'Reach {p["gateway"]} by bus, car, rail or flight as appropriate',
             f'Book the {island_name} boat crossing; check season and weather',
             'Arrange local transport to your accommodation'],
            [{'name':p['name']+' – ferry bookings / information','url':p['url']}], 18,
            'Water crossings are seasonal or weather-dependent; check exact operating dates.'))
        if island_name == 'Langkawi':
            result.append(make('bus', 'Coach / train to mainland jetty + ferry',
                'Travel to Kuala Perlis or Kuala Kedah by suitable land transport, then continue by ferry. Langkawi itself is not reachable by a direct mainland coach or train.',
                ['Find transport to Kuala Perlis or Kuala Kedah','Continue by passenger ferry'],
                BUS_URLS + KTM + [{'name':'Langkawi Ferry Line','url':p['url']}], 26))
        elif island_name == 'Perhentian Islands':
            result.append(make('bus','Coach / shuttle to Kuala Besut + boat',
                'Check buses or shuttles to Kuala Besut. Boat transfer to the islands is a separate booking.',
                ['Reach Kuala Besut jetty','Transfer to the booked boat'],
                BUS_URLS + [{'name':'Perhentian Trans','url':p['url']}],27))
        elif island_name == 'Tioman Island':
            result.append(make('bus','Coach to Mersing / Tanjung Gemok + ferry',
                'Reach one of the Tioman ferry terminals by coach or road; check which jetty matches your ferry booking.',
                ['Reach Mersing or Tanjung Gemok','Board the confirmed Tioman ferry'],
                BUS_URLS + [{'name':'Bluewater Express','url':p['url']}],27))

    if 'Genting Highlands' in {a,b}:
        result.append(make('cable-car','Coach + Awana SkyWay cable car',
            'The Genting express bus reaches the mid-hill terminal; the Awana SkyWay connects onwards to the resort. For other origins, a transfer via KL may be needed.',
            ['Check coach connections to Sky Sentral / Genting Highlands Premium Outlets terminal',
             'Buy or check Awana SkyWay tickets for the ascent'],
            [{'name':'Resorts World Genting – express bus','url':'https://www.rwgenting.com/en/getting-here/express-bus.html'},
             {'name':'Awana SkyWay – cable car tickets','url':'https://www.rwgenting.com/en/getting-here/cable-car.html'}], 18))

    if a in ISLANDS or b in ISLANDS:
        # A taxi cannot cross water. For island journeys suggest only shore-side or
        # local cab after the sea/air leg, rather than an impossible direct Grab.
        result.append(make('cab','Taxi / Grab for connecting land legs',
            'A local cab can help between airport, terminal, jetty and hotel where service exists; it cannot make the sea crossing.',
            ['Use a ride-hailing app for the land portions only'],GRAB,45))
    elif east:
        result.append(make('cab','Taxi / Grab at the destination',
            'Use a local ride-hailing service for airport transfers and in-city trips where vehicles are available; not a ride across the sea.',
            ['Arrange your airport pickup in the app'],GRAB,45))

    # De-duplicate modes while permitting an intentional bus+boat and boat entry.
    return sorted(result,key=lambda x:x['priority'])

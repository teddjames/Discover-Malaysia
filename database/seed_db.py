import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / "database" / "tourism.db"


def seed_database():
    try:
        from database.init_db import initialize_database
    except ModuleNotFoundError:
        from init_db import initialize_database
    initialize_database()

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()


    # ==========================================
    # DESTINATIONS
    # ==========================================

    destinations = [

        (
            "Kuala Lumpur",
            "kuala-lumpur",
            "Malaysia's vibrant capital city.",
            "twintowers.jpg"
        ),

        (
            "Batu Caves",
            "batu-caves",
            "A famous limestone cave and Hindu pilgrimage site.",
            "Batucavesstatue.jpg"
        ),

        (
            "Genting Highlands",
            "genting-highlands",
            "A mountain resort destination famous for entertainment and adventure.",
            "genting.jpg"
        )

    ]


    cursor.executemany(
        """
        INSERT OR IGNORE INTO destinations
        (name, slug, description, image)

        VALUES (?, ?, ?, ?)
        """,

        destinations
    )


    # ==========================================
    # GET DESTINATION IDS
    # ==========================================

    cursor.execute(
        "SELECT id, slug FROM destinations"
    )

    destination_ids = {
        row[1]: row[0]
        for row in cursor.fetchall()
    }


    # ==========================================
    # ATTRACTIONS
    # ==========================================

    attractions = [

        (
            destination_ids["kuala-lumpur"],
            "Petronas Twin Towers",
            "petronas-twin-towers",
            "landmark",
            "One of Kuala Lumpur's most iconic landmarks.",
            4.7,
            98,
            "twintowers.jpg"
        ),

        (
            destination_ids["kuala-lumpur"],
            "Central Market",
            "central-market",
            "culture",
            "A historic marketplace featuring Malaysian arts, crafts and culture.",
            4.4,
            0,
            "centralmarket.jpg"
        ),

        (
            destination_ids["batu-caves"],
            "Batu Caves",
            "batu-caves-attraction",
            "culture",
            "A famous limestone cave complex and Hindu pilgrimage site.",
            4.7,
            0,
            "Batucavesstatue.jpg"
        ),

        (
            destination_ids["genting-highlands"],
            "Genting SkyWorlds",
            "genting-skyworlds",
            "adventure",
            "A mountain theme park featuring rides and entertainment.",
            4.5,
            120,
            "genting.jpg"
        )

    ]


    cursor.executemany(
        """
        INSERT OR IGNORE INTO attractions
        (
            destination_id,
            name,
            slug,
            category,
            description,
            rating,
            price,
            image
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,

        attractions
    )


    # ==========================================
    # HOTELS
    # ==========================================

    hotels = [

        (
            destination_ids["kuala-lumpur"],
            "Mandarin Oriental, Kuala Lumpur",
            "Mandarin Oriental, Kuala Lumpur",
            "hotel",
            "A stylish hotel in Bukit Bintang.",
            4.5,
            180,
            "hotel-1.jpg"
        ),

        (
            destination_ids["kuala-lumpur"],
            "Grand Hyatt Kuala Lumpur",
            "Grand Hyatt Kuala Lumpur",
            "hotel",
            "Accommodation close to KLCC and the Petronas Twin Towers.",
            4.6,
            220,
            "hotel-2.jpg"
        ),

        (
            destination_ids["genting-highlands"],
            "Grand Ion Delemen Hotel, Genting Highlands",
            "Grand Ion Delemen Hotel, Genting Highlands",
            "hotel",
            "Accommodation close to Genting's major attractions.",
            4.4,
            250,
            "hotel-3.jpg"
        )

    ]


    cursor.executemany(
        """
        INSERT OR IGNORE INTO hotels
        (
            destination_id,
            name,
            slug,
            type,
            description,
            rating,
            price_per_night,
            image
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,

        hotels
    )


    # ==========================================
    # TRANSPORT
    # ==========================================

    transport_routes = [

        (
            "Kuala Lumpur",
            "Batu Caves",
            "Train",
            45,
            5,
            10,
            "Train service where available."
        ),

        (
            "Kuala Lumpur",
            "Batu Caves",
            "Bus",
            60,
            5,
            15,
            "Estimated bus journey."
        ),

        (
            "Kuala Lumpur",
            "Batu Caves",
            "Grab",
            30,
            20,
            35,
            "Estimated ride-hailing price."
        ),

        (
            "Kuala Lumpur",
            "Genting Highlands",
            "Bus",
            90,
            10,
            20,
            "Bus connection to Genting."
        ),

        (
            "Kuala Lumpur",
            "Genting Highlands",
            "Grab",
            70,
            80,
            120,
            "Estimated ride-hailing price."
        )

    ]


    # Likewise, the original transport_routes table has no unique route key.
    existing_routes = {(r[0], r[1], r[2]) for r in cursor.execute(
        'SELECT origin, destination, transport_type FROM transport_routes')}
    transport_routes = [r for r in transport_routes if (r[0],r[1],r[2]) not in existing_routes]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO transport_routes
        (
            origin,
            destination,
            transport_type,
            duration_minutes,
            min_price,
            max_price,
            notes
        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,

        transport_routes
    )


    # ==========================================
    # ACTIVITIES
    # ==========================================

    activities = [

        # --------------------------------------
        # KUALA LUMPUR — CULTURE
        # --------------------------------------

        (
            destination_ids["kuala-lumpur"],
            "Explore Central Market",
            "culture",
            "Explore Malaysian art, crafts, souvenirs and local culture at the historic Central Market.",
            "2 hours",
            0,
            4.4
        ),

        (
            destination_ids["kuala-lumpur"],
            "Visit Petronas Twin Towers",
            "culture",
            "Visit Kuala Lumpur's most iconic landmark and enjoy views of the city from the towers.",
            "2–3 hours",
            98,
            4.7
        ),

        (
            destination_ids["kuala-lumpur"],
            "Explore Chinatown & Petaling Street",
            "culture",
            "Explore one of Kuala Lumpur's busiest cultural districts, filled with markets, food and historic streets.",
            "2–3 hours",
            0,
            4.3
        ),


        # --------------------------------------
        # KUALA LUMPUR — FOOD
        # --------------------------------------

        (
            destination_ids["kuala-lumpur"],
            "Jalan Alor Food Street",
            "food",
            "Experience one of Kuala Lumpur's most famous food streets with Malaysian street food and local dishes.",
            "2 hours",
            30,
            4.5
        ),

        (
            destination_ids["kuala-lumpur"],
            "Malaysian Food Experience",
            "food",
            "Try a variety of Malaysian dishes including nasi lemak, satay, roti canai and local desserts.",
            "2 hours",
            40,
            4.6
        ),


        # --------------------------------------
        # KUALA LUMPUR — PHOTOGRAPHY
        # --------------------------------------

        (
            destination_ids["kuala-lumpur"],
            "Kuala Lumpur City Photography Walk",
            "photography",
            "Capture Kuala Lumpur's skyline, architecture, street scenes and famous landmarks.",
            "3 hours",
            0,
            4.6
        ),

        (
            destination_ids["kuala-lumpur"],
            "Bukit Bintang Night Photography",
            "photography",
            "Photograph Kuala Lumpur's colourful nightlife, neon streets and busy city atmosphere.",
            "2 hours",
            0,
            4.5
        ),


        # --------------------------------------
        # KUALA LUMPUR — SHOPPING
        # --------------------------------------

        (
            destination_ids["kuala-lumpur"],
            "Bukit Bintang Shopping",
            "shopping",
            "Explore some of Kuala Lumpur's most popular shopping malls and retail areas.",
            "3 hours",
            0,
            4.5
        ),


        # --------------------------------------
        # KUALA LUMPUR — NIGHTLIFE
        # --------------------------------------

        (
            destination_ids["kuala-lumpur"],
            "Kuala Lumpur Nightlife",
            "nightlife",
            "Experience Kuala Lumpur after dark with restaurants, rooftop views and entertainment.",
            "3 hours",
            0,
            4.4
        ),


        # --------------------------------------
        # BATU CAVES — CULTURE
        # --------------------------------------

        (
            destination_ids["batu-caves"],
            "Explore Batu Caves",
            "culture",
            "Visit the famous limestone caves, Hindu temples and the iconic golden Lord Murugan statue.",
            "2–3 hours",
            0,
            4.7
        ),


        # --------------------------------------
        # BATU CAVES — PHOTOGRAPHY
        # --------------------------------------

        (
            destination_ids["batu-caves"],
            "Batu Caves Photography",
            "photography",
            "Photograph the colourful staircase, giant golden statue and dramatic limestone surroundings.",
            "2 hours",
            0,
            4.7
        ),


        # --------------------------------------
        # BATU CAVES — NATURE
        # --------------------------------------

        (
            destination_ids["batu-caves"],
            "Explore Batu Caves Nature",
            "nature",
            "Explore the limestone landscape and natural surroundings around the Batu Caves complex.",
            "2 hours",
            0,
            4.3
        ),


        # --------------------------------------
        # GENTING — ADVENTURE
        # --------------------------------------

        (
            destination_ids["genting-highlands"],
            "Genting SkyWorlds",
            "adventure",
            "Enjoy rides, attractions and entertainment at Genting SkyWorlds theme park.",
            "5–6 hours",
            120,
            4.5
        ),

        (
            destination_ids["genting-highlands"],
            "Genting Highlands Cable Car",
            "adventure",
            "Ride the cable car through the mountains and enjoy panoramic views of the surrounding highlands.",
            "1 hour",
            10,
            4.5
        ),


        # --------------------------------------
        # GENTING — NATURE
        # --------------------------------------

        (
            destination_ids["genting-highlands"],
            "Genting Highlands Mountain Experience",
            "nature",
            "Enjoy the cool mountain climate and scenic highland views away from the city.",
            "2 hours",
            0,
            4.3
        ),


        # --------------------------------------
        # GENTING — SHOPPING
        # --------------------------------------

        (
            destination_ids["genting-highlands"],
            "Genting Premium Shopping",
            "shopping",
            "Explore shopping, entertainment and dining options around the Genting resort area.",
            "3 hours",
            0,
            4.2
        )

    ]


    # Activities have no UNIQUE constraint in the original schema. Filter out
    # existing activity identities first so running seed_db twice is safe.
    already_seeded = {(r[0], r[1], r[2]) for r in cursor.execute(
        'SELECT destination_id, name, category FROM activities')}
    activities = [a for a in activities if (a[0], a[1], a[2]) not in already_seeded]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO activities
        (
            destination_id,
            name,
            category,
            description,
            duration,
            price,
            rating
        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,

        activities
    )



    # Additional destination discovery entries. Attraction, hotel and activity
    # listings are only shown where real records have been added to the database.
    extra_destinations = [
        ("Penang", "penang", "Penang Island’s heritage, beaches and renowned food culture, including George Town.", ""),
        ("Langkawi", "langkawi", "An island escape with beaches, forests and scenic viewpoints.", ""),
        ("Melaka", "melaka", "A historic riverside city known for its multicultural heritage.", ""),
        ("Cameron Highlands", "cameron-highlands", "Cool highland scenery, tea plantations and walking trails.", ""),
        ("Ipoh", "ipoh", "Limestone hills, heritage streets and local food favourites.", ""),
        ("Kota Kinabalu", "kota-kinabalu", "Sabah's coastal gateway to islands and mountain adventures.", ""),
        ("Kuching", "kuching", "Sarawak's riverside capital and gateway to rainforest experiences.", ""),
        ("Johor Bahru", "johor-bahru", "A lively southern city with food, shopping and family attractions.", ""),
        ("Taman Negara", "taman-negara", "A tropical rainforest destination with guided nature experiences.", ""),
        ("Perhentian Islands", "perhentian-islands", "Clear-water island escapes popular for snorkelling and beaches.", ""),
        ("Tioman Island", "tioman-island", "A scenic island known for beaches, diving and forested hills.", ""),
        ("Putrajaya", "putrajaya", "Lakeside architecture, gardens and striking modern landmarks.", "")
    ]
    cursor.executemany("INSERT OR IGNORE INTO destinations (name,slug,description,image) VALUES (?,?,?,?)", extra_destinations)

    _add_location_content(connection)

    # ==========================================
    # SAVE DATABASE
    # ==========================================

    connection.commit()

    connection.close()

    print("Database seeded successfully.")



def _add_location_content(db):
    """Starter guide content. Distances from GPS use approximate centre points
    unless an attraction/hotel has an individual latitude/longitude.
    Never imply that the seed ratings/prices are live quotes.
    """
    centres={
       'kuala-lumpur':(3.1390,101.6869), 'batu-caves':(3.2379,101.6831),
       'genting-highlands':(3.4216,101.7935),'penang':(5.4141,100.3288),
       'langkawi':(6.3500,99.8000),'melaka':(2.1896,102.2501),
       'cameron-highlands':(4.4705,101.3761),'ipoh':(4.5975,101.0901),
       'kota-kinabalu':(5.9804,116.0735),'kuching':(1.5535,110.3593),
       'johor-bahru':(1.4927,103.7414),'taman-negara':(4.3868,102.4010),
       'perhentian-islands':(5.9100,102.7350),'tioman-island':(2.7902,104.1690),
       'putrajaya':(2.9264,101.6964)
    }
    # The Penang guide uses George Town as its approximate map anchor, not the whole state.
    for slug,(lat,lon) in centres.items():
        db.execute('UPDATE destinations SET latitude=?,longitude=? WHERE slug=?',(lat,lon,slug))
    for slug,lat,lon in [
      ('petronas-twin-towers',3.1578,101.7118),('central-market',3.1457,101.6958),
      ('batu-caves-attraction',3.2379,101.6831),('genting-skyworlds',3.4236,101.7941)]:
        db.execute('UPDATE attractions SET latitude=?,longitude=? WHERE slug=?',(lat,lon,slug))

    destinations={r['slug']:r['id'] for r in db.execute('SELECT id,slug FROM destinations')}
    extra_attractions=[
      ('penang','Khoo Kongsi','culture','Historic clanhouse with distinctive architecture.'),
      ('penang','Penang Street Art','culture','Explore the murals and streets of George Town.'),
      ('penang','Penang Hill','nature','Hilltop views and forest landscapes near George Town.'),
      ('penang','Kek Lok Si Temple','culture','Hilltop Buddhist temple complex in Air Itam.'),
      ('penang','Chew Jetty','culture','Historic waterfront clan settlement in George Town.'),
      ('penang','Batu Ferringhi Beach','nature','Northern Penang beach destination.'),
      ('penang','Penang National Park','nature','Coastal forest walks on Penang Island.'),
      ('langkawi','Langkawi Sky Bridge','nature','A high-altitude pedestrian bridge with island views.'),
      ('langkawi','Kilim Karst Geoforest Park','nature','Mangroves and limestone landscapes.'),
      ('melaka','A Famosa','culture','Historic Portuguese-era fortress remains.'),
      ('melaka','Jonker Street','food','Historic street known for shops, heritage and food.'),
      ('cameron-highlands','BOH Tea Centre','nature','Tea plantation landscapes and visitor facilities.'),
      ('cameron-highlands','Mossy Forest','nature','Cool highland forest with unusual mossy vegetation.'),
      ('ipoh','Concubine Lane','culture','Heritage lane in Ipoh old town.'),
      ('ipoh','Kek Lok Tong','nature','Limestone cave temple and landscaped grounds.'),
      ('kota-kinabalu','Tanjung Aru Beach','nature','Coastal beach renowned for its sunset views.'),
      ('kota-kinabalu','Kota Kinabalu City Mosque','culture','A mosque beside a reflective lagoon.'),
      ('kuching','Kuching Waterfront','culture','Scenic riverfront promenade in Kuching.'),
      ('kuching','Sarawak Cultural Village','culture','Open-air cultural site outside central Kuching.'),
      ('johor-bahru','Sultan Abu Bakar State Mosque','culture','Historical mosque overlooking the Straits of Johor.'),
      ('johor-bahru','Johor Bahru Old Chinese Temple','culture','Historic temple in central Johor Bahru.'),
      ('taman-negara','Taman Negara National Park','nature','Rainforest hiking and guided nature experiences.'),
      ('perhentian-islands','Long Beach, Perhentian Kecil','nature','Sandy beach on Perhentian Kecil.'),
      ('perhentian-islands','Coral Bay, Perhentian Kecil','nature','Quieter beach and sunset views.'),
      ('tioman-island','Juara Beach','nature','Tioman coast with forested mountains.'),
      ('tioman-island','Salang Beach','nature','A coastal village beach on Tioman.'),
      ('putrajaya','Putra Mosque','culture','Landmark mosque near Putrajaya Lake.'),
      ('putrajaya','Putrajaya Botanical Garden','nature','Landscape gardens and walking paths.')
    ]
    import re
    for slug,name,category,description in extra_attractions:
        id=destinations.get(slug)
        if not id:continue
        key=re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-')
        db.execute("""INSERT OR IGNORE INTO attractions(destination_id,name,slug,category,description,rating,price,image)
                      VALUES(?,?,?,?,?,NULL,NULL,NULL)""",(id,name,key,category,description))

    # Create starter itinerary activities for the additional destination entries.
    # NULL price/rating means unverified, NOT free/zero or an actual review score.
    # An estimated 2-hour visit is a suggested planning block, not operating hours.
    for slug,name,category,description in extra_attractions:
        destination_id=destinations.get(slug)
        if destination_id is None:continue
        activity_name='Explore '+name
        exists=db.execute('SELECT 1 FROM activities WHERE destination_id=? AND name=?',
                          (destination_id,activity_name)).fetchone()
        if not exists:
            db.execute('''INSERT INTO activities
              (destination_id,name,category,description,duration,price,rating)
              VALUES(?,?,?,?,?,NULL,NULL)''',
              (destination_id,activity_name,category,description,'2 hours'))

    # Only seed hotel profiles with independently verified public property pages.
    # Availability and prices are never stored or implied for these additional hotels.
    hotels=[
      ('penang','Eastern & Oriental Hotel','https://www.booking.com/hotel/my/eastern-oriental.html'),
      ('langkawi','Berjaya Langkawi Resort','https://www.booking.com/hotel/my/berjaya-langkawi-beach-spa-resort.html'),
      ('melaka','Casa del Rio Melaka','https://www.booking.com/hotel/my/casa-del-rio-melaka.html'),
      ('taman-negara','Mutiara Taman Negara','https://www.booking.com/hotel/my/mutiara-taman-negara.html')
    ]
    for slug,name,link in hotels:
        id=destinations.get(slug)
        if not id:continue
        key=re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-')
        db.execute("""INSERT OR IGNORE INTO hotels
         (destination_id,name,slug,type,description,rating,price_per_night,image,booking_url)
         VALUES(?,?,?,?,?,NULL,NULL,NULL,?)""",(id,name,key,'hotel',
         'Property profile for trip planning; check the provider for live details.',link))
        db.execute('UPDATE hotels SET booking_url=? WHERE slug=?',(link,key))


if __name__ == "__main__":
    seed_database()
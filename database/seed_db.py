import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / "database" / "tourism.db"


def seed_database():

    connection = sqlite3.connect(DATABASE_PATH)

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


    # ==========================================
    # SAVE DATABASE
    # ==========================================

    connection.commit()

    connection.close()

    print("Database seeded successfully.")


if __name__ == "__main__":
    seed_database()
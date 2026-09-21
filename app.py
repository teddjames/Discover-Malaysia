from flask import Flask, render_template, request

from database.db import get_db_connection

app = Flask(__name__)


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# ABOUT
# ==========================================

@app.route("/about")
def about():
    return render_template("about.html")


# ==========================================
# EXPLORE
# ==========================================

@app.route("/explore")
def explore():
    return render_template("explore.html")


# ==========================================
# ATTRACTIONS
# ==========================================

@app.route("/attractions")
def attractions():

    connection = get_db_connection()

    attractions = connection.execute(
        """
        SELECT
            attractions.*,
            destinations.name AS destination_name

        FROM attractions

        JOIN destinations
        ON attractions.destination_id = destinations.id

        ORDER BY attractions.rating DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "attractions.html",
        attractions=attractions
    )


# ==========================================
# HOTELS
# ==========================================

@app.route("/hotels")
def hotels():

    connection = get_db_connection()

    hotels = connection.execute(
        """
        SELECT
            hotels.*,
            destinations.name AS destination_name

        FROM hotels

        JOIN destinations
        ON hotels.destination_id = destinations.id

        ORDER BY hotels.rating DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "hotels.html",
        hotels=hotels
    )


# ==========================================
# TRANSPORT PAGE
# ==========================================

@app.route("/transport")
def transport():

    return render_template("transport.html")


# ==========================================
# TRANSPORT API
# ==========================================

@app.route("/api/transport")
def transport_api():

    origin = request.args.get("origin")
    destination = request.args.get("destination")

    if not origin or not destination:

        return {
            "error": "Origin and destination are required."
        }, 400


    connection = get_db_connection()

    routes = connection.execute(
        """
        SELECT
            transport_type,
            duration_minutes,
            min_price,
            max_price,
            notes

        FROM transport_routes

        WHERE origin = ?
        AND destination = ?

        ORDER BY min_price ASC
        """,

        (origin, destination)

    ).fetchall()

    connection.close()


    return {

        "origin": origin,

        "destination": destination,

        "routes": [

            {
                "transport_type":
                    route["transport_type"],

                "duration_minutes":
                    route["duration_minutes"],

                "min_price":
                    route["min_price"],

                "max_price":
                    route["max_price"],

                "notes":
                    route["notes"]

            }

            for route in routes

        ]

    }


# ==========================================
# TRIP PLANNER PAGE
# ==========================================

@app.route("/trip-planner")
def trip_planner():

    return render_template(
        "trip_planner.html"
    )


# ==========================================
# TRIP PLANNER API
# ==========================================

# ==========================================
# TRIP PLANNER API
# ==========================================

@app.route(
    "/api/trip-planner",
    methods=["POST"]
)
def trip_planner_api():

    # ------------------------------------------
    # GET USER PREFERENCES
    # ------------------------------------------

    data = request.get_json()

    if not data:

        return {
            "error":
                "No trip preferences were provided."
        }, 400


    days = data.get("days")

    budget = data.get("budget")

    interests = data.get(
        "interests",
        []
    )

    destinations = data.get(
        "destinations",
        []
    )


    # ------------------------------------------
    # VALIDATION
    # ------------------------------------------

    if not days:

        return {
            "error":
                "Trip length is required."
        }, 400


    if not budget:

        return {
            "error":
                "Budget is required."
        }, 400


    if not destinations:

        return {
            "error":
                "Please select at least one destination."
        }, 400


    try:

        days = int(days)

    except (TypeError, ValueError):

        return {
            "error":
                "Invalid trip length."
        }, 400


    if days not in [1, 2, 3, 4, 5, 7]:

        return {
            "error":
                "Invalid trip length."
        }, 400


    # ------------------------------------------
    # DATABASE
    # ------------------------------------------

    connection = get_db_connection()


    # ------------------------------------------
    # GET DESTINATIONS
    # ------------------------------------------

    placeholders = ",".join(
        ["?"] * len(destinations)
    )


    destination_query = f"""
        SELECT
            id,
            name,
            slug

        FROM destinations

        WHERE name IN ({placeholders})
    """


    destination_rows = connection.execute(
        destination_query,
        destinations
    ).fetchall()


    destination_ids = [
        row["id"]
        for row in destination_rows
    ]


    if not destination_ids:

        connection.close()

        return {
            "error":
                "No matching destinations were found."
        }, 404


    # ------------------------------------------
    # GET ACTIVITIES
    # ------------------------------------------

    destination_placeholders = ",".join(
        ["?"] * len(destination_ids)
    )


    if interests:

        interest_placeholders = ",".join(
            ["?"] * len(interests)
        )


        activity_query = f"""

            SELECT

                activities.*,

                destinations.name
                AS destination_name

            FROM activities

            JOIN destinations

            ON activities.destination_id =
               destinations.id

            WHERE activities.destination_id
            IN ({destination_placeholders})

            AND activities.category
            IN ({interest_placeholders})

            ORDER BY
                activities.rating DESC

        """


        query_parameters = (
            destination_ids
            + interests
        )


        activity_rows = connection.execute(
            activity_query,
            query_parameters
        ).fetchall()


    else:

        activity_query = f"""

            SELECT

                activities.*,

                destinations.name
                AS destination_name

            FROM activities

            JOIN destinations

            ON activities.destination_id =
               destinations.id

            WHERE activities.destination_id
            IN ({destination_placeholders})

            ORDER BY
                activities.rating DESC

        """


        activity_rows = connection.execute(
            activity_query,
            destination_ids
        ).fetchall()


    # ------------------------------------------
    # CLOSE DATABASE
    # ------------------------------------------

    connection.close()


    # ------------------------------------------
    # CONVERT ACTIVITIES
    # ------------------------------------------

    activities = [

        {
            "id":
                activity["id"],

            "name":
                activity["name"],

            "category":
                activity["category"],

            "description":
                activity["description"],

            "duration":
                activity["duration"],

            "price":
                activity["price"],

            "rating":
                activity["rating"],

            "destination":
                activity["destination_name"]

        }

        for activity in activity_rows

    ]


    # ------------------------------------------
    # BUILD DAY-BY-DAY ITINERARY
    # ------------------------------------------

    itinerary = []

    remaining_activities = activities.copy()


    for day_number in range(1, days + 1):

        day_activities = []

        used_destinations = set()

        total_minutes = 0

        total_cost = 0


        # --------------------------------------
        # TARGET DAY LENGTH
        # --------------------------------------

        target_minutes = 480


        # --------------------------------------
        # SELECT ACTIVITIES
        # --------------------------------------

        for activity in remaining_activities[:]:

            duration_text = activity["duration"]


            # Convert duration to minutes

            if "hour" in duration_text:

                try:

                    hours = float(
                        duration_text
                        .split("–")[0]
                        .replace("hours", "")
                        .replace("hour", "")
                        .strip()
                    )

                    duration_minutes = int(
                        hours * 60
                    )

                except ValueError:

                    duration_minutes = 120

            else:

                duration_minutes = 120


            # ----------------------------------
            # DON'T OVERLOAD THE DAY
            # ----------------------------------

            if (
                total_minutes
                + duration_minutes
                > target_minutes
            ):

                continue


            # ----------------------------------
            # ADD ACTIVITY
            # ----------------------------------

            day_activities.append(
                activity
            )


            total_minutes += (
                duration_minutes
            )


            total_cost += (
                activity["price"]
                or 0
            )


            used_destinations.add(
                activity["destination"]
            )


            remaining_activities.remove(
                activity
            )


            # Aim for roughly 3–4 activities

            if len(day_activities) >= 4:

                break


        # --------------------------------------
        # CREATE DAY
        # --------------------------------------

        itinerary.append({

            "day":
                day_number,

            "activities":
                day_activities,

            "total_cost":
                total_cost,

            "total_minutes":
                total_minutes,

            "destinations":
                list(used_destinations)

        })


    # ------------------------------------------
    # RETURN COMPLETE ITINERARY
    # ------------------------------------------

    return {

        "days":
            days,

        "budget":
            budget,

        "interests":
            interests,

        "destinations":
            destinations,

        "activities":
            activities,

        "itinerary":
            itinerary

    }

# ==========================================
# ITINERARY PAGE
# ==========================================

@app.route("/itinerary")
def itinerary():

    return render_template(
        "itinerary.html"
    )


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
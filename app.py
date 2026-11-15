"""Discover Malaysia: nearby discovery, destination guides, stays and trip planning.

GPS coordinates are used for a nearby search and not stored in SQLite.
They are sent as query parameters; browser history and server access logs may
contain the submitted coordinates.
Google Maps / Booking.com links are optional external navigation.
"""
from datetime import date, datetime, timedelta
from math import radians, sin, cos, asin, sqrt
from urllib.parse import urlencode
from flask import Flask, abort, render_template, request
from database.db import get_db_connection
from transport_guide import options_for

app = Flask(__name__)


def distance_km(lat1, lon1, lat2, lon2):
    """Great-circle distance, not road mileage or travel time."""
    r = 6371.0
    dlat, dlon = radians(lat2-lat1), radians(lon2-lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return r*2*asin(min(1,sqrt(a)))


def get_destinations(connection):
    return [dict(x) for x in connection.execute('SELECT * FROM destinations ORDER BY name')]


def geo_options(connection):
    """Use a selected city centre or an explicitly shared browser position."""
    near = request.args.get('near','').strip()[:100]
    radius = request.args.get('radius','75')
    try: radius = min(500, max(5, int(radius)))
    except (ValueError,TypeError): radius = 75
    lat,lon = request.args.get('lat',''),request.args.get('lon','')
    center = None
    geo_source = ''
    if lat and lon:
        try:
            lt,lg = float(lat),float(lon)
            if -90<=lt<=90 and -180<=lg<=180:
                center=(lt,lg);geo_source='Your shared location'
        except (ValueError,TypeError): pass
    if center is None and near:
        row=connection.execute('SELECT name,latitude,longitude FROM destinations WHERE slug=?',(near,)).fetchone()
        if row and row['latitude'] is not None and row['longitude'] is not None:
            center=(row['latitude'],row['longitude']);geo_source=row['name']+' (city centre)'
    return dict(near=near, radius=radius, lat=lat if center and geo_source=='Your shared location' else '', lon=lon if center and geo_source=='Your shared location' else '', center=center,geo_source=geo_source)


def sort_by_proximity(rows,geo,limit=None):
    results=[]
    for row in rows:
        d=dict(row)
        d['distance_km']=None
        lt,lg=d.get('latitude'),d.get('longitude')
        if geo['center']:
            if lt is None or lg is None:continue
            d['distance_km']=round(distance_km(*geo['center'],lt,lg),1)
            if d['distance_km']>geo['radius']:continue
        results.append(d)
    if geo['center']:
        results.sort(key=lambda x:(x['distance_km'],x.get('name','')))
    return results[:limit] if limit else results


def maps_search(search_term):
    return 'https://www.google.com/maps/search/?'+urlencode({'api':1,'query':search_term})


def maps_directions(destination, origin='', mode='driving'):
    args={'api':1,'destination':destination,'travelmode':mode}
    if origin:args['origin']=origin
    return 'https://www.google.com/maps/dir/?'+urlencode(args)


def booking_search(place):
    return 'https://www.booking.com/searchresults.html?'+urlencode({'ss':place+', Malaysia','selected_currency':'MYR'})


def linked_hotels(rows):
    result=[]
    for item in rows:
        h=dict(item)
        # Only source-verified property URLs are used directly. Other entries
        # link to a Booking.com search where the visitor chooses the property.
        h['booking_link']=h.get('booking_url') or booking_search(h['name']+', '+h['destination_name'])
        h['maps_link']=maps_directions(h['name']+', '+h['destination_name']+', Malaysia')
        result.append(h)
    return result


@app.route('/')
def home():
    db=get_db_connection()
    destinations=db.execute("SELECT * FROM destinations ORDER BY CASE slug WHEN 'kuala-lumpur' THEN 0 WHEN 'penang' THEN 1 WHEN 'langkawi' THEN 2 WHEN 'genting-highlands' THEN 3 WHEN 'melaka' THEN 4 WHEN 'kota-kinabalu' THEN 5 ELSE 6 END, name LIMIT 6").fetchall()
    db.close()
    return render_template('index.html',destinations=destinations)


@app.route('/about')
def about():
    # Older projects may not include about.html; redirect to the guide.
    from flask import redirect, url_for
    return redirect(url_for('explore'))


@app.route('/explore')
def explore():
    query=request.args.get('q','').strip()[:120]
    db=get_db_connection()
    geo=geo_options(db)
    params=[]
    sql='SELECT * FROM destinations'
    if query:
        sql+=' WHERE name LIKE ? OR description LIKE ?'
        params=[f'%{query}%',f'%{query}%']
    sql+=' ORDER BY name'
    rows=db.execute(sql,params).fetchall()
    destinations=sort_by_proximity(rows,geo)
    cities=get_destinations(db)
    db.close()
    return render_template('explore.html',destinations=destinations,all_destinations=cities,query=query,geo=geo)


@app.route('/destinations/<slug>')
def destination_detail(slug):
    if slug=='george-town':
        from flask import redirect, url_for
        return redirect(url_for('destination_detail',slug='penang'),code=301)
    db=get_db_connection()
    destination=db.execute('SELECT * FROM destinations WHERE slug=?',(slug,)).fetchone()
    if destination is None:
        db.close();abort(404)
    attractions=db.execute('SELECT * FROM attractions WHERE destination_id=? ORDER BY CASE WHEN rating>0 THEN 0 ELSE 1 END,rating DESC,name LIMIT 6',(destination['id'],)).fetchall()
    hotels=db.execute('SELECT h.*, d.name AS destination_name FROM hotels h JOIN destinations d ON h.destination_id=d.id WHERE d.id=? ORDER BY h.name LIMIT 4',(destination['id'],)).fetchall()
    origins=get_destinations(db)
    db.close()
    destination=dict(destination)
    name=destination['name']+', Malaysia'
    return render_template('destination_detail.html',d=destination,attractions=attractions,hotels=linked_hotels(hotels),origins=origins,booking_link=booking_search(destination['name']),driving_link=maps_directions(name,mode='driving'),transit_link=maps_directions(name,mode='transit'),more_attractions_link=maps_search('attractions near '+name))


@app.route('/attractions')
def attractions():
    query=request.args.get('q','').strip()[:120]
    location=request.args.get('location','').strip()[:100]
    category=request.args.get('category','').strip()[:50]
    db=get_db_connection();geo=geo_options(db)
    conditions=[];params=[]
    if query:
        conditions.append('(a.name LIKE ? OR a.description LIKE ? OR d.name LIKE ?)')
        params.extend([f'%{query}%']*3)
    if location:
        conditions.append('d.slug=?');params.append(location)
    if category:
        conditions.append('a.category=?');params.append(category)
    where=(' WHERE '+' AND '.join(conditions)) if conditions else ''
    sql="""SELECT a.id,a.destination_id,a.name,a.slug,a.category,a.description,a.rating,a.price,a.image, d.name AS destination_name,d.slug AS destination_slug,
          COALESCE(a.latitude,d.latitude) AS latitude,
          COALESCE(a.longitude,d.longitude) AS longitude,
          CASE WHEN a.latitude IS NULL THEN 1 ELSE 0 END AS approximate_location
          FROM attractions a JOIN destinations d ON a.destination_id=d.id"""+where+' ORDER BY a.rating DESC,a.name'
    rows=db.execute(sql,params).fetchall()
    found=sort_by_proximity(rows,geo)
    for x in found:
        x['maps_link']=maps_directions(x['name']+', '+x['destination_name']+', Malaysia')
    cities=get_destinations(db)
    categories=db.execute('SELECT DISTINCT category FROM attractions WHERE category IS NOT NULL ORDER BY category').fetchall()
    place=next((x['name'] for x in cities if x['slug']==location),None) or (str(geo['center'][0])+','+str(geo['center'][1]) if geo['geo_source']=='Your shared location' else geo['geo_source']) or 'Malaysia'
    nearby_link=maps_search('tourist attractions near '+place+', Malaysia')
    db.close()
    return render_template('attractions.html',attractions=found,destinations=cities,categories=categories,query=query,location=location,category=category,geo=geo,nearby_link=nearby_link)


@app.route('/hotels')
def hotels():
    query=request.args.get('q','').strip()[:120]
    location=request.args.get('location','').strip()[:100]
    accommodation_type=request.args.get('type','').strip()[:50]
    db=get_db_connection();geo=geo_options(db)
    conditions=[];params=[]
    if query:
        conditions.append('(h.name LIKE ? OR h.description LIKE ? OR d.name LIKE ?)');params.extend([f'%{query}%']*3)
    if location:conditions.append('d.slug=?');params.append(location)
    if accommodation_type:conditions.append('h.type=?');params.append(accommodation_type)
    where=(' WHERE '+' AND '.join(conditions)) if conditions else ''
    sql="""SELECT h.id,h.destination_id,h.name,h.slug,h.type,h.description,h.rating,h.price_per_night,h.image,h.booking_url, d.name AS destination_name,d.slug AS destination_slug,
          COALESCE(h.latitude,d.latitude) AS latitude,
          COALESCE(h.longitude,d.longitude) AS longitude,
          CASE WHEN h.latitude IS NULL THEN 1 ELSE 0 END AS approximate_location
          FROM hotels h JOIN destinations d ON h.destination_id=d.id"""+where+' ORDER BY h.name'
    rows=sort_by_proximity(db.execute(sql,params).fetchall(),geo)
    found=linked_hotels(rows)
    cities=get_destinations(db)
    types=db.execute('SELECT DISTINCT type FROM hotels WHERE type IS NOT NULL ORDER BY type').fetchall()
    chosen=next((x['name'] for x in cities if x['slug']==location),None)
    if not chosen and geo['center']:
        ranked=sort_by_proximity(cities,dict(geo,radius=500000))
        chosen=ranked[0]['name'] if ranked else None
    chosen=chosen or geo['geo_source'] or 'Malaysia'
    booking_link=booking_search(chosen)
    nearby_link=maps_search('accommodation near '+(str(geo['center'][0])+','+str(geo['center'][1]) if geo['geo_source']=='Your shared location' else chosen)+', Malaysia')
    db.close()
    return render_template('hotels.html',hotels=found,destinations=cities,types=types,query=query,location=location,accommodation_type=accommodation_type,geo=geo,booking_link=booking_link,nearby_link=nearby_link,chosen_place=chosen)


@app.route('/transport')
def transport():
    db=get_db_connection()
    origins=[r[0] for r in db.execute('SELECT DISTINCT origin FROM transport_routes ORDER BY origin')]
    routes_dest=[r[0] for r in db.execute('SELECT DISTINCT destination FROM transport_routes ORDER BY destination')]
    destinations=get_destinations(db)
    db.close()
    origin=request.args.get('origin','')[:100]
    destination=request.args.get('destination','')[:100]
    if origin and origin not in origins: origins.append(origin)
    if destination and destination not in routes_dest: routes_dest.append(destination)
    return render_template('transport.html',origins=origins,destinations=routes_dest,all_destinations=destinations,selected_origin=origin,selected_destination=destination)


@app.route('/api/transport')
def transport_api():
    origin=request.args.get('origin','').strip()[:100]
    destination=request.args.get('destination','').strip()[:100]
    if not origin or not destination:
        return {'error':'Origin and destination are required.'},400
    db=get_db_connection()
    source=db.execute('SELECT * FROM destinations WHERE name=?',(origin,)).fetchone()
    target=db.execute('SELECT * FROM destinations WHERE name=?',(destination,)).fetchone()
    if not source or not target:
        db.close()
        return {'error':'Choose origins and destinations from the destination list.'},400
    if origin==destination:
        db.close()
        return {'error':'Choose two different destinations.'},400
    rows=db.execute("""SELECT transport_type,duration_minutes,min_price,max_price,notes
        FROM transport_routes WHERE origin=? AND destination=?
        GROUP BY transport_type,duration_minutes,min_price,max_price,notes
        ORDER BY min_price""",(origin,destination)).fetchall()
    db.close()
    return dict(
        origin=origin,destination=destination,
        routes=[dict(r) for r in rows],
        recommendations=options_for(dict(source),dict(target)),
        maps_driving=maps_directions(destination+', Malaysia',origin+', Malaysia',mode='driving'),
        maps_transit=maps_directions(destination+', Malaysia',origin+', Malaysia',mode='transit'),
        disclaimer='Transport modes are suggested ways to investigate, not confirmed direct services. Prices, dates, seats, and operating times must be checked on the provider website.'
    )


# ==========================================
# TRIP PLANNER PAGE
# ==========================================

@app.route("/trip-planner")
def trip_planner():

    connection = get_db_connection()
    destinations = connection.execute("SELECT name,slug FROM destinations ORDER BY name").fetchall()
    connection.close()
    selected=request.args.get('destination','').strip()
    matching=next((d['name'] for d in destinations if selected in (d['name'],d['slug'])),None)
    return render_template('trip_planner.html', destinations=destinations, selected_destination=matching)


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

    if not isinstance(data,dict) or not data:

        return {
            "error":
                "No trip preferences were provided."
        }, 400


    # The browser sends two calendar dates; days are inclusive (arrival and
    # departure both appear on the itinerary). Legacy numeric "days" requests
    # remain supported for compatibility with older clients.
    start_raw = data.get('start_date')
    end_raw = data.get('end_date')
    start_day = end_day = None
    if start_raw is not None or end_raw is not None:
        if not isinstance(start_raw,str) or not isinstance(end_raw,str):
            return {'error':'Select both arrival and departure dates.'},400
        try:
            start_day = date.fromisoformat(start_raw)
            end_day = date.fromisoformat(end_raw)
        except ValueError:
            return {'error':'Please select valid calendar dates.'},400
        if end_day < start_day:
            return {'error':'Departure date cannot be earlier than arrival date.'},400
        days = (end_day-start_day).days + 1
    else:
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

    if (not isinstance(destinations, list) or not isinstance(interests, list)
            or len(destinations) > 30 or len(interests) > 30
            or any(not isinstance(x,str) for x in destinations)):
        return {"error": "Invalid selection."}, 400


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


    if days < 1 or days > 90:

        return {
            "error":
                "Invalid trip length."
        }, 400


    if budget not in ('conservative','moderate','luxury'):
        return {'error':'Choose a valid budget.'},400

    allowed_interests={'food','photography','culture','adventure','shopping','nightlife','nature','family','anything'}
    if any(not isinstance(i,str) or i not in allowed_interests for i in interests):
        return {'error':'Please choose valid interests.'},400
    # Anything means show every activity category, regardless of other choices.
    if 'anything' in interests:
        interests=['anything']
    interest_filter=[] if 'anything' in interests else interests

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


    if interest_filter:

        interest_placeholders = ",".join(
            ["?"] * len(interest_filter)
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
            + interest_filter
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


    interest_fallback=False
    if interest_filter and not activity_rows:
        activity_rows=connection.execute(f'''SELECT activities.*, destinations.name AS destination_name
            FROM activities JOIN destinations ON activities.destination_id=destinations.id
            WHERE activities.destination_id IN ({destination_placeholders})
            ORDER BY activities.rating DESC''', destination_ids).fetchall()
        interest_fallback=True

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

    # Rotate activities across days, rather than consuming everything on day 1.
    remaining_activities = activities.copy()


    per_day = max(1, (len(remaining_activities) + days - 1) // days)
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

            if len(day_activities) >= min(4,per_day):

                break


        # --------------------------------------
        # CREATE DAY
        # --------------------------------------

        itinerary.append({

            "date": (start_day + timedelta(days=day_number-1)).isoformat() if start_day else None,
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
        "nights": max(0, days-1),
        "start_date": start_day.isoformat() if start_day else None,
        "end_date": end_day.isoformat() if end_day else None,

        "budget":
            budget,
        "interest_fallback": interest_fallback,

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

    return render_template("itinerary.html")


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
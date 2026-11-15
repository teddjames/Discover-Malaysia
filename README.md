# Discover Malaysia — Explore, Stay, Travel & Plan

An upgraded Flask + SQLite travel platform built around the flow **Discover → Explore → Stay → Directions → Booking provider**. Includes the light editorial sage-and-ivory photographic landing page, interactive globe, and an activity-based trip planner connected to each destination guide.

## Website description

**Discover Malaysia** is an interactive travel discovery and planning platform built to help visitors explore Malaysia in one connected experience. Travellers can browse selected well-known destinations, search for nearby attractions and accommodation using a manually selected city or their optional browser location, and open destination guides that bring together places to visit, hotel-provider links, travel directions, and transportation options. The transport guide suggests suitable flights, trains, buses, taxis, ferries, cable cars and connecting journeys where relevant, with links to operators so travellers can check current schedules and booking availability. The trip planner lets visitors select their own arrival and departure dates (up to 90 calendar days), choose a budget style, pick destinations and interests—including an **Anything & Everything** choice—and generate a day-by-day itinerary based on curated activities in the SQLite database. The service is an independent discovery and planning guide, not a direct hotel reservation or ticketing engine, and focuses on popular locations rather than claiming comprehensive national coverage.

## New: immersive 3D interface

The preceding release introduced the dark emerald 3D globe. In this edition the globe remains available in a dedicated exploration section, while the landing page uses an airy, photograph-led design featuring:

- A **fully interactive projected 3D globe** made with HTML Canvas: drag to rotate, tap/click a destination marker to open its guide, hover or focus the destination shortcuts to centre a city, and use the reset button to return to Malaysia. Malaysia is highlighted against real simplified global coastlines.
- The land shape data lives in `static/data/world-geo.json`, simplified from **Natural Earth low-resolution geography (public domain)**. Country outlines are decorative, not a navigational map or precise geographical boundary reference.
- **3D-depth cards**, cursor-following perspective tilts, glass-like information surfaces, soft ambience, scroll reveals and a premium charcoal/emerald palette. Cards become conventional clickable links and can be filtered by Cities & culture / Nature & highlands / Islands & beaches.
- A location search at the centre of the hero, and direct links to itinerary generation, destinations, accommodation and travel routes.
- Native, no-CDN-dependent globe rendering (the rest of the page uses Google Fonts when online, with local font fallbacks). The globe works without WebGL or extra JavaScript dependencies. If the geographic JSON cannot load, the globe displays a graticule-style fallback.
- Mobile-friendly layout, accessible destination shortcuts, keyboard-visible focus rings, an accessible skip link, and reduced-motion support. Decorative animations pause when the globe is off-screen or the page is hidden.

**Added/changed:** `templates/index.html`, `templates/base.html`, `static/css/immersive.css`, `static/js/immersive.js`, `static/data/world-geo.json`, and `app.py` (home featured-order only). All existing routes, database tables, calendar planner and transport recommendation logic remain intact.

**Images:** This edition bundles 15 user-supplied travel photographs as optimised WebP files under `static/images/editorial/`. Photographs appear on the landing page and throughout destination discovery; other specialised images may be added as needed.

## New in this version

- **Discover Malaysia** is the site name and brand across the landing page, navigation, and footer.
- The landing page is the starting point for destination search, attractions, accommodation, routes, and itinerary planning.
- **Penang** replaces George Town as the destination name and URL slug (`/destinations/penang`), with George Town covered within its attractions. Older `/destinations/george-town` links redirect to the new URL.
- Destination pages now have **Plan a trip here**, pre-selecting that destination when the user opens the Trip Planner.
- An explicit site disclaimer reads: **“Not all exploration destinations are captured here. Just well known ones.”**
- The destination content list is illustrative, not comprehensive; the planner can only suggest activities included in the database. Additional destinations now have suggested itinerary activities. Unverified ticket prices and ratings are left blank (not zero).

## Functionality

- **Use my location** (optional browser geolocation, with consent). Search within a configurable 10–500 km straight-line radius, sorted by proximity.
- **Manual location selection** works even if GPS is off, unavailable, or denied.
- Destination, attraction and stay searches use a parameterised SQLite query. Discover from 15 starter destinations and 32 sample attraction records (numbers may increase as you expand the database).
- **Destination detail pages** at `/destinations/<slug>` combine local highlights, hotel listings, a link to external accommodation search, Google Maps directions, and a link to the transport comparator.
- **More nearby** links open Google Maps searches, so visitors can discover places beyond your curated SQLite records.
- **Check availability** links to source-verified Booking.com property pages for selected properties, or to Booking.com property searches. Visitors select dates and complete bookings at the third-party provider. **No reservation or payment happens in Discover Malaysia.**
- Transport now includes route-sensitive flight, bus, train, cab, drive, boat and Genting cable-car guidance with provider links. Existing SQLite fares remain separately marked illustrative, and Google Maps supplies supplemental directions.
- Seed scripts are idempotent with respect to newly inserted activity and route records (older existing duplicates aren't deleted).

## Run in VS Code

From the project root (`app.py` should be in this folder):

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python database/init_db.py
python database/seed_db.py
python app.py
```

Open http://127.0.0.1:5000.

**This ZIP includes all 15 destination photos supplied for the redesign.** You can still add more photography under `static/images/` as you expand the attraction and hotel catalogues.

**If merging with your existing project:** first **back up `database/tourism.db`** and retain your original DB to preserve personal additions. Copy the updated source, templates, static JS/CSS, schema and seed files, **do not overwrite your own tourism.db** unless you specifically want to use the bundled demo DB. Then run `init_db.py` and `seed_db.py` to migrate it in-place, adding GPS coordinates and curated starter entries without dropping your tables.

## Try the new flow

1. Start on the **Discover Malaysia** landing page → search **Penang** → open the destination guide.
2. Select **Find somewhere to stay** → the Stay page is filtered to that destination. Click **Check availability** → Booking.com opens in a new tab.
3. Back in the Langkawi guide, choose **Driving directions** (Google Maps) or **Compare transport** to view any stored routes and Maps fallbacks.
4. Select **Plan a trip here** on a destination guide to open the planner with that destination already selected. Or visit **Attractions** or **Stay**, select a city in **SEARCH NEAR**, set radius and submit. For GPS, click **Use my location** and grant browser permission.

## Technical notes and limitations

- **Geolocation:** requires HTTPS or localhost in most browsers, and explicit browser permission. Latitude/longitude are sent to Flask via GET query parameters, which can appear in browser history or web-server access logs. The app **does not permanently store coordinates in SQLite**. For stronger privacy in production, switch location search to a POST/API workflow with logging controls.
- **Proximity:** calculated as great-circle (straight-line) kilometres. Some older/starter hotels and attractions inherit an **approximate destination-centre coordinate**; this is labelled in results and should **not** be interpreted as precise distance to a property. It is not road distance, journey time, or a route planner.
- **Coverage:** the curated SQLite catalogue is intentionally finite. Google Maps search expands *discovery* coverage outside the guide. Booking.com opens externally for larger stay coverage and availability. Neither provider's results are integrated into the Flask database. Production-grade embedded universal search would need a licensed places/hotels API and the provider's terms/credentials.
- **Bookings:** Discover Malaysia does not hold rooms, take deposits, process payments, or verify live availability or room rates.
- **Fares and legacy ratings:** existing sample price/rating/route estimates are historical/unverified and should **not** be published as live quotes. Added attraction/hotel entries have no invented prices or ratings.
- **Trip planner:** Choose your own arrival/departure dates (up to 90 inclusive calendar days) and use the Anything & Everything interest to include all stored categories. The day planner uses only existing database activities and suggested time blocks; it does not compute road travel time, opening-hour feasibility, or a guaranteed budget. Missing prices are omitted from listed-price totals. If no activities match the chosen interests it may fall back to other stored activities and labels that choice.
- **Travel logistics:** islands and other destinations may require flights, ferries or guided transfers. Google Maps may not show every suitable route; check operators before booking.
- **Images:** the original photographs were not provided in the uploaded source files. Place your own assets under `static/images/`. New listings use placeholders.

## Files changed

- `app.py` — location search, linked destination guide, external booking and directions URLs
- `database/init_db.py` — backward-compatible migration for latitude/longitude/booking URL
- `database/seed_db.py` — coordinates, broader attractions, verified example property links, idempotent insertion
- `templates/_location_search.html` — reusable GPS/manual nearby filter
- `templates/destination_detail.html` — complete destination journey
- `templates/{explore,attractions,hotels,transport,index,base}.html` — new linked workflows
- `static/js/location.js`, `static/js/transport.js` — permission-based GPS and directions fallback
- `static/css/style.css` — new forms, detail page, booking panels and mobile layouts
- `tests/test_app.py` — Flask smoke tests

### Test after installing Flask

```powershell
python -m unittest discover -s tests -v
```

**Development:** this is a functioning local codebase with SQLite search and external booking/directions handoffs. It is not a real-time hotel booking engine or a live transport API.

## Renaming existing records

`python database/init_db.py` migrates an existing `george-town` destination row to `penang` in place, retaining its primary key and existing attraction and hotel associations. Then `python database/seed_db.py` adds new records only if missing. If you had independently created a separate `penang` row in your database already, review and merge those two entries manually before using the new seed. Back up `tourism.db` before any migration.

## Final touches — transport provider guidance and calendar trip planner (15 Nov 2026)

### Transport: all relevant ways to investigate

The **Transport** page now generates route-sensitive transport suggestions for any two of the 15 curated destinations. It groups practical possibilities under **flight, coach/bus, train/urban rail, Grab/taxi, self-drive, ferry/boat and, for Genting, cable car**. It includes **connecting legs** when an island or a remote destination cannot be reached directly. Each suggestion includes **where to check or book** using an external provider, including:

- **Flights:** AirAsia MOVE (`https://www.airasia.com/flights/`), Malaysia Airlines (`https://www.malaysiaairlines.com/my/en/home.html`).
- **Trains:** official KTMB Integrated Ticketing System (`https://online.ktmb.com.my/`).
- **Buses/coaches:** Easybook (`https://www.easybook.com/en-my`), BusOnlineTicket (`https://www.busonlineticket.com/`).
- **Grab and taxis:** Grab Malaysia (`https://www.grab.com/my/transport/`) — enter route and check real availability in the app.
- **Langkawi:** ferry via Kuala Kedah or Kuala Perlis (`https://www.langkawiferryline.com/`).
- **Tioman:** ferry via Mersing or Tanjung Gemok (`https://www.mim.com.my/`).
- **Perhentian Islands:** boat via Kuala Besut (`https://www.perhentiantrans.com/`).
- **Genting Highlands:** express bus and Awana SkyWay on Resorts World Genting's own booking/info pages (`https://www.rwgenting.com/en/getting-here/express-bus.html` and `https://www.rwgenting.com/en/getting-here/cable-car.html`).

Operator links are homepage/booking-page entry points, **not pre-filled, confirmed tickets**. You must check schedules, availability, transfers, weather, seasons and prices for your travel dates. Bus and rail options can require transfers, flights can require connections, and **cars, taxis, buses and trains cannot directly travel to offshore islands**. The helper `transport_guide.py` contains the recommendation logic and reviewable provider links so you can maintain them. The existing sample transport estimates remain labelled historical and should not be used for pricing decisions. This guide strives to list useful modes, not guarantee every possible route/service: a comprehensive real-time travel engine would require licensed provider APIs.

### Trip planner: custom dates and Anything

Under **When are you visiting?**, choose **arrival** and **departure** from native browser date-picker calendars. Date length is computed automatically, **including arrival and departure days**; the site also shows the number of nights. Dates can span **1 to 90 inclusive days**. On submission, the Flask backend validates both dates and labels every day of the itinerary with the correct calendar date. It also supports the older `days` API field for backwards compatibility.

The **budget controls are unchanged**: Conservative, Moderate, Luxury. These are preference labels, **not validated spending limits**; the planner lists only known sample activity prices and does not include full transport/accommodation budgets. The new **Anything & Everything** interest chooses all available categories (no category filter). Selecting a specific interest deselects Anything; choosing Anything clears specific interests. When a trip is longer than the recorded activity list, days without an activity are labelled open/free exploration days instead of inventing activities.

### Test the new version

```powershell
python -m unittest discover -s tests -v
```

Useful manual checks: Transport from **Kuala Lumpur → Penang** (flight, coach, KTM, road), **Kuala Lumpur → Langkawi** (flight or land + ferry), **Kuala Lumpur → Tioman Island** (road/coach + ferry), and **Kuala Lumpur → Genting Highlands** (bus + cable car). Then create a **4-day / 3-night** planner itinerary using two dates; try **Anything & Everything** and a single specific interest, and verify that day headings show the chosen dates.

## New: Editorial Photography Edition — 15 November 2026

This release updates the **visual design** while preserving the destination, booking-link, nearby-search, transport and trip-planner workflows of the preceding 3D edition.

**Visual direction:** visual travel culture with the visual restraint of a high-end beauty/skin clinic: warm ivory, eucalyptus/sage green, darker botanical headings, airy spacing, graceful serif typography, sculptural photo masks, pill actions, translucent photography overlays, and refined card depth. The previous dark emerald globe is preserved as a separate interactive chapter.

### 15 bundled destination photographs

All 15 images provided by the project owner have been optimised as WebP for responsive loading under `static/images/editorial/`:

- `batu-caves.webp`, `cameron-highlands.webp`, `genting-highlands.webp`
- `ipoh.webp`, `johor-bahru.webp`, `kota-kinabalu.webp`
- `kuala-lumpur.webp`, `kuching.webp`, `langkawi.webp`
- `melaka.webp`, `penang.webp`, `perhentian-islands.webp`
- `putrajaya.webp`, `taman-negara.webp`, `tioman-island.webp`

You do **not** need to copy your earlier photos to display the 15 photographed destinations in this edition. The design links directly to these WebP assets instead of depending on older database image fields. Other image types or destination-specific attraction/property photographs may still be added as your catalogue grows.

**Photo usage:** The images were supplied for this redesign. Check the original photographer/rights-holder's permission or applicable licence before deploying the site publicly. A destination photo shown beside a hotel is labelled **Destination view · Not property photo**, to avoid misrepresenting it as a photo of that hotel. Likewise, attraction cards with area-level imagery are labelled **Area photography**.

### Updated files

- `templates/base.html` — editorial navbar, typography, accessible mobile menu and refined footer.
- `templates/index.html` — entirely redesigned photograph-led landing page with a featured image carousel, destination search, photographic journal, interactive destination flashcards, functional map/globe, four-step journey and a strong itinerary call to action.
- `templates/explore.html`, `templates/destination_detail.html`, `templates/attractions.html`, `templates/hotels.html` — accurate use of the bundled place photography.
- `templates/trip_planner.html` — fixes the page-hero alignment in the new light layout (planning controls/logic preserved).
- `static/css/editorial.css` — the responsive visual redesign and card-face transitions.
- `static/js/editorial.js` — image slider (arrows, keyboard, touch) and keyboard-accessible quick-view flashcards with destination/stay/transport/plan shortcuts.
- `static/js/immersive.js` — adjusts featured-place filtering to hide the complete flashcard while keeping the existing globe intact.

### Test the interactions

1. On the landing page use the arrows on the featured photograph to switch destinations, or swipe the photo on mobile.
2. Select **Coast & islands** to filter the home destination cards.
3. Choose a destination's **Quick view** control: the card flips to show four useful next steps. Choose **Back to photo** or press `Esc` to return.
4. Use the navigation to test **Experiences**, **Stays**, **Getting around** and the calendar-based **Trip planner**.
5. Rotate the globe by dragging, or focus the destination shortcuts below it to highlight a place.

Motion is progressive-enhancement only; the site respects **prefers-reduced-motion** and supports keyboard focus and mobile navigation. Photos in the new landing page are bundled and served locally. Google Fonts are optional: the site falls back to local serif/sans-serif fonts offline.

If upgrading an existing local instance, **back up your `database/tourism.db`** and copy the new source/templates/CSS/JS/images, retaining the original database if it contains your own records. This is a visual upgrade, so no database reset is necessary for existing valid data.

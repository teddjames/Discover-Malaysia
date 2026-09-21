# 🇲🇾 Malaysia Explorer

> A tourism discovery and trip-planning web application focused on Kuala Lumpur, Batu Caves and Genting Highlands.

**Malaysia Explorer** is a Flask-based tourism and travel-planning web application designed to help visitors explore selected destinations around Kuala Lumpur and plan their trips more efficiently.

The platform combines destination discovery, tourist attractions, accommodation information, transportation options and a personalised trip planner into a single application.

 **Project Status: In Development**

This project is actively being developed. Some features are currently functional, while others are being expanded and refined.

---

## Project Overview

Planning a trip to Malaysia often involves using multiple platforms to research:

- Tourist attractions
- Hotels
- Transportation
- Activities
- Prices
- Travel times
- Daily itineraries

Malaysia Explorer aims to bring these elements together into one simple and visually engaging platform.

The current scope focuses on:

- 🇲🇾 Kuala Lumpur
- Batu Caves
- Genting Highlands

The application is intentionally limited to the Kuala Lumpur city area and destinations extending as far as Genting Highlands.

---

## Project Objectives

The main objectives of Malaysia Explorer are to:

1. Help users discover popular Malaysian destinations.
2. Display tourist attractions and their information.
3. Provide accommodation information and ratings.
4. Compare transportation options and estimated prices.
5. Help users plan trips based on:
   - Trip duration
   - Budget
   - Interests
   - Destinations
6. Generate personalised activity recommendations.
7. Develop an expandable foundation for a future tourism booking platform.

---

# Current Features

## Destination Exploration

Users can explore the destinations currently supported by the application:

### Kuala Lumpur

Malaysia's capital city and the main destination covered by the platform.

### Batu Caves

A famous limestone cave complex and Hindu pilgrimage site located outside central Kuala Lumpur.

### Genting Highlands

A mountain resort destination known for entertainment, attractions and cooler weather.

---

## Tourist Attractions

The attractions section retrieves attraction information from the SQLite database.

Current examples include:

- Petronas Twin Towers
- Central Market
- Batu Caves
- Genting SkyWorlds

Each attraction can contain information such as:

- Name
- Category
- Description
- Rating
- Price
- Image
- Destination

Attractions are retrieved from the database and displayed dynamically using Flask and Jinja templates.

---

## Accommodation

The accommodation section currently supports hotel information.

Hotel records include:

- Hotel name
- Type
- Description
- Rating
- Price per night
- Destination
- Image

Current sample accommodation data includes hotels around Kuala Lumpur and Genting Highlands.

> Airbnb functionality is planned as part of the future development of the project.

---

## Transportation

Malaysia Explorer includes a transportation system for selected routes.

Currently supported transportation types include:

- Train
- Bus
- Grab

The application can return:

- Transport type
- Estimated journey duration
- Minimum estimated price
- Maximum estimated price
- Additional notes

### Example

A user can search:

```text
Kuala Lumpur → Batu Caves

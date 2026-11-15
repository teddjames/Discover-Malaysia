"""Run after installing requirements: python -m unittest discover -s tests -v"""
import unittest
from app import app


class WebsiteSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    def assert_page(self, url, expected):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, (url, response.data[:500]))
        self.assertIn(expected.encode('utf-8'), response.data)

    def test_home(self):
        self.assert_page('/', 'Travel beyond')

    def test_immersive_landing_and_3d_globe(self):
        self.assert_page('/', 'id="malaysiaGlobe"')
        self.assert_page('/', 'Create my itinerary')
        self.assert_page('/', 'data-destination-filter="island"')

    def test_discover_malaysia_brand(self):
        self.assert_page('/', 'DISCOVER')
        self.assert_page('/', 'Not all exploration destinations are captured here.')

    def test_penang_destination_and_legacy_redirect(self):
        self.assert_page('/destinations/penang', 'Penang')
        r=self.client.get('/destinations/george-town')
        self.assertEqual(r.status_code, 301)
        self.assertIn('/destinations/penang', r.headers['Location'])

    def test_planner_preselects_penang(self):
        r=self.client.get('/trip-planner?destination=penang')
        self.assertEqual(r.status_code,200)
        self.assertIn(b'data-value="Penang"',r.data)
        self.assertIn(b'planner-option selected',r.data)

    def test_explore_city_search(self):
        self.assert_page('/explore?q=Langkawi', 'Langkawi')

    def test_explore_nearby(self):
        self.assert_page('/explore?near=kuala-lumpur&radius=25', 'near Kuala Lumpur')

    def test_attractions_by_place(self):
        self.assert_page('/attractions?location=langkawi', 'Langkawi Sky Bridge')

    def test_stays_by_place(self):
        self.assert_page('/hotels?location=penang', 'Eastern &amp; Oriental Hotel')

    def test_destination_guide(self):
        self.assert_page('/destinations/melaka', 'Casa del Rio Melaka')

    def test_unknown_destination_404(self):
        response = self.client.get('/destinations/not-a-real-destination')
        self.assertEqual(response.status_code, 404)

    def test_transport_api(self):
        result = self.client.get('/api/transport?origin=Kuala%20Lumpur&destination=Batu%20Caves')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.get_json()['routes']), 3)

    def test_transport_google_maps_fallback(self):
        response = self.client.get('/api/transport?origin=Ipoh&destination=Langkawi')
        self.assertEqual(response.status_code, 200)
        self.assertIn('google.com/maps/dir/', response.get_json()['maps_driving'])

if __name__ == '__main__':
    unittest.main()

# The additional tests below are discovered by unittest along with the
# original smoke tests. They exercise custom calendar dates and the unfiltered
# Anything preference through the actual Flask JSON API.
class CalendarAndTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client=app.test_client()

    def test_trip_dates_and_anything(self):
        res=self.client.post('/api/trip-planner',json={
            'start_date':'2026-11-25','end_date':'2026-11-28',
            'budget':'moderate','interests':['anything'],
            'destinations':['Penang']})
        self.assertEqual(res.status_code,200,res.get_data(as_text=True)[:500])
        data=res.get_json()
        self.assertEqual(data['days'],4)
        self.assertEqual(data['nights'],3)
        self.assertEqual([d['date'] for d in data['itinerary']],
                         ['2026-11-25','2026-11-26','2026-11-27','2026-11-28'])
        self.assertGreater(len(data['activities']),0)
        self.assertEqual(data['interests'],['anything'])

    def test_trip_reversed_dates_rejected(self):
        res=self.client.post('/api/trip-planner',json={
            'start_date':'2026-11-28','end_date':'2026-11-25',
            'budget':'moderate','interests':['anything'],'destinations':['Penang']})
        self.assertEqual(res.status_code,400)

    def test_trip_more_than_ninety_days_rejected(self):
        res=self.client.post('/api/trip-planner',json={
            'start_date':'2026-11-25','end_date':'2027-03-30',
            'budget':'moderate','interests':['anything'],'destinations':['Penang']})
        self.assertEqual(res.status_code,400)

    def test_transport_recommendations_to_tioman(self):
        r=self.client.get('/api/transport?origin=Kuala%20Lumpur&destination=Tioman%20Island')
        self.assertEqual(r.status_code,200)
        self.assertIn('ferry',{x['mode'] for x in r.get_json()['recommendations']})

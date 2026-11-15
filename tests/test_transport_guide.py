import unittest
from database.db import get_db_connection
from transport_guide import options_for

class TransportGuideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db=get_db_connection()
        cls.places={row['name']:dict(row) for row in db.execute('SELECT * FROM destinations')}
        db.close()

    def modes(self,a,b):
        return {o['mode'] for o in options_for(self.places[a],self.places[b])}

    def test_air_bus_train_road_for_penang(self):
        m=self.modes('Kuala Lumpur','Penang')
        self.assertTrue({'flight','bus','train','car'}.issubset(m),m)

    def test_tioman_recommends_ferry_not_direct_car(self):
        m=self.modes('Kuala Lumpur','Tioman Island')
        self.assertIn('ferry',m)
        self.assertIn('bus',m)
        self.assertNotIn('car',m)

    def test_lgk_flight_or_ferry(self):
        m=self.modes('Kuala Lumpur','Langkawi')
        self.assertTrue({'flight','ferry'}.issubset(m),m)

    def test_east_malaysia_has_flight_not_road_over_water(self):
        m=self.modes('Penang','Kuching')
        self.assertIn('flight',m)
        self.assertNotIn('car',m)

    def test_genting_cable_car(self):
        self.assertIn('cable-car',self.modes('Kuala Lumpur','Genting Highlands'))

    def test_kuala_lumpur_batu_caves_local_bus_and_rail(self):
        m=self.modes('Kuala Lumpur','Batu Caves')
        self.assertTrue({'bus','train','cab'}.issubset(m),m)

    def test_recommendations_have_linked_providers(self):
        for o in options_for(self.places['Kuala Lumpur'],self.places['Perhentian Islands']):
            self.assertTrue(o['providers'])
            self.assertTrue(all(x['url'].startswith('https://') for x in o['providers']))
            self.assertEqual(o['availability'],'Check with provider – not live')

if __name__=='__main__':unittest.main()

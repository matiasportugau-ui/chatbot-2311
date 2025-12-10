import os
import unittest
from unittest.mock import patch
from factura_express import get_token, obtener_productos

class TestFacturaExpress(unittest.TestCase):
    @patch('factura_express.requests.post')
    def test_get_token_success(self, mock_post):
        mock_post.return_value.json.return_value = {'token': 'dummy-token'}
        mock_post.return_value.raise_for_status = lambda: None
        os.environ['FE_EMISOR_ID'] = '123'
        os.environ['FE_USERNAME'] = 'user'
        os.environ['FE_PASSWORD_HASH'] = 'hashed'
        self.assertEqual(get_token(), 'dummy-token')

    @patch('factura_express.requests.get')
    def test_obtener_productos_success(self, mock_get):
        mock_get.return_value.json.return_value = {'productos': [{'id': 1}]}
        mock_get.return_value.raise_for_status = lambda: None
        products = obtener_productos('dummy-token', 1, 1, 0, 10)
        self.assertIsInstance(products, list)
        self.assertEqual(products[0]['id'], 1)

if __name__ == '__main__':
    unittest.main()

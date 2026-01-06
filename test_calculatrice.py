import unittest
from calculatrice import addition, soustraction

class TestCalculatrice(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(addition(2, 2), 4)
        self.assertEqual(addition(-1, 1), 0)

    def test_soustraction(self):
        self.assertEqual(soustraction(5, 2), 3)

if __name__ == '__main__':
    unittest.main()

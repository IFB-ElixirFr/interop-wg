import unittest


class MyTestCase(unittest.TestCase):


    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        print("STARTING all tests")

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        print("ENDING all tests")

    def test_something(self):
        self.assertFalse(False)

    def test_another_thing(self):
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()

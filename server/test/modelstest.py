import unittest

import server.models


class ModelsTest(unittest.TestCase):

    def testGoogleNewsModelLoad(self):
        model = server.models.get_model(server.models.MODEL_GOOGLE_NEWS)
        self.assertIsNotNone(model, "The GoogleNews model was None :-(")

    def testModelLoadFails(self):
        with self.assertRaises(server.models.UnknownModelException):
            server.models.get_model("MY MADE UP MODEL NAME!")

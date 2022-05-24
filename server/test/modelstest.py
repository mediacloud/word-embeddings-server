import unittest

import server.models


class ModelsTest(unittest.TestCase):

    def testGoogleNewsModelLoad(self):
        model = server.models.get_google_news_model()
        self.assertIsNotNone(model, "The GoogleNews model was None :-(")

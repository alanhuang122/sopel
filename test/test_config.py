# coding=utf-8


import os
import tempfile
import unittest
from sopel import config
from sopel.config import types


class FakeConfigSection(types.StaticSection):
    attr = types.ValidatedAttribute('attr')


class ConfigFunctionalTest(unittest.TestCase):
    def read_config(self):
        configo = config.Config(self.filename)
        configo.define_section('fake', FakeConfigSection)
        return configo

    def setUp(self):
        self.filename = tempfile.mkstemp()[1]
        with open(self.filename, 'w') as fileo:
            fileo.write(
                "[core]\n"
                "owner=embolalia"
            )

        self.config = self.read_config()

    def tearDown(self):
        os.remove(self.filename)

    def test_validated_string_when_none(self):
        self.config.fake.attr = None
        self.assertEqual(self.config.fake.attr, None)

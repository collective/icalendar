# -*- coding: utf-8 -*-
# unittest/unittest2 importer
import unittest
if not hasattr(unittest.TestCase, 'assertIsNotNone'):
    import unittest2 as unittest
unittest  # pep 8

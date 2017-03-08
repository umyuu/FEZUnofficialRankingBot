# -*- coding: utf-8 -*-
#
import pytest
import numpy as np
# pylint: disable=W0611
import conftest
# pylint: enable=W0611
from serializer import Serializer

# pylint: disable=C0103
class TestClass(object):
    def test_naivebayes(self):
        pass
if __name__ == '__main__':
    pytest.main("--capture=sys")

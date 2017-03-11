# -*- coding: utf-8 -*-
import pytest
# pylint: disable=W0611
import conftest
# pylint: enable=W0611
from event import SimpleEvent

# pylint: disable=C0103
class TestClass(object):
    def test_add(self):
        """
            SimpleEvent => SimpleEvent += 1 => TypeError
        """
        ev = SimpleEvent()
        with pytest.raises(TypeError):
            ev += 1
    def test_remove(self):
        """
            SimpleEvent => SimpleEvent#Empty remove => ValueError
        """
        ev = SimpleEvent()
        with pytest.raises(ValueError):
            ev -= self.event_remove
    def test_clear(self):
        ev = SimpleEvent()
        ev += self.event_clear
        ev.clear()
        assert len(ev.handlers) == 0
    def event_clear(self):
        pass
    def event_remove(self):
        pass
if __name__ == '__main__':
    pytest.main("--capture=sys")

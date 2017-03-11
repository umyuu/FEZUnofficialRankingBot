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
    def base_filtered(self):
        """
            note: method define order 
                1,base_filtered 
                2,filtered
        """
        pass
    def test_eventOrdering(self):
        events = SimpleEvent()
        addList = [self.base_filtered, self.filtered]
        for event in addList:
            events += event
        for i, event in enumerate(events.handlers):
            if addList[i] != event:
                raise Exception('compare x:{0},y:{1}'.format(addList[i], event))
    def filtered(self):
        pass

if __name__ == '__main__':
    pytest.main("--capture=sys")

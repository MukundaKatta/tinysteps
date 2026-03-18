"""Integration tests for Tinysteps."""
from src.core import Tinysteps

class TestTinysteps:
    def setup_method(self):
        self.c = Tinysteps()
    def test_10_ops(self):
        for i in range(10): self.c.detect(i=i)
        assert self.c.get_stats()["ops"] == 10
    def test_service_name(self):
        assert self.c.detect()["service"] == "tinysteps"
    def test_different_inputs(self):
        self.c.detect(type="a"); self.c.detect(type="b")
        assert self.c.get_stats()["ops"] == 2
    def test_config(self):
        c = Tinysteps(config={"debug": True})
        assert c.config["debug"] is True
    def test_empty_call(self):
        assert self.c.detect()["ok"] is True
    def test_large_batch(self):
        for _ in range(100): self.c.detect()
        assert self.c.get_stats()["ops"] == 100

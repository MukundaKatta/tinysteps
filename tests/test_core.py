"""Tests for Tinysteps."""
from src.core import Tinysteps
def test_init(): assert Tinysteps().get_stats()["ops"] == 0
def test_op(): c = Tinysteps(); c.detect(x=1); assert c.get_stats()["ops"] == 1
def test_multi(): c = Tinysteps(); [c.detect() for _ in range(5)]; assert c.get_stats()["ops"] == 5
def test_reset(): c = Tinysteps(); c.detect(); c.reset(); assert c.get_stats()["ops"] == 0
def test_service_name(): c = Tinysteps(); r = c.detect(); assert r["service"] == "tinysteps"

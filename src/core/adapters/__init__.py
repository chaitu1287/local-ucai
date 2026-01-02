"""Customer platform adapters."""

from src.core.adapters.base import BaseAdapter
from src.core.adapters.intercom import IntercomAdapter
from src.core.adapters.test import TestAdapter
from src.core.adapters.factory import AdapterFactory

__all__ = ["BaseAdapter", "IntercomAdapter", "TestAdapter", "AdapterFactory"]

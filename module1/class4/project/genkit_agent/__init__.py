"""Genkit Agent Package

A Python package for building AI agents using Google Genkit and Gemini integration.
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .agent import GenkitAgent
from .config import Config

__all__ = ["GenkitAgent", "Config"]
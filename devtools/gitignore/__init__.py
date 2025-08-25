"""
Gitignore generator module.
"""

from .cli import cli
from .generator import GitignoreGenerator
from .detector import ProjectDetector

__all__ = ["cli", "GitignoreGenerator", "ProjectDetector"]

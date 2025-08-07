"""
Pipe - A lightweight, plugin-based data pipeline processor

This package provides a framework for building data processing pipelines
with a plugin-based architecture.
"""

__version__ = '0.1.0'
__author__ = 'Osman Abdullahi'

from .core.app import PipeApp
from .plugins.pluginbase import PluginBase, InputPlugin, DecoderPlugin, OutputPlugin, PluginError

__all__ = [
    'PipeApp',
    'PluginBase',
    'InputPlugin',
    'DecoderPlugin',
    'OutputPlugin',
    'PluginError',
] 
"""
Plugin Base Module

This module provides the base class for all Pipe plugins.
"""

import logging
from typing import Any, Callable, Dict, Optional

class PluginError(Exception):
    """Base exception class for plugin-related errors"""
    pass

class PluginBase:
    """
    Base class for all Pipe plugins.
    
    This class provides common functionality and interface for all plugin types.
    Plugins should inherit from this class and implement the required methods.
    """

    def __init__(self, config: Dict[str, str], callback: Optional[Callable[[Any], None]] = None):
        """
        Initialize the plugin with configuration and optional callback.
        
        Args:
            config: Plugin configuration dictionary
            callback: Optional callback function for data processing
        """
        self.config = config
        self.callback = callback
        self.response = None
        self.logger = logging.getLogger(f"{__package__}.{self.__class__.__name__}")
        
        # Set configuration values from defaults
        for key, value in self.defaults.items():
            setattr(self, key, config.get(key, value))
        
        # Initialize plugin
        self.initialize()

    @property
    def defaults(self) -> Dict[str, str]:
        """
        Get default configuration values for the plugin.
        
        Returns:
            Dictionary of default configuration values
        """
        return {}

    def initialize(self) -> None:
        """
        Initialize the plugin.
        
        This method is called after the plugin is instantiated and can be
        overridden by subclasses to perform initialization tasks.
        """
        pass

    def run(self) -> None:
        """
        Run the plugin.
        
        This method should be implemented by subclasses to perform the
        plugin's main functionality.
        """
        raise NotImplementedError("Plugin must implement run() method")

    def respond(self, data: Any) -> None:
        """
        Send a response back to the input plugin.
        
        Args:
            data: Data to send as response
        """
        self.response = data

class InputPlugin(PluginBase):
    """
    Base class for input plugins.
    
    Input plugins are responsible for reading data from a source and passing
    it to the pipeline through the callback function.
    """

    def run(self) -> None:
        """
        Run the input plugin.
        
        This method should be implemented by subclasses to read data from
        the source and call the callback function for each piece of data.
        """
        raise NotImplementedError("Input plugin must implement run() method")

class DecoderPlugin(PluginBase):
    """
    Base class for decoder plugins.
    
    Decoder plugins transform data from one format to another.
    """

    def decode(self, data: Any) -> Any:
        """
        Decode the input data.
        
        Args:
            data: Input data to decode
            
        Returns:
            Decoded data
        """
        raise NotImplementedError("Decoder plugin must implement decode() method")

class OutputPlugin(PluginBase):
    """
    Base class for output plugins.
    
    Output plugins are responsible for writing data to a destination.
    """

    def handle_raw(self, data: Any) -> None:
        """
        Handle raw data from the input plugin.
        
        Args:
            data: Raw data to handle
        """
        pass

    def handle_decoded(self, data: Any) -> None:
        """
        Handle decoded data from decoder plugins.
        
        Args:
            data: Decoded data to handle
        """
        raise NotImplementedError("Output plugin must implement handle_decoded() method") 
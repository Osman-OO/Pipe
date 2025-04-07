"""
Pipe - Core Application Module

This module contains the main application class that orchestrates the data pipeline.
"""

import argparse
import configparser
import importlib
import sys
import logging
import logging.handlers
from typing import List, Dict, Any, Optional

from ..plugins.pluginbase import PluginError, PluginBase

class Pipeline:
    """Represents a single data pipeline configuration"""
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.input_plugin = None
        self.decoder_plugins = []
        self.output_plugins = []

class PipeApp:
    """
    Main application class for the Pipe data pipeline processor.
    Handles configuration, plugin management, and data flow.
    """

    def __init__(self):
        """Initialize the Pipe application"""
        self.configfile = None
        self.config = None
        self.pipeline = None
        self.option_override = None
        self.loglevel = logging.INFO
        self.verbose = False
        self.debug = False

        # Default configuration values
        self.defaults = {
            'main': {
                'logfile': '/var/log/pipe/pipe.log',  # Default log file location
                'loglevel': 'info',                   # Default logging level
            },
            'plugins': {
                'input': 'fileread',                  # Default input plugin
                'decode': 'noop',                     # Default decoder plugin
                'output': 'print',                    # Default output plugin
            },
        }

    def process_options(self) -> None:
        """Parse command line arguments and set configuration options"""
        parser = argparse.ArgumentParser(
            description='Pipe Pipeline Processor',
            formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(
                prog, max_help_position=38, width=120
            )
        )
        parser.add_argument(
            '-c', '--config',
            action='store',
            dest='configfile',
            default=self.configfile,
            help='path to configuration file'
        )
        parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            dest='verbose',
            default=False,
            help='send logging to stderr in addition to logfile'
        )
        parser.add_argument(
            '-d', '--debug',
            action='store_true',
            dest='debug',
            default=False,
            help='output debug messages (equals -O loglevel=debug)'
        )
        parser.add_argument(
            '-O', '--opt',
            action='append',
            dest='option',
            help='override config option'
        )
        args = parser.parse_args()
        self.configfile = args.configfile
        self.verbose = args.verbose
        self.debug = args.debug
        self.option_override = args.option

    def read_configfile(self) -> None:
        """Read and parse configuration file, applying any command line overrides"""
        self.config = configparser.ConfigParser()
        if self.configfile:
            self.config.read(self.configfile)
        
        # Ensure required sections exist
        for section in ['main', 'plugins']:
            if section not in self.config:
                self.config[section] = {}

        # Apply command line overrides
        if self.option_override:
            for opt in self.option_override:
                try:
                    key, val = opt.split('=', 1)
                    keypart = key.rpartition('.')
                    section = keypart[0] or 'main'
                    if keypart[2]:
                        if section not in self.config:
                            self.config[section] = {}
                        self.config[section][keypart[2]] = val
                except ValueError:
                    pass

    def get_config_value(self, key: str, section: str = 'main') -> str:
        """Get configuration value with fallback to defaults"""
        return self.config[section].get(key, self.defaults[section][key])

    def setup_logging(self) -> None:
        """Configure logging system"""
        self.root_logger = logging.getLogger()
        self.logger = logging.getLogger(__package__)
        self.formatter = logging.Formatter(
            '%(asctime)s [%(process)d] %(levelname)s: %(name)s: %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )

        # Set log level
        if self.debug:
            self.loglevel = logging.DEBUG
        else:
            levelstr = self.get_config_value('loglevel').upper()
            self.loglevel = getattr(logging, levelstr)
        
        self.logger.setLevel(self.loglevel)

        # Setup handlers
        if self.verbose:
            self._setup_verbose_logging()
        
        logfile = self.get_config_value('logfile')
        if logfile:
            self._setup_file_logging(logfile)
        else:
            self.root_logger.addHandler(logging.NullHandler())
            self.logger.info('No logfile configured.')

    def _setup_verbose_logging(self) -> None:
        """Configure verbose logging to stderr"""
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(self.formatter)
        self.root_logger.addHandler(handler)
        self.logger.info('Verbose output configured.')

    def _setup_file_logging(self, logfile: str) -> None:
        """Configure file logging"""
        try:
            handler = logging.handlers.WatchedFileHandler(logfile)
            handler.setFormatter(self.formatter)
            self.root_logger.addHandler(handler)
        except (IOError, PermissionError) as e:
            print(f"Could not open logfile: {e}")
            sys.exit(1)

    def create_pipeline(self) -> None:
        """Create and configure the data pipeline"""
        self.pipeline = Pipeline(self.config)
        self._setup_input_plugin()
        self._setup_decoder_plugins()
        self._setup_output_plugins()

    def _setup_input_plugin(self) -> None:
        """Initialize and configure the input plugin"""
        plugin_name = self.get_config_value('input', 'plugins')
        self.logger.debug(f'Configuring input plugin: {plugin_name}')
        
        try:
            plugin_module = importlib.import_module(f'.plugins.{plugin_name}', package=__package__)
            plugin_class = getattr(plugin_module, plugin_name.rpartition('.')[2].capitalize())
            
            if plugin_name not in self.config:
                self.config[plugin_name] = {}
            self.config[plugin_name]['loglevel'] = str(self.loglevel)
            
            self.pipeline.input_plugin = plugin_class(
                self.config[plugin_name],
                callback=self._input_callback
            )
        except ImportError as e:
            self.logger.exception(f'Plugin not found: {e}')
            sys.exit(1)

    def _setup_decoder_plugins(self) -> None:
        """Initialize and configure decoder plugins"""
        decoder_names = self.get_config_value('decode', 'plugins').split(',')
        for decoder_name in decoder_names:
            self.logger.debug(f'Configuring decoder plugin: {decoder_name}')
            
            try:
                decoder_module = importlib.import_module(f'.plugins.{decoder_name}', package=__package__)
                decoder_class = getattr(decoder_module, decoder_name.rpartition('.')[2].capitalize())
                
                if decoder_name not in self.config:
                    self.config[decoder_name] = {}
                self.config[decoder_name]['loglevel'] = str(self.loglevel)
                
                decoder = decoder_class(
                    self.config[decoder_name],
                    callback=self._output_callback
                )
                self.pipeline.decoder_plugins.append(decoder)
            except ImportError as e:
                self.logger.exception(f'Decoder plugin not found: {e}')
                sys.exit(1)

    def _setup_output_plugins(self) -> None:
        """Initialize and configure output plugins"""
        output_names = self.get_config_value('output', 'plugins').split(',')
        for output_name in output_names:
            self.logger.debug(f'Configuring output plugin: {output_name}')
            
            try:
                output_module = importlib.import_module(f'.plugins.{output_name}', package=__package__)
                output_class = getattr(output_module, output_name.rpartition('.')[2].capitalize())
                
                if output_name not in self.config:
                    self.config[output_name] = {}
                self.config[output_name]['loglevel'] = str(self.loglevel)
                
                output = output_class(self.config[output_name])
                self.pipeline.output_plugins.append(output)
            except ImportError as e:
                self.logger.exception(f'Output plugin not found: {e}')
                sys.exit(1)

    def _input_callback(self, data: Any) -> None:
        """Handle data from input plugin and pass through decoder chain"""
        # Pass raw data to output plugins
        for output in self.pipeline.output_plugins:
            output.handle_raw(data)
        
        # Process through decoder chain
        try:
            current_data = data
            for decoder in self.pipeline.decoder_plugins:
                current_data = decoder.decode(current_data)
                
                if decoder.response:
                    try:
                        self.pipeline.input_plugin.respond(decoder.response)
                    except AttributeError:
                        pass
                
                if current_data:
                    self._output_callback(current_data)
        except PluginError as e:
            self.logger.error(e)
        except Exception as e:
            self.logger.exception(e)
            raise

    def _output_callback(self, data: Any) -> None:
        """Pass decoded data to all output plugins"""
        for output in self.pipeline.output_plugins:
            output.handle_decoded(data)

    def run(self) -> None:
        """Main application entry point"""
        self.process_options()
        self.read_configfile()
        self.setup_logging()
        self.create_pipeline()
        self.pipeline.input_plugin.run()

if __name__ == '__main__':
    app = PipeApp()
    app.run() 
import argparse
import configparser
import importlib
import sys
import logging
import logging.handlers
from .plugins.pluginbase import PluginError

class App(object):
    """
    Main application class for the Pipe data pipeline processor.
    Handles configuration, plugin management, and data flow.
    """

    configfile      = None
    config          = None
    output          = []
    option_override = None
    loglevel        = logging.INFO

    # Default configuration values
    defaults    = {
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

    def process_options(self):
        """Parse command line arguments and set configuration options"""
        parser = argparse.ArgumentParser(description='Pipe Pipeline Processor',
            formatter_class=lambda prog: argparse.ArgumentDefaultsHelpFormatter(prog, max_help_position=38, width=120))
        parser.add_argument('-c', '--config', action='store', dest='configfile', default=self.configfile,
            help='path to configuration file')
        parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False,
            help='send logging to stderr in addition to logfile')
        parser.add_argument('-d', '--debug', action='store_true', dest='debug', default=False,
            help='output debug messages (equals -O loglevel=debug)')
        parser.add_argument('-O', '--opt', action='append', dest='option',
            help='override config option')
        args = parser.parse_args()
        self.configfile = args.configfile
        self.verbose = args.verbose
        self.debug = args.debug
        self.option_override = args.option

    def read_configfile(self):
        """Read and parse configuration file, applying any command line overrides"""
        self.config = configparser.ConfigParser()
        if self.configfile:
            self.config.read(self.configfile)
        if not 'main' in self.config:
            self.config['main'] = {}
        if not 'plugins' in self.config:
            self.config['plugins'] = {}
        if self.option_override is not None:
            for opt in self.option_override:
                try:
                    key,val = opt.split('=',1)
                    keypart = key.rpartition('.')
                    section = keypart[0] or 'main'
                    if keypart[2]:
                        if not section in self.config:
                            self.config[section] = {}
                        self.config[section][keypart[2]] = val
                except ValueError as e:
                    pass

    def confval(self, key, section='main'):
        """Get configuration value with fallback to defaults"""
        return self.config[section].get(key, self.defaults[section][key])

    def create_plugins(self):
        """Initialize and configure all plugins based on configuration"""
        try:
            # Initialize input plugin
            input_plugin = self.confval('input', 'plugins')
            self.logger.debug('Configured input plugin: %s' % input_plugin)
            input_module = importlib.import_module('.plugins.%s' % input_plugin, package=__package__)
            input_class = getattr(input_module, input_plugin.rpartition('.')[2].capitalize())
            if not input_plugin in self.config:
                self.config[input_plugin] = {}
            self.config[input_plugin]['loglevel'] = str(self.loglevel)
            self.input = input_class(self.config[input_plugin], callback=self.input_callback)

            # Initialize decoder plugins
            self.decode = []
            decode_plugins = self.confval('decode', 'plugins').split(',')
            for decode_plugin in decode_plugins:
                self.logger.debug('Configured decode plugin: %s' % decode_plugin)
                decode_module = importlib.import_module('.plugins.%s' % decode_plugin, package=__package__)
                decode_class = getattr(decode_module, decode_plugin.rpartition('.')[2].capitalize())
                if not decode_plugin in self.config:
                    self.config[decode_plugin] = {}
                self.config[decode_plugin]['loglevel'] = str(self.loglevel)
                config = self.config[decode_plugin]
                self.decode.append(decode_class(config, callback=self.output_callback))

            # Initialize output plugins
            self.output = []
            output_plugins = self.confval('output', 'plugins').split(',')
            for output_plugin in output_plugins:
                self.logger.debug('Configured output plugin: %s' % output_plugin)
                output_module = importlib.import_module('.plugins.%s' % output_plugin, package=__package__)
                output_class = getattr(output_module, output_plugin.rpartition('.')[2].capitalize())
                if not output_plugin in self.config:
                    self.config[output_plugin] = {}
                self.config[output_plugin]['loglevel'] = str(self.loglevel)
                config = self.config[output_plugin]
                self.output.append(output_class(config))

        except ImportError as e:
            self.logger.exception('Plugin not found: %s' % e)
            sys.exit(1)
        except AttributeError as e:
            self.logger.exception('Plugin error, plugin base class missing: %s' % e)
            raise
            sys.exit(1)
        except Exception as e:
            self.logger.exception(e)
            raise
            sys.exit(1)

    def input_callback(self, data):
        """Handle data from input plugin and pass through decoder chain"""
        for output in self.output:
            output.handle_raw(data)
        try:
            for dec in self.decode:
                data = dec.decode(data)
        except PluginError as e:
            self.logger.error(e)
            data = None
        except Exception as e:
            self.logger.exception(e)
            raise
        if dec.response:
            try:
                self.input.respond(dec.response)
            except AttributeError:
                pass
        if data:
            self.output_callback(data)

    def output_callback(self, data):
        """Pass decoded data to all output plugins"""
        for output in self.output:
            output.handle_decoded(data)

    def setup_logging(self):
        """Configure logging system"""
        self.root_logger = logging.getLogger()
        self.logger = logging.getLogger(__package__)
        self.formatter = logging.Formatter('%(asctime)s [%(process)d] %(levelname)s: %(name)s: %(message)s','%Y-%m-%d %H:%M:%S')

        if self.debug:
            self.loglevel = logging.DEBUG
            self.logger.setLevel(logging.DEBUG)
        else:
            levelstr = self.confval('loglevel').upper()
            self.loglevel = getattr(logging, levelstr)
            self.logger.setLevel(self.loglevel)
            self.logger.debug('Loglevel (str): %s' % levelstr)
        self.logger.debug('Loglevel (int): %d' % self.loglevel)

        if self.verbose:
            self.setup_verbose()

        logfile = self.confval('logfile')
        if logfile:
            try:
                loghandler = logging.handlers.WatchedFileHandler(logfile)
            except (IOError, PermissionError) as e:
                print("Could not open logfile: %s" % e)
                sys.exit(1)

            loghandler.setFormatter(self.formatter)
            self.root_logger.addHandler(loghandler)
        else:
            self.root_logger.addHandler(logging.NullHandler())
            self.logger.info('No logfile configured.')

    def setup_verbose(self):
        """Configure verbose logging to stderr"""
        loghandler = logging.StreamHandler(sys.stderr)
        loghandler.setFormatter(self.formatter)
        self.root_logger.addHandler(loghandler)
        self.logger.info('Verbose output configured.')

    def run(self):
        """Main application entry point"""
        self.process_options()
        self.read_configfile()
        self.setup_logging()
        self.create_plugins()
        self.input.run()

if __name__ == '__main__':
    app = App()
    app.run()

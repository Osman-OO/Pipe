# Pipeline

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue.svg)](https://www.python.org/downloads/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A lightweight, plugin-based data pipeline processor for handling and transforming data streams.

> Created and maintained by [Osman Abdullahi](https://github.com/Osman-OO)

## Features

- 🔌 Plugin-based architecture
- 📦 Easy to extend with custom plugins
- 🔄 Support for multiple data formats
- ⚡ Efficient data processing
- 🛠️ Simple configuration

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run a basic example
./run_pipe -v -d -O logfile= -O fileread.filename=/etc/passwd
```

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Usage](#-usage)
- [Plugins](#-plugins)
- [Configuration](#-configuration)
- [Examples](#-examples)
- [Development](#-development)

## ✨ Features

- **Plugin-based Architecture**: Easily extendable with custom plugins
- **Flexible Data Processing**: Handle both streaming and batch data
- **Simple Configuration**: Configure via command line or INI files
- **Multiple Input Sources**: File, network, and custom input plugins
- **Data Transformation**: Chain multiple decoders for complex processing
- **Various Output Options**: Files, databases, web services, and more

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/Osman-OO/pipe.git
cd pipe
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🛠 Usage

### Basic Pipeline

A pipeline consists of:
- One input plugin
- One or more decoder plugins
- One or more output plugins

### Command Line Options

```bash
./run_pipe [options]

Options:
  -c, --config FILE    Configuration file path
  -v, --verbose        Enable verbose output
  -d, --debug          Enable debug logging
  -O KEY=VALUE         Override configuration option
```

### Configuration Example

```ini
[main]
logfile = /var/log/pipe/pipe.log
loglevel = info

[plugins]
input = sniffer
decode = solaredge
output = datafile

[sniffer]
interface = eth0
protocols = tcp,udp
ports = 53
```

## 🔌 Plugins

### Input Plugins
- `fileread`: Read from files
- `sniffer`: Network packet capture
- `tshark`: Advanced packet capture using tshark
- `listen`: TCP server

### Decoder Plugins
- `hexlify`: Convert binary to hex
- `solaredge`: SolarEdge inverter data decoder
- `noop`: Pass-through decoder

### Output Plugins
- `print`: Console output
- `datafile`: File output
- `solaredge_peewee`: Database output

## 📝 Examples

### 1. File Processing
```bash
./run_pipe -v -d -O logfile= -O fileread.filename=/etc/passwd
```

### 2. Network Monitoring
```bash
sudo ./run_pipe -v -d -O logfile= -O plugins.input=sniffer \
  -O sniffer.interface=eth0 -O sniffer.protocols=tcp,udp -O sniffer.ports=53
```

### 3. SolarEdge Data Processing
```bash
./run_pipe -c examples/solaredge.ini
```

## 🛠 Development

### Creating a Plugin

1. Create a new Python file in `pipe/plugins/`
2. Inherit from `Pluginbase`
3. Implement required methods
4. Add configuration defaults

Example plugin structure:
```python
from .pluginbase import Pluginbase

class MyPlugin(Pluginbase):
    defaults = {
        'option1': 'default1',
        'option2': 'default2'
    }

    def initialize(self):
        # Plugin initialization
        pass

    def run(self):
        # Plugin logic
        pass
```

# Implementation details

When Pipe starts, it runs the following sequence, which I hope is self-explanatory:

```
def run(self):
    self.process_options()
    self.read_configfile()
    self.setup_logging()
    self.create_plugins()
    self.input.run()
```

* Command line options can be used to change certain parameters, the most
  important one being the location of the configuration file. But Pipe can be
  used without a configuration file, with all plugin options on the command line,
  if you like.
* The ini-style configuration file contains configuration for the main program
  and all the plugins. This is where the pipeline is defined. This can look,
  for example, like this:

```
[plugins]
input = sniffer
decode = solaredge.decode
output = print,datafile

[sniffer]
interface = vlan11

[solaredge.decode]
privkey = 12345678901234567890123456789012
```

For each defined plugin, Pipe tries to do the following:
1. Import a Python module with the name of the plugin from the *plugins*
   directory.
2. Within the module, locate a class with the same name, but capitalized
   (module *fileread* -> class *Fileread*).
3. Instantiate the class, passing its configuration, and store the instance for
   later use.

Each plugin is supposed to be a subclass of *plugins.pluginbase.Pluginbase*. This
doesn't do much, except set class attributes from the plugin configuration,
setup a logger and call an initialization method on the plugin if present.

The input plugin is passed a callback function, that it is supposed to call for
each chunk of data it wants to send into the pipeline. It takes a single
argument: the data. The callback function then takes care of calling the
decoders and output plugins. As an illustration, the simplest input plugin
*run()* method that I can think of is this:

```
    def run(self):
        with open(self.filename) as f:
            for line in f:
                self.callback(line.rstrip())
```

Plugins are instantiated only once for the lifetime of the Pipe process, which
means you can use them to temporarily hold intermediate data. That can be
convenient, if you need to buffer a certain amount of data before processing
it.

# Use case: SolarEdge telemetry data

This project includes support for processing and storing telemetry data from SolarEdge solar power inverters. The system can:

* Read data directly from the inverter over a serial connection
* Make the inverter talk to your own server instead of SolarEdge's server
* Sniff the communication between the inverter and the server

The data processing pipeline includes:
* Network packet capture for data collection
* Decryption and decoding of the SolarEdge protocol
* Storage in various formats (files, databases)

The system supports multiple output formats including:
* Raw data files
* JSON formatted files
* Database storage (MySQL, PostgreSQL, SQLite)

# Learn by example

## Reading and printing a file

The following example can be run in the root directory of the Pipe repository
and demonstrates the most basic usage of Pipe:

```
./run_pipe -v -d -O logfile= -O fileread.filename=/etc/passwd
```

What this means and does is:
* Run the Pipe application with verbose output (`-v` = logging to stderr)
* Set the log level to 'debug' (`-d`)
* Do not load a config file (no `-c`), so rely on built-in defaults
* The default plugins are 'fileread' for input, 'noop' for decode and 'print'
  for output
* Do not write to a logfile (`-O logfile=`), because we already have `-v`
* Tell *fileread* to read `/etc/passwd`
* The *noop* plugin will do nothing except wrap the data in a dict like so: `{
  'data': data }`
* The *print* plugin will print both the raw data and the decoded data as JSON
  to stdout

When you run this, quite a lot of output will appear on your screen:

* Log messages on stderr
* Raw input data and decoded data on stdout

If you would like to see only the decoded data, leave out `-v` (which obsoletes
`-d` when there is no logfile) and tell *print* not to print raw data:

```
./run_pipe -O logfile= -O fileread.filename=/etc/passwd -O print.print_raw=no
```

You will see each line from your *passwd* file, but wrapped as data by the *noop*
plugin.

TIP: if you run it with `-v`, you will find messages in the output containing the
words '*Setting attribute:*'. Together, these lines represent all the different
options that can be set for the pipeline you have configured.

## Sniffing DNS packets and printing the data in hexadecimal form

Again, this is not a very useful example, but it illustrates another possible
way to use Pipe. In contrast with the previous example, which processed a file
and terminated, this example will keep running until you interrupt it.

```
sudo ./run_pipe -v -d -O logfile= -O plugins.input=sniffer \
  -O sniffer.interface=eth1 -O sniffer.protocols=tcp,udp -O sniffer.ports=53 \
  -O plugins.decode=hexlify,noop -O print.print_raw=no
```

Explanation:
* Run Pipe with sudo, because the type of network socket that *sniffer* wants to
  open requires root
* Again, log to stderr (`-v`) on debug level (`-d`) and don't use a logfile
  (`-O logfile=`)
* Set the input plugin to *sniffer* (`-O plugins.input=sniffer`)
* Configure the sniffer for both UDP and TCP port 53 on interface `eth1` (the
  `-O sniffer.xxx` options)
* Set the decoders to *hexlify* and *noop*. This means that the raw binary data
  from *sniffer* will first be passed to *hexlify*, which will just call
  [binascii.hexlify()](https://docs.python.org/3/library/binascii.html#binascii.hexlify)
  on the data, and the result will be passwd to *noop*, which will wrap the
  hexlify'd data in a dictionary.
* Tell the *print* plugin not to print raw data.

The result will be, apart from the debugging output, the printing of information like this:

```
{"data": "ef5f01000001000000000000037777770977696b697065646961036f72670000010001"}

```

which is just what we asked for: a hexadecimal string representation of the
data from DNS packets, wrapped in a JSON object. Should you decide to decode
the data I quoted here, you will find it is a DNS request for the A record of
*www.wikipedia.org*.

# Configuration files

Pipe can be configured entirely on the command line (with `-O` options), or you
can use a configuration file. Configuration files are ini-files and Pipe parses
them with [the configparser module](https://docs.python.org/3/library/configparser.html).

Both Pipe itself and all plugins use sections in the configuration file. Pipe itself uses
two configuration sections (`[main]` and `[plugins]`), and every plugin gets the
configuration from the section that is named after the plugin.

## Configuration file example

The configuration file for the DNS sniffer pipeline example above, but with a
logfile instead of debug output on STDERR and with both the raw data and the
"decoded" data written to a file, looks like this:

```
[main]
logfile = /tmp/pipe.log
loglevel = debug

[plugins]
input = sniffer
decode = hexlify,noop
output = datafile

[sniffer]
interface = eth1
protocols = tcp,udp
ports = 53

[datafile]
raw_data_dir = /tmp
decoded_data_dir = /tmp
```

If you save this to a file named `examples/dnssniffer.ini`, you can run the pipeline like this:

```
sudo ./run_pipe -c examples/dnssniffer.ini
```

No output will appear on your screen, but 3 files will appear in `/tmp`:

* `pipe.log`, the log file;
* `<yyyymmddhhmmss>.raw` (the datafile plugin uses [time.strftime()](https://docs.python.org/3/library/time.html#time.strftime)
  to generate a filename) with the raw data, hexlify'd;
* `<yyyymmddhhmmss>.data`, with the same hexlify'd data, but in concatenated JSON format,
  wrapped in an object's `data` property.

To see which configuration keys are available for each plugin, you'll have to
look at the source code for now. Each plugin that is actually configurable
defines a property called 'defaults' that holds the default values for all
possible options.

from future import standard_library
standard_library.install_aliases()
from configparser import SafeConfigParser


# Get config
config = SafeConfigParser()
config.read('vegadns/api/config/default.ini')
config.read('vegadns/api/config/local.ini')

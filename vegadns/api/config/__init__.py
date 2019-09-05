from future import standard_library
from configparser import SafeConfigParser
standard_library.install_aliases()


# Get config
config = SafeConfigParser()
config.read('vegadns/api/config/default.ini')
config.read('vegadns/api/config/local.ini')

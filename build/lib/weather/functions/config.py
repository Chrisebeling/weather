import configparser
import pkg_resources
import os

def set_path(des_path, target_key='path', config_file='dataconfig.conf', section='data'):
    '''Update settings in data config file.

    Keyword Arguments:
    config_dict -- A dict of keys and settings, keys must be in current config file
    config_file -- The config file to update (Default 'database_config.ini')
    section -- The section of the config file to update (Default 'mysql')
    '''
    path = pkg_resources.resource_filename(
            __name__,
            os.path.join('resources', config_file)
        )

    config = configparser.ConfigParser(allow_no_value=True)
    config.read(path)
    
    assert target_key in config[section], 'key must be in current config. {} not in current config'.format(key)
    config.set(section, target_key, des_path)
    
    cfg_file = open(path,'w')
    config.write(cfg_file)
    cfg_file.close()

def get_path(target_key='path', config_file='dataconfig.conf', section='data'):
    path = pkg_resources.resource_filename(
            __name__,
            os.path.join(os.pardir, 'resources', config_file)
        )

    config = configparser.ConfigParser(allow_no_value=True)
    config.read(path)

    return config[section][target_key]

def print_path(config_file='dataconfig.conf', section='data'):
    path = resource_string(
            __name__,
            os.path.join('resources', config_file)
        )

    config = configparser.ConfigParser(allow_no_value=True)
    config.read(path)

    for option in config.options(section):
        print("{}:::{}".format(option,
                               config.get(section, option)))
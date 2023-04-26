import configparser
import os

from .utils import PluginDir

CONFIG_FILE_PATH = os.path.join(PluginDir, 'config.ini')


class ConfigFile:
    def __init__(self, config_path):
        self.config_path = config_path
        self.cfg = configparser.ConfigParser()
        self.cfg.read(config_path)
        self.sections = self.cfg.sections()
        if 'Tianditu' not in self.sections or 'Other' not in self.sections:
            self.initConfigFile()
            print("generate config file")

    def saveConfig(self):
        with open(self.config_path, 'w') as f:
            self.cfg.write(f)

    def setValue(self, section, key, value):
        self.cfg.set(section, key, value)
        self.saveConfig()

    def getValue(self, section, key):
        try:
            value = self.cfg.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            # print("section or key do not exist")
            value = ''
            self.setValue(section, key, value)
        return value

    def getValueBoolean(self, section, key):
        try:
            value = self.cfg.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            # print("section or key do not exist")
            value = False
            self.setValue(section, key, str(value))
        return value

    def initConfigFile(self):
        current_sections = self.cfg.sections()
        for s in current_sections:
            self.cfg.remove_section(s)
        self.cfg.add_section('Tianditu')
        self.cfg.set('Tianditu', 'key', '')
        self.cfg.set('Tianditu', 'keyisvalid', 'False')
        self.cfg.set('Tianditu', 'random', 'False')
        self.cfg.set('Tianditu', 'subdomain', 't0')
        self.cfg.add_section('Other')
        self.cfg.set('Other', 'extramap', 'False')
        self.saveConfig()

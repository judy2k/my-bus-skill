import logging
import os
import sys

LOG = logging.getLogger(__name__)

class EnvValidationError(Exception):
    pass


class ConfigMeta(type):
    def __init__(cls, name, bases, attr_dict):
        for k, v in attr_dict.items():
            if isinstance(v, EnvVar):
                v.default_env_var_name(k.upper())


class EnvVar(object):
    def __init__(self, default=None, env_var_name=None, required=True):
        self.env_var_name = env_var_name
        self.value = default
        self.required = required and default is None
        self.default = default

    def default_env_var_name(self, val):
        if self.env_var_name is None:
            self.env_var_name = val

    def populate(self):
        val = os.getenv(self.env_var_name)
        if val is None:
            if self.required:
                raise EnvValidationError("Environment variable {self.env_var_name} is required.".format(self=self))
            else:
                self.value = self.default
        else:
            self.value = self.convert_type(val)

    def convert_type(self, val):
        return val

    def __get__(self, instance, owner):
        return self.value


class BoolVar(EnvVar):
    _true_vals = {'true', 'yes', 'on', '1'}
    _fals_vals = {'false', 'no', 'off', '0'}

    def convert_type(self, val):
        if val is None:
            return self.default
        if val.lower() in self._true_vals:
            return True
        elif val.lower() in self._fals_vals:
            return False
        else:
            raise EnvValidationError(
                "Invalid boolean value '{val}' for environment variable {var}".format(val=val, var=self.env_var_name))


class IntVar(EnvVar):
    def convert_type(self, val):
        try:
            return int(val, 10)
        except ValueError as ve:
            raise EnvValidationError(
                "Invalid integer value '{val}' for environment variable {var}".format(val=val, var=self.env_var_name))


class Config(object):
    __metaclass__ = ConfigMeta

    def __init__(self, exit_on_failure=True):
        self.validate(exit_on_failure)

    def validate(self, exit_on_failure):
        validation_failure = False
        for k, v in vars(self.__class__).items():
            if isinstance(v, EnvVar):
                try:
                    v.populate()
                except EnvValidationError as ev:
                    print >>sys.stderr, ev
                    validation_failure = True
        if validation_failure and exit_on_failure:
            sys.exit(64)  # EX_USAGE in sysexits.h
        return not validation_failure

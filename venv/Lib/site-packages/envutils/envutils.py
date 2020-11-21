import logging
import os

logger = logging.getLogger(__name__)


def get_from_environment(env, default):
    """Read an environment variable.

    :param env: the environment variable name
    :param default: the default value
    :return:
    """
    try:
        v = os.environ[env]
        logger.info('Reading from environment: {}'.format(env))
    except KeyError:
        v = default
        logger.warning('Not found. Using default value: {}={}'.format(env, default))
    finally:
        return v


def get_int_from_environment(env, default):
    """Read an environment variable as an integer.

    :param env: the environment variable name
    :param default: the default value
    :return:
    """
    try:
        v = int(os.environ[env])
        logger.info('Reading from environment: {}'.format(env))
    except KeyError:
        v = default
        logger.warning('Not found. Using default value: {}={}'.format(env, default))
    except ValueError:
        v = default
        logger.warning('Failed to parse. Using default value: {}={}'.format(env, default))
    finally:
        return v


def get_bool_from_environment(env, default):
    """Read an environment variable as a boolean.

    :param env: the environment variable name
    :param default: the default value
    :return:
    """
    try:
        v = os.environ[env].lower()
        if v == 'true':
            v = True
        elif v == 'false':
            v = False
        else:
            raise ValueError
        logger.info('Reading from environment: {}'.format(env))
    except KeyError:
        v = default
        logger.warning('Not found. Using default value: {}={}'.format(env, default))
    except ValueError:
        v = default
        logger.warning('Failed to parse. Using default value: {}={}'.format(env, default))
    finally:
        return v

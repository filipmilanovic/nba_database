import os
import uuid

from envutils import envutils


def test_get_existing_envvar():
    key = 'TEST_VAR'
    value = 'test_value'
    os.environ[key] = value
    got = envutils.get_from_environment(key, 'default')
    assert got == value


def test_get_nonexisting_envvar():
    key = str(uuid.uuid4())
    got = envutils.get_from_environment(key, 'default')
    assert got == 'default'


def test_get_parsable_int_envvar():
    key = 'TEST_VAR'
    value = '42'
    os.environ[key] = value
    got = envutils.get_int_from_environment(key, 123)
    assert got == 42


def test_get_nonparsable_int_envvar():
    key = 'TEST_VAR'
    value = '123aaa'
    os.environ[key] = value
    got = envutils.get_int_from_environment(key, 123)
    assert got == 123


def test_get_parsable_bool_envvar():
    key = 'TEST_VAR'
    value = 'True'
    os.environ[key] = value
    got = envutils.get_bool_from_environment(key, False)
    assert got == True


def test_get_nonparsable_bool_envvar():
    key = 'TEST_VAR'
    value = 'Fasle'
    os.environ[key] = value
    got = envutils.get_bool_from_environment(key, True)
    assert got == True

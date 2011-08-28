"""
Test the logger module.
"""

# Author: Gael Varoquaux <gael dot varoquaux at normalesup dot org>
# Copyright (c) 2009 Gael Varoquaux
# License: BSD Style, 3 clauses.

import shutil
import os
import sys
import StringIO
from tempfile import mkdtemp
import re
from test.test_support import captured_stdout

import nose
from numpy.testing import assert_

from .. import logger
from ..logger import PrintTime


# XXX: look at stdlib test_logging.py; use more from it (BaseTest?)


###############################################################################
# Test fixtures

env = dict()

def setup():
    """ Test setup.
    """
    cachedir = mkdtemp()
    if os.path.exists(cachedir):
        shutil.rmtree(cachedir)
    env['dir'] = cachedir


def teardown():
    """ Test teardown.
    """
    #return True
    shutil.rmtree(env['dir'])


###############################################################################
# Utilities
#
# XXX: need utility (context manager?) for safely using tempfiles without
#      leaving them on failures do most tests with StringIO, but not all of
#      them.  Also needs to redirect stdout, and have that be testable.

def assert_logfile_contents(lines_read, lines_desired, style=None):
    """Assert that logfile contents are as expected."""
    assert_(len(lines_read) == len(lines_desired))
    for line_read, line_desired in zip(lines_read, lines_desired):
        assert_(compare_line(line_read, line_desired))


def compare_logfile_line(line_read, line_desired, style=None):
    """Compare a single line from a read in logfile with expected line.

    Time/date stamps can be checked for style, or just checked for any of the
    known formats.
    """
    # compare time, compare the rest exactly


def match_formatted_time(time_str, style='EU'):
    """Match a logged time with regexp.

    Styles:
      - EU: 15:45:01
      - US: 03:45:01 PM
      - custom: see logging module docs

    """
    def _check_match(matched):
        """Check that we got a match,return it as a string."""
        if matched is None:
            raise AssertionError("Time %s did not match `style`" % time_str)

        return matched.group()

    eu_match = '[0-2]\d:\d\d:\d\d'
    us_match = '[0-1]\d:\d\d:\d\d [A|P]M'
    if style == 'EU':
        matched = _check_match(re.match(eu_match, time_str))
        day = int(matched[:2])
        month = int(matched[3:5])
    elif style == 'US':
        matched = _check_match(re.match(us_match, time_str))
        day = int(matched[3:5])
        month = int(matched[:2])
    else:
        matched = _check_match(re.match(style, time_str))

    if style in ['EU', 'US']:
        # Don't do this for custom style; just assume that's OK
        assert_(0 < day < 32)
        assert_(0 < month < 13)

    return matched


def match_formatted_date(date_str, style='EU'):
    """Match a logged time with regexp.

    Styles:
      - EU: dd/mm/yyyy
      - US: mm/dd/yyyy
      - custom: see logging module docs

    """
    eu_match = '[0-3]]d/[0-1]\d/\d\d\d\d'
    us_match = '[0-1]]d/[0-3]\d/\d\d\d\d'
    if style == 'EU':
        matched = re.match(eu_match, date_str)
        day = matched.XXX
    elif style == 'US':
        matched = re.match(us_match, datetime_str)
    else:
        matched = re.match(style, datetime_str)

    if matched is None:
        raise AssertionError("Date %s did not match `style`" % datetime_str)

    return matched.group()


###############################################################################
# Tests
def test_basic_logfile():
    """Write a simple logfile."""
    logfile = os.path.join(env['dir'], 'testlog.log')
    logger.set_log_options(filename=logfile, stdout=logger.INFO,
                           verbose=logger.INFO)
    msg = "A basic test."
    logger.info(msg)
    # rewind/close logfile
    # assert logfile contents equals:
    fh = open(logfile, 'r')
    lines = fh.readlines()
    fh.close()
    assert_logfile_contents(lines, "INFO: " + msg)


def test_stdout_only():
    """Ensure we can send output only to stdout, and check log levels."""
    logfile = os.path.join(env['dir'], 'testlog.log')
    logger.set_log_options(filename=logfile, stdout=logger.WARNING,
                           verbose=0)
    with captured_stdout() as output:
        logger.warn("Line 1")
        logger.info("Line 2")
        logger.debug("Line 3")
        logger.critical("Line 4")
        logger.error("Line 5")
        assert_log_lines(output, DESIRED)
        # XXX: find easy way to construct desired result


def test_stdout_silent():
    """"""
    logger.set_log_options(stdout=0)
    with captured_stdout() as output:
        logger.critical("Line 1")
        assert_log_lines([])


def test_print_time():
    """ A simple smoke test for PrintTime.
    """
    try:
        orig_stderr = sys.stderr
        sys.stderr = StringIO.StringIO()
        print_time = PrintTime(logfile=os.path.join(env['dir'], 'test.log'))
        print_time('Foo')
        # Create a second time, to smoke test log rotation.
        print_time = PrintTime(logfile=os.path.join(env['dir'], 'test.log'))
        print_time('Foo')
        # And a third time
        print_time = PrintTime(logfile=os.path.join(env['dir'], 'test.log'))
        print_time('Foo')
        printed_text = sys.stderr.getvalue()
        # Use regexps to be robust to time variations
        match = r"Foo: 0\..s, 0\.0min\nFoo: 0\..s, 0.0min\nFoo: " + \
                r".\..s, 0.0min\n"
        if not re.match(match, printed_text):
            raise AssertionError('Excepted %s, got %s' %
                                    (match, printed_text))
    finally:
        sys.stderr = orig_stderr

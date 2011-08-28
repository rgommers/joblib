"""
Helpers for logging.

This module needs much love to become useful.
"""

# Author: Gael Varoquaux <gael dot varoquaux at normalesup dot org>
# Copyright (c) 2008 Gael Varoquaux
# License: BSD Style, 3 clauses.


import time
import sys
import os
import shutil
import logging
import pprint


# Define mapping between log level constants from stdlib logging module and
# this module.  We want higher level to mean more verbose.
DEBUG = logging.CRITICAL  # 50
INFO = logging.ERROR  # 40
WARNING = logging.WARNING  # 30
ERROR = logging.INFO  # 20
CRITICAL = logging.DEBUG  #10

PROGRESS = 45  # level for progress reporting, in between DEBUG and INFO


def set_log_options(filename=None, stdout=INFO, verbose=INFO, rotating=True,
                    numlogs=6, maxfilesize=10):
    """Set joblib logging options.

    Parameters
    ----------
    filename : str or file-like object, optional
        The file to which to log.  If not given, logging happens only to stdout
        (if `stdout` is True).  If `filename` is a string starting with "~",
        this character is expanded to the current HOME directory
        (``os.environ["HOME"]``).
    stdout : int, optional
        The verbosity for displaying log messages on stdout.  Default is INFO
        (= 40).  Set to 0 for a completely silent stdout.
    verbose : int, optional
        The logging verbosity.  All messages with a log level <= `verbose` will
        be logged.  The default is INFO (= 40).  See Notes for more details.
    rotating: bool, optional
        If True (default), use `numlogs` number of rotating logs when logging
        to file.
    numlogs : int, optional
        The maximum number of rotating log files.  Default is 6.
    maxfilesize : int, optional
        The maximum file size for a single log file in kb.  Default is 10.

    Returns
    -------
    None

    Notes
    -----
    The definition of the verbosity integers (= log levels) is as follows::

      -  0 :          : No output - complete quiet.
      - 10 : CRITICAL : Serious error, program may be unable to continue.
      - 20 : ERROR : The software has not been able to perform some function.
      - 30 : WARNING : Indication that something unexpected happened.
      - 40 : INFO : Confirmation that things are working as expected.
      - 45 : PROGRESS : Progress reporting.
      - 50 : DEBUG : Detailed information, typically used for debugging.

    Note that the log levels in the Python standard library module `logging`
    are the opposite (``logging.DEBUG == 10``, ``logging.CRITICAL == 50``).
    This definition was chosen to ensure that 0 means no output at all, and
    a higher verbose integer means more detailed output.

    Examples
    --------

    """
    if isinstance(filename, basestring) and filename.startswith('~'):
        filename.replace('~', os.environ["HOME"], 1)

    return None


def get_log_options():
    """Get the current logging options.

    These are either the defaults, or the ones set by a call to
    `set_log_options`.

    """
    raise NotImplementedError


def set_log_format(timestyle="US", level='lower'):
    """Set the log message format.

    Parameters
    ----------
    timestyle : {"EU", "US"}, optional
        The style in which the date and time information is displayed.  Default
        is "EU", which is ...
    level : {"upper", "lower", "short"}, optional
        The style in which the level of the log message is displayed.

    Returns
    -------
    None

    """
    raise NotImplementedError


def set_default_logger(loggerobj):
    """Use a custom logger.

    Parameters
    ----------
    loggerobj : object
        A custom logger object.

    Returns
    -------
    None

    Notes
    -----
    `loggerobj` should have at least these methods: XXX

    Examples
    --------

    """
    raise NotImplementedError


def log_header(msg):
    """Insert identifier message into log file.

    Parameters
    ----------
    msg : str
        The message to insert.
    top_char : str, optional
        Character to use to form the top line of the header.  Default is '_'.
    bottom_char : str, optional
        Character to use to form the bottom line of the header.
        Default is '_'.
    bottom_tag : str, optional
        The tag (string) to use on the closing line of the header.
        Default is None, which means using the name of the module from which
        the `log_header` call was made.
        To not use any tag, use ``bottom_tag == ''``.

    Returns
    -------
    None

    """
    raise NotImplementedError


def _squeeze_time(t):
    """Remove .1s to the time under Windows: this is the time it take to
    stat files. This is needed to make results similar to timings under
    Unix, for tests
    """
    if sys.platform.startswith('win'):
        return max(0, t - .1)
    else:
        return t


def format_time(t):
    t = _squeeze_time(t)
    return "%.1fs, %.1fmin" % (t, t / 60.)


def short_format_time(t):
    t = _squeeze_time(t)
    if t > 60:
        return "%4.1fmin" % (t / 60.)
    else:
        return " %5.1fs" % (t)


###############################################################################
# class `Logger`
###############################################################################
class Logger(object):
    """ Base class for logging messages.
    """

    def __init__(self, depth=3):
        """
            Parameters
            ----------
            depth: int, optional
                The depth of objects printed.
        """
        self.depth = depth

    def warn(self, msg):
        logging.warn("[%s]: %s" % (self, msg))

    def debug(self, msg):
        # XXX: This conflicts with the debug flag used in children class
        logging.debug("[%s]: %s" % (self, msg))

    def format(self, obj, indent=0):
        """ Return the formated representation of the object.
        """
        if 'numpy' in sys.modules:
            import numpy as np
            print_options = np.get_printoptions()
            np.set_printoptions(precision=6, threshold=64, edgeitems=1)
        else:
            print_options = None
        out = pprint.pformat(obj, depth=self.depth, indent=indent)
        if print_options:
            np.set_printoptions(**print_options)
        return out


###############################################################################
# class `PrintTime`
###############################################################################
class PrintTime(object):
    """ Print and log messages while keeping track of time.
    """

    def __init__(self, logfile=None, logdir=None):
        if logfile is not None and logdir is not None:
            raise ValueError('Cannot specify both logfile and logdir')
        # XXX: Need argument docstring
        self.last_time = time.time()
        self.start_time = self.last_time
        if logdir is not None:
            logfile = os.path.join(logdir, 'joblib.log')
        self.logfile = logfile
        if logfile is not None:
            if not os.path.exists(os.path.dirname(logfile)):
                os.makedirs(os.path.dirname(logfile))
            if os.path.exists(logfile):
                # Rotate the logs
                for i in range(1, 9):
                    if os.path.exists(logfile + '.%i' % i):
                        try:
                            shutil.move(logfile + '.%i' % i,
                                        logfile + '.%i' % (i + 1))
                        except:
                            "No reason failing here"
                # Use a copy rather than a move, so that a process
                # monitoring this file does not get lost.
                try:
                    shutil.copy(logfile, logfile + '.1')
                except:
                    "No reason failing here"
            try:
                logfile = file(logfile, 'w')
                logfile.write('\nLogging joblib python script\n')
                logfile.write('\n---%s---\n' % time.ctime(self.last_time))
            except:
                """ Multiprocessing writing to files can create race
                    conditions. Rather fail silently than crash the
                    caculation.
                """
                # XXX: We actually need a debug flag to disable this
                # silent failure.

    def __call__(self, msg='', total=False):
        """ Print the time elapsed between the last call and the current
            call, with an optional message.
        """
        if not total:
            time_lapse = time.time() - self.last_time
            full_msg = "%s: %s" % (msg, format_time(time_lapse))
        else:
            # FIXME: Too much logic duplicated
            time_lapse = time.time() - self.start_time
            full_msg = "%s: %.2fs, %.1f min" % (msg, time_lapse,
                                                time_lapse / 60)
        print >> sys.stderr, full_msg
        if self.logfile is not None:
            try:
                print >> file(self.logfile, 'a'), full_msg
            except:
                """ Multiprocessing writing to files can create race
                    conditions. Rather fail silently than crash the
                    caculation.
                """
                # XXX: We actually need a debug flag to disable this
                # silent failure.
        self.last_time = time.time()

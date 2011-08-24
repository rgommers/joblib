Logging facilities
==================

Starting logging
----------------

In order to monitor jobs and diagnose problems, joblib has logging facilities
built in.  By default these do nothing; they can be turned on by::

    from joblib import logger
    logger.start()

Starting the logging without giving any parameters will result in messages of
log level "info" or higher being printed to the screen.  This behavior can be
customized in several ways with keyword arguments to `logger.start`.  For
example, to log to a file, disable printing to screen and log all messages with
level "debug" or higher, use::

    from joblib import logger
    logger.start(filename='example.log', stdout=False, verbose='debug')

Rotating logs are used when logging to a file, which means that when a file
reaches its size limit (default is 10 kb) it is renamed from "<filename.log>"
to "<filename.log.1>" and new messages are written to a new "<filename.log>".
Up to six log files are used before old information gets overwritten.  These
settings can be controlled like::

    from joblib import logger
    logger.start(filename='example.log', rotating=True, numlogs=25)

.. note:: The ``logger.start()`` interface is designed to be as simple as
          possible to use.  Users familiar with the `logging` module from the
          Python standard library can use its interface instead if preferred. 
          For documentation we refer to XXX:link.


Controlling formatting
----------------------

The default format of a `joblib` log message is ``TIME LOGLEVEL: message``. 
For example, when an error with message "random failure" is logged on August
24th 2011 at 3.51 PM, this will show up in the log as::

    24/08/2011 15:51:00 ERROR: random failure

The formatting of this message can be controlled with `logger.set_format`.  To
for example switch to US style date and time representation and make the log
level name lowercase, use::

    logger.set_format(timestyle="US", level='lower')

The default representation of functions decorated with `Memory.cache`
identifies the function by its name, address in memory and full path to the
cachedir.  This is informative but quite verbose.  To use another identifier,
set the "name" attribute of the `MemorizedFunc` object.  This can be done in
the decorator itself::

    memory = Memory(cachedir=<mycachedir>, verbose=1)
    @memory.cache(name='MyModuleFunc')
    def func():
        ...


Inserting identifiers
---------------------

A log file quickly fills up and is usually quite dense and hard to read.  It is
always possible to manually insert a comment as an identifier to find things at
a later point in time with::

    import logging
    logging.info("My identifier")

More visually distinct identifiers are time-consuming to construct by hand
though, which is where the `logger.insert_id` function helps.  The call
``logger.insert_id("Running simulation X.Y on data Z")`` shows up in the log
file (with blank lines above and below) as::

    -----------------------------------------------------------------
        Running simulation X.Y on data Z
        Time: 15:51:00
        Date: 24/08/2011
    =================================================================


Custom loggers
--------------

The logging behavior can be customized in several ways by simple keyword
arguments to `logger.start`, as described above.  For more extensive
customization a custom logger can be used instead::

    mylogger = MyLogger(fancy=True)
    logger.use(mylogger)

This logger should be an object that provides at least the following methods:
debug, info, warning, error, critical, exception, XXX: what else?

XXX: describe other requirements (picklability?)


Combining with external logging 
-------------------------------

The joblib logging is based on the ``logging`` module from the Python standard
library.  This means that integrating the joblib logging with logging from
Python itself and from other libraries or end user code is straightforward.
...

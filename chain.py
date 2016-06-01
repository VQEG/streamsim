"""
This application transmits a collection of raw video material through configurable networks and stores the
obtained results.
"""

__author__ = 'Alexander Dethof'

from chainApp.processingChain import ProcessingChain

# True if the error warnings should be displayed more detailed; False if the error messages should be just shown and
# the application should exit by displaying it. By default the debug mode is set to false!
DEBUG_MODE = False


def __execute_chain():
    """
    Creates a new processing chain and executes it
    """

    processing_chain = ProcessingChain()

    try:
        from atexit import register
        register(processing_chain.cleanup)

        processing_chain.execute()
    except KeyboardInterrupt:
        processing_chain.cleanup()


if __name__ == '__main__':
    if DEBUG_MODE:
        __execute_chain()
    else:
        try:
            __execute_chain()
        except BaseException, e:
            exit('\033[1m\033[91m%s:\033[0m %s' % (e.__class__.__name__, str(e)))
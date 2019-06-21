import logging


class ExampleException(Exception):
    pass


def simple_record() -> logging.LogRecord:
    return logging.getLogger(__name__).makeRecord(
        "example", logging.INFO, "simple_record", 0, "An example log message", (), None
    )


def extra_record() -> logging.LogRecord:
    return logging.getLogger(__name__).makeRecord(
        "example",
        logging.INFO,
        "extra_record",
        0,
        "An example log message",
        ({"a": 1},),
        None,
        extra={"b": 2},
    )


def error_record() -> logging.LogRecord:
    try:
        raise ExampleException("Hello world")
    except ExampleException as error:
        return logging.getLogger(__name__).makeRecord(  # type: ignore
            "example",
            logging.INFO,
            "error_record",
            0,
            "An example log message caused by an error",
            (),
            (type(error), error, error.__traceback__),
        )

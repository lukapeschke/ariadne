from reprlib import repr  # pylint: disable=redefined-builtin
from traceback import format_exception

from typing import List, Optional, Union, cast

from graphql import ExecutionResult, GraphQLError

from .types import ErrorFormatter


def format_errors(
    result: ExecutionResult, format_error: ErrorFormatter, debug: bool = False
) -> List[dict]:
    if result.errors:
        return [format_error(e, debug) for e in result.errors]
    return []


def format_error(error: GraphQLError, debug: bool = False) -> dict:
    formatted = error.formatted
    if debug:
        if "extensions" not in formatted:
            formatted["extensions"] = {}
        formatted["extensions"]["exception"] = get_error_extension(error)
    return formatted


def get_error_extension(error: GraphQLError) -> Optional[dict]:
    unwrapped_error = unwrap_graphql_error(error)
    if unwrapped_error is None or not error.__traceback__:
        return None

    unwrapped_error = cast(Exception, unwrapped_error)
    return {
        "stacktrace": get_formatted_traceback(unwrapped_error),
        "context": get_formatted_context(unwrapped_error),
    }


def unwrap_graphql_error(
    error: Union[GraphQLError, Optional[Exception]]
) -> Optional[Exception]:
    if isinstance(error, GraphQLError):
        return unwrap_graphql_error(error.original_error)
    return error


def get_formatted_traceback(error: Exception) -> List[str]:
    formatted = []
    for line in format_exception(type(error), error, error.__traceback__):
        formatted.extend(line.rstrip().splitlines())
    return formatted


def get_formatted_context(error: Exception) -> Optional[dict]:
    tb_last = error.__traceback__
    while tb_last and tb_last.tb_next:
        tb_last = tb_last.tb_next
    if tb_last is None:
        return None
    return {key: repr(value) for key, value in tb_last.tb_frame.f_locals.items()}
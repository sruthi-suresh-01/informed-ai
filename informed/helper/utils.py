import traceback


def get_concise_exception_traceback(exc: Exception, num_lines: int = 2) -> str:
    tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
    return "".join(tb_lines[-num_lines:])

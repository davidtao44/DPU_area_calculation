class AreaLabError(Exception):
    """An expected application error."""


class InvalidConfiguration(AreaLabError):
    pass


class NotFound(AreaLabError):
    pass


class QueueFull(AreaLabError):
    pass


class PipelineFailure(AreaLabError):
    pass

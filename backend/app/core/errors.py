from __future__ import annotations


class ApplicationError(Exception):
    pass


class ConfigurationError(ApplicationError):
    pass


class EntityNotFoundError(ApplicationError):
    pass


class PersistenceError(ApplicationError):
    pass


class ProviderUnavailableError(ApplicationError):
    pass


class ProviderOutputError(ApplicationError):
    pass

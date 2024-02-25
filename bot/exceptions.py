class AnyError(Exception):
    """
    Исключение возникающее при любых ошибках.
    """

    pass


class ServiceManUnregisteredError(Exception):
    """
    Исключение возникающее при получении запроса
    от незарегистрированного инженера.
    """

    pass


class ServiceInfoExistError(Exception):
    """Исключение возникающее при сохранении второго обслуживания за день."""

    pass


class PontExistError(Exception):
    """Исключение возникающее если точки нет в базе"""
    pass

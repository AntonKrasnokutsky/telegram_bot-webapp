class ServiceManUnregisteredError(Exception):
    """
    Исключение возникающее при получении запроса
    от незарегистрированного инженера.
    """

    pass


class ServiceInfoExistError(Exception):
    """Исключение возникающее при сохранении второго обслуживания за день."""

    pass

from exceptions import AnyError


def test():
    raise AnyError('Тест сообщения')


try:
    test()
except AnyError as ex:
    print(ex.args[0])

def strict(func):
    def wrapper(*args, **kwargs):
        annotations = func.__annotations__
        arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]
        for index, arg_name in enumerate(arg_names):
            if arg_name in annotations:

                expected_type = annotations[arg_name]

                # Проверка позиционный или именованный параметр
                if index < len(args):
                    value = args[index]
                else:
                    value = kwargs.get(arg_name)

                if not isinstance(value, expected_type):
                    raise TypeError(f'Переданный параметр "{arg_name}" не соответствует аннотации')
            else:
                raise TypeError(f'У переданного параметра "{arg_name}" нет типа')
        return func(*args, **kwargs)
    return wrapper

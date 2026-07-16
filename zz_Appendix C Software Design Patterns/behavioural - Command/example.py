"""A small contrast: closure first, Command object only with extra needs."""


class InvalidName(ValueError):
    """Raised when a stored request contains no usable name."""


def rename(old_name, new_name):
    if not new_name.strip():
        raise InvalidName("new name must not be blank")
    return f"{old_name}->{new_name}"


def make_command(function, *arguments):
    """Store a function and its arguments as a zero-argument closure."""
    def execute():
        return function(*arguments)

    return execute


class RenameCommand:
    """Object form; useful only when identity or metadata earns the class."""

    def __init__(self, command_id, old_name, new_name):
        self.command_id = command_id
        self.old_name = old_name
        self.new_name = new_name

    def execute(self):
        return rename(self.old_name, self.new_name)


def main():
    closure = make_command(rename, "draft", "ready")
    print(f"function-command={closure()}")

    command = RenameCommand("cmd-1", "draft", "ready")
    print(f"object-command={command.command_id}:{command.execute()}")
    try:
        make_command(rename, "draft", " ")()
    except InvalidName as error:
        print(f"boundary={error}")
    print(f"recovery={make_command(rename, 'draft', 'safe')()}")


if __name__ == "__main__":
    main()

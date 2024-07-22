import handlers


class Commands():
    command: str = ''
    parameters = []
    description: str = ''
    usage: str = ''
    handler: callable = None
    shorthand: str = ""

    def __init__(self, command: str, parameters: list, description: str, usage: str, handler: callable, shorthand: str = ""):
        self.command = command
        self.parameters = parameters
        self.description = description
        self.usage = usage
        self.handler = handler
        self.shorthand = shorthand


def show_help_message():
    print("Available commands:")
    for c in cmds:
        print(f"    {c.command} {c.shorthand}")
        print(f"        {c.usage} - {c.description}")


cmds = [
    Commands("available", [], "Show available lua version",
             usage="available", handler=handlers.available, shorthand="a"),
    Commands("install", ['version'], "Install a specific version lua",
             usage="install <version>", handler=handlers.install, shorthand="i"),
    Commands("uninstall", ['version'],
             "Uninstall a specific version lua", "uninstall <version>", handler=handlers.uninstall, shorthand="u"),
    Commands("use", ['version'], "Use a specific version lua",
             "use <version>", handler=handlers.use),
    Commands("list", [], "List all installed lua versions",
             "list", handler=handlers.get_install_list, shorthand="l"),
    Commands('help', [], 'Show this help message',
             'help', handler=show_help_message, shorthand="h"),
]


class CmdParser():
    def __init__(self):
        self.cmds = cmds

    def parse(self, cmd: list):
        if len(cmd) == 0:
            return None
        for c in self.cmds:
            if c.command == cmd[0] or c.shorthand == cmd[0]:
                if len(cmd) - 1 != len(c.parameters):
                    print(f"Usage: {c.usage}")
                    return None
                if len(c.parameters) == 0:
                    return c.handler()
                return c.handler(*cmd[1:])
        print("Invalid command")
        show_help_message()
        return None

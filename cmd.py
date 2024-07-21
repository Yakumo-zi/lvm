import handlers


class Commands():
    command: str = ''
    parameters = []
    description: str = ''
    usage: str = ''
    handler: callable = None


cmds = [
    Commands("available", [], "Show available lua version",
             "available", handlers.available),
    Commands("install", ['version'], "Install a specific version lua",
             "install <version>", handlers.install),
    Commands("uninstall", ['version'],
             "Uninstall a specific version lua", handlers.uninstall),
    Commands("use", ['version'], "Use a specific version lua",
             "use <version>", handlers.use),
    Commands("list", [], "List all installed lua versions",
             "list", handlers.get_install_list),
    Commands('help', [], 'Show this help message', 'help', None),
]

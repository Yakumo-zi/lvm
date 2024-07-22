import cmd
import sys
import handlers
if __name__ == "__main__":
    parser = cmd.CmdParser()
    handlers.get_available()
    parser.parse(sys.argv[1:])

from .core import cli
from .web import app, run_web

def main():
    ans = None
    while ans == None:
        ans = input("Cli or WebUI? ").lower().strip()[0]
        if ans not in ["c","w"]:
            ans = None
    try:
        if ans == "c":
            cli()
        else:
            run_web()
    except KeyboardInterrupt:
        print("\nExiting...")
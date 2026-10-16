from core import get_keys, run

def cli():
    conf = get_keys()
    convo = []
    while True:
        convo.append({"role":"user", "content":input(">")})
        convo.append({"role":"AI","content":""})
        convo = run(convo, lambda x: print(x, end=" ", flush=True), conf)
        print()

def main():
    cli()


if __name__ == "__main__":
    main()

import colorama


def print_available_streams(player):
    print(f"{colorama.Style.BRIGHT}{colorama.Fore.GREEN}Welcome to RadioPi!{colorama.Style.RESET_ALL}")
    print("Available streams")
    print("=================")
    for idx, stream in enumerate(player.streams):
        if stream.name == player.current_stream().name:
            style = colorama.Style.BRIGHT
            text = f"[{idx}] {stream.name} - {stream.url} [currently listening]"
        else:
            style = colorama.Style.DIM
            text = f"[{idx}] {stream.name} - {stream.url}"
        print(style + text + colorama.Style.RESET_ALL)
    print("=================")


def error(msg):
    print(f"{colorama.Style.BRIGHT}{colorama.Fore.RED}{msg}{colorama.Style.RESET_ALL}")

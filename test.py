import colorama

colorama.init()


def move_cursor(x, y):
    print("\x1b[{};{}H".format(y + 1, x + 1))


def clear():
    print("\x1b[2J")


clear()
move_cursor(0, 0)
print("hello")
print("hola")
# return to first line
move_cursor(0, 0)
print("aloha")
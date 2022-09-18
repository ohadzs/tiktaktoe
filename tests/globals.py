
def a():
    global x
    x = 6

def b():
    global x
    print(x)

a()
b()
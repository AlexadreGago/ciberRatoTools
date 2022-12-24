


def realOrientation(compass):
    if (compass>= 0 and compass<= 45) or (compass>= -45 and compass<= 0):  # right
        return "right"
    elif (compass<= -45 and compass>= -135):  # down
        return "down"
    elif (compass<= 135 and compass>= 45):  # up
        return "up"
    elif (compass<= 180 and compass>= 135) or (compass <=135 and compass >=-180) :  # down
        return "left"
    else:
        return ""

def main():
    for i in range(-180, 180):
        print(i, realOrientation(i))
    
main()
    
        

import math
# remaining= -5
# previouspowerLR = (-0.15, 0.15) 

# power = -0.23

# rot = ( ((0.5 * power) + (0.5 * previouspowerLR[1] )) - ((0.5 * -power) + (0.5 * previouspowerLR[0] )) )

# print(math.degrees(rot))

# print(math.radians(remaining))
      
# #power =  (  (0.5 * previouspowerLR[1]) - (0.5 * previouspowerLR[0])  ) - math.radians(remaining) 
# power = math.radians(remaining) -  (0.5 * previouspowerLR[1]) + (0.5 * previouspowerLR[0])
# if power > 0.15:
#     power = 0.15
# rot = ( ((0.5 * power) + (0.5 * previouspowerLR[1] )) - ((0.5 * -power) + (0.5 * previouspowerLR[0] )) )
# print("real rotation: ", math.degrees(rot))


# print("pwoer", power)



#remaining = ( ((0.5 * power) + (0.5 * previouspowerLR[1] )) + ((0.5 * power) - (0.5 * previouspowerLR[0] )) )

#remaining = power + 0.5previouspowerLR[1] - 0.5previouspowerLR[0]
#-power = -remaining + 0.5previouspowerLR[1] - 0.5previouspowerLR[0]
#power = remaining - 0.5previouspowerLR[1] + 0.5previouspowerLR[0]


# 55.0 remaining:  35.0 power:  0.15 previouspowerLR:  (-0.15, 0.15)
# 71.0 remaining:  19.0 power:  0.15 previouspowerLR:  (-0.15, 0.15)
# 87.0 remaining:  3.0 power:  0.0976401224401701 previouspowerLR:  (-0.15, 0.15)




#-----------------------------------------------------------------------------------------


x = 10
y = 10

compass = 0


def roundcoord(num):
    return (num + 2 - 1) & -2
print(roundcoord(1011))


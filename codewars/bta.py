# There was a test in your class and you passed it. Congratulations!
# But you're an ambitious person. You want to know if you're better than the average student in your class.
# You receive an array with your peers' test scores. Now calculate the average and compare your score!
# Return true if you're better, else false!
# Note: Your points are not included in the array of your class's points. Do not forget them when calculating the average score!

def better_than_average(class_points, your_points):
    total_class = []
    for point in class_points:
        total_class.append(point)
    total_class.append(50)
    q = len(total_class)
    av = sum(total_class) / q
    return av


x = better_than_average([41, 75, 72, 56, 80, 82, 81, 33], 50)
print(x)


# sum of 41, 75, 72, 56, 80, 82, 81, 33 = 520 Add 50 & divide by 9 = 63.3%

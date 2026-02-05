stuff = [['id', 'first', 'last'], [1, 'anthony', 'garo'], [2, 'raul', 'veras']]
print stuff

for i in range(len(stuff)):
    if i == 0:
        stuff[i].append('email')
    else:
        stuff[i].append(stuff[i][1][0] + stuff[i][2] + "@gmail.com")
    
print stuff

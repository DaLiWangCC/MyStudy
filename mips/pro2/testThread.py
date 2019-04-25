import _thread
from sklearn import pipeline
import pipeline
import grapevine
import time
import queue
x = 0
y = 0

def cal_print_1(i):
    global  x
    x += 1
    print()
    global y
    y += 1
    print("hh\n")
    print("t1 x  ",x,"t1 y  ",y," ",i)

def cal_print_2(i):
    global  x
    x = 11
    global y
    y = 11
    print("s x  ",x,"s y  ",y," ",i)
    time.sleep(1)


# _thread.start_new(cal_print_1,())
# _thread.start_new(cal_print_2,())
# for i in range(0,130):
    # pipe_lr = pipeline.Pipeline([('sc', cal_print_1()),('pca', cal_print_2()), ])
def ts(i):
    # grapevine.cat(cal_print_1(i), cal_print_2(i))

    print("dd ",i)
    grapevine.cat(cal_print_1(i), cal_print_2(i))

ts(1)


qu = queue.Queue(4)

for i in range(0,4):
    qu.put("gg")
    if not qu.full():
        print("full")
    else:
        print("not full")

list = ['a','b','c']

print(list)
for str in list:
    if str =='a':
        list.remove(str)
print(list)

# pipe_lr.fit(X_train, y_train)
# print('Test accuracy: %.3f' % pipe_lr.score(X_test, y_test))


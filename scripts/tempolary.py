import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as pat
import numpy as np

fig = plt.figure()
ax = plt.subplot()

def clock(i):
    # circle = [ax.add_patch(pat.Wedge(center=(0, 0), r=1, color=[0+i/60,0,1-i/60], theta1 = 95-i*(360/60), theta2 = 85-i*(360/60)))]
    x = np.array([j for j in range(10)])
    y = np.array([j for j in range(10)])
    color = np.zeros(10)
    color[i%10] = i%10
    circle = [ax.scatter(x,y, c = color)]
    #center：中心のxy座標,r：ウェッジの半径,color：RGBでの色指定(各色0~1),theta：ウェッジの角度を指定
    #circleをリストにすることに注意してください。あとでimgsに追加できるようにするためです。
    return circle

#リストimgsに、各秒ごとのclockを追加していきます。
imgs=[]
for i in range(60):
    imgs.append(clock(i))

ani = animation.ArtistAnimation(fig, imgs, interval=1000, repeat=True)
plt.axis("scaled")
plt.show()

# ani.save("second_hand.gif", writer="imagemagick")#gifとして保存

import pyautogui
import time
import cv2
from PIL import Image

class Solver:
    # 15*23
    tile_data = []
    # make data base of color and rgb
    color = [
        [97,205,203], # sky blue0
        [7,202,58], # green1
        [205,97,37], # brown2
        [255,148,54], # orange3
        [255,97,107], # red4
        [253,141,249], # pink5
        [186,188,188], # grey6
        [204,201,116], # yellow7
        [202,107,199], # purple8
        [0,116,246], # blue9
        [245,247,247], # null white10
        [235,237,237], # null grey11
        [0,0,0] # null black12
    ]
    thresh = 10
    hit_call = False
    hit_result = [] # [y, x]
    pass_tile = [[0]*23 for i in range(15)] # tile that already checked

    def __init__(self):
        self.img = cv2.imread('screenshot.png')
        #crop image by coordinates
        self.img = self.img[158:533, 185:760]
        # print img size
        print(self.img.shape)
        cv2.imwrite('crop.png', self.img)
        im = Image.open('crop.png')
        self.pix = im.load()
        self.find_color()
        print(self.tile_data)
        cv2.imwrite('result.png', self.img)

    def find_color(self):
        # loop for each tile
        for i in range(15):
            tile_row = []
            for j in range(23):
                # get pixel color
                r, g, b = self.pix[((j+1)*25-13), ((i+1)*25-13)]
                print(r, g, b, j , i)
                # calculate distance to each color
                distance = []
                for color in self.color:
                    distance.append(abs(r-color[0])+abs(g-color[1])+abs(b-color[2]))
                # find the minimum distance
                min_distance = min(distance)
                # find the index of minimum distance
                index = distance.index(min_distance)
                print(index)
                # if distance is less than threshold
                if min_distance < self.thresh:
                    # append index to tile_data
                    tile_row.append(index)

                else:
                    # append 9 to tile_data
                    tile_row.append(12)

                # plot a colored dot on the tile
                self.img = cv2.circle(self.img, ((j+1)*25-13, (i+1)*25-13), radius=0, color=(list(reversed(self.color[index]))), thickness=-1)
                if (tile_row[j] == 11) or (tile_row[j] == 10):
                    tile_row[j] = 12
                    self.img = cv2.circle(self.img, ((j+1)*25-13, (i+1)*25-13), radius=0, color=(list(reversed(self.color[12]))), thickness=-1)


                # adding row to tile_data
                if j == 22:
                    self.tile_data.append(tile_row)
                    print (len(tile_row))
                    tile_row = []
        # write to txt file
        with open('tile_data.txt', 'w') as f:
            for item in self.tile_data:
                f.write("%s\n" % item)


    def tile_hit(self,y,x):
        self.hit_call = True
        self.hit_result.append(y)
        self.hit_result.append(x)

    def check_tile_decider(self):
        checking_color = []
        print('[decider]enter')
        print('[decider]',self.pass_tile)
        # find color to check
        for i in range(15):
            for j in range(23):
                # check if tile is already checked
                if self.pass_tile[i][j] == True:
                    print('[decider]passing tile',[i,j])
                    continue
                if self.tile_data[i][j] == 12:
                    self.pass_tile[i][j] = True
                    print('[decider]passing tile',[i,j])
                    pass
                else:
                    checking_color.append(i)  # row
                    checking_color.append(j)  # column
                    checking_color.append(self.tile_data[i][j]) # color
                    print('[decider]', checking_color)
                    return checking_color
                # no tile any more
                if i == 14 and j == 22:
                    print('[decider]no tile any more')
                    return False


    def cross_point_calc(self, hit_result, checking_color):
        cross_point_1 = [ hit_result[0], checking_color[1] ]
        cross_point_2 = [ checking_color[0], hit_result[1] ]
        print('[cross check]',checking_color)
        print('[cross check]',hit_result)
        print('[cross check]',cross_point_1)
        print('[cross check]',cross_point_2)
        # check for each cross point
        # first have to check if hit_result and checking_color is not in the same row or column
        while True:
            if hit_result[0] == checking_color[0]:
                print('[cross check]same row')
                if hit_result[1] < checking_color[1]:
                    cross_point_1[1] -= 1
                    # no need to check cross point 2 since it is in the same row
                else:
                    cross_point_1[1] += 1
                    # no need to check cross point 2 since it is in the same row
                break
            elif hit_result[1] == checking_color[1]:
                print('[cross check]same column')
                if hit_result[0] < checking_color[0]:
                    cross_point_1[0] += 1
                    # no need to check cross point 2 since it is in the same column
                else:
                    cross_point_1[0] -= 1
                    # no need to check cross point 2 since it is in the same column
                break
            else:
                break

        # cros point 1
        counter = 0
        print('[cross check]cross point 1',cross_point_1)
        # check left
        if cross_point_1[1] != 0:
            for i in range(cross_point_1[1])[::-1]:
                if self.tile_data[cross_point_1[0]][i] == 12:
                    pass
                elif self.tile_data[cross_point_1[0]][i] == checking_color[2]:
                    counter += 1
                    break
                else:
                    break
        # check right
        if cross_point_1[1] != 22:
            for i in range(cross_point_1[1]+1, 23):
                if self.tile_data[cross_point_1[0]][i] == 12:
                    pass
                elif self.tile_data[cross_point_1[0]][i] == checking_color[2]:
                    counter += 1
                    break
                else:
                    break
        # check up
        if cross_point_1[0] != 0:
            for i in range(cross_point_1[0])[::-1]:
                if self.tile_data[i][cross_point_1[1]] == 12:
                    pass
                elif self.tile_data[i][cross_point_1[1]] == checking_color[2]:
                    counter += 1
                    break
                else:
                    break
        # check down
        if cross_point_1[0] != 14:
            for i in range(cross_point_1[0]+1, 15):
                if self.tile_data[i][cross_point_1[1]] == 12:
                    pass
                elif self.tile_data[i][cross_point_1[1]] == checking_color[2]:
                    counter += 1
                    break
                else:
                    break

        # count check
        if counter == 2 or counter == 3 or counter == 4:
            print('[cross check]counter',counter)
            if self.tile_data[cross_point_1[0]][cross_point_1[1]] == 12:
                print('[cross check]cross point 1 hit')
                return [cross_point_1[0], cross_point_1[1]]


        # croos point 2
        print('[cross check]cross point 2',cross_point_2)
        counter = 0
        # check left
        if cross_point_2[1] != 0:
            for i in range(cross_point_2[1])[::-1]:
                if self.tile_data[cross_point_2[0]][i] == 12:
                    pass
                elif self.tile_data[cross_point_2[0]][i] == checking_color[2]:
                    counter += 1
                    break
                else:
                    break
        # check right
        if cross_point_2[1] != 22:
            for i in range(cross_point_2[1]+1, 23):
                if self.tile_data[cross_point_2[0]][i] == 12:
                    pass
                elif self.tile_data[cross_point_2[0]][i] == checking_color[2]:
                    counter += 1
                    break
                else:
                    break
        # check up
        if cross_point_2[0] != 0:
            for i in range(cross_point_2[0])[::-1]:
                if self.tile_data[i][cross_point_2[1]] == 12:
                    pass
                elif self.tile_data[i][cross_point_2[1]] == checking_color[2]:
                    counter += 1
                    break
                else:
                    break

        # check down
        if cross_point_2[0] != 14:
            for i in range(cross_point_2[0]+1, 15):
                if self.tile_data[i][cross_point_2[1]] == 12:
                    pass
                elif self.tile_data[i][cross_point_2[1]] == checking_color[2]:
                    counter += 1
                    break
                else:
                    break

        # # count check
        if counter == 2 or counter == 3 or counter == 4:
            print('[cross check]cross point 2 hit')
            return [cross_point_2[0], cross_point_2[1]]

    def tile_solver(self):
        self.hit_call = False
        while True:
            # define checking color
            checking_color = self.check_tile_decider()
            if checking_color == False:
                print('[tile solver]no tile any more')
                return False
            # find the same color
            while True:
                # check left
                if checking_color[1] != 0:
                    for i in range(checking_color[1])[::-1]:
                        print('[tile solver]checking left', i)
                        if self.tile_data[checking_color[0]][i] == checking_color[2]:
                            # if its next to the checking tile
                            if i == checking_color[1]-1:
                                break
                            self.tile_hit(checking_color[0], i)
                            break
                        elif self.tile_data[checking_color[0]][i] == 12:
                            # check up
                            if checking_color[0] != 0:
                                for j in range(checking_color[0])[::-1]:
                                    if self.tile_data[j][i] == checking_color[2]:
                                        self.tile_hit(j, i)
                                        break
                                    elif self.tile_data[j][i] == 12:
                                        pass
                                    else:
                                        break
                            # check down
                            if checking_color[0] != 14:
                                for j in range(checking_color[0]+1, 15):
                                    if self.tile_data[j][i] == checking_color[2]:
                                        self.tile_hit(j, i)
                                        break
                                    elif self.tile_data[j][i] == 12:
                                        pass
                                    else:
                                        break
                        else:
                            break

                        # break on hit
                        if self.hit_call:
                            break
                if self.hit_call:
                    break
                # check right
                if checking_color[1] != 22:
                    for i in range(checking_color[1]+1, 23):
                        print('[tile solver]checking right', i)
                        if self.tile_data[checking_color[0]][i] == checking_color[2]:
                            # if its next to the checking tile
                            if i == checking_color[1]+1:
                                break
                            self.tile_hit(checking_color[0], i)
                            break
                        elif self.tile_data[checking_color[0]][i] == 12:
                            # check up
                            if checking_color[0] != 0:
                                for j in range(checking_color[0])[::-1]:
                                    if self.tile_data[j][i] == checking_color[2]:
                                        self.tile_hit(j, i)
                                        break
                                    elif self.tile_data[j][i] == 12:
                                        pass
                                    else:
                                        break
                            # check down
                            if checking_color[0] != 14:
                                for j in range(checking_color[0]+1, 15):
                                    if self.tile_data[j][i] == checking_color[2]:
                                        self.tile_hit(j, i)
                                        break
                                    elif self.tile_data[j][i] == 12:
                                        pass
                                    else:
                                        break
                        else:
                            break

                        # break on hit
                        if self.hit_call:
                            break
                if self.hit_call:
                    break
                # check up
                if checking_color[0] != 0:
                    for i in range(checking_color[0])[::-1]:
                        print('[tile solver]checking up', i)
                        if self.tile_data[i][checking_color[1]] == checking_color[2]:
                            # if its next to the checking tile
                            if i == checking_color[0]-1:
                                break
                            self.tile_hit(i, checking_color[1])
                            break
                        elif self.tile_data[i][checking_color[1]] == 12:
                            # check left
                            if checking_color[1] != 0:
                                for j in range(checking_color[1])[::-1]:
                                    if self.tile_data[i][j] == checking_color[2]:
                                        self.tile_hit(i, j)
                                        break
                                    elif self.tile_data[i][j] == 12:
                                        pass
                                    else:
                                        break
                            # check right
                            if checking_color[1] != 22:
                                for j in range(checking_color[1]+1, 23):
                                    if self.tile_data[i][j] == checking_color[2]:
                                        self.tile_hit(i, j)
                                        break
                                    elif self.tile_data[i][j] == 12:
                                        pass
                                    else:
                                        break
                        else:
                            break

                        # break on hit
                        if self.hit_call:
                            break
                if self.hit_call:
                    break
                # check down
                if checking_color[0] != 14:
                    for i in range(checking_color[0]+1, 15):
                        print('[tile solver]checking down', i)
                        if self.tile_data[i][checking_color[1]] == checking_color[2]:
                            # if its next to the checking tile
                            if i == checking_color[0]+1:
                                break
                            self.tile_hit(i, checking_color[1])
                            break
                        elif self.tile_data[i][checking_color[1]] == 12:
                            # check left
                            if checking_color[1] != 0:
                                for j in range(checking_color[1])[::-1]:
                                    if self.tile_data[i][j] == checking_color[2]:
                                        self.tile_hit(i, j)
                                        break
                                    elif self.tile_data[i][j] == 12:
                                        pass
                                    else:
                                        break
                            # check right
                            if checking_color[1] != 22:
                                for j in range(checking_color[1]+1, 23):
                                    if self.tile_data[i][j] == checking_color[2]:
                                        self.tile_hit(i, j)
                                        break
                                    elif self.tile_data[i][j] == 12:
                                        pass
                                    else:
                                        break
                        else:
                            break

                        # break on hit
                        if self.hit_call:
                            break
                if self.hit_call:
                    break
                else:
                    print('[tile solver]no hit')
                    self.pass_tile[checking_color[0]][checking_color[1]] = True
                    break
            # break on hit
            if self.hit_call:
                print('[tile solver]hit', self.hit_result)
                break

        # callculate cross point
        return self.cross_point_calc(self.hit_result, checking_color)

    def tile_data_update(self,click_tile):
        cross_color = [] # left right up down
        cross_tile = [] # left right up down
        deleted_color = []
        # check left
        if click_tile[1] != 0:
            for i in range(click_tile[1])[::-1]:
                if self.tile_data[click_tile[0]][i] == 12:
                    pass
                else:#check length of cross_color
                    cross_color.append(self.tile_data[click_tile[0]][i])
                    cross_tile.append([click_tile[0],i])
                    print('[update]append')
                    break
        # check right
        if click_tile[1] != 22:
            for i in range(click_tile[1]+1, 23):
                if self.tile_data[click_tile[0]][i] == 12:
                    pass
                else:
                    cross_color.append(self.tile_data[click_tile[0]][i])
                    cross_tile.append([click_tile[0],i])
                    print('[update]append')
                    break
        # check up
        if click_tile[0] != 0:
            for i in range(click_tile[0])[::-1]:
                if self.tile_data[i][click_tile[1]] == 12:
                    pass
                else:
                    cross_color.append(self.tile_data[i][click_tile[1]])
                    cross_tile.append([i,click_tile[1]])
                    print('[update]append')
                    break
        # check down
        if click_tile[0] != 14:
            for i in range(click_tile[0]+1, 15):
                if self.tile_data[i][click_tile[1]] == 12:
                    pass
                else:
                    cross_color.append(self.tile_data[i][click_tile[1]])
                    cross_tile.append([i,click_tile[1]])
                    print('[update]append')
                    break

        # check which color is the same
        print('[update]',cross_color)
        for i in range(len(cross_color)):
            for j in range(len(cross_color)):
                if i==j:
                    continue
                if cross_color[i] == cross_color[j]:
                    deleted_color.append(cross_color[i])
                    self.tile_data[cross_tile[i][0]][cross_tile[i][1]] = 12
                    self.tile_data[cross_tile[j][0]][cross_tile[j][1]] = 12
            # over 3 same color then delete
            for j in deleted_color:
                if cross_color[i] == j:
                    self.tile_data[cross_tile[i][0]][cross_tile[i][1]] = 12
        # write to txt file
        with open('tile_data.txt', 'w') as f:
            for item in self.tile_data:
                f.write("%s\n" % item)

    def init_variables(self):
        self.hit_call = False
        self.hit_result = []
        self.pass_tile = [[0]*23 for i in range(15)]




# start main
if __name__ == '__main__':
    print(pyautogui.size()) # Get the screen size
    # put delay to 5 seconds
    time.sleep(2)
    # take current mouse position
    print(pyautogui.position())

    pyautogui.moveTo(456, 357) # Move the mouse to XY coordinates over num_second seconds
    # click the mouse
    pyautogui.click()

    time.sleep(1)
    # take screenshot
    pyautogui.screenshot('screenshot.png')

    solver = Solver()
    result = True
    n=0

    while result:
      result = solver.tile_solver()
      print(result)
      if result == False:
          break
      time.sleep(0.01)
      pyautogui.moveTo(185+result[1]*25+13, 158+result[0]*25+13)
      time.sleep(0.01)
      pyautogui.click()
      solver.tile_data_update(result)
      solver.init_variables()

      n+=1

      if n == 100:
          break

    # print end showy
    print('end')



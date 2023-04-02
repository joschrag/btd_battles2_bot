import cv2
import time
import numpy as np
import pyautogui
import pynput


class Tower:
    def __init__(self, name: str, upgrades, ingPic=None):
        self.name = name
        self.upgrades = upgrades
        self.upgradeKeys = [",", ".", "-"]
        self.ingPic = ingPic

    def Try2Upgrade(self):
        for idx, path in enumerate(self.upgrades):
            for i in range(idx):
                pynput.keyboard.Controller().tap(self.upgradeKeys[path])


def getImg(file):
    mainpath = "C:/Users/Jonas/Pictures/Bloons_py/"
    filepath = file
    path = mainpath + filepath
    img = cv2.imread(path, cv2.COLOR_BGR2GRAY)
    return img


def Takescreenshot(file):
    mainpath = "C:/Users/Jonas/Pictures/Bloons_py/"
    filepath = mainpath + file
    pyautogui.screenshot(filepath)


def LocateInImage(search_img, source_img, show=False, getPos=False) -> bool:
    tempimg = source_img.copy()
    result = cv2.matchTemplate(source_img, search_img, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    # print('Best match top left position: %s' % str(max_loc))
    # print('Best match confidence: %s' % max_val)
    threshold = 0.65

    if float(max_val) >= threshold:
        # print("Found some!!")
        height, width = search_img.shape[:2]
        top_left = max_loc
        bottom_right = (top_left[0] + width, top_left[1] + height)
        if getPos:
            return [top_left[0] + width / 2, top_left[1] + height / 2]
        if show:
            cv2.rectangle(tempimg, top_left, bottom_right, (0, 0, 255), 5)
            cv2.imshow("image", tempimg)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        return True
    else:
        # print('Nothing')
        return False


def Try2PlaceTower(tower, isLeft):
    k = 5
    l = 5
    if isLeft:
        start = 225
        TowerPosList = {
            "hero": [150, 130],
            "first": [150, 240],
            "second": [150, 320],
            "third": [150, 400],
        }
    else:
        start = 1075
        TowerPosList = {
            "hero": [1775, 130],
            "first": [1775, 240],
            "second": [1775, 320],
            "third": [1775, 400],
        }
    for i in range(k):
        for j in range(l):
            stepX = np.floor_divide(695, k)
            stepY = np.floor_divide(895, l)
            x = start + i * stepX
            y = 90 + j * stepY
            DragTower(TowerPosList[tower], [x, y])


# TODO:  2.) Heroplacement -stop if placed (greycheck)
#       6.) Towerplacement - ""
#       3.) maperkennung                                    done
#       4.) individuelle platzierung pro map und Seite      in Progress
#       7.) Upgrades
#       5.) Rundencounter (surrender@round 6)
#       1.) Fehler: gegner disconnect in towerselect        done
#       8.) Truhendiscarder                                 done
#       9.) else bei clickerror


def preprocessScreenshot(file):
    Takescreenshot(file)
    time.sleep(0.1)
    Image = getImg(file)
    cv2.imshow("", Image)
    cv2.waitKey(0)
    return Image


def InMainMenu(curImage) -> bool:
    bool1 = LocateInImage(fight_btn, curImage)
    bool2 = LocateInImage(menu_fight_btn, curImage)
    return bool1 and bool2


def InMapSelection(curImage) -> bool:
    return LocateInImage(name, curImage) and LocateInImage(banner, curImage)


def InTowerSelection(curImage) -> bool:
    return LocateInImage(glue_gunner, curImage) and LocateInImage(
        fight_btn, curImage
    )


def InGameActual(curImage) -> bool:
    return (
        LocateInImage(surrender, curImage)
        or LocateInImage(chat, curImage)
        or LocateInImage(eco, curImage)
    )


def HasLost(curImage) -> bool:
    return LocateInImage(okay_btn_menu, curImage)


def DragTower(tower, targetPos):
    pyautogui.click(x=tower[0], y=tower[1])
    pyautogui.dragTo(
        x=targetPos[0], y=targetPos[1], button="left", duration=0.5
    )


def on_press(key):
    global break_program
    if key == pynput.keyboard.Key.page_up:
        print("ending Programm")
        break_program = True
        return False


def isChestScreen(curImage) -> bool:
    return (
        LocateInImage(bigChest, curImage)
        or LocateInImage(smallChest, curImage)
        or LocateInImage(mightyChest, curImage)
    )


def isErrorScreen(curImage) -> bool:
    return LocateInImage(connError, curImage)


def handleError(curImage):
    pos = LocateInImage(okay_btn, curImage, getPos=True)
    if not (type(pos) == bool):
        pyautogui.click(x=pos[0], y=pos[1])


def GetMapInfo(curImage, Map2Check) -> bool:
    return LocateInImage(Map2Check, curImage)


def BuildTowers(curMap, isLeft, index) -> None:
    if isLeft:
        TowerPosList = {
            "hero": [150, 130],
            "first": [150, 240],
            "second": [150, 320],
            "third": [150, 400],
        }
        towerList = towerposLeft[curMap]
    else:
        towerList = towerposRight[curMap]
        TowerPosList = {
            "hero": [1775, 130],
            "first": [1775, 240],
            "second": [1775, 320],
            "third": [1775, 400],
        }
    for pos in towerList:
        DragTower(tower=TowerPosList[index], targetPos=pos)
        time.sleep(1.5)
        file = "captures/0.png"
        Takescreenshot(file)
        time.sleep(0.1)
        Image = getImg(file)
        if HasLost(Image):
            break


def FindAreas(curMap, otherMap, leftside: bool = False):
    # Findet weiß markierte Buildareas
    # TODO wasserareas markieren
    middle = pyautogui.size()[0] / 2
    top = 60
    bottom = 1020
    if leftside:
        left = 200
        right = middle
    else:
        left = middle
        right = 1720

    font = cv2.FONT_HERSHEY_COMPLEX
    _, threshold = cv2.threshold(otherMap, 254, 255, cv2.THRESH_BINARY)

    # Detecting contours in image.
    contours, hierarchy = cv2.findContours(
        threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )

    # Going through every contours found in the image.
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if not (area < 1000):
            for part in cnt[0]:
                if (
                    np.all(part[0] > left)
                    and np.all(part[0] < right)
                    and np.all(part[1] > top)
                    and np.all(part[1] < bottom)
                ):
                    approx = cv2.approxPolyDP(
                        cnt, 0.009 * cv2.arcLength(cnt, True), True
                    )
                    # draws boundary of contours.
                    cv2.drawContours(curMap, [approx], 0, (0, 0, 255), 5)
                    # print(np.reshape(approx,(-1,2)))
                    # Used to flatted the array containing
                    # the co-ordinates of the vertices.
                    n = approx.ravel()
                    i = 0

                    for j in n:
                        if i % 2 == 0:
                            x = n[i]
                            y = n[i + 1]

                            # String containing the co-ordinates.
                            string = str(x) + " " + str(y)

                            # text on remaining co-ordinates.
                            cv2.putText(
                                curMap, string, (x, y), font, 0.5, (0, 255, 0)
                            )
                        i = i + 1

    # Showing the final image.
    cv2.imshow("image2", curMap)

    # Exiting the window if 'q' is pressed on the keyboard.
    if cv2.waitKey(0) & 0xFF == ord("q"):
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main_menu = getImg("main_menu.png")
    game_left = getImg("ingame_left.png")
    map_selection = getImg("map_selection.png")
    tower_select = getImg("tower_select.png")
    defeat = getImg("endscreen.png")
    surrendermenu = getImg("surrender_menu.png")
    right = getImg("map_selection_right.png")
    chestScreen = getImg("ChestScreen.png")
    chestScreen2 = getImg("ChestScreen_2.png")

    toMainMenu = getImg("to_main_menu_btn.png")
    discard_btn = getImg("discard.png")
    fight_btn = getImg("kampf.png")
    name = getImg("name.png")
    menu_fight_btn = getImg("mm_kampf.png")
    banner = getImg("banner.png")
    surrender = getImg("surrender.png")
    okay_btn = getImg("okay.png")
    accept_btn = getImg("acceptance.png")
    ready_btn = getImg("ready.png")
    glue_gunner = getImg("glue.png")
    eco = getImg("eco.png")
    chat = getImg("chat.png")
    connError = getImg("Error.png")
    okay_btn_menu = getImg("okay_defeat.png")
    smallChest = getImg("smallChest.png")
    bigChest = getImg("bigChest.png")
    mightyChest = getImg("mightyChest.png")

    # mapnames
    glade = getImg("maps/glade.png")
    docks = getImg("maps/docks.png")
    castle = getImg("maps/castle.png")
    dino = getImg("maps/dino.png")
    garden = getImg("maps/garden.png")
    wall = getImg("maps/wall.png")
    sand = getImg("maps/sand.png")
    mayan = getImg("maps/mayan.png")
    mines = getImg("maps/bloontonium.png")
    basalt = getImg("maps/basalt.png")
    koru = getImg("maps/koru.png")

    # ingame maps
    castleTest = getImg("maps_ingame/castle_ingame.png")
    gladeTest = getImg("maps_ingame/glade_ingame.png")

    # buildareaMaps
    docksBuild = getImg("buildareas/docks.png")
    gladeBuild = getImg("buildareas/glade.png")
    castleBuild = getImg("buildareas/castle.png")
    dinoBuild = getImg("buildareas/dino.png")
    gardenBuild = getImg("buildareas/garden.png")
    wallBuild = getImg("buildareas/wall.png")
    sandBuild = getImg("buildareas/sands.png")
    mayanBuild = getImg("buildareas/mayan.png")
    minesBuild = getImg("buildareas/bloontonium.png")
    basaltBuild = getImg("buildareas/basalt.png")
    koruBuild = getImg("buildareas/koru.png")

    maps = {
        "glade": glade,
        "dino": dino,
        "castle": castle,
        "garden": garden,
        "wall": wall,
        "koru": koru,
        "mayan": mayan,
        "sand": sand,
        "mines": mines,
        "docks": docks,
        "basalt": basalt,
    }
    mapBuilds = {
        "glade": gladeBuild,
        "dino": dinoBuild,
        "castle": castleBuild,
        "garden": gardenBuild,
        "wall": wallBuild,
        "koru": koruBuild,
        "mayan": mayanBuild,
        "sand": sandBuild,
        "mines": minesBuild,
        "docks": docksBuild,
        "basalt": basaltBuild,
    }
    towerposRight = {
        "glade": [
            [1425, 400],
            [1500, 430],
            [1400, 530],
            [1525, 560],
            [1400, 670],
        ],
        "dino": [
            [1255, 690],
            [1400, 720],
            [1400, 800],
            [1160, 265],
            [1175, 450],
        ],
        "castle": [
            [1275, 640],
            [1275, 555],
            [1425, 575],
            [1440, 690],
            [1400, 785],
        ],  # 3 zu hoch
        "garden": [
            [1450, 300],
            [1400, 375],
            [1275, 530],
            [1400, 740],
            [1450, 815],
        ],  # 3 zu hoch
        "wall": [
            [1200, 645],
            [1280, 700],
            [1315, 645],
            [1400, 700],
            [1450, 645],
        ],  # 1,3,5 zu hoch
        "koru": [
            [1380, 570],
            [1300, 590],
            [1540, 485],
            [1535, 580],
            [1500, 700],
        ],
        "mayan": [
            [1515, 335],
            [1375, 490],
            [1300, 535],
            [1125, 685],
            [1350, 325],
        ],  # 2,#4
        "sand": [
            [1350, 670],
            [1440, 540],
            [1275, 540],
            [1220, 600],
            [1475, 600],
        ],
        "mines": [
            [1500, 815],
            [1400, 770],
            [1275, 700],
            [1250, 535],
            [1520, 655],
        ],
        "docks": [
            [1585, 270],
            [1585, 345],
            [1585, 475],
            [1075, 400],
            [1075, 450],
        ],  # 4 too high
        "basalt": [
            [1220, 890],
            [1475, 890],
            [1350, 890],
            [1475, 225],
            [1220, 235],
        ],
    }  # 1,#2,#3 zu hoch?
    towerposLeft = {
        "glade": [
            [670, 430],
            [740, 475],
            [660, 535],
            [720, 555],
            [640, 675],
        ],  # 1,#2 zu hoch ?
        "dino": [[660, 690], [515, 720], [520, 825], [720, 260], [775, 400]],
        "castle": [
            [510, 555],
            [505, 675],
            [645, 645],
            [625, 500],
            [540, 430],
        ],  # komplett falsch
        "garden": [
            [465, 300],
            [515, 375],
            [665, 530],
            [475, 750],
            [525, 820],
        ],  # 3 zu hoch
        "wall": [[655, 645], [600, 700], [550, 645], [475, 700], [415, 645]],
        "koru": [[600, 575], [525, 535], [760, 625], [780, 500], [645, 705]],
        "mayan": [[415, 350], [545, 490], [630, 545], [775, 685], [555, 335]],
        "sand": [
            [570, 670],
            [665, 535],
            [470, 540],
            [440, 590],
            [690, 595],
        ],  # 3 zu eng1 ?
        "mines": [[400, 830], [550, 770], [680, 690], [675, 525], [400, 650]],
        "docks": [[335, 255], [340, 335], [335, 470], [850, 400], [850, 450]],
        "basalt": [[435, 890], [550, 890], [675, 890], [450, 240], [700, 240]],
    }

    places2cropLeft = {
        "hero": [[120, 60], [180, 160]],
        "first": [[120, 185], [180, 245]],
        "second": [[120, 265], [180, 325]],
        "third": [[120, 350], [180, 410]],
    }
    places2cropRight = {
        "hero": [[1740, 60], [1810, 160]],
        "first": [[1745, 185], [1800, 245]],
        "second": [[1745, 265], [1805, 325]],
        "third": [[1745, 350], [1805, 410]],
    }
    ## Towerposition
    break_program = False
    ## cropping images
    # print("Shape of the image", castleTest.shape)
    # for key, pos in places2cropLeft.items():
    #     print([pos[0][1],pos[1][0],pos[0][1],pos[1][1]])
    #     crop = gladeTest[pos[0][1]:pos[1][1],pos[0][0]:pos[1][0]]
    #     cv2.imshow('original', gladeTest)
    #     cv2.imshow('cropped', crop)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()

    size = pyautogui.size()
    index = 0
    time.sleep(2)
    for cmap in mapBuilds.values():
        FindAreas(cmap, cv2.cvtColor(cmap, cv2.COLOR_BGR2GRAY), False)
        FindAreas(cmap, cv2.cvtColor(cmap, cv2.COLOR_BGR2GRAY), True)

    searching = False
    ingame = False
    leftSide = True
    inTowerSelect = False
    defeated = False
    inMain = True
    builtTowers = 0
    round = 0
    builtTowers = 0
    currentMap = None
    isInGame = False
    print("Ready")
    keyboard = pynput.keyboard.Controller()
    mouse = pynput.mouse.Controller()
    leftMouse = pynput.mouse.Button.left

    # ice_tower = Tower("ice_monkey",[0,1,2])

    # ice_tower.Try2Upgrade()

    # pyautogui.press("W")
    # keyboard.tap("w")

    # with pynput.keyboard.Listener(on_press=on_press) as listener:
    #     while break_program == False:
    #         time.sleep(0.5)

    #         file = "captures/0.png"
    #         Takescreenshot(file)
    #         time.sleep(0.1)
    #         Image = getImg(file)
    #         if inMain:
    #             #in Mainmenu
    #             if isChestScreen(Image):
    #                 #discard Chest
    #                 print("Discarding Chest")
    #                 pos = LocateInImage(discard_btn,Image,False,True)
    #                 if(not(type(pos) == bool)):
    #                     pyautogui.click(x=pos[0],y=pos[1])
    #                 time.sleep(1)
    #                 pos = LocateInImage(toMainMenu,Image,False,True)
    #                 if(not(type(pos) == bool)):
    #                     pyautogui.click(x=pos[0],y=pos[1])
    #                 time.sleep(1)

    #             if InMainMenu(Image):
    #                 round += 1
    #                 print(f"---------{round}-----------")
    #                 print("Suche nach Match")
    #                 pos = LocateInImage(fight_btn,Image,False,True)
    #                 if(not(type(pos) == bool)):
    #                     pyautogui.click(x=pos[0],y=pos[1])
    #                 time.sleep(1)
    #                 searching = True
    #                 inMain = False
    #         if searching:
    #             #searching for a Match
    #             if isErrorScreen(Image):
    #                 handleError(Image)
    #                 inMain = True
    #                 searching = False
    #             if InMapSelection(Image):
    #                 #found a match
    #                 print("Mapauswahl")
    #                 currentMap = None
    #                 pos = LocateInImage(name,Image,getPos = True)
    #                 if pos[0] < size[0]/2:
    #                     leftSide = True
    #                     print("Links")
    #                 else :
    #                     leftSide = False
    #                     print("Rechts")
    #                 searching = False
    #                 time.sleep(1)
    #                 pos = LocateInImage(ready_btn,Image,getPos = True)
    #                 if(not(type(pos) == bool)):
    #                     pyautogui.click(x=pos[0],y=pos[1])
    #                 inTowerSelect = True

    #         if inTowerSelect:
    #             for map_name, map in maps.items():
    #                     if(GetMapInfo(Image,map)):
    #                         currentMap = map_name
    #                         print(f"playing on {currentMap}",)
    #             if isErrorScreen(Image):
    #                 handleError(Image)
    #                 inMain = True
    #                 inTowerSelect = False
    #             if InTowerSelection(Image):
    #                 pos = LocateInImage(fight_btn,Image,getPos = True)
    #                 if(not(type(pos) == bool)):
    #                     pyautogui.click(x=pos[0],y=pos[1])
    #                 inTowerSelect = False
    #                 print("Türme ausgewählt")
    #                 time.sleep(1)
    #             if isErrorScreen(Image):
    #                 handleError(Image)
    #                 inMain = True
    #             else:
    #                 ingame = True

    #         if ingame:
    #             if isErrorScreen(Image):
    #                 handleError(Image)
    #                 inMain = True
    #                 ingame = False

    #             #im Spiel baue Türme
    #             if InGameActual(Image) and currentMap is None:
    #                     print("BUILDING TOWERS")
    #                     ninja = 'second'
    #                     ice = 'third'
    #                     obyn = 'hero'
    #                     Try2PlaceTower(tower=ninja,isLeft = leftSide)
    #                     time.sleep(4)
    #                     Try2PlaceTower(tower=obyn,isLeft = leftSide)

    #             if InGameActual(Image) and not(currentMap is None):
    #                 isInGame = True
    #                 ingame = False

    #         if isInGame:
    #             tower2build = ["hero","first","second","third"]
    #             BuildTowers(currentMap,isLeft = leftSide,index = tower2build[builtTowers])
    #             time.sleep(4)
    #             builtTowers += 1
    #             print(f"Built {builtTowers} Tower.")
    #             if HasLost(Image):
    #                 print("zurück zum Hauptmenu")
    #                 pos = LocateInImage(okay_btn_menu,Image,getPos=True)
    #                 if(not(type(pos) == bool)):
    #                     builtTowers = 0
    #                     pyautogui.click(x=pos[0],y=pos[1])
    #                     inMain = True
    #                     defeated = False
    #                     time.sleep(3)
    #             else:
    #                 if builtTowers > len(tower2build)-1:
    #                     isInGame=False
    #                     #TODO goto upgrading
    #                     defeated=True
    #                     builtTowers = 0
    #         if defeated:
    #             if HasLost(Image):
    #                 print("zurück zum Hauptmenu")
    #                 if(not(type(pos) == bool)):
    #                     pos = LocateInImage(okay_btn_menu,Image,getPos=True)
    #                 pyautogui.click(x=pos[0],y=pos[1])
    #                 inMain = True
    #                 defeated = False
    #                 time.sleep(3)
    #     listener.join()

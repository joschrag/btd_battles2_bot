import cv2
import time
import numpy as np
import pyautogui
import pynput
from typing import Union
import string
from collections import Counter
import matplotlib as mpl
import matplotlib.pyplot as plt

# import keyboardUtils.hwInput as kbd
import toml

##### TODO's ######
# 1. Placement                   done
# 1.5    fix placementchecks
# 2. Placement verification      done
# 2.5 PLacment + Upgrades in Waves
# 2.5+ Check for loseScreen
# 3. Upgrades
# 4. ChestManager
# 5. LoginScreenHandler


class Bot:
    def __init__(
        self,
        loadout: dict,
        buttons: dict,
        heropic: dict,
        maps: dict,
        towers: dict,
        buildstage,
        casualMode: bool,
    ) -> None:
        self.loadout = loadout
        self.buttons = buttons
        self.heropic = heropic
        self.maps = maps
        self.towers = towers
        self.statedict = {
            "main": False,
            "search": False,
            "hero": False,
            "tower": False,
            "ingame": False,
            "aftergame": False,
            "chest": False,
            "error": False,
        }
        self.loadoutPos = [[490, 660], [360, 800], [490, 800]]
        self.isLeft = False
        self.buildstage = buildstage
        self.casualMode = casualMode

    def GetScreenState(self) -> dict:
        self.img = PM.PreprocessScreenshot()
        self.statedict["main"] = (
            PM.LocateInImage(self.buttons["casual"], self.img, threshold=0.7)
            or PM.LocateInImage(self.buttons["ranked"], self.img, threshold=0.7)
        ) and PM.LocateInImage(
            self.buttons["menu_fight_btn"], self.img, threshold=0.7
        )
        self.statedict["hero"] = (
            PM.LocateInImage(self.heropic["ocean"][1], self.img, threshold=0.8)
            and PM.LocateInImage(
                self.heropic["gwen"][1], self.img, threshold=0.8
            )
            and PM.LocateInImage(
                self.heropic["quincy"][1], self.img, threshold=0.8
            )
        )
        self.statedict["tower"] = PM.LocateInImage(
            self.buttons["glue_gunner"], self.img, threshold=0.7
        ) and PM.LocateInImage(
            self.buttons["fight_btn2"], self.img, threshold=0.7
        )
        self.statedict["ingame"] = (
            PM.LocateInImage(self.buttons["surrender"], self.img, threshold=0.7)
            or PM.LocateInImage(self.buttons["eco"], self.img, threshold=0.7)
            or PM.LocateInImage(self.buttons["chat"], self.img, threshold=0.7)
        )
        self.statedict["error"] = PM.LocateInImage(
            self.buttons["connError"], self.img, threshold=0.7
        ) or PM.LocateInImage(
            self.buttons["connError2"], self.img, threshold=0.7
        )
        self.statedict["chest"] = (
            PM.LocateInImage(
                self.buttons["smallChest"], self.img, threshold=0.7
            )
            or PM.LocateInImage(
                self.buttons["bigChest"], self.img, threshold=0.7
            )
            or PM.LocateInImage(
                self.buttons["mightyChest"], self.img, threshold=0.7
            )
        )
        self.statedict["aftergame"] = PM.LocateInImage(
            self.buttons["okay_btn_menu"], self.img, threshold=0.7
        )
        return self.statedict

    def ActOnState(self) -> None:
        for key, val in self.statedict.items():
            if val:
                self.TakeAction(state=key)

    def SearchMatch(self) -> None:
        self.img = PM.PreprocessScreenshot()
        if self.casualMode == True:
            btn = "casual"
        else:
            btn = "ranked"
        pos = PM.LocateInImage(self.buttons[btn], self.img, getPos=True)
        if type(pos) is np.ndarray:
            pyautogui.click(pos[0], pos[1])

    def GetCurHero(self) -> str:
        selectedHero = None
        height = []
        self.img = PM.PreprocessScreenshot()
        for hero, pic in self.heropic.items():
            pos = PM.LocateInImage(pic[1], self.img, getPos=True)
            height.append(pos[1])
            # print(f"{height=}")
        idx = np.argmin(height)
        for key, value in self.heropic.items():
            if idx == value[0]:
                selectedHero = key
        print(f"Selected Hero is {selectedHero}!")
        return selectedHero

    def PickHero(self, hero) -> None:
        self.img = PM.PreprocessScreenshot()
        img = self.heropic[hero][1]
        pos = PM.LocateInImage(img, self.img, getPos=True)
        if type(pos) is np.ndarray:
            pyautogui.click(pos[0], pos[1])
        return

    def ConfirmLoadout(self) -> None:
        print("Confirming Loadout")
        self.img = PM.PreprocessScreenshot()
        pos = PM.LocateInImage(self.buttons["fight_btn"], self.img, getPos=True)
        if type(pos) is np.ndarray:
            pyautogui.click(pos[0], pos[1])
        return

    def GetCurLoadout(self) -> list:
        # Schneidet den Bildbereich aus und geht jeden Turm durch, wenn dieser erkannt wird füge diesen zum loadout hinzu.
        self.img = PM.PreprocessScreenshot()
        crop = self.img[600:900, 300:550]
        liste = []
        xlist = []
        ylist = []
        for tower in self.towers.values():
            if not (tower.IsHero()):
                if PM.LocateInImage(tower.GetImg(), crop):
                    pos = PM.LocateInImage(tower.GetImg(), crop, getPos=True)
                    xlist.append(pos[0])
                    ylist.append(pos[1])
                    liste.append(tower.GetName())
        minY = np.argmin(ylist)
        minX = np.argmin(xlist)
        firstTower = liste[minY]
        secondTower = liste[minX]
        thirdTower = liste[3 - (minX + minY)]
        loadout = [firstTower, secondTower, thirdTower]
        return loadout

    def ChangeLoadout(self, curLoadout) -> None:
        for idx, tower in enumerate(
            [
                self.loadout["first"],
                self.loadout["second"],
                self.loadout["third"],
            ]
        ):
            #   Click on tower pos -> search new Tower -> click on new Tower
            #   Wenn new Tower zu weit links -> schon ausgewählt -> gehe tower weiter streiche tower pos
            print(tower)
            while True:
                self.img = PM.PreprocessScreenshot()
                if PM.LocateInImage(self.towers[tower].GetImg(), self.img):
                    pos = PM.LocateInImage(
                        self.towers[tower].GetImg(), self.img, getPos=True
                    )
                    if pos[0] > 580:
                        pyautogui.click(pos[0], pos[1])
                        time.sleep(0.2)
                        print(
                            [self.loadoutPos[idx][0], self.loadoutPos[idx][1]]
                        )
                        pyautogui.click(
                            self.loadoutPos[idx][0], self.loadoutPos[idx][1]
                        )
                        break
                    else:
                        break
                else:
                    pyautogui.moveTo(1200, 720)
                    if (
                        PM.LocateInImage(self.towers["ice"].GetImg(), self.img)
                        and PM.LocateInImage(
                            self.towers["dart"].GetImg(), self.img
                        )
                        and PM.LocateInImage(
                            self.towers["boomer"].GetImg(), self.img
                        )
                        and PM.LocateInImage(
                            self.towers["tack"].GetImg(), self.img
                        )
                    ):
                        pyautogui.drag(-500, 0, 0.4, button="left")
                    else:
                        pyautogui.drag(500, 0, 0.4, button="left")
                    time.sleep(1)

        print("Changing Towers")

    def ConfirmMap(self) -> str:
        self.img = PM.PreprocessScreenshot()
        for map_name, map in maps.items():
            if PM.LocateInImage(map, self.img, threshold=0.8):
                currentMap = map_name
                print(f"playing on {currentMap}")

        # TODO ChangeMap
        self.img = PM.PreprocessScreenshot()
        pos = PM.LocateInImage(self.buttons["ready_btn"], self.img, getPos=True)
        if type(pos) is np.ndarray:
            pyautogui.click(pos[0], pos[1])
        return currentMap

    def HandleError(self) -> None:
        self.img = PM.PreprocessScreenshot()
        pos = PM.LocateInImage(self.buttons["okay_btn"], self.img, getPos=True)
        if type(pos) is np.ndarray:
            pyautogui.click(pos[0], pos[1])
        return

    def GetSideInfo(self):
        self.img = PM.PreprocessScreenshot()
        pos = PM.LocateInImage(self.buttons["name"], self.img, getPos=True)
        if type(pos) is np.ndarray:
            pyautogui.click(pos[0], pos[1])
        return pos[0] < 540

    def TakeAction(self, state) -> None:
        if state == "error":
            self.HandleError()
            self.statedict["error"] = False
            return
        if state == "main":
            self.SearchMatch()
            self.statedict["main"] = False
            return
        if state == "hero":
            self.isLeft = self.GetSideInfo()
            print(f"Playing on Leftside: {str(self.isLeft)}")
            self.hero = self.GetCurHero()
            print("Checking Hero")
            if self.hero != self.loadout["hero"]:
                self.PickHero(self.loadout["hero"])
                self.hero = self.loadout["hero"]
            print(f"Selected {self.hero}")
            self.curMap = self.ConfirmMap()
            self.statedict["hero"] = False
            return
        if state == "tower":
            loadout = self.GetCurLoadout()
            if not (
                Counter(loadout)
                == Counter(
                    [
                        self.loadout["first"],
                        self.loadout["second"],
                        self.loadout["third"],
                    ]
                )
            ):
                self.ChangeLoadout(loadout)
            time.sleep(0.5)
            self.loadout = [self.hero, *self.GetCurLoadout()]
            self.ConfirmLoadout()
            self.statedict["tower"] = False
            return
        if state == "ingame":
            GM.StartGame(
                self.curMap, self.isLeft, self.loadout, self.buildstage
            )
            self.statedict["ingame"] = False
            return
        if state == "aftergame":
            self.GoToMain()
            self.statedict["aftergame"] = False
            return
        if state == "chest":
            curChest = self.detectChest()
            self.OpenChest(curChest)
            self.statedict["chest"] = False
            return

    def SetLoadout(self, loadout: list) -> None:
        self.loadout = loadout


class Tower:
    def __init__(
        self,
        name: str,
        img,
        price: int,
        uprades,
        footprint,
        isWater: bool = False,
        hero: bool = False,
    ) -> None:
        self.name = name
        self.price = price
        self.img = img
        self.isWater = isWater
        self.footprint = footprint
        self.ugrades = uprades
        self.hero = hero

    def GetInfo(self) -> None:
        s = "a" if self.hero else "not a"
        print(
            f"Name: {self.name}, Price {self.price}, footprint: {self.footprint}. Im {s} hero"
        )

    def GetName(self) -> str:
        return self.name

    def GetPrice(self) -> int:
        return self.price

    def GetImg(self) -> np.ndarray:
        return self.img

    def IsHero(self) -> bool:
        return self.hero


class GameManager:
    def __init__(self, towerDict, buttons) -> None:
        self.money = 650
        self.twKeys = ["q", "w", "e", "r"]
        self.upKeys = [",", ".", "-"]
        self.towerDict = towerDict
        self.buttons = buttons

    def StartGame(self, map, isLeft, loadout, buildstage):
        print("Game started")
        self.map = map
        self.isLeft = isLeft
        self.loadout = loadout
        self.buildstage = buildstage
        self.Play()

    def Play(self):
        towers2build = [
            1,
            0,
            3,
            2,
            2,
            2,
            3,
            3,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            2,
            2,
            2,
            2,
            3,
            3,
            3,
            3,
        ]
        index = 0
        print(self.loadout)
        # Funktioniert nicht :(
        with pynput.keyboard.Listener(on_press=on_press) as listener:
            while break_program == False:
                self.img = PM.PreprocessScreenshot()
                if PM.LocateInImage(
                    self.buttons["okay_btn_menu"], self.img, threshold=0.7
                ):
                    return
                self.money = self.GetMoney()
                if (
                    self.money
                    >= self.towerDict[self.loadout[towers2build[index]]].price
                ):
                    self.SearchTowerSpot(
                        self.towerDict[self.loadout[towers2build[index]]]
                    )
                    print("---------------------")
                    index = index + 1
                    time.sleep(1)

    def GetMoney(self) -> int:
        image = PM.PreprocessScreenshot()
        # cv2.imshow("",image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        crop = image[35:65, 780:910]
        valArray = []
        for key, num in numbers.items():
            if PM.LocateInImage(num, crop, threshold=0.75):
                # print(f"{key=}")
                pos = PM.LocateInImage(
                    num, crop, multi=True, threshold=0.75, getPos=True
                )
                idx = 0
                # print(f"{pos=}")
                while True:
                    p1 = pos[idx]
                    xDiff = np.abs(np.add(pos[:, 0], -p1[0])) + np.abs(
                        np.add(pos[:, 1], -p1[1])
                    )
                    pos = np.delete(
                        pos, np.where((xDiff < 5) & (xDiff != 0)), axis=0
                    )
                    idx += 1
                    if idx > pos.shape[0] - 1:
                        break
                # print(f"{pos=}")
                for i in range(pos.shape[0]):
                    valArray.append([key, pos[i, 0]])
                # print(f"{valArray=}")
        valArray.sort(key=lambda x: x[1], reverse=True)
        # print(f"{valArray=}")
        summe = 0
        for i, num in enumerate(valArray):
            summe += 10**i * num[0]
        self.money = summe
        print(f"Money: {self.money}")
        return self.money

    def GetCurrentBuildMap(
        self, curMap: str, isLeft: bool, index: int
    ) -> np.ndarray:
        side = "left" if isLeft else "right"
        return self.buildstage[curMap + "Build"][side][index]

    def SearchTowerSpot(self, tower: Tower):
        print(f"Building {tower.GetName()}")
        curStage = self.GetCurrentBuildMap(self.map, self.isLeft, 2)
        if self.isLeft:
            self.offsetX = 200
        else:
            self.offsetX = 960
        self.offsetY = 80
        i = 1
        with pynput.keyboard.Listener(on_press=on_press) as listener:
            offsetX = int(np.round(tower.footprint[0] / 2))
            offsetY = int(np.round(tower.footprint[1] / 2))
            diagoffset = int(np.round(tower.footprint[2] / 2))
            for y in range(0, 961, 10):
                for x in range(0, 761, 10):
                    if break_program == False:
                        newY = y + 25 * (np.fmod(i, 2))
                        print(f"{x},{y}")
                        if (
                            newY + offsetY < 961
                            and 0 < newY - offsetY
                            and 0 < x - offsetX
                            and x + offsetX < 761
                        ):
                            if (
                                curStage[newY + offsetY][x] == 1
                                and curStage[newY - offsetY][x] == 1
                                and curStage[newY][x - offsetX] == 1
                                and curStage[newY][x + offsetX] == 1
                                and curStage[newY + diagoffset][x + diagoffset]
                                == 1
                                and curStage[newY - diagoffset][x - diagoffset]
                                == 1
                                and curStage[newY + diagoffset][x - diagoffset]
                                == 1
                                and curStage[newY - diagoffset][x + offsetX]
                                == 1
                            ):
                                print(f"{x},{y}")
                                if self.BuildTower(
                                    tower,
                                    self.loadout.index(tower.GetName()),
                                    np.array(
                                        [x + self.offsetX, y + self.offsetY]
                                    ),
                                ):
                                    curStage[
                                        newY - offsetY : newY + offsetY,
                                        x - offsetX : x + offsetX,
                                    ] = 0
                                    print("built a Tower")
                                    plt.imshow(curStage)
                                    plt.show()
                                    time.sleep(0.2)
                                    return
                                else:
                                    kbd.Press("esc")
                                    time.sleep(0.2)
                    i = i + 1

    def BuildTower(
        self, tower: Tower, indexLoadout: int, pos: np.ndarray
    ) -> bool:
        pyautogui.moveTo(pos[0], pos[1])
        time.sleep(0.5)
        kbd.Press(self.twKeys[indexLoadout])
        time.sleep(0.5)
        pyautogui.leftClick(pos[0], pos[1])
        time.sleep(0.5)
        ##Confirm Tower is placed
        pyautogui.leftClick(pos[0], pos[1])
        self.img = PM.PreprocessScreenshot()
        if PM.LocateInImage(
            buttons["info"], self.img, debug=True
        ) or PM.LocateInImage(buttons["sell"], self.img, debug=True):
            print(f"Built Tower: {tower.GetName()}")
            return True

        return False

    def UpgradeTower(self, tower: Tower, pos: np.ndarray, upPath) -> bool:
        time.sleep(0.5)
        pyautogui.leftClick(pos[0], pos[1])
        time.sleep(0.5)
        kbd.Press(self.upKeys["upPath"])
        self.img = PM.PreprocessScreenshot()
        if PM.LocateInImage(
            buttons["info"], self.img, debug=True
        ) or PM.LocateInImage(buttons["sell"], self.img, debug=True):
            print(f"Upgraded Tower: {tower.GetName()}")
            return True

        return False


def on_press(key):
    global break_program
    if key == pynput.keyboard.Key.page_up:
        print("ending Programm")
        break_program = True
        return False


if __name__ == "__main__":
    IM = ImportManager("C:/Users/Jonas/Pictures/Bloons_py/")
    PM = PictureManager("C:/Users/Jonas/Pictures/Bloons_py/")

    small = [60, 50, 40]  # side+top 60 diag 39
    medium = [70, 60, 45]  # side 70 top 60 diag 45
    large = [80, 70, 55]  # 80 70 55
    xlarge = [120, 110, 80]

    testImages = [
        "main_menu",
        "game_left",
        "map_selection",
        "tower_select",
        "defeat",
        "surrendermenu",
        "right",
        "chestScreen",
        "chestScreen2",
        "hero1",
        "hero2",
    ]
    buttons = [
        "toMainMenu",
        "discard_btn",
        "fight_btn",
        "name",
        "menu_fight_btn",
        "banner",
        "surrender",
        "okay_btn",
        "accept_btn",
        "ready_btn",
        "glue_gunner",
        "eco",
        "chat",
        "connError",
        "okay_btn_menu",
        "smallChest",
        "bigChest",
        "mightyChest",
        "connError2",
        "fight_btn2",
        "info",
        "sell",
        "casual",
        "ranked",
    ]
    mapImages = [
        "glade",
        "docks",
        "castle",
        "dino",
        "garden",
        "wall",
        "sand",
        "mayan",
        "mines",
        "basalt",
        "koru",
    ]
    mapBuilds = [
        "gladeBuild",
        "dinoBuild",
        "castleBuild",
        "gardenBuild",
        "wallBuild",
        "koruBuild",
        "mayanBuild",
        "sandBuild",
        "minesBuild",
        "docksBuild",
        "basaltBuild",
    ]

    testImagesPaths = [
        "main_menu.png",
        "ingame_left.png",
        "map_selection.png",
        "tower_select.png",
        "endscreen.png",
        "surrender_menu.png",
        "map_selection_right.png",
        "ChestScreen.png",
        "ChestScreen_2.png",
        "towers/heros.png",
        "towers/heros2.png",
    ]
    buttonsPaths = [
        "to_main_menu_btn.png",
        "discard.png",
        "kampf.png",
        "name.png",
        "mm_kampf.png",
        "banner.png",
        "surrender.png",
        "okay.png",
        "acceptance.png",
        "ready.png",
        "glue.png",
        "eco.png",
        "chat.png",
        "Error.png",
        "okay_defeat.png",
        "smallChest.png",
        "bigChest.png",
        "mightyChest.png",
        "ConnError2.png",
        "fight_btn2.png",
        "info.png",
        "sell.png",
        "casual.png",
        "Rangliste.png",
    ]
    mapImagesPaths = [
        "maps/glade.png",
        "maps/docks.png",
        "maps/castle.png",
        "maps/dino.png",
        "maps/garden.png",
        "maps/wall.png",
        "maps/sand.png",
        "maps/mayan.png",
        "maps/bloontonium.png",
        "maps/basalt.png",
        "maps/koru.png",
    ]
    mapBuildsPaths = [
        "buildareas/glade.png",
        "buildareas/dino.png",
        "buildareas/castle.png",
        "buildareas/garden.png",
        "buildareas/wall.png",
        "buildareas/koru.png",
        "buildareas/mayan.png",
        "buildareas/sands.png",
        "buildareas/bloontonium.png",
        "buildareas/docks.png",
        "buildareas/basalt.png",
    ]
    numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    numberPaths = [
        "numbers/zero.png",
        "numbers/one.png",
        "numbers/two.png",
        "numbers/three.png",
        "numbers/four.png",
        "numbers/five.png",
        "numbers/six.png",
        "numbers/seven.png",
        "numbers/eight.png",
        "numbers/nine.png",
    ]

    heroes = [
        "quincy",
        "gwen",
        "obyn",
        "striker",
        "cyber",
        "science",
        "ocean",
        "biker",
    ]
    heroesPath = [
        "heros/quincy.png",
        "heros/gwen.png",
        "heros/obyn.png",
        "heros/jones.png",
        "heros/cyber.png",
        "heros/science.png",
        "heros/ocean.png",
        "heros/biker.png",
    ]
    heroPrices = [500, 900, 650, 750, 500, 900, 650, 750]
    towerList = [
        "dart",
        "boomer",
        "ice",
        "tack",
        "bomb",
        "glue",
        "heli",
        "ace",
        "sub",
        "bucc",
        "sniper",
        "mortar",
        "dartling",
        "ninja",
        "alch",
        "wiz",
        "super",
        "druid",
        "farm",
        "village",
        "spike",
        "engi",
    ]
    waterList = [
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        True,
        True,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
    ]
    towerPath = [
        "towers/dart.png",
        "towers/boomer.png",
        "towers/ice.png",
        "towers/tack.png",
        "towers/bomb.png",
        "towers/glue.png",
        "towers/heli.png",
        "towers/ace.png",
        "towers/sub.png",
        "towers/bucc.png",
        "towers/sniper.png",
        "towers/mortar.png",
        "towers/dartling.png",
        "towers/ninja.png",
        "towers/alch.png",
        "towers/wiz.png",
        "towers/super.png",
        "towers/druid.png",
        "towers/farm.png",
        "towers/village.png",
        "towers/spike.png",
        "towers/engi.png",
    ]
    towerPrices = [
        200,
        235,
        500,
        280,
        600,
        200,
        1100,
        800,
        325,
        500,
        350,
        750,
        750,
        500,
        550,
        400,
        2300,
        425,
        1100,
        800,
        1200,
        450,
    ]
    towerFootprint = [
        small,
        medium,
        small,
        small,
        medium,
        medium,
        xlarge,
        xlarge,
        medium,
        large,
        small,
        xlarge,
        large,
        small,
        small,
        medium,
        medium,
        medium,
        xlarge,
        xlarge,
        large,
        medium,
    ]
    buildstage = {
        "gladeBuild": {
            "left": np.array([], dtype=int),
            "right": np.array([], dtype=int),
        },
        "dinoBuild": {
            "left": np.array([], dtype=int),
            "right": np.array([], dtype=int),
        },
        "castleBuild": {
            "left": np.array([], dtype=int),
            "right": np.array([], dtype=int),
        },
        "gardenBuild": {
            "left": np.array([], dtype=int),
            "right": np.array([], dtype=int),
        },
        "wallBuild": {
            "left": np.array([], dtype=int),
            "right": np.array([], dtype=int),
        },
        "koruBuild": {
            "left": np.array([], dtype=int),
            "right": np.array([], dtype=int),
        },
        "mayanBuild": {
            "left": np.array([], dtype=int),
            "right": np.array([], dtype=int),
        },
        "sandBuild": {
            "left": np.array([], dtype=int),
            "right": np.array([], dtype=int),
        },
        "minesBuild": {
            "left": np.array([], dtype=int),
            "right": np.array([], dtype=int),
        },
        "docksBuild": {
            "left": np.array([], dtype=int),
            "right": np.array([], dtype=int),
        },
        "basaltBuild": {
            "left": np.array([], dtype=int),
            "right": np.array([], dtype=int),
        },
    }
    # print(buildstage.keys())

    tests = IM.GetMultImages(testImagesPaths, testImages)
    buttons = IM.GetMultImages(buttonsPaths, buttons)
    maps = IM.GetMultImages(mapImagesPaths, mapImages)
    mapBuilds = IM.GetMultImages(mapBuildsPaths, mapBuilds)
    heroPics = IM.GetMultImages(heroesPath, heroes, numbered=True)
    towerPics = IM.GetMultImages(towerPath, towerList)
    numbers = IM.GetMultImages(numberPaths, numbers)
    loadout = {
        "hero": "biker",
        "first": "dart",
        "second": "farm",
        "third": "ace",
    }
    towerDict = {}
    # Alle Türme als Klasse in dict hinzufügen
    for idx, tower in enumerate(towerList):
        towerDict[tower] = Tower(
            tower,
            towerPics[tower],
            towerPrices[idx],
            [],
            towerFootprint[idx],
            waterList[idx],
            False,
        )

    for idx, hero in enumerate(heroes):
        towerDict[hero] = Tower(
            hero, heroPics[hero], heroPrices[idx], [], [70, 60, 45], False, True
        )
    GM = GameManager(towerDict, buttons)

    # for tower in towerDict.values():
    #     tower.GetInfo()

    # IM.ShowImage(heroPics)
    # IM.ShowImage(primaryTowers)
    # IM.ShowImage(militaryTowers)
    # IM.ShowImage(magicTowers)
    # IM.ShowImage(supportTowers)
    # np.fromfile('C:/Users/Jonas/Pictures/Bloons_py/grid/sands.dat')
    # PM.ShowImage(cv2.cvtColor(build,cv2.COLOR_BGR2GRAY))

    ##Importiere die buildarea arrays
    # buildstage = IM.LoadGrid(buildstage)
    c_dict = {"tower": {}}
    print("Imported all")
    for i in range(len(towerList)):
        c_dict["tower"][f"{towerList[i]}"] = {}
        c_dict["tower"][f"{towerList[i]}"]["water"] = waterList[i]
        c_dict["tower"][f"{towerList[i]}"]["cost"] = towerPrices[i]
        c_dict["tower"][f"{towerList[i]}"]["footprint"] = towerFootprint[i]
        c_dict["tower"][f"{towerList[i]}"]["path"] = towerPath[i]

    h_dict = {"hero": {}}
    print("Imported all")
    for i in range(len(heroes)):
        h_dict["hero"][f"{heroes[i]}"] = {}
        h_dict["hero"][f"{heroes[i]}"]["water"] = False
        h_dict["hero"][f"{heroes[i]}"]["cost"] = heroPrices[i]
        h_dict["hero"][f"{heroes[i]}"]["footprint"] = [70, 60, 45]
        h_dict["hero"][f"{heroes[i]}"]["path"] = heroesPath[i]

    with open("resources/tower.toml", "w", encoding="utf8") as f:
        toml.dump(h_dict, f)
        toml.dump(c_dict, f)

    # +time.sleep(1)
#   keyboard.press_and_release("w")
# Bot = Bot(loadout,buttons,heroPics,maps,towerDict,buildstage,False)
# # #PM.ShowImage(buttons)
# loadout2 = Bot.GetCurLoadout()
# Bot.ActOnState()

# GM.GetMoney()
# break_program = False
# print(buildstage["wallBuild"]["left"][1].shape)
# plt.imshow(buildstage["wallBuild"]["right"][3],cmap='binary')
# i=1
# curStage = buildstage["koruBuild"]["right"][3]
# print(curStage.shape)
# for y in range(40,921,5):
#     for x in range(15,666,5):
#         newY = y+25*(np.fmod(i,2))
#         if curStage[newY+15][x] == 1 and curStage[newY-15][x] == 1 and curStage[newY][x-15] == 1 and curStage[newY][x+15] == 1:
#             print(f"{newY=},{x=}")
#             print(curStage[newY-50:newY+50,x-50:x+50].shape)
#             curStage[newY-50:newY+50,x-50:x+50] = 0
#             plt.scatter(x,newY,cmap='Blues',s=2)
#         i=i+1

# plt.imshow(curStage)
# plt.show()
# with pynput.keyboard.Listener(on_press=on_press) as listener:
#     while break_program == False:
#         Bot.GetScreenState()
#         print(Bot.GetScreenState())
#         Bot.ActOnState()
# xP, yP = pyautogui.position()
# curStage = buildstage["mayanBuild"]["right"][-1]
# top  = 80
# left = 960
# print(xP,yP)
# # print(curStage.shape)
# if left < xP-15 and xP+15 < left + 760 and top < yP -15 and yP +15  < top+960:
#     if curStage[yP-top][xP-left] == 1 :
#         print(xP,yP,"ja")

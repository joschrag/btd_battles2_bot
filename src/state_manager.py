from picture_manager import PictureManager
from pathlib import Path
from typing import Optional
class State:
    def __init__(self, name, PM:PictureManager|None = None):
        self.name = name
        self.PM = PM if PM is not None else PictureManager(Path.cwd() / "resources")
    
    def on_enter(self):
        print(f"Entering state: {self.name}")
    
    def on_exit(self):
        print(f"Exiting state: {self.name}")

class VerifyInstall(State):
    def __init__(self):
        super().__init__("VerifyInstall")

    def on_enter(self):
        super().on_enter()
        self.wait_for_finish()

    def wait_for_finish(self):
        pass

class VerifyExternalLoad(State):
    def __init__(self):
        super().__init__("VerifyExternalLoad")

    def on_enter(self):
        super().on_enter()
        self.wait_for_finish()

    def wait_for_finish(self):
        pass

class VerifyPytests(State):
    def __init__(self):
        super().__init__("VerifyPytests")

    def on_enter(self):
        super().on_enter()
        self.wait_for_finish()

    def wait_for_finish(self):
        pass

class StartGame(State):
    def __init__(self):
        super().__init__("StartGame")

    def on_enter(self):
        super().on_enter()
        self.wait_for_finish()

    def wait_for_finish(self):
        pass

class OpenDaily(State):
    def __init__(self):
        super().__init__("OpenDaily")

    def on_enter(self):
        super().on_enter()
        self.wait_for_finish()

    def wait_for_finish(self):
        pass

class CollectDaily(State):
    def __init__(self):
        super().__init__("CollectDaily")

    def on_enter(self):
        super().on_enter()
        self.wait_for_finish()

    def wait_for_finish(self):
        pass

class MainMenu(State):
    def __init__(self):
        super().__init__("MainMenu")

    def on_enter(self):
        super().on_enter()
        self.wait_for_finish()

    def wait_for_finish(self):
        pass

class SearchMatch(State):
    def __init__(self):
        super().__init__("SearchMatch")

    def on_enter(self):
        super().on_enter()
        self.wait_for_finish()

    def wait_for_finish(self):
        pass

class GameError(State):
    def __init__(self):
        super().__init__("GameError")

    def on_enter(self):
        super().on_enter()
        self.wait_for_finish()

    def wait_for_finish(self):
        pass

class HeroSelect(State):
    def __init__(self):
        super().__init__("HeroSelect")

    def on_enter(self):
        super().on_enter()
        self.wait_for_finish()

    def wait_for_finish(self):
        pass

class TowerSelect(State):
    def __init__(self):
        super().__init__("TowerSelect")

    def on_enter(self):
        super().on_enter()
        self.wait_for_finish()

    def wait_for_finish(self):
        pass

class BuildTowers(State):
    def __init__(self):
        super().__init__("BuildTowers")

    def on_enter(self):
        super().on_enter()
        self.wait_for_finish()

    def wait_for_finish(self):
        pass

class CheckMoney(State):
    def __init__(self):
        super().__init__("CheckMoney")

    def on_enter(self):
        super().on_enter()
        self.wait_for_finish()

    def wait_for_finish(self):
        pass

class SendBloons(State):
    def __init__(self):
        super().__init__("SendBloons")

    def on_enter(self):
        super().on_enter()
        self.wait_for_finish()

    def wait_for_finish(self):
        pass

class UpgradeTowers(State):
    def __init__(self):
        super().__init__("UpgradeTowers")

    def on_enter(self):
        super().on_enter()
        self.wait_for_finish()

    def wait_for_finish(self):
        pass

class GameOver(State):
    def __init__(self):
        super().__init__("UpgradeTowers")

    def on_enter(self):
        super().on_enter()
        self.wait_for_finish()

    def wait_for_finish(self):
        pass

class HandleBox(State):
    def __init__(self):
        super().__init__("HandleBox")

    def on_enter(self):
        super().on_enter()
        self.wait_for_finish()

    def wait_for_finish(self):
        pass

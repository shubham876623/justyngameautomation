from PySide6.QtCore import QThread, QTimer, Signal, Slot, QObject

#from pynput.mouse import Controller
import pyautogui
import keyboard
import platform

from bot_pkg import denseEssProcess
from bot_pkg import pollivneachCourseFile
from bot_pkg import basicFunctions
from bot_pkg import RunescapeGame
from bot_pkg import bloods
from bot_pkg import runecrafting
from bot_pkg import seers
from bot_pkg import cooker
from bot_pkg import construction
from bot_pkg import smithing
from bot_pkg import wines
from bot_pkg import ardouge
from bot_pkg import woodcutter


class Bot_r(QObject):

    stopped = Signal(bool)
    start_dense = Signal(bool)
    stop_dense = Signal(bool)
    start_pollivneach = Signal(bool)
    stop_pollivneach = Signal(bool)
    
    send_info_ = Signal(list)

    def __init__(self, parent):
        super(Bot_r, self).__init__()

        self._timer_feedback = QTimer()
        self._timer_feedback.setInterval(100)
        self._timer_feedback.timeout.connect(self._print_feedback)
        self.parent = parent
        
        self._timer_dense_ess_bot = QTimer()
        self._timer_dense_ess_bot.timeout.connect(self._dense_ess_start)
        self.start_dense.connect(self._start_dense_timer)
        self.stop_dense.connect(self._stop_dense_timer)
        self._timer_pollivneach_bot = QTimer()
        self.start_pollivneach.connect(self._start_pollivneach_timer)
        self.stop_pollivneach.connect(self._stop_pollivneach_timer)

        #self._mouse = Controller()
        self._bot_active = False
        self._feedback_active = False
        self._game_started = False
        self._current_phase = 'Base'
        self._default_x = 1366
        self._default_y = 768
        self._seconds_mining = 140
        self._bot_name = str()
        self._step = str()

        self._mark_of_grace = False
        self._box_count = 0

        self._setup = False
        self._wait_color = 0
        self._default_attempts = 0
        self._waiting = False
        self._start_emited = False

    def run(self):
        #global botActive, secondsMining, currentPhase, waiting
        # send to logger
        #label_feedback.config(text="The bot has been activated!\nUse the - key to stop the bot.")
        self._bot_active = True
        self._key_stop = keyboard.add_hotkey('equal', self.disable_bot)

        # bot config
        if self._bot_name == "Dense Ess":
            if self._step == "Find Wizard":
                self._current_phase = "Base"
                self._waiting = False

            elif self._step == "Fast Travel":
                self._current_phase = "Base"
                self._waiting = True

            elif self._step == "Climb Rock":
                self._current_phase = "RockHop"
                self._waiting = False

            elif self._step == "Walk to Runestone":
                self._current_phase = "MinesMap"
                self._waiting = False

            elif self._step == "Mine":
                self._current_phase = "Large Rock"
                self._waiting = False

            elif self._step == "Teleport Home":
                self._current_phase = "Teleport Home"
                self._waiting = False

            elif self._step == "Bank Deposit":
                self._current_phase = "Bank"
                self._waiting = False

            basicFunctions.downOrient()
            self._dense_ess_start()

        elif self._bot_name == "Pollivneach":
            if self._step == 'Base':
                self._current_phase = 'Base'
            elif self._step == 'Barrel':
                self._current_phase = 'Barrel'
            basicFunctions.downOrient()
            basicFunctions.upOrient()
            self._pollivneach_start()

        elif self._bot_name == "Donator Zone":
            self._hunting_start()

        elif self._bot_name == "Bloods":
            self._bloods_start()

        elif self._bot_name == "Runecrafting":
            self._runecrafting_start()

        elif self._bot_name == "Seers":
            self._seers_start()

        elif self._bot_name == "Cooker":
            self._cooker_start()

        elif self._bot_name == "Construction":
            self._construction_start()

        elif self._bot_name == "Smithing":
            self._smithing_start()

        elif self._bot_name == "Wines":
            self._wines_start()

        elif self._bot_name == "Ardouge":
            self._ardouge_start()

        elif self._bot_name == "Woodcutter":
            self._woodcutter_start()

    def disable_bot(self):
        #label_feedback.config(text="The bot has been disabled") send to log
        self._bot_active = False
        self._waiting = False
        self._setup = False
        self._currentPhase = "Base"
        
    def send_info(self, value: list):
        self.send_info_.emit(value)
        
    def update_values(self, bot_name: str, step: str, mining_seconds: int=140):
        self._bot_name = bot_name
        self._seconds_mining = mining_seconds
        self._step = step

    @Slot()
    def _start_dense_timer(self):
        self._timer_dense_ess_bot.start()
        self._start_emited = True
    
    @Slot()
    def _stop_dense_timer(self):
        self._timer_dense_ess_bot.stop()
        self._start_emited = False
        
    @Slot()
    def _start_pollivneach_timer(self):
        self._start_emited = True
        self._timer_pollivneach_bot.start()
    
    @Slot()
    def _stop_pollivneach_timer(self):
        self._timer_pollivneach_bot.stop()
        self._start_emited = False
        
    def enable_feedback(self):
        """Enable the print feedback"""
        self._feedback_active = True
        self._timer_feedback.start()

    def disable_feedback(self):
        """Disable print feedback"""
        self._feedback_active = False
        
    def _keyboard_controller(self):
        self._bot_active = False

    def _print_feedback(self):
        """Qtimer call function for mouse feedback """
        if self._feedback_active:
            x, y = pyautogui.position()
            #x += 95
            #y += 41
            color = pyautogui.screenshot()
            color = color.getpixel((x, y))
            ss = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
            ss += ' RGB: ('+ str(color[0]).rjust(3)
            ss += ', ' + str(color[1]).rjust(3)
            ss += ', ' + str(color[2]).rjust(3) + ')'

            #label_mouse_info.config(text=ss);
            # probably send to log
        if not self._feedback_active:
            self._timer_feedback.stop()

    def _close_thread(self):
        self.stopped.emit(True)
    
    def _dense_ess_start(self):
        """Dense ess bot handle"""
        reset_timer = denseEssProcess(self._current_phase, self._waiting, self._seconds_mining, self)
        self._timer_dense_ess_bot.setInterval(reset_timer)
        if self._bot_active:
            if not self._start_emited:
                self.start_dense.emit(True)
        else:
            self.stop_dense.emit(True)
            self._close_thread()

    def _pollivneach_start(self):
        """Pollivneach bot handle"""
        reset_timer = pollivneachCourseFile.pollinveachCourse(self._current_phase, self)
        self._timer_pollivneach_bot.setInterval(reset_timer)
        self._timer_pollivneach_bot.timeout.connect(self._pollivneach_start)
        if self._bot_active:
            if not self._start_emited:
                self.start_pollivneach.emit(True)
        else:
            self.stop_pollivneach.emit(True)
            self._close_thread()

    def _hunting_start(self):
        """Hunting bot handle"""
        if self._bot_active:
            RunescapeGame.start(self._setup, self)
            if not self._setup:
                self._setup = True
            self._hunting_start()
        else:
            self._close_thread()

    def _bloods_start(self):
        """Blood bot handle"""
        if self._bot_active:
            bloods.run(self)
            self._bloods_start()
        else:
            self._close_thread()

    def _runecrafting_start(self):
        """Runecrafting bot handle"""
        print('trying renecraft bot')
        if self._bot_active:
            runecrafting.run()
            self._runecrafting_start()
        else:
            self._close_thread()

    def _seers_start(self):
        """Seers bot handle"""
        if self._bot_active:
            seers.run()
            self._seers_start()
        else:
            self._close_thread()

    def _cooker_start(self):
        """Cooker bot handle"""
        if self._bot_active:
            cooker.run(self._setup)
            if not self._setup:
                self._setup = True
            self._cooker_start()
        else:
            self._close_thread()

    def _construction_start(self):
        """Construction bot handle"""
        if self._bot_active:
            construction.run()
            self._construction_start()
        else:
            self._close_thread()

    def _smithing_start(self):
        """Smithing bot handle"""
        if self._bot_active:
            smithing.run()
            self._smithing_start()
        else:
            self._close_thread()

    def _wines_start(self):
        """Wine bot handle"""
        if self._bot_active:
            wines.run()
            self.wines_start()
        else:
            self._close_thread()

    def _ardouge_start(self):
        """Ardouge bot handle"""
        if self._bot_active:
            ardouge.run()
            self._ardouge_start()
        else:
            self._close_thread()

    def _woodcutter_start(self):
        """Woodcutter bot handle"""
        if self._bot_active:
            woodcutter.run()
            self._woodcutter_start()
        else:
            self._close_thread()

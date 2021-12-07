from constants import CLOCK_SPEED, CYCLES_PER_DIVIDER_INCREMENT, TIMER_ADDR, TIMER_CONTROL_ADDR, TIMER_MODULATOR_ADDR
from interrupts import InterruptControl
from mmu import Mmu
from utils import Interrupt, is_bit_set


class TimerControl:
    '''
    A general purpose class to control timers and timer related
    functionality in PyBoy
    '''

    def __init__(self, mmu: Mmu, interrupts: InterruptControl):
        self.mmu = mmu
        self.interrupts = interrupts

        self.divider_counter = CYCLES_PER_DIVIDER_INCREMENT
        self.timer_counter = 0

    def update_timers(self, cycles: int):
        '''
        Update the timers based on CPU cycles
        '''

        self.update_divider_register(cycles)

        freq = self.get_timer_frequency()

        # If Timer is enabled, update it
        if self.is_timer_enabled():

            self.timer_counter += cycles
            if self.timer_counter >= freq:
                # If we have counted enough cycles, increment timer
                self.timer_counter -= freq
                self.mmu.increment_timer_register()

                # If the Timer overflows (i.e. rolled around to 0) then
                # Request a Timer interrupt and set the timer to the value
                # in the Timer Modulo register (i.e. 0xFF06)
                if self.mmu.read_byte(TIMER_ADDR) == 0:
                    self.interrupts.request_interrupt(Interrupt.TIMER)
                    self.mmu.write_byte(TIMER_ADDR, self.mmu.read_byte(TIMER_MODULATOR_ADDR))

    def is_timer_enabled(self):
        '''
        Returns whether or not the timer is currently enabled by looking at Bit 2
        of the TAC (Timer control) register
        '''

        return is_bit_set(self.mmu.read_byte(TIMER_CONTROL_ADDR), 2)

    def get_timer_frequency(self):
        '''
        Get the frequency in which the timer should increment by looking at Bit 0 and 1
        of the TAC (Timer control) register
        '''

        freq_compare_val = self.mmu.read_byte(TIMER_CONTROL_ADDR) & 0x3

        # These values are taken from the Pan Docs
        if freq_compare_val == 0:
            return int(CLOCK_SPEED / 4096)
        elif freq_compare_val == 1:
            return int(CLOCK_SPEED / 262144)
        elif freq_compare_val == 2:
            return int(CLOCK_SPEED / 65536)
        else:
            return int(CLOCK_SPEED / 16384)

    def update_divider_register(self, cycles: int):
        '''
        After certain number of cycles, increment the divider register
        '''

        self.divider_counter -= cycles
        if self.divider_counter <= 0:
            self.divider_counter = CYCLES_PER_DIVIDER_INCREMENT
            self.mmu.increment_divider_register()

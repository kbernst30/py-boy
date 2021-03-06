from constants import INTERRUPT_ENABLE_ADDR, INTERRUPT_FLAG_ADDR
from mmu import Mmu
from utils import Interrupt, is_bit_set, set_bit


class InterruptControl:
    '''
    A general purpose class to control interrupt logic for PyBoy
    '''

    def __init__(self, mmu: Mmu):
        self.mmu = mmu

    def get_servicable_interrupt(self) -> Interrupt:
        '''
        Return the next interrupt to service in order of priority, if enabled and requested

        :return the number of cycles necessary to perform a service
        '''

        interrupts = [i for i in Interrupt]
        interrupts.sort()

        # Interrupts are serviced in order of priority, as defined in their bit values
        for interrupt in interrupts:

            # if the interrupt is requested and enabled, we can tell the CPU to handle it
            if self.is_interrupt_enabled(interrupt) and self.is_interrupt_requested(interrupt):
                return interrupt

        return None

    def request_interrupt(self, interrupt: Interrupt):
        '''
        Request a specific interrupt setting the value in the IF register
        '''

        interrupts_requested = self.mmu.read_byte(INTERRUPT_FLAG_ADDR)
        interrupts_requested = set_bit(interrupts_requested, interrupt.value)
        self.mmu.write_byte(INTERRUPT_FLAG_ADDR, interrupts_requested)

    def is_interrupt_enabled(self, interrupt: Interrupt) -> bool:
        '''
        Return whether or not the requested interrupt is enabled in the IE register
        '''

        interrupts_enabled = self.mmu.read_byte(INTERRUPT_ENABLE_ADDR)
        return is_bit_set(interrupts_enabled, interrupt.value)

    def is_interrupt_requested(self, interrupt: Interrupt) -> bool:
        '''
        Return whether or not the requested interrupt is requested in the IF register
        '''

        interrupts_requested = self.mmu.read_byte(INTERRUPT_FLAG_ADDR)
        return is_bit_set(interrupts_requested, interrupt.value)

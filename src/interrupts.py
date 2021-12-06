from constants import INTERRUPT_ENABLE_ADDR, INTERRUPT_FLAG_ADDR
from cpu import Cpu
from mmu import Mmu
from utils import Interrupt, is_bit_set


class InterruptControl:
    '''
    A general purpose class to control interrupt logic for PyBoy
    '''

    def __init__(self, mmu: Mmu, cpu: Cpu):
        self.mmu = mmu
        self.cpu = cpu

    def service_interrupts(self):
        '''
        Service interrupts in order of priority, if enabled and requested
        '''
        interrupts = [i for i in Interrupt]
        interrupts.sort()

        # If interrupts are enabled globally
        if self.is_interrupt_master_enabled():

            # Interrupts are serviced in order of priority, as defined in their bit values
            for interrupt in interrupts:

                # if the interrupt is requested and enabled, we can tell the CPU to handle it
                if self.is_interrupt_enabled(interrupt) and self.is_interrupt_requested(interrupt):
                    self.cpu.service_interrupt(interrupt)

    def is_interrupt_master_enabled(self) -> bool:
        '''
        Return whether or not the CPU has enabled or disabled interrupts
        '''

        return self.cpu.is_interrupts_enabled()

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

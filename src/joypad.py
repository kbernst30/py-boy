from utils import Button, JoypadMode


class Joypad:
    '''
    Holds internal state of the Joypad
    '''

    def __init__(self):
        # Hold internal state of joypad, 1 for unpressed and 0 for pressed
        self.state = {button: 1 for button in Button}

    def get_button_state(self, button: Button):
        '''
        Get the internal pressed or unpressed state of a button
        '''

        return self.state[button]

    def set_button_state(self, button: Button):
        self.state[button] = 0

    def reset_button_state(self, button: Button):
        self.state[button] = 1

    def get_buttons_for_mode(self, mode: JoypadMode) -> int:
        '''
        Get the lower nibble for the joypad register based on the
        joypad mode
        '''

        if mode == JoypadMode.DIRECTION:
            down = self.state[Button.DOWN]
            up = self.state[Button.UP]
            left = self.state[Button.LEFT]
            right = self.state[Button.RIGHT]

            return (down << 3) | (up << 2) | (left << 1) | right

        elif mode == JoypadMode.ACTION:
            start = self.state[Button.START]
            select = self.state[Button.SELECT]
            b = self.state[Button.B]
            a = self.state[Button.A]

            return (start << 3) | (select << 2) | (b << 1) | a

        # Shouldn't get here but if we do, assume all buttons unpressed
        return 0xF

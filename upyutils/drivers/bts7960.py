from machine import Pin, PWM


class InvalidSpeedError(Exception):
    """
    Raised when an invalid motor speed is provided.

    Valid speed values are between -100 and 100 inclusive.
    """

    def __init__(self) -> None:
        message = "Speed must be between -100 and 100."
        super().__init__(message)


class BTS7960:
    """
    BTS7960 motor driver controller.

    This class provides speed and direction control for a DC motor
    using a BTS7960 H-bridge module.

    Parameters
    ----------
    rpwm_pin : int
        GPIO connected to RPWM.
    lpwm_pin : int
        GPIO connected to LPWM.
    ren_pin : int
        GPIO connected to R_EN.
    len_pin : int
        GPIO connected to L_EN.
    freq : int, default=1000
        PWM frequency in Hz.

    Notes
    -----
    Speed values range from -100 to 100:

    * 100: Full forward speed.
    * 0: Motor stopped.
    * -100: Full reverse speed.
    """

    def __init__(
        self,
        rpwm_pin: int,
        lpwm_pin: int,
        ren_pin: int,
        len_pin: int,
        freq: int = 1000
    ) -> None:

        self.r_pwm = PWM(Pin(rpwm_pin), freq=freq)
        self.l_pwm = PWM(Pin(lpwm_pin), freq=freq)

        self.r_enable = Pin(ren_pin, Pin.OUT)
        self.l_enable = Pin(len_pin, Pin.OUT)

        self._speed = 0.0

        self.stop()

    @property
    def speed(self) -> float:
        """
        Current motor speed.

        Returns
        -------
        float
            Current speed value in the range [-100, 100].
        """
        return self._speed

    def _enable(self) -> None:
        """Enable the motor driver."""
        self.r_enable.value(1)
        self.l_enable.value(1)

    def _disable(self) -> None:
        """Disable the motor driver."""
        self.r_enable.value(0)
        self.l_enable.value(0)

    def set_speed(self, speed: float) -> None:
        """
        Set motor speed and direction.

        Parameters
        ----------
        speed : float
            Desired speed in the range [-100, 100].

        Raises
        ------
        InvalidSpeedError
            If speed is outside the valid range.
        """
        if not -100 <= speed <= 100:
            raise InvalidSpeedError()

        self._speed = speed

        if speed > 0:
            self._enable()

            self.l_pwm.duty(511)

            duty = int(
                511.5 + ((speed / 100.0) * (1023 - 511.5))
            )

            self.r_pwm.duty(duty)

        elif speed < 0:
            self._enable()

            self.r_pwm.duty(511)

            duty = int(
                511.5 * (1 - (speed / 100.0))
            )

            self.l_pwm.duty(duty)

        else:
            self._disable()

            self.r_pwm.duty(511)
            self.l_pwm.duty(511)

    def start(self, speed: float) -> None:
        """
        Alias for :meth:`set_speed`.

        Parameters
        ----------
        speed : float
            Desired speed in the range [-100, 100].
        """
        self.set_speed(speed)

    def stop(self) -> None:
        """
        Stop the motor.

        Equivalent to setting the speed to zero.
        """
        self.set_speed(0)

    def brake(self) -> None:
        """
        Apply active braking.

        Both PWM channels are driven high while the driver remains
        enabled, causing the motor to brake rapidly.
        """
        self._enable()

        self.r_pwm.duty(1023)
        self.l_pwm.duty(1023)

        self._speed = 0
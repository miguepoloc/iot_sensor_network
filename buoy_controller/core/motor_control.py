import time

import machine


class BaseMotorController:
    """Clase Base (Interfaz) para cualquier controlador de motor"""

    def stop(self):
        """This method is used to stop the motor"""
        raise NotImplementedError

    def up(self):
        """This method is used to move the motor up"""
        raise NotImplementedError

    def down(self):
        """This method is used to move the motor down"""
        raise NotImplementedError

    def is_moving(self):
        """This method is used to check if the motor is moving"""
        raise NotImplementedError


class MotorL298N(BaseMotorController):
    def __init__(self, pin_up, pin_down):
        """Controlador L298N tradicional (IN1, IN2) puenteado"""
        self.pin_up = machine.Pin(pin_up, machine.Pin.OUT)
        self.pin_down = machine.Pin(pin_down, machine.Pin.OUT)
        self.stop()

    def stop(self):
        print("[L298N] Deteniendo...")
        self.pin_up.value(0)
        self.pin_down.value(0)

    def up(self):
        print("[L298N] Subiendo sensores...")
        self.pin_down.value(0)
        time.sleep_ms(50)
        self.pin_up.value(1)

    def down(self):
        print("[L298N] Bajando sensores...")
        self.pin_up.value(0)
        time.sleep_ms(50)
        self.pin_down.value(1)

    def is_moving(self):
        return self.pin_up.value() == 1 or self.pin_down.value() == 1


class MotorHW166(BaseMotorController):
    def __init__(self, pin_ain1, pin_ain2, pin_pwm):
        """
        Controlador HW-166 para ESP32 (TB6612FNG).
        AIN1 y AIN2 controlan sentido. PWM controla velocidad.
        """
        self.ain1 = machine.Pin(pin_ain1, machine.Pin.OUT)
        self.ain2 = machine.Pin(pin_ain2, machine.Pin.OUT)

        # Configurar PWM en el pin de potencia a 1kHz
        pwm_pin = machine.Pin(pin_pwm, machine.Pin.OUT)
        self.pwm = machine.PWM(pwm_pin, freq=1000)
        self.stop()

    def stop(self):
        print("[HW-166] Deteniendo...")
        self.pwm.duty(0)  # Velocidad cero
        self.ain1.value(0)
        self.ain2.value(0)

    def up(self):
        print("[HW-166] Subiendo sensores...")
        self.pwm.duty(0)  # Cortar poder antes de invertir giro
        self.ain1.value(1)  # Dirección A
        self.ain2.value(0)
        self.pwm.duty(1023)  # Potencia máxima (ESP32 usa 0-1023)

    def down(self):
        print("[HW-166] Bajando sensores...")
        self.pwm.duty(0)
        self.ain1.value(0)  # Dirección B
        self.ain2.value(1)
        self.pwm.duty(1023)  # Potencia máxima

    def is_moving(self):
        return self.pwm.duty() > 0


class MotorServo(BaseMotorController):
    def __init__(self, pin_signal):
        """
        Controlador para Servomotor (Ej. SG90 de 180° o 360° Rotación Continua).
        Requiere señal PWM a 50Hz. En hardware de ESP32, el timer tiene resolución 0-1023.
        Valores típicos de duty cycle a 50Hz (20ms periodo):
          - ~40 (1ms) = Giro completo izquierda (0°) o Rotación atrás rápida
          - ~77 (1.5ms) = Centro (90°) o Parado (Si es Rotación Continua)
          - ~115 (2ms) = Giro completo derecha (180°) o Rotación adelante rápida
        """
        self.servo = machine.PWM(machine.Pin(pin_signal), freq=50)
        self.moving = False
        self.stop()

    def stop(self):
        print("[Servo] Detenido (o en posición central)")
        # Para rotación continua: 77 detiene el motor.
        # Para 180 grados: 77 posiciona en 90°
        self.servo.duty(77)
        self.moving = False

    def up(self):
        print("[Servo] Girando/Movilizando UP (Lento)...")
        # 77 es el centro. Entre más cerca a 77, más lento gira.
        self.servo.duty(85)  # Antes 115 (Rápido), ahora 85 (Lento)
        self.moving = True

    def down(self):
        print("[Servo] Girando/Movilizando DOWN (Lento)...")
        # 77 es el centro. Entre más cerca a 77, más lento gira.
        self.servo.duty(69)  # Antes 40 (Rápido), ahora 69 (Lento)
        self.moving = True

    def is_moving(self):
        return self.moving

---
sidebar_position: 3
---

# PiSugar3 I2C Datasheet

   **Register address:**

   0x57
![I2C address table](https://cdn.pisugar.com/img/I2Ctable.png)

* In the I2C register, the retention bit is reserved for the system test interface and it is forbidden to write the data.
* When directly modifying the I2C register, you need to read the value of the corresponding register first. Write the calculated value into this register after performing AND operation on the BIT bits that need to be modified. At the same time, make sure that only the bits that need to be modified are modified, and the values of other bits cannot be modified at will.

## Function specifications
PiSugar 3 has many advanced power functions that can be set up, which are described below.

Some functions can be operated on WebUI, indicating that this function does not need to be manually set up by I2C, only in WebUI. At the same time, the WebUI interface can be set up directly through the command line. The function set through the WebUI will retain the settings  in the Raspberry Pi system and will not be set to the default value after restart or battery reset.

1. Write Protection

   **Register address:**

   Write protection: 0x0B

   **Register operation:**

   can be read or written

   **Operating instructions:**

   When reading, 1 indicates that the PiSugar registers can be written, 0 indicates that the registers cannot be written.
   
   Writing 0x29 to this register will make other registers writable, and writing any other value (such as 0xff) will make other register unwritable
   
   The following functions are not affected by write protection
   Reading data.

   Feed watchdog

   TAP Button State Cleanup

   **Minimum firmware version: 1.2.4**

1. External power supply detection

   **Register address:**

   the 7th bit of the 0X02 address

   **Register operation:**

   can be read or written

   **Data description:**

   1 means external power supply access, 0 means no external power supply

   **Function description:**

   It can be judged whether the external power supply is connected by querying the 7th bit of the 0X02 address. The detection is to detect whether the power input interface has voltage. If the plug is inserted but there is no power supply, it will be detected that the external power supply is not connected.

   WebUI supports reading the status.

1. Charging switch

   **Register address:**

   the 6th bit of the 0X02 address

   **Register operation:**

   can be read or written

   **Data description:**

   1 is on, 0 is off

   **Function description:**

   When charging switch is turned on, once the external power access,  the device begins charging.


   **default value:**

   This function will be reset to on each time the device is turned off
   **WebUI does not support this function.**

1. Output switch

   **Register address:**

   the 2th bit of the 0X02 address

   **Register operation:**

   can be read or written

   **Data description:**

   1 is on, 0 is off

   **Function description:**

   When output switch is turned off, PiSugar does not output voltage. When output switch is turned on, PiSugar outputs 5V voltage. If the automatic hibernate function is turned on and PiSugar is turned off, the PiSugar system will immediately go into the hibernate state, and I2C will be inoperable.

   (About turning off PiSugar: The shutdown command is executed in the PiSugar-Poweroff client.)


   **default value:**

   This function will be reset to on each time the device is turned on.
   **WebUI does not support this function.**

1. Output switch with delay

   **Register address:**

   the 5th bit of the 0X02 address. 0x09 Set Delay Time

   **Register operation:**

   can be read or written

   **Data description:**

   Set 0 is poweroff

   **Function description:**

    When setting the control bit to off, PiSugar will count down by the number set by 0x09 bit. When the countdown reaches 0, the system output will be turned off.

    PiSugar will not start countdown immediately after setting 0x09. Each time you use a delay, set 0x09 first, then set 0x02 to start countdown to turn off the output.

    Delay range 0-255 seconds, inaccurate timing.


   **default value:**

   0x09 will be reset to zero each time you restart.

   **WebUI does not support this function.**

   **Minimum firmware version: 1.0.6**


1. Automatically resume booting when power is reconnected

   **Register address:**

   the 4th bit of the 0X02 address.

   **Register operation:**

   can be read or written.

   **Data description:**

   1 is on, 0 is off.

   **Function description:**

   a. When this function is turned on and PiSugar is turned off, once the external power supply is restored, PiSugar will automatically turn on and start the external output.

   b. When this function is turned off, once the external power supply is restored, PiSugar will charge, but will not output externally.

   If you need to awake the Raspberry Pi even when PiSugar is powered on, please refer to the SCL awakening function.

   **default value:**

   This function is on by default. It resets to on each time the PiSugar system is completely reset.
WebUI supports this function.

1. Anti-mistaken touch function

   **Register address:**

   the 3rd bit of the 0X02 address.

   **Register operation:**

   can be read or written.

   **Data description:**

   1 is on, 0 is off.

   **Function description:**

   a. When anti-mistaken touch function is turned on, if PiSugar shuts down, first short press the power button, and then release, the LED will indicate the current power. Next, press and hold the power button to achieve the purpose of booting. When anti-mistaken touch function is turned off, short press the power button to trigger the boot.

   b. Whether the function is turned on or not, when PiSugar is turned on, it needs to be turned off by a long press.

   c. We can judge whether the current power button is pressed by reading the last bit of the 0X02 address.

   **default value:**

   This function is on by default. It resets to on each time the PiSugar system is completely reset.

   **WebUI does not support this function.**

1. Automatic hiberate function:

   **Register address:**

   the 6th bit of the 0X03 address.

   **Register operation:**

   can be read or written.

   **Data description:**

   1 is on, 0 is off.

   **Function description:**

   This function is related to the output switch function.

   a. When automatic hibernate function is turned on, once the output function is turned off, PiSugar will go into hibernate. At that time, I2C communication and custom switches are not available, while the power button, external power detection, RTC and timer switch machines work normally.

   b. When the automatic hibernate function is turned off, PiSugar is always on regardless of whether the output switch is off. At that time, all functions including I2C are working normally.

   c. This function can be used to maintain PiSugar's I2C communication after shutdown, so as to awake or perform other status queries.

   d. When PiSugar turns off the output but does not go into hibernate, the power consumption is 1mA
   default: This function is on by default, it resets to on when restarting the device.

   **WebUI does not support this function.**

1. Soft shutdown function

   **Register address:**

   set up:he 4th bit of the 0x03 address;
   
   query whether to enter the soft shutdown state: the 3rd bit of the 0x03 address.

   **Register operation:**

   can be read or written

   **Data description:**

   1 is on, 0 is off

   **Function description:**

   The soft shutdown function is set for shutdown behavior for the power button.

   a. When the soft shutdown function is turned off, while PiSugar is working, press and hold the power button for more than 2 seconds to directly turn off the power.

   b. When the soft shutdown function is turned on, press and hold the power button will not directly turn off the output. Instead, it indicates that the system has triggered the shutdown process and should start to execute the shutdown command through the 3rd query bit of the 0x03 address.


   **default value:**

   This function is off by default, it resets to off when restarting.

1. Chip temperature

   **Register address:**

   0X04 address.

   **Register operation:**

   can be read

   **Data description:**

   0 means -40 degrees Celsius

   **Function description:**

   The temperature measurement is in the range of -40 to 85 degrees Celsius. This temperature is only the temperature of the chip itself, it does not represent the temperature of the Raspberry Pi, nor does it represent the temperature of the battery.

   **WebUI does not support this function.**

1. Software watchdog

   **Register address:**

   The function switch: the 7th bit of the 0X06 address, the watchdog reset: the 5th bit of the 0x06 address, the watchdog interval time: the 0x07 address.

   **Register operation:**

   can be read or written.

   **Data description:**

   1 is on, 0 is off.

   Writing 1 on the watchdog reset setting bit will reset the watchdog timer (kicking the dog).

   The watchdog delay is set to the register value X 2s, for example, when the register value is 0x05, the actual watchdog delay is 5X2s=10s.

   **Function description:**

   The software watchdog provides a watchdog other than the Raspberry Pi system, which restarts the Raspberry Pi system when the Raspberry Pi system crashes. When this function is turned on, if the watchdog timer is not reset (kicking the dog) within the software watchdog time interval, PiSugar will temporarily turn off the output to achieve the purpose of restarting the Raspberry Pi system. The operation of kicking the dog needs to be completed by the user.

   **default value:**

   This function is off by default. It is off by default each time it restarts.

   **WebUI does not support this function.**

   **Operation example:**
   
   https://github.com/PiSugar/pisugar-power-manager-rs/blob/master/scripts/SoftwareWatchdogPiSugar3.sh

1. Boot watchdog

   **Register address:**

   The function switch is the 4th position of 0x06 address, the reset of boot watchdog is set to the 3rd position of 0x06 address, and the restart times of boot soft watchdog is limited to 0x0a address.

   **Register operation:**

   can be read or written.

   **Data description:**

   1 is on, 0 is off.

   Writing 1 to the boot watchdog reset setting bit will end this round(feeding the dog). The minimum restart times of the boot watchdog is 1.

   **Function description:**

   Provides a watchdog function that monitors whether the system is turned on properly. When the Raspberry Pi system is turned on, the dog feeding operation should be performed as soon as possible. The dog feeding operation only needs to be done once in a single start.
   
   If the dog is not fed for more than a minute and a half and the function is not turned off, PiSugar will power off and restart, and start the watchdog again. 
   
   The number of restarts can be limited by 0x0a.
   
   Dog feeding needs to be done by the user.

   **default value:**

   This function is off by default. It is off by default every time the system is reset.

   **WebUI does not support this function.**
   
   **Minimum firmware version: 1.0.6**

   **Operation example:**
   
   https://github.com/PiSugar/pisugar-power-manager-rs/blob/master/scripts/BootWatchdogPiSugar3.sh

1. Charging protection

   **Register address:**

   the 7th bit of the 0X20 address.

   **Register operation:**

   can be read or written.

   **Data description:**

   1 is on, 0 is off.

   **Function description:**

   PiSugar 3 provides hardware charging protection function.

   When this function is turned on, the fully charged power is approximately equivalent to 80% of the battery power, and the voltage will be limited to about 3.8V. Enabling this function will greatly extend the cycle life of the battery by about 8 times (calculated as the battery cycle life doubles for every 0.1V drop in the charge cut-off voltage). It is recommended to turn it on under long-term charging conditions.

   **default value:**

   This function is off by default, it resets to off when restarting.

   **WebUI supports this function.**

1. SCL awakening

   **Register address:**

   the 3rd bit of the 0X20 address.

   **Register operation:**

   can be read or written.

   **Data description:**

   1 is on, 0 is off.

   **Function description:**

   This function is related to the booting function.

   When the function is turned on, the SCL pin will be pulled down once PiSugar is turned on. If the Raspberry Pi is connected to the power supply but not turned on, it will be awakened.

   **default value:**

   This function is off by default, it resets to off when restarting.
   
   **WebUI does not support this function.**

1. Battery capacity reading

   **Register address:**

   0X22, 0X23, 0X2A

   **Register operation:**

   can be read

   **Data description:**

   0x22 is high battery voltage, 0x23 is low battery voltage. When reading, you should first arrange the two bits of data in order to get the actual voltage in mA.

   For example, if the data read are 0x10 and 0x1F, the combined result will be 0x101F=4127mV=4.127V.

   The 0X2A address is the calculated battery power percentage.

   **Function description:**

   WebUI can read the battery power percentage


1. Timing boot function

   **Register address:**

   control bit: the 7th bit of 0x40, data address: 0x44-0x47

   **Register operation:**

   can be read or written.

   **Data description:**

   Write the control bit to 1 to turn on the timing boot function, write 0 to turn off the timing boot function. The Weekday bit ranked by bit represents from Sunday to Saturday, where 0 represents Sunday.

   **Function description:**

   a. When the function is turned on, PiSugar will turn on the output each time the specified time is reached.

   b. This function will not be reset due to restart.

   c. Turning off this function requires manual settings.

   **WebUI supports this function**

1. Custom I2C address
   
   **Register address:**

   0x50

   **Register operation:**

   can be read or written.

   **Data description:**

   the highest bit is even parity check bit. If the number of 1 in the data is odd, the highest bit is 1, otherwise it is 0

   For example, if the data is 0x57, the binary representation is 0b010110111, and the count of 1 is 5, so the highest bit is 1, and the final date is 0xd7, the binary representation is 0b11010111

   **Function description:**

   Changing this register will change the operation address of I2C (0x57 by default). The change takes effect immediately.

   The I2C address range is 0x03-0x77. If date beyond the range, it will not be written successfully.

   **Default value**

   0xd7 (actual address 0x57). This value will not be reset whether turned off or reset the system. So if you want change it, make sure you know what are you doing.


   **WebUI not supports this function**

   If you want to change the I2C address of WebUI, you can modify i2c_addr of /etc/pisugar-server/config.json

   If the i2c_addr isn't in your file, you can add it.

   For example, the address is 0x30:
   "i2c_addr"= 48,
   
   **Minimum firmware version: 1.0.6**

1. LED Control
   
   **Register address:**

   control bit: the 0-3 bit of 0xE0

   **Register operation:**

   can be read or written.

   **Data description:**

   1 is on, 0 is off.
   
   **Function description:**

   These four bits directly control the corresponding four LEDs.

   This control is non-exclusive, so it may be necessary to perform refresh writes occasionally to maintain the LED states.

   **WebUI not supports this function**

   **Minimum firmware version: 1.0.0**

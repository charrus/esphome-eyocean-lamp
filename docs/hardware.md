# Hardware

## LILYGO T-Embed CC1101

The dedicated package targets the **T-Embed CC1101** variant, not arbitrary T-Embed boards. Verify the exact board revision against the [vendor pin reference](https://github.com/Xinyuan-LilyGO/T-Embed-CC1101/blob/master/examples/utilities.h) before flashing.

| Function | GPIO / setting |
| --- | --- |
| Shared SPI MOSI / MISO / clock | 9 / 10 / 11 |
| CC1101 chip select | 12 |
| RF receive / transmit signal | 38 / 3 |
| Peripheral power rail enable | 15 |
| SD card chip select | 13 |
| nRF chip select / chip enable | 44 / 43 |
| Antenna routing | 47 and 48 both high for 433 MHz |
| LCD chip select / data-command | 41 / 16 |
| LCD backlight | 21 |

The board definition is `esp32-s3-devkitc-1`, using ESP-IDF, 16 MB flash, and octal PSRAM at 80 MHz. This board identifier alone does not configure the T-Embed's peripherals.

Power and shared-bus initialization matter: output setup priority is 1100; the boot initialization runs at priority 1050, deselects unused chip selects, enables the rail, and waits a blocking 10 ms. Preserve this ordering. Keep unused shared-bus devices inactive; do not add peripherals without checking pin conflicts and power requirements.

The LCD is configured as ST7789V, 170 × 320 pixels, offsets 35/0, rotation 270°, inverted colours, RGB ordering, and 20 MHz SPI. Fonts are Google Fonts `Roboto Mono` at sizes 14 and 20. First-time font retrieval requires network access.

The receiver uses 192 RMT symbols and the transmitter 64. RMT, DMA, memory, and shared-bus resources are finite. Do not casually add other resource-heavy peripherals; a valid YAML file does not prove successful runtime allocation.

## Generic ESP32-S3 plus CC1101

`examples/esp32s3-cc1101.yaml` uses these **illustrative** assignments:

| Signal | ESP32-S3 GPIO |
| --- | --- |
| SPI MOSI | 9 |
| SPI MISO | 10 |
| SPI clock | 11 |
| CC1101 CS | 12 |
| RF receive signal | 38 |
| RF transmit signal | 3 |

Consult both your board schematic and your CC1101 module pinout. Match the module's receive/transmit signal connections to the configuration; do not infer header order from this table. Check whether GPIOs are already used by flash, PSRAM, USB, boot strapping, or onboard peripherals. A module may need different signal routing or antenna switching from the integrated T-Embed.

Disconnect power before wiring. Use the module's specified supply and logic levels (standard CC1101 modules use 3.3 V logic, not 5 V), common ground, suitable decoupling, and an antenna matched to the operating band. Verify your specific module rather than assuming every breakout has regulation or level shifting. Do not transmit without a suitable antenna.

## Deployment checks

1. Review wiring, board revision, radio band, and regional restrictions.
2. Keep the lamp transmission switch disabled and omit the optional proxy during initial bring-up.
3. Validate and compile the chosen example; inspect startup logs after an explicitly authorized installation.
4. Confirm radio and display initialization independently before investigating the lamp protocol.

Neither successful compilation nor a populated candidate decoder proves that this hardware can control your lamp. The sanitized examples have not yet been physically tested with the lamp.

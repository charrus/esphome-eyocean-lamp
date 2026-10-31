# Verification record

The initial examples were checked with ESPHome **2026.10.1**, Python 3.14 and ESP-IDF builds.

| Example | YAML validation | Full firmware compile |
| --- | --- | --- |
| `examples/esp32s3-cc1101.yaml` | Passed | Passed (exit 0) |
| `examples/t-embed-cc1101.yaml` | Passed | Passed (exit 0) |
| `examples/t-embed-cc1101-with-proxy.yaml` | Passed | Passed (exit 0) |

Builds used disposable **synthetic** Wi-Fi credentials and API/OTA encryption keys, a zero remote ID and a zero XOR key. They were not uploaded. Do not distribute or install the test firmware; build your own after configuring credentials and remote identity.

`python -m unittest discover -s tests -v` verifies:

- ESPHome validation of all three examples in an isolated directory with temporary test credentials;
- default lamp-transmission opt-in and zero identity;
- absence of the removed custom RF recording/playback implementation;
- absence of private network addresses in public examples/packages and absence of tracked `secrets.yaml` files (local ignored credentials are allowed);
- native C++ compilation/execution of the **actual YAML encoder and decoder lambdas**, using an explicitly synthetic frame, all six supported command bytes, leading noise, truncation, invalid pulse widths and wrong polarity.

The GitHub Actions workflow runs validation and synthetic tests; it does **not** run firmware compilation or deploy devices. See [GitHub Actions](https://github.com/charrus/esphome-eyocean-lamp/actions) for current hosted CI results; the local results above are separate checks.

## What these checks do not prove

Compilation and synthetic tests do not prove physical CC1101 initialization, LCD orientation, RF range, regulatory compliance, identity attribution, pairing, or any lamp response. The generic wiring example is illustrative. Recheck your exact board and test reception before deliberately enabling transmission. Candidate decoded frames are not authenticated, and lamp state is not observable through these controls.

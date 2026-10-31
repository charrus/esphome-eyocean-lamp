# EYOCEAN lamp control with ESPHome

Repository: [charrus/esphome-eyocean-lamp](https://github.com/charrus/esphome-eyocean-lamp).

Local ESPHome packages for controlling a compatible EYOCEAN lounge/desk lamp through a CC1101 radio. This is support for one published protocol family, **not every lamp sold under the EYOCEAN name**.

The configuration provides command buttons and receive-side candidate decoding. It does not contain RF recording/playback or automatic remote learning. The lamp sends no state feedback: buttons issue commands, not confirmed on/off, brightness, or colour-temperature states.

## Status and safety

- ESPHome required/tested version: **2026.10.1**. Schema validation, compilation, and operation on physical hardware are separate checks.
- Sanitized examples have not yet been physically tested with the lamp. Synthetic tests do not establish real RF compatibility.
- `remote_id` defaults to `0x0000` and `xor_key` to `0x00`. Lamp transmission requires a nonzero remote ID and the **Allow RF control** switch enabled. That switch resets to off at boot.
- Candidate decoding never rewrites substitutions. Identify and enter your own remote values manually; share remote identities only when you intentionally choose to publish them, as with the user-reported pairs below.
- The optional RF proxy has separate, unguarded TX/RX endpoints. **Allow RF control is not a global radio safety switch.** Leave the proxy out unless you need it.
- Use only authorized equipment and frequencies permitted in your region.

## Layout

| Path | Purpose |
| --- | --- |
| `packages/eyocean.yaml` | Lamp encoder, candidate decoder, command buttons, globals, and transmission guard |
| `packages/t-embed-cc1101.yaml` | LILYGO T-Embed CC1101 hardware, power initialization, and LCD |
| `packages/rf-proxy.yaml` | Optional `ir_rf_proxy` TX/RX endpoints |
| `examples/t-embed-cc1101.yaml` | T-Embed lamp example |
| `examples/esp32s3-cc1101.yaml` | Generic ESP32-S3/CC1101 example with illustrative wiring |
| `examples/t-embed-cc1101-with-proxy.yaml` | T-Embed example including the optional proxy |
| `examples/secrets.yaml.example` | Placeholder credentials; copy locally to `secrets.yaml` |

## Local setup

Run from a Git checkout of the repository in a Python environment supported by ESPHome (Python 3.14 was used for the recorded checks). The tests also require **Git** and **g++** on `PATH`.

```sh
git clone https://github.com/charrus/esphome-eyocean-lamp.git
cd esphome-eyocean-lamp
python -m venv .venv
. .venv/bin/activate  # POSIX shell; PowerShell: .venv/Scripts/Activate.ps1
python -m pip install -r requirements-dev.txt
cp examples/secrets.yaml.example examples/secrets.yaml
python -m unittest discover -s tests -v
```

Edit `examples/secrets.yaml` locally. Supply `wifi_ssid`, `wifi_password`, and a valid `api_key`. The API encryption and OTA encryption settings reference the same `api_key` secret in these examples. Never put real credentials in the template or commit a real `secrets.yaml`.

Choose an example, review its substitutions and all hardware settings, and follow [hardware notes](docs/hardware.md). The generic example's GPIO assignments are illustrative, not a universal board pin map. The T-Embed display uses Google Fonts (`Roboto Mono`, sizes 14 and 20), so the first build may need network access to download fonts.

Validate the selected example before deployment:

```sh
esphome config examples/t-embed-cc1101.yaml
esphome compile examples/t-embed-cc1101.yaml
```

After editing credentials and reviewing hardware, you can deliberately install the **non-proxy** example with `remote_id: "0x0000"` for initial candidate decoding. Lamp commands are blocked by the zero identity; this is not strictly receive-only firmware, because transmitter support is still compiled in. If you already know your remote values, enter them before building. Install deliberately:

```sh
esphome run examples/t-embed-cc1101.yaml
```

Substitute another example path when using different hardware. Compilation is not flashing; flashing is not proof of lamp operation. After deployment, inspect initialization logs and test one authorized physical command at a time. Enable **Allow RF control** only when ready to transmit.

### Determine remote values

With lamp control disabled, press several distinct buttons on the original physical remote and inspect the candidate decode text sensors/logs. Use the [protocol notes](docs/protocol.md) to check a consistent remote identity, command mapping, and XOR key across those presses. Enter verified values in your local example's `remote_id` and `xor_key` substitutions. A candidate is not proof that a packet came from your remote; there is no automatic pairing or learning.

### Known working remotes

These reported working pairs were supplied for documentation, with upstream issue sources linked where available, in the same table style as [bl4ko/eyocean-ha](https://github.com/bl4ko/eyocean-ha/tree/main#decoded-remote-codes).

| Remote | Remote ID | XOR key | Source |
| --- | --- | --- | --- |
| Remote 1 (6 buttons) | `0xC6FB` | `0x58` | User-reported working |
| Remote 2 (6 buttons) | `0xB4B3` | `0x62` | User-reported working |
| Remote 3 (6 buttons) | `0xC9CE` | `0x62` | [bl4ko/eyocean-ha #6](https://github.com/bl4ko/eyocean-ha/issues/6) |
| Remote 4 (6 buttons) | `0xE054` | `0x51` | [bl4ko/eyocean-ha #7](https://github.com/bl4ko/eyocean-ha/issues/7) |

Remote IDs and XOR keys are **per remote**, not universal model defaults. All four listed remotes have **six buttons**; the linked issues provide additional model details for Remotes 3 and 4. These pairs have not been independently reproduced in this repository's tests. See [configuration snippets and usage notes](docs/protocol.md#known-working-remotes). Runnable examples retain zero-ID defaults; nothing is enabled automatically.

### XOR-key derivation hypothesis

**This formula matches four of the five known six-button remotes, but is not a general six-button rule.** The six-button `0xE054` remote is a counterexample: its reported key is `0x51`, while the formula predicts `0xD1`. The known five-button remote also does not match.

```text
xor_key = high_byte(remote_id) XOR low_byte(remote_id) XOR 0x65
```

Here, `high_byte = (remote_id >> 8) & 0xFF` and `low_byte = remote_id & 0xFF`.

| Remote ID | Buttons | Reported XOR key | Predicted XOR key | Match | Source |
| --- | --- | --- | --- | --- | --- |
| `0xBAD1` | 5 | `0x4E` | `0x0E` | No | [Upstream known remotes](https://github.com/bl4ko/eyocean-ha/tree/main#decoded-remote-codes) |
| `0xDCCF` | 6 | `0x76` | `0x76` | Yes | [Upstream known remotes](https://github.com/bl4ko/eyocean-ha/tree/main#decoded-remote-codes) |
| `0xC6FB` | 6 | `0x58` | `0x58` | Yes | User-reported working |
| `0xB4B3` | 6 | `0x62` | `0x62` | Yes | User-reported working |
| `0xC9CE` | 6 | `0x62` | `0x62` | Yes | [bl4ko/eyocean-ha #6](https://github.com/bl4ko/eyocean-ha/issues/6) |
| `0xE054` | 6 | `0x51` | `0xD1` | No | [bl4ko/eyocean-ha #7](https://github.com/bl4ko/eyocean-ha/issues/7) |

For example, `0xC6 XOR 0xFB XOR 0x65 = 0x58`. The upstream **five-button remote `0xBAD1`** instead satisfies `0xBA XOR 0xD1 XOR 0x25 = 0x4E`; the constants `0x25` and `0x65` differ by `0x40`.

The six-button `0xE054` pair instead satisfies `0xE0 XOR 0x54 XOR 0xE5 = 0x51`; its reported key and the `0x65` formula's prediction differ by `0x80`. Preserve the reported `0x51`, not the predicted `0xD1`.

Button count alone does not identify the derivation constant in the available data. The five-button `0xBAD1` and six-button `0xE054` reports require different constants from the other four remotes. More independent pairs and full-frame captures are needed to investigate a more general relationship. Do not discard reported keys or treat the formula's predictions as corrections.

**Keep `xor_key` explicitly configured.** This hypothesis is not used by the firmware. For a correctly decoded full frame, extract the actual key as `command_byte XOR final_byte` and check it across several distinct original-remote button presses. A mathematical fit is not physical RF verification or authentication.

### ESPHome Device Builder

These examples use local includes such as `../packages/eyocean.yaml`. They are not automatic import URLs.

Either keep the repository hierarchy and use the CLI commands above, or copy your chosen example into the Device Builder configuration root and copy `packages/` alongside it. **For `t-embed-cc1101-with-proxy.yaml`, also copy its included base file `t-embed-cc1101.yaml` beside it.** In all copied examples, change **every** `../packages/…` include to `packages/…`, including optional hardware/proxy includes. Put your local `secrets.yaml` in that configuration root. Retain the API, OTA, and Wi-Fi secret references. Validate and compile the copied configuration before choosing to install it.

## Further reading

- [Hardware and wiring](docs/hardware.md)
- [Protocol and command limitations](docs/protocol.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Validation, compile results and test limits](docs/validation.md)
- [Review and publish your own GitHub repository](docs/publishing.md)

## References and licensing

Protocol reference: [bl4ko/eyocean-ha](https://github.com/bl4ko/eyocean-ha). Vendor pin reference: [LILYGO T-Embed CC1101 utilities.h](https://github.com/Xinyuan-LilyGO/T-Embed-CC1101/blob/master/examples/utilities.h). These references are attribution and compatibility context, not a claim that upstream code was copied or that its license covers this repository.

This project is licensed under the [MIT License](LICENSE). Copyright (c) 2026 Charlie Rusbridger. Referenced third-party projects retain their own licenses and copyright notices.

# Troubleshooting

Start with **Allow RF control** off. Omit the optional proxy while diagnosing, because its transmission path is not blocked by that switch. Do not repeatedly transmit to compensate for uncertain wiring or protocol identification.

## Configuration cannot find packages or secrets

Run CLI commands from the repository root with an example path, for example:

```sh
esphome config examples/t-embed-cc1101.yaml
```

Keep `examples/` and `packages/` as siblings. Put private credentials in `examples/secrets.yaml`, copied from `examples/secrets.yaml.example`. Supply the exact secret names `wifi_ssid`, `wifi_password`, and `api_key`.

If copying an example into the Device Builder configuration root, copy `packages/` alongside it and change every `../packages/…` include to `packages/…`. When using `t-embed-cc1101-with-proxy.yaml`, also copy its base `t-embed-cc1101.yaml` beside it and update that file's package paths too. Put `secrets.yaml` in that root too. There is no published automatic import URL to use instead.

## Validation succeeds but compilation fails

Use the pinned development requirements and ESPHome 2026.10.1:

```sh
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
esphome compile examples/t-embed-cc1101.yaml
```

Read the first actionable compiler error. YAML validation does not type-check C++ lambdas or prove resource availability. Do not silently replace component options with guesses from a different ESPHome release.

If the failure is a font download, the T-Embed LCD needs Google Fonts `Roboto Mono` sizes 14 and 20. Restore access to the font service or deliberately adapt your private display configuration to available local fonts; RF protocol tuning will not fix a font download failure.

## Board boots but radio or display fails

Check the exact board variant, supply, common ground, SPI wiring, chip selects, and runtime logs. On the T-Embed CC1101, preserve rail enable, unused-device deselection, antenna routing, and boot ordering described in [hardware notes](hardware.md). Incorrect shared-bus initialization can look like a defective radio.

Resource-allocation errors need attention even after a successful build. The example reserves 192 receive RMT symbols and 64 transmit symbols. Remove newly added peripherals or resolve their allocation/pin conflicts before adjusting RF timing.

## No candidate packets appear

Confirm that the receive path actually initialized and that the observation interval included a deliberate press on the original remote. An interval with no confirmed press is inconclusive, not proof of incompatibility.

Check the remote battery, antenna/band, receive wiring, and distance. Change one variable at a time. Do not infer a protocol or change modulation solely because one observation interval was empty.

## Candidates appear, but lamp commands do nothing

- Confirm several distinct physical button presses yield a consistent remote identity and derived XOR key.
- Enter your own verified `remote_id` and `xor_key` substitutions and rebuild/install the edited configuration deliberately. Candidate reception never updates them automatically.
- A zero identity blocks lamp commands. **Allow RF control** must also be enabled; it turns off again after reboot.
- Check transmitter wiring and initialization independently of receiver operation.
- Check command variants, particularly night (`0x41`) and timer (`0x4D`). Do not assume all EYOCEAN lamps use this family.

Test a single authorized command and observe the actual lamp. A send log reports an attempted transmission, not acknowledgement or successful operation.

## Home Assistant does not show a light state

This is intentional. The lamp supplies no feedback, so the package exposes command buttons rather than a confirmed stateful light. Neither an RF candidate nor a send event establishes absolute brightness or power state.

## RF still transmits with lamp control disabled

If you included `packages/rf-proxy.yaml`, its endpoints are independent of the lamp guard. Remove the optional proxy from your private configuration and rebuild/install when you need that path absent. Proxy frequency metadata does not retune the radio.

## Sharing diagnostics

Share ESPHome version, board revision, selected example, redacted initialization errors, and whether a physical press was confirmed. Remove Wi-Fi credentials, API/OTA keys, addresses or names you consider private, and your remote identity/key. Do not upload `secrets.yaml`, firmware build directories, or unreviewed logs.

Passing synthetic tests or compiling does not establish lamp compatibility. Physical operation of these sanitized examples remains unverified.

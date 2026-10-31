# EYOCEAN protocol family

Reference: [bl4ko/eyocean-ha](https://github.com/bl4ko/eyocean-ha). This repository targets that published RF family; the EYOCEAN brand name is not a compatibility guarantee.

## Frame and timing

A frame is 32 bits, sent most-significant bit first:

```text
(remote_id << 16) | (cmd << 8) | (cmd ^ xor_key)
```

`remote_id` is a 16-bit remote identity; `cmd` and `xor_key` are 8-bit values. Treat the identity as belonging to a particular remote, not as a universal lamp model code.

| Symbol | High pulse | Low pulse |
| --- | --- | --- |
| Sync | 250 µs | 6250 µs |
| One | 750 µs | 250 µs |
| Zero | 250 µs | 750 µs |

Transmission repeats the frame eight times. These nominal timings describe the encoder, not a claim that every received pulse will match exactly.

## Commands

| Action | Command |
| --- | --- |
| Power | `0x51` |
| Brightness | `0x5B` |
| Colour temperature | `0x5A` |
| Reading | `0x49` |
| Night | `0x41` |
| Timer | `0x4D` |

Variants may assign commands differently, including swapping night and timer. Verify against several distinct buttons on your original remote rather than assuming this table proves compatibility.

## Candidate decoding, not learning

The receive path exposes candidate decode information. For a candidate frame, a possible XOR key is the command byte XOR the last byte. That relation is **not integrity checking or authentication**: any pair of bytes produces some candidate key.

Collect several distinct, intentionally pressed physical buttons and check that the identity and derived key stay consistent while commands change as expected. Separate background traffic from your remote. A repeated candidate by itself is not evidence of origin, correct modulation, or successful lamp control.

No receive event changes `remote_id`, `xor_key`, or other substitutions. There is no automatic pairing, learning, raw recording, or playback workflow. Enter verified values manually in your local configuration. Publish remote identities only with their owner's permission; the two pairs below were explicitly supplied for documentation.

## Known working remotes

Following the known-remotes table style in [bl4ko/eyocean-ha](https://github.com/bl4ko/eyocean-ha/tree/main#decoded-remote-codes), these are **user-reported working pairs**. The user confirms both local remotes have **six buttons**. Model numbers were not supplied, and these reports have not been independently reproduced as part of this repository's tests.

| Remote | Remote ID | XOR key | Source |
| --- | --- | --- | --- |
| Remote 1 (6 buttons) | `0xC6FB` | `0x58` | User-reported working; shared with permission |
| Remote 2 (6 buttons) | `0xB4B3` | `0x62` | User-reported working; shared with permission |

Remote 1 substitutions:

```yaml
substitutions:
  remote_id: "0xC6FB"
  xor_key: "0x58"
```

Remote 2 substitutions:

```yaml
substitutions:
  remote_id: "0xB4B3"
  xor_key: "0x62"
```

Merge **one** pair into the existing `substitutions:` block of your local example; do not add a second block or combine values from different rows. These are per-remote identities, not universal EYOCEAN defaults or a pairing mechanism. Use your own captured pair unless you are controlling a lamp that already recognizes the selected remote. The XOR key is an independent per-remote value, not something this project derives from the remote ID. Night-light and timer command assignments can still vary by model.

The runnable examples deliberately retain zero-ID defaults and require explicitly enabling **Allow RF control**; these documentation snippets do not change them.

The [README's derivation hypothesis](../README.md#xor-key-derivation-hypothesis), `high_byte(remote_id) XOR low_byte(remote_id) XOR 0x65`, matches all three known six-button remotes, including both local pairs. The upstream five-button remote does not match. This is evidence for a family-specific rule, not a universal guarantee based only on button count; the firmware continues to use the explicitly configured key.

## Transmission boundaries and state

The lamp's `send_command` path requires both **Allow RF control** enabled and a nonzero `remote_id`. The switch restores to off on every boot. The default `0x0000` identity deliberately blocks this lamp command path; `xor_key: 0x00` is only a placeholder, not a known universal key.

The optional `ir_rf_proxy` endpoints do not pass through this lamp guard. Proxy transmission and reception remain independent of the lamp switch, and a proxy frequency value is metadata, not a command to retune the CC1101. Omit the proxy if it is not required.

The lamp provides no confirmed state feedback. A transmitted power command cannot establish whether the lamp is now on or off. Brightness and colour-temperature commands likewise do not establish absolute levels. This is why controls are exposed as command buttons rather than a stateful light entity.

Synthetic encoder/decoder tests can check internal consistency. Only authorized physical tests with the intended remote, radio, and lamp can establish real compatibility; that verification has not yet been completed for these sanitized examples.

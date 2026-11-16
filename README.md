# Syncrify

**Bidirectional synchronization for Indigo and Insteon KeypadLinc devices.**

Syncrify connects Insteon KeypadLinc buttons with Indigo devices through logical Bond devices, keeping all three representations synchronized.

Rather than treating a keypad button as simply a switch, Syncrify gives each button a logical counterpart in Indigo. Changes originating from the keypad, the Bond, or the bound device are propagated to the other participants.

## What it does

Syncrify provides three-way synchronization:

- **Keypad → Bond → Device:** A physical KeypadLinc button changes its corresponding Bond and bound Indigo device.
- **Bond → Keypad → Device:** A change to the logical Bond is reflected in the physical keypad and bound device.
- **Device → Bond → Keypad:** Changes originating from the bound device are reflected in the Bond and physical keypad.

The objective is simple: regardless of where a change originates, the other participants stay in alignment.

## How it works

Syncrify creates a logical Bond for each configured KeypadLinc button.

Each Bond represents the relationship between a physical keypad button and its associated Indigo device.

This architecture provides a consistent synchronization point while keeping the physical keypad and the bound device loosely coupled.

### Keypad support

Syncrify recognizes the configured button count of each KeypadLinc.

- **6-button KeypadLinc:** Buttons B3–B6.
- **8-button KeypadLinc:** Buttons B2–B8.

The plugin uses the keypad's configuration to determine which buttons are available for bonding.

## Feedback-loop prevention

Bidirectional synchronization introduces an important challenge: changes propagated from one participant must not trigger an endless cycle of additional changes.

Syncrify incorporates intent tracking to distinguish an originating change from changes resulting from synchronization.

This allows changes to propagate in either direction without creating repetitive command loops.

## Current development status

Syncrify has been tested with multiple KeypadLinc devices and associated Indigo devices.

Current testing includes:

- Nine KeypadLinc devices.
- 35 logical Bonds.
- Keypad-to-Bond synchronization.
- Bond-to-keypad synchronization.
- Bound-device-to-Bond synchronization.
- Bidirectional propagation without feedback loops.

## Design philosophy

Syncrify is built around a simple principle:

**The keypad, the logical Bond, and the bound device should behave as three representations of the same intent.**

The synchronization mechanism should be predictable, avoid unnecessary commands, and remain stable regardless of which participant initiates a change.

---

*Syncrify is an Indigo Domotics plugin. Development and documentation are ongoing.*

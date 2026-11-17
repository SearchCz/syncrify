# Getting Started with Syncrify

## Before You Install

**A little preparation now can save you some cleanup later.**

Syncrify uses your KeypadLinc device names when naming the Bond devices it creates. Before installing Syncrify, take a moment to review the names of all your Insteon KeypadLinc devices in Indigo.

Choose names that are descriptive, consistent, and that you'll be happy to see reflected in the names of their associated Bonds.

Once you've enabled Automatic Bond Creation, Syncrify will use those names as the basis for the new Bond device names.

## Configure Syncrify

After installing and enabling the plugin, you should see the Syncrify plugin configuration window.
![](docs/images/PluginConfig.png)
The configuration window is divided into three sections: General, Automatic Bond Creation, and ReSync.

## General

### Syncrify Active

Enables or disables Syncrify's synchronization functionality.

When enabled, Syncrify monitors the relevant Indigo and Insteon activity and coordinates changes between KeypadLinc buttons, their Bonds, and their associated devices.

When disabled, Syncrify sits mostly idle but remains enabled, allowing you to make configuration changes as needed.

### Enable Debug Logging

Enables additional diagnostic information in the Indigo event log.

This is normally unnecessary during everyday operation, but can be useful when investigating unexpected behaviour, when requested as part of support, or simply if you want to peek inside the black box and see the machinations at work.

## Automatic Bond Creation

### Enable Automatic Bond Creation

When enabled, Syncrify scans your Indigo setup for configured Insteon KeypadLinc devices and automatically creates one Bond device for each available accessory button.

You don't need to create these devices individually. Syncrify can do it for you, and will repeat the process any time the plugin is restarted.

Once the Bonds have been created, you can configure each one to select the Indigo device it will control.

Disabling Automatic Bond Creation does not disable existing Bonds. It simply prevents Syncrify from automatically creating new ones.

**Pro Tip:** There's also an option in the plugin menu that will fill in the device description for you, once you've identified which device you want each Bond to control.

### Destination Folder for Bond Devices

Specifies the Indigo device folder where newly created Bond devices will be placed.

The default folder name is `Syncrify`. You can change this to an existing folder name or choose a different name for Syncrify's Bond devices.

## ReSync

ReSync provides an additional layer of reliability by keeping tabs on whether bound devices and keypad buttons reach their intended state.

If a participant doesn't appear to reach the requested state, Syncrify can re-issue the instruction automatically.

### Enable ReSync (Automatic Retries)

Enables or disables automatic retries when a synchronization instruction does not appear to have succeeded.

Disabling ReSync does not disable synchronization itself. Syncrify will still issue the initial instructions; it simply won't make additional attempts if a participant fails to reach its intended state.

### Maximum Retries After Initial Attempt

Sets the maximum number of additional attempts Syncrify will make after the initial instruction.

For example, a setting of `3` allows up to four attempts in total: the original instruction plus three retries.

### Delay Between Attempts

Specifies how long Syncrify waits before retrying an instruction that has not yet been confirmed.

The default is 15 seconds. Keep in mind that KeypadLinc buttons can take a while to respond to LED set and clear instructions, so allow enough time to avoid unnecessary repetition.

---

Once you've reviewed these settings, click **Save**. If you've enabled AutoBond, Syncrify is ready for you to start configuring your Bonds.

See [Bond Configuration](BondConfiguration.md) for the next step.
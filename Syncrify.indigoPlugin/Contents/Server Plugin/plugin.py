#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# Copyright (c) 2026, Perceptive Automation, LLC. All rights reserved.
# https://www.indigodomo.com

try:
    # This is primarily for IDEs - the indigo package is always included when a plugin is started.
    import indigo
except ImportError:
    pass

import os
import sys
import time
import time
from datetime import datetime

# Note the "indigo" module is automatically imported and made available inside
# our global name space by the host process.

################################################################################
class Plugin(indigo.PluginBase):
    ########################################
    def __init__(self, plugin_id, plugin_display_name, plugin_version, plugin_prefs):
        super().__init__(plugin_id, plugin_display_name, plugin_version, plugin_prefs)
        isDebug: bool = False

    ########################################
    def startup(self):
        self.logger.debug("startup called")
        self.bondByBoundDevice = {}
        self.bondByKeypadButton = {}
        self.bondedKeypads = {}
        indigo.devices.subscribeToChanges()
        indigo.insteon.subscribeToIncoming()
        self.obligations = {}
#        self.mapBoundDevices()
        self.mapKeypadButtons()
        autoBondEnabled = self.pluginPrefs.get("autoBondEnabled", True)

        if autoBondEnabled:
            folderName = self.pluginPrefs.get("deviceFolder", "Syncrify")
            self.createBonds(folderName)
        else:
            self.mapKeypadButtons()

        self.initBonds()

    def mapBoundDevices(self):
        return
        self.bondByBoundDevice = {}

        for bond in indigo.devices:

            if bond.deviceTypeId != "syncrifyBond":
                continue

            props = bond.pluginProps

            if not props.get("active", True):
                continue

            boundDeviceId = props.get("boundDeviceId", "")

            # No bound device? Nothing to map here.
            if not boundDeviceId:
                continue

            try:
                boundDeviceId = int(boundDeviceId)

                self.bondByBoundDevice.setdefault(
                    boundDeviceId, []
                ).append(bond.id)

                if props.get("debug", False):
                    self.logger.info(
                        f"Mapped bound device: {boundDeviceId} -> "
                        f"{bond.name} [{bond.id}]"
                    )

            except Exception as e:
                self.logger.error(
                    f"Unable to map bound device for {bond.name}: {e}"
                )
        if self.isDebugActive():
            self.logger.info(
                f"Syncrify mapped {len(self.bondByBoundDevice)} bound devices"
            )

    def mapKeypadButtons(self):

        self.bondByKeypadButton = {}
        self.bondedKeypads = {}
        self.bondByBoundDevice = {}

        for dev in indigo.devices:

            if dev.deviceTypeId != "syncrifyBond":
                continue

            props = dev.pluginProps

            if not props.get("active", True):
                continue

            keypadId = props.get("keypadId")
            keypadButton = props.get("keypadButton")
            boundDeviceId = props.get("boundDeviceId", "")

            if not keypadId or keypadButton is None:
                if self.isDebug(dev):
                    self.logger.warning(
                        f"{dev.name}: Missing keypad ID or button number"
                    )
                continue

            keypadId = int(keypadId)
            keypadButton = int(keypadButton)

            keypad = indigo.devices[keypadId]
            address = str(keypad.address).upper()

            key = (address, keypadButton)
            self.bondByKeypadButton[key] = dev.id

            # Record this keypad and its configured buttons
            self.bondedKeypads.setdefault(keypadId, []).append(keypadButton)

            if boundDeviceId:
                self.bondByBoundDevice.setdefault(
                    int(boundDeviceId), []
                ).append(dev.id)

            if self.isDebugActive(dev):
                self.logger.info(
                    f"Mapped {dev.name}: keypad={key}, "
                    f"boundDevice={boundDeviceId or 'Unassigned'}"
                )
    
    def shutdown(self):
        if self.isDebugActive():
            self.logger.debug("shutdown called")

    def toggle_debug(self):
        """Toggle plugin debug level."""
        self.isDebugActive = not self.isDebugActive
        if self.isDebugActive():
            self.logger.debug("toggling debug level off.")
        else:
            self.logger.info("toggling debug level on.")

    ########################################
    # deviceStartComm() is called on application launch for all of our plugin defined
    # devices, and it is called when a new device is created immediately after its
    # UI settings dialog has been validated. This is a good place to force any properties
    # we need the device to have, and to clean up old properties.
    def deviceStartComm(self, dev):
        # self.logger.debug(f"deviceStartComm: {dev.name}")
        props = dev.pluginProps
        if dev.deviceTypeId == "syncrifyBond":
            self.updateInsteonAddress(dev)


    ########################################
    # Relay / Dimmer Action callback
    ######################
    def actionControlDevice(self, action, dev):

        lastInstruction = dev.states.get("lastInstruction", None)
        ###### TURN ON ######
        if action.deviceAction == indigo.kDeviceAction.TurnOn:
            # Command hardware module (dev) to turn ON here:
            # ** IMPLEMENT ME **
            send_success = True        # Set to False if it failed.

            if send_success:
                # If success then log that the command was successfully sent.
                if self.isDebugActive():
                    self.logger.info(f"sent \"{dev.name}\" on")

                # And then tell the Indigo Server to update the state.
                dev.updateStateOnServer("onOffState", True)
                if lastInstruction != "ON":
                    self.register(dev, "bond", f"{dev.name} [{dev.id}]", True)
            else:
                # Else log failure but do NOT update state on Indigo Server.
                if self.isDebugActive():
                    self.logger.error(f"send \"{dev.name}\" on failed")

        ###### TURN OFF ######
        elif action.deviceAction == indigo.kDeviceAction.TurnOff:
            # Command hardware module (dev) to turn OFF here:
            # ** IMPLEMENT ME **
            send_success = True        # Set to False if it failed.

            if send_success:
                # If success then log that the command was successfully sent.
                if self.isDebugActive():
                    self.logger.info(f"sent \"{dev.name}\" off")

                # And then tell the Indigo Server to update the state:
                dev.updateStateOnServer("onOffState", False)
                if lastInstruction != "OFF":
                    if self.isDebugActive():
                        self.logger.info(f"reconciling \"{dev.name}\" off")
                    self.register(dev, "bond", f"{dev.name} [{dev.id}]", False)


            else:
                # Else log failure but do NOT update state on Indigo Server.
                if self.isDebugActive():
                    self.logger.error(f"send \"{dev.name}\" off failed")

        ###### TOGGLE ######
        elif action.deviceAction == indigo.kDeviceAction.Toggle:
            # Command hardware module (dev) to toggle here:
            # ** IMPLEMENT ME **
            new_on_state = not dev.onState
            send_success = True        # Set to False if it failed.

            if send_success:
                # If success then log that the command was successfully sent.
                if self.isDebugActive():
                    self.logger.info(f"sent \"{dev.name}\" toggle")

                # And then tell the Indigo Server to update the state:
                if new_on_state:
                    self.register(dev, "bond", f"{dev.name} [{dev.id}]", True)
                else:
                    self.register(dev, "bond", f"{dev.name} [{dev.id}]", False)

                dev.updateStateOnServer("onOffState", new_on_state)
            else:
                # Else log failure but do NOT update state on Indigo Server.
                if self.isDebugActive():
                    self.logger.error(f"send \"{dev.name}\" toggle failed")

        ###### SET BRIGHTNESS ######
        elif action.deviceAction == indigo.kDeviceAction.SetBrightness:
            # Command hardware module (dev) to set brightness here:
            # ** IMPLEMENT ME **
            new_brightness = action.actionValue
            send_success = True        # Set to False if it failed.

            if send_success:
                # If success then log that the command was successfully sent.
                if self.isDebugActive():
                    self.logger.info(f"sent \"{dev.name}\" set brightness to {new_brightness}")

                # And then tell the Indigo Server to update the state:
                dev.updateStateOnServer("brightnessLevel", new_brightness)
            else:
                # Else log failure but do NOT update state on Indigo Server.
                if self.isDebugActive():
                    self.logger.error(f"send \"{dev.name}\" set brightness to {new_brightness} failed")

        ###### BRIGHTEN BY ######
        elif action.deviceAction == indigo.kDeviceAction.BrightenBy:
            # Command hardware module (dev) to do a relative brighten here:
            # ** IMPLEMENT ME **
            new_brightness = min(dev.brightness + action.actionValue, 100)
            send_success = True        # Set to False if it failed.

            if send_success:
                # If success then log that the command was successfully sent.
                if self.isDebugActive():
                    self.logger.info(f"sent \"{dev.name}\" brighten to {new_brightness}")

                # And then tell the Indigo Server to update the state:
                dev.updateStateOnServer("brightnessLevel", new_brightness)
            else:
                # Else log failure but do NOT update state on Indigo Server.
                if self.isDebugActive():
                    self.logger.error(f"send \"{dev.name}\" brighten to {new_brightness} failed")

        ###### DIM BY ######
        elif action.deviceAction == indigo.kDeviceAction.DimBy:
            # Command hardware module (dev) to do a relative dim here:
            # ** IMPLEMENT ME **
            new_brightness = max(dev.brightness - action.actionValue, 0)
            send_success = True        # Set to False if it failed.

            if send_success:
                # If success then log that the command was successfully sent.
                if self.isDebugActive():
                    self.logger.info(f"sent \"{dev.name}\" dim to {new_brightness}")

                # And then tell the Indigo Server to update the state:
                dev.updateStateOnServer("brightnessLevel", new_brightness)
            else:
                # Else log failure but do NOT update state on Indigo Server.
                if self.isDebugActive():
                    self.logger.error(f"send \"{dev.name}\" dim to {new_brightness} failed")

        ###### SET COLOR LEVELS ######
        elif action.deviceAction == indigo.kDeviceAction.SetColorLevels:
            # action.actionValue is a dict containing the color channel key/value
            # pairs. All color channel keys (redLevel, greenLevel, etc.) are optional
            # so plugin should handle cases where some color values are not specified
            # in the action.
            action_color_vals = action.actionValue

            # Construct a list of channel keys that are possible for what this device
            # supports. It may not support RGB or may not support white levels, for
            # example, depending on how the device's properties (SupportsColor, SupportsRGB,
            # SupportsWhite, SupportsTwoWhiteLevels, SupportsWhiteTemperature) have
            # been specified.
            channel_keys = []
            using_white_channels = False
            if dev.supportsRGB:
                channel_keys.extend(['redLevel', 'greenLevel', 'blueLevel'])
            if dev.supportsWhite:
                channel_keys.extend(['whiteLevel'])
                using_white_channels = True
            if dev.supportsTwoWhiteLevels:
                channel_keys.extend(['whiteLevel2'])
            elif dev.supportsWhiteTemperature:
                channel_keys.extend(['whiteTemperature'])
            # Note having 2 white levels (cold and warm) takes precedence over
            # the use of a white temperature value. You cannot have both, although
            # you can have a single white level and a white temperature value.

            # Next enumerate through the possible color channels and extract that
            # value from the actionValue (action_color_vals).
            kv_list = []
            result_vals = []
            for channel in channel_keys:
                if channel in action_color_vals:
                    brightness = float(action_color_vals[channel])
                    brightness_byte = int(round(255.0 * (brightness / 100.0)))

                    # Command hardware module (dev) to change its color level here:
                    # ** IMPLEMENT ME **

                    if channel in dev.states:
                        kv_list.append({'key':channel, 'value':brightness})
                    result = str(int(round(brightness)))
                elif channel in dev.states:
                    # If the action doesn't specify a level that is needed (say the
                    # hardware API requires a full RGB triplet to be specified, but
                    # the action only contains green level), then the plugin could
                    # extract the currently cached red and blue values from the
                    # dev.states[] dictionary:
                    cached_brightness = float(dev.states[channel])
                    cached_brightness_byte = int(round(255.0 * (cached_brightness / 100.0)))
                    # Could show in the Event Log '--' to indicate this level wasn't
                    # passed in by the action:
                    result = '--'
                    # Or could show the current device state's cached level:
                    #    result = str(int(round(cached_brightness)))

                # Add a comma to separate the RGB values from the white values for logging.
                if channel == 'blueLevel' and using_white_channels:
                    result += ","
                elif channel == 'whiteTemperature' and result != '--':
                    result += " K"
                result_vals.append(result)
            # Set to False if it failed.
            send_success = True

            result_vals_str = ' '.join(result_vals)
            if send_success:
                # If success then log that the command was successfully sent.
                if self.isDebugActive():
                    self.logger.info(f"sent \"{dev.name}\" set color to {result_vals_str}")

                # And then tell the Indigo Server to update the color level states:
                if len(kv_list) > 0:
                    dev.updateStatesOnServer(kv_list)
            else:
                # Else log failure but do NOT update state on Indigo Server.
                if self.isDebugActive():
                    self.logger.error(f"send \"{dev.name}\" set color to {result_vals_str} failed")

    ########################################
    # General Action callback
    ######################
    def actionControlUniversal(self, action, dev):
        ###### BEEP ######
        if action.deviceAction == indigo.kUniversalAction.Beep:
            # Beep the hardware module (dev) here:
            # ** IMPLEMENT ME **
            self.logger.info(f"sent \"{dev.name}\" beep request")

        ###### ENERGY UPDATE ######
        elif action.deviceAction == indigo.kUniversalAction.EnergyUpdate:
            # Request hardware module (dev) for its most recent meter data here:
            # ** IMPLEMENT ME **
            self.logger.info(f"sent \"{dev.name}\" energy update request")

        ###### ENERGY RESET ######
        elif action.deviceAction == indigo.kUniversalAction.EnergyReset:
            # Request that the hardware module (dev) reset its accumulative energy usage data here:
            # ** IMPLEMENT ME **
            self.logger.info(f"sent \"{dev.name}\" energy reset request")

        ###### STATUS REQUEST ######
        elif action.deviceAction == indigo.kUniversalAction.RequestStatus:
            # Query hardware module (dev) for its current status here:
            # ** IMPLEMENT ME **
            self.logger.info(f"sent \"{dev.name}\" status request")

    ########################################
    # Custom Plugin Action callbacks (defined in Actions.xml)
    ######################
    def set_backlight_brightness(self, plugin_action, dev):
        try:
            new_brightness = int(plugin_action.props.get("brightness", 100))
        except ValueError:
            # The int() cast above might fail if the user didn't enter a number:
            self.logger.error(f"set backlight brightness action to device \"{dev.name}\" -- invalid brightness value")
            return
        # Command hardware module (dev) to set backlight brightness here:
        # FIXME: add implementation here
        send_success = True     # Set to False if it failed.
        if send_success:
            # If success then log that the command was successfully sent.
            self.logger.info(f"sent \"{dev.name}\" set backlight brightness to {new_brightness}")
            # And then tell the Indigo Server to update the state:
            dev.updateStateOnServer("backlightBrightness", new_brightness)
        else:
            # Else log failure but do NOT update state on Indigo Server.
            self.logger.error(f"send \"{dev.name}\" set backlight brightness to {new_brightness} failed")

    def keypadList(self, filter="", valuesDict=None, typeId="", targetId=0):
        
        menu = []
        for dev in indigo.devices:

#            self.logger.info(
#                f"{dev.name} | {dev.pluginId} | {dev.deviceTypeId} | {dev.model}"
#                )


            if "KeypadLinc" in dev.model:
                menu.append((str(dev.id), dev.name))

        return menu

    def buttonList(self, filter="", valuesDict=None, typeId="", targetId=0):
        return [
            (str(i), str(i + 1)) for i in range(8)
        ]

    def deviceList(self, filter="", valuesDict=None, typeId="", targetId=0):
        
        menu = [ (0, "Unassigned")]
        for dev in indigo.devices:


            if not ("KeypadLinc" in dev.model ):
                menu.append((str(dev.id), dev.name))

        return menu

    def deviceUpdated(self, origDev, newDev):

        debug = self.isDebugActive()
        isBond = False
        isBoundKeypad = False
        isBoundDevice = False
        isSwitched = False

        deviceId = int(newDev.id)

        #CZ

        if newDev.deviceTypeId == "syncrifyBond":
            isBond = True   
        else:
            if deviceId in self.bondByBoundDevice:
                isBoundDevice = True    

            if ("KeypadLinc" in newDev.model ):
                if int(newDev.id) in self.bondedKeypads:
                    isBoundKeypad = True
                    if debug:
                        self.logger.info(
                            f"deviceUpdated: KeypadLinc {newDev.name} [{newDev.id}]"
                        )
        
        oldState = origDev.states.get("onOffState", None)
        newState = newDev.states.get("onOffState", None)

        # Ignore updates that don't change the ON/OFF state
        if oldState == newState:
            isSwitched = False
        else:
            isSwitched = True

        # now we are ready to work with the device update. 
        # We have categorized the update to the point of being actionable. 
        # isBond, isBounKeypad, isBoundDevice, isSwitched.


        # execute depending on device type
        if isBond:
            self.bondUpdated(origDev, newDev, isSwitched)

        if isBoundDevice:
            self.boundDeviceUpdated(origDev, newDev, isSwitched)

        if isBoundKeypad:
            self.boundKeypadUpdated(origDev, newDev, isSwitched)

    def boundKeypadUpdated(self, origDev, newDev, isSwitched):

        debug = self.isDebugActive(newDev)


        changedButtons = {}

        # Determine configurable buttons
        if "6 Button" in newDev.model:
            buttons = range(3, 7)
        else:
            buttons = range(2, 9)

        for button in buttons:

            stateName = f"keypadButtonLed{button}"

            oldState = origDev.states.get(stateName, None)
            newState = newDev.states.get(stateName, None)
#            if debug:
#                self.logger.info(
#                    f"KeypadLinc {newDev.name} [{newDev.id}]: "
#                    f"Button {button}: oldState={oldState}, newState={newState}"
#               )

            if oldState != newState:
                bondId = self.bondByKeypadButton.get(
                    (str(newDev.address).upper(), button)
                )

                if bondId is None:
                    if debug:
                        self.logger.info(
                            f"No Bond found for {newDev.name}, button {button}"
                        )
                    continue

                bond = indigo.devices[bondId]

                result = self.isObligated(int(newDev.id), button, newState)

                if result is True:
                    if debug:
                        self.logger.info(
                            f"{newDev.name}: Fulfilled obligation for "
                            f"{bond.name}"
                         )
                    continue

                
                else:
                    continue

                    # Retrieve the Bond for this keypad button

                    self.register(
                        bond,
                        "key",
                        f"{newDev.name} [{newDev.id}] button {button}",
                        newState
                    )

    def boundDeviceUpdated(self, origDev, newDev, isSwitched):

        if not isSwitched:
            return

        deviceId = int(newDev.id)
        debug = self.isDebugActive()

        bondIds = self.bondByBoundDevice.get(deviceId, [])

        if debug:
            self.logger.info(
                f"Found {len(bondIds)} Bonds for {newDev.name} [{deviceId}]"
            )

        newState = newDev.states.get("onOffState", None)

        if newState is None:
            if debug:
                self.logger.info(
                    f"deviceUpdated: {newDev.name} has no onOffState"
                )
            return

        if debug:
            self.logger.info(
                f"deviceUpdated: {newDev.name} onOffState={newState}"
            )

        for bondId in bondIds:

            bond = indigo.devices[bondId]

            if debug:
                self.logger.info(
                    f"Checking Bond {bond.name} [{bond.id}]: "
                    f"active={self.isActive(bond)}, "
                    f"state={bond.states.get('onOffState', None)}"
                )

            if not self.isActive(bond):
                if debug:
                    self.logger.info(
                        f"Skipping inactive Bond {bond.name}"
                    )
                continue

            # --------------------------------------------------
            # Check whether this update fulfills an obligation
            # --------------------------------------------------

            result = self.isObligated(deviceId, 0, newState)

            if result is True:
                if debug:
                    self.logger.info(
                        f"{newDev.name}: Fulfilled obligation for "
                        f"{bond.name}"
                    )
                continue

            if result is None:
                if debug:
                    self.logger.info(
                        f"{newDev.name}: State conflicts with outstanding "
                        f"obligation for {bond.name}; obligation retained"
                    )
                continue

            # --------------------------------------------------
            # No obligation: this device may be the initiator
            # --------------------------------------------------

            bondState = bond.states.get("onOffState", None)

            if bondState != newState:

                if debug:
                    self.logger.info(
                        f"Registering new intent for {bond.name}: "
                        f"Bond state {bondState} != device state {newState}"
                    )

                self.register(
                    bond,
                    "boundDevice",
                    f"{newDev.name} [{newDev.id}]",
                    newState
                )

            elif debug:
                self.logger.info(
                    f"Skipping {bond.name}: states already match"
                )

    def bondUpdated(self, origDev, newDev, isSwitched):

        debug = self.isDebugActive(newDev)

        # --------------------------------------------------
        # Handle Bond configuration changes
        # --------------------------------------------------

        configChanged = origDev.pluginProps != newDev.pluginProps

        if configChanged:

            if debug:
                self.logger.info(
                    f"{newDev.name}: Bond configuration changed"
                )

            if (
                origDev.pluginProps.get("keypadId")
                != newDev.pluginProps.get("keypadId")
            ):
                if debug:
                    self.logger.info(
                        f"{newDev.name}: Keypad selection changed "
                        f"{origDev.pluginProps.get('keypadId')} -> "
                        f"{newDev.pluginProps.get('keypadId')}"
                    )

                self.updateInsteonAddress(newDev)

            self.mapKeypadButtons()
            self.mapBoundDevices()

        # --------------------------------------------------
        # Only proceed for an actual state transition
        # --------------------------------------------------

        if not isSwitched:
            return

        state = newDev.states.get("onOffState", None)

        if state is None:
            return

        # --------------------------------------------------
        # Identify the initiator
        # --------------------------------------------------

        initiator = newDev.states.get("lastInstructionSourceType", "")

        if debug:
            self.logger.info(
                f"{newDev.name}: State changed to "
                f"{'ON' if state else 'OFF'}; "
                f"initiator={initiator}"
            )

        # --------------------------------------------------
        # Create obligations for the other participants
        # --------------------------------------------------

        self.spawn(newDev, initiator, state)

    def insteonCommandReceived(self, cmd):
        if cmd.cmdScene is None:
            if self.isDebugActivesDebugActive():
                self.logger.debug(
                    f"Ignoring Insteon command with no scene: address={cmd.address}"
                )
            return

        key = (cmd.address.upper(), int(cmd.cmdScene))

        bondId = self.bondByKeypadButton.get(key)

        if bondId is None:
            return


        bond = indigo.devices[bondId]
        if not self.isActive(bond):
            return
        
        cmdFunc = cmd.cmdFunc

    
        if self.isDebugActive():
            self.logger.info(
                f"Keypad {key} {cmdFunc} pressed, triggering Bond {bond.name} ({bond.id})"
            )

        if cmdFunc == "on":
            self.register(bond, "key", f"{bond.name} [{bond.id}]", True)
        elif cmdFunc == "off":
            self.register(bond, "key", f"{bond.name} [{bond.id}]", False)


    def reconcileXDEELTETHISX(self, bond, initiator, iName, state):

        now = time.time()
        bond.updateStatesOnServer([
            {"key": "lastInstruction", "value": "ON" if state else "OFF"},
            {"key": "lastInstructionSourceType", "value": initiator},
            {"key": "lastInstructionSourceName", "value": iName},
            {"key": "lastInstructionEpoch", "value": int(now)},
            {
                "key": "lastInstructionDatetime",
                "value": datetime.fromtimestamp(now).strftime("%Y-%m-%d %H:%M:%S")
            }
        ])
                
        # Synchronize controlled bond
        if initiator != "bond":
            bond.updateStateOnServer("onOffState", state)
            if state:
                self.turnOn(bond.id)
            else:
                self.turnOff(bond.id)

        # Synchronize KeypadLinc
        if initiator != "key":
            keypad = indigo.devices[int(bond.pluginProps.get("keypadId"))]
            button = int(bond.pluginProps.get("keypadButton"))

            indigo.dimmer.setLedState(
                keypad.id,
                index=button - 1,
                value=state
            )


        # Synchronize bound device
        if initiator != "boundDevice":
            boundDeviceId = bond.pluginProps.get("boundDeviceId")

            if boundDeviceId:
                boundDeviceId = int(boundDeviceId)

                if state:
                    self.turnOn(boundDeviceId)
                else:
                    self.turnOff(boundDeviceId)

    def turnOn(self,deviceId):
        indigo.device.turnOn(deviceId) 

    def turnOff(self,deviceId):
        indigo.device.turnOff(deviceId) 

    def updateInsteonAddress(self, dev):

        keypadId = dev.pluginProps.get("keypadId")

        if not keypadId:
            self.logger.warning(f"{dev.name}: No KeypadLinc selected")
            return

        try:
            keypad = indigo.devices[int(keypadId)]
            address = keypad.address


            dev.updateStateOnServer("insteonAddress", str(address).upper())

            if self.isDebugActive():
                self.logger.info(
                    f"{dev.name}: Insteon address set to {address}"
                )

        except Exception as e:
            self.logger.error(
                f"{dev.name}: Unable to retrieve Insteon address: {e}"
            )

    def isActive(self, bond=None):

        if not self.pluginPrefs.get("active", True):
            return False

        if bond and not bond.pluginProps.get("active", True):
            return False

        return True

    def isDebugActive(self, bond=None):

        # Plugin-wide debug
        if self.pluginPrefs.get("debug", False):
            return True

        # Per-Bond debug
        if bond and bond.pluginProps.get("debug", False):
            return True

        return False


    def createBonds(self, folderName):

        self.mapKeypadButtons()
        reMap = False

        folderId = indigo.devices.folders.getId(folderName)

        if (folderId is None) or (folderId == 0):
            folder = indigo.devices.folder.create(folderName)
            folderId = folder.id

        self.logger.info(f"Creating Bonds in folder '{folderName}' [{folderId}]")

        for dev in indigo.devices:

            if "KeypadLinc" in dev.model:
                
                keypadId = dev.id
                address = str(dev.address).upper()
                keypadName = dev.name

                if dev.buttonConfiguredCount == 6:
                    buttons = range(3, 7)
                elif dev.buttonConfiguredCount == 8:
                    buttons = range(2, 9)
                else:
                    self.logger.warning(
                        f"{dev.name}: Unknown button configuration "
                        f"({dev.buttonConfiguredCount}); skipping"
                    )
                    continue

                for button in buttons:
                    # create Bond
                    
                    key = (address, button)

                    if key in self.bondByKeypadButton:
                        continue

                    reMap = True
                    bondName = f"{keypadName} [B{button}]"

                    props = {
                        "keypadId": str(keypadId),
                        "keypadButton": str(button),
                        "boundDeviceId": "",
                        "active": True,
                        "debug": False
                    }

                    newBond = indigo.device.create(
                        protocol=indigo.kProtocol.Plugin,
                        pluginId=self.pluginId,
                        deviceTypeId="syncrifyBond",
                        name=bondName,
                        props=props,
                        folder=folderId
                    )

                    self.logger.info(
                        f"Created new Bond: {newBond.name} [{newBond.id}]"
                    )
        if reMap:
            self.mapKeypadButtons()

    def initBonds(self):

        if self.isDebugActive():
            self.logger.info("Initializing Syncrify Bonds")

        for bond in indigo.devices:

            if bond.deviceTypeId != "syncrifyBond":
                continue

            if not self.isActive(bond):
                continue

            debug = self.isDebugActive(bond)

            try:
                keypadId = int(bond.pluginProps.get("keypadId"))
                button = int(bond.pluginProps.get("keypadButton"))

                keypad = indigo.devices[keypadId]

                boundDeviceId = bond.pluginProps.get("boundDeviceId", "")
                state = None

                # Prefer the controlled device when assigned
                if boundDeviceId:
                    try:
                        boundDevice = indigo.devices[int(boundDeviceId)]
                        state = boundDevice.states.get("onOffState", None)

                    except Exception as e:
                        self.logger.warning(
                            f"{bond.name}: Unable to read bound device "
                            f"{boundDeviceId}: {e}"
                        )

                # Otherwise use the current KeypadLinc LED state
                if state is None:
                    ledStates = keypad.ledStates

                    if button - 1 < len(ledStates):
                        state = ledStates[button - 1]
                    else:
                        self.logger.warning(
                            f"{bond.name}: Button {button} not found "
                            f"in KeypadLinc LED states"
                        )
                        continue

                # Synchronize Bond state
                if bond.states.get("onOffState") != state:
                    bond.updateStateOnServer("onOffState", state)

                # Synchronize keypad LED
                if keypad.ledStates[button - 1] != state:
                    indigo.dimmer.setLedState(
                        keypad.id,
                        index=button - 1,
                        value=state
                    )

                if debug:
                    self.logger.info(
                        f"Initialized {bond.name}: "
                        f"{'ON' if state else 'OFF'}"
                    )

            except Exception as e:
                self.logger.error(
                    f"{bond.name}: Initialization failed: {e}"
                )

        if self.isDebugActive():
            self.logger.info("Syncrify Bond initialization complete")


    def auditBond(self, bond):

        keypadId = bond.pluginProps.get("keypadId")
        button = bond.pluginProps.get("keypadButton")
        boundDeviceId = bond.pluginProps.get("boundDeviceId", "")

        self.auditBondChanges(keypadId, button, boundDeviceId, bond.name)

    def auditBondChanges(self, keypadId, button, boundDeviceId="", bondName=""):

        keypadId = int(keypadId)
        button = int(button)

        keypad = indigo.devices[keypadId]
        address = str(keypad.address).upper()

        self.logger.info("")
        self.logger.info("=" * 60)
        self.logger.info(f"Syncrify Audit: {bondName}")
        self.logger.info(f"Keypad: {keypad.name} [{address}]")
        self.logger.info(f"Button: {button}")
        self.logger.info(
            f"Bound device: {boundDeviceId or 'Unassigned'}"
        )
        self.logger.info("=" * 60)

        keypadConflicts = 0
        boundDeviceConflicts = 0
        potentialConflicts = 0

        # --------------------------------------------------
        # Scan triggers listening to the physical keypad button
        # --------------------------------------------------

        self.logger.info("SCANNING KEYPAD BUTTON TRIGGERS")

        for trigger in indigo.triggers:

            if self.isDeprecatedTrigger(trigger):
                continue

            if not hasattr(trigger, "buttonOrGroup"):
                continue


            if (
                getattr(trigger, "commandSourceType", None)
                == indigo.kDeviceSourceType.DeviceId
                and trigger.deviceId == keypadId
                and trigger.buttonOrGroup == button
            ):

                keypadConflicts += 1

                if trigger.enabled:
                    self.logger.error(
                        f"KEYPAD CONFLICT: {trigger.name} [{trigger.id}] | "
                        f"Command: {trigger.command} | "
                        f"Enabled: {trigger.enabled}"
                    )
                else:
                    self.logger.warning(
                    f"KEYPAD CONFLICT: {trigger.name} [{trigger.id}] | "
                    f"Command: {trigger.command} | "
                    f"Enabled: {trigger.enabled}"
                   )


        # --------------------------------------------------
        # Scan triggers listening to the bound device
        # --------------------------------------------------

        if boundDeviceId:

            boundDeviceId = int(boundDeviceId)

            self.logger.info("SCANNING BOUND DEVICE TRIGGERS")

            for trigger in indigo.triggers:

                if self.isDeprecatedTrigger(trigger):
                    continue

                if not isinstance(trigger, indigo.DeviceStateChangeTrigger):
                    continue

                if trigger.deviceId == boundDeviceId:

                    boundDeviceConflicts += 1

                    if trigger.enabled:
                        self.logger.error(
                            f"BOUND DEVICE CONFLICT: {trigger.name} [{trigger.id}] | "
                            f"State: {trigger.stateSelector} | "
                            f"Change: {trigger.stateChangeType} | "
                            f"Enabled: {trigger.enabled}"
                        )
                    else:
                        self.logger.warning(
                            f"BOUND DEVICE CONFLICT: {trigger.name} [{trigger.id}] | "
                            f"State: {trigger.stateSelector} | "
                            f"Change: {trigger.stateChangeType} | "
                            f"Enabled: {trigger.enabled}"
                        )

        else:
            self.logger.info("BOUND DEVICE UNASSIGNED - SKIPPING SCAN")

        # --------------------------------------------------
        # Summary
        # --------------------------------------------------

        self.logger.info("-" * 60)
        self.logger.info(
            f"Audit complete: {keypadConflicts} keypad conflicts, "
            f"{boundDeviceConflicts} bound device conflicts, "
            f"{potentialConflicts} potential conflicts"
        )
        self.logger.info("=" * 60)

    def auditBondButtonPressed(self, valuesDict, typeId, devId):

        if typeId != "syncrifyBond" or not devId:
            return valuesDict

        bond = indigo.devices[devId]

        self.logger.info(
            f"Manual audit requested for {bond.name} [{bond.id}]"
        )

        self.auditBond(bond)

        return valuesDict

    def debug1(self):
        trigger = indigo.triggers[706189818]

        self.logger.info(f"TRIGGER: {trigger.name}")

        for attr in dir(trigger):
            if not attr.startswith("_"):
                try:
                    self.logger.info(f"{attr}: {getattr(trigger, attr)}")
                except Exception as e:
                    self.logger.info(f"{attr}: <error: {e}>")

        for i, action in enumerate(trigger.actions):
            self.logger.info(f"ACTION {i + 1}: {type(action)}")

            for attr in dir(action):
                if not attr.startswith("_"):
                    try:
                        self.logger.info(f"  {attr}: {getattr(action, attr)}")
                    except Exception as e:
                        self.logger.info(f"  {attr}: <error: {e}>")

    def debug2(self):
        trigger = indigo.triggers[706189818]

        for attr in dir(trigger):
            self.logger.info(f"TRIGGER ACTION ATTRIBUTE: {attr}")

    def validateDeviceConfigUi(self, valuesDict, typeId, devId):

        if typeId == "syncrifyBond" and valuesDict.get("auditOnSave", False):

            self.logger.info("Auditing pending Bond configuration")

            self.auditBondChanges(
                valuesDict.get("keypadId"),
                valuesDict.get("keypadButton"),
                valuesDict.get("boundDeviceId", ""),
                valuesDict.get("name", "Unnamed Bond")
            )

        return (True, valuesDict)

    def isDeprecatedTrigger(self, trigger):

        if trigger.enabled:
            return False

        folderId = trigger.folderId
        folder = indigo.triggers.folders.get(folderId)

        return folder is not None and folder.name.lower() == "deprecated"

    def isObligated(self, deviceId, button, state):

        key = (deviceId, button)
        obligation = self.obligations.get(key)

        # No outstanding obligation: this is an unsolicited change
        if obligation is None:
            return False

        # Observed state matches the obligation: fulfilled
        if obligation["state"] == state:
            del self.obligations[key]
            return True

        # An obligation exists, but the reported state conflicts with it.
        # Leave the obligation intact.
        return None    


    def register(self, bond, iType, iName, state):

        if self.isDebugActive(bond):
            self.logger.info(
                f"Registering obligation for {bond.name} [{bond.id}] "
                f"initiated by {iType} ({iName}) to set state to "
                f"{'ON' if state else 'OFF'}"
            )

        now = time.time()
        bond.updateStatesOnServer([
            {"key": "onOffState", "value": state},
            {"key": "lastInstruction", "value": "ON" if state else "OFF"},
            {"key": "lastInstructionEpoch", "value": int(now)},
            {"key": "lastInstructionSourceType", "value": iType},
            {"key": "lastInstructionSourceName", "value": iName},
            {   "key": "lastInstructionDatetime",
                "value": datetime.fromtimestamp(now).strftime("%Y-%m-%d %H:%M:%S"),
            }
        ])

    def spawn(self, bond, initiator, state):

        keypadId = int(bond.pluginProps.get("keypadId", 0))
        button = int(bond.pluginProps.get("keypadButton", 0))
        boundDeviceId = int(bond.pluginProps.get("boundDeviceId", 0) or 0)

        maxRetries, retryDelay = self.getRetrySettings()

        # Keypad obligation
        if initiator != "key":
            self.createObligation(
                keypadId, button, state, maxRetries+1, retryDelay
            )

            self.executeObligation(keypadId, button)

        # Bound-device obligation
        if initiator != "boundDevice" and boundDeviceId:
            self.createObligation(
                boundDeviceId, 0, state, maxRetries+1, retryDelay
            )

            self.executeObligation(boundDeviceId, 0)

    def createObligation(self, deviceId, button, state, tries, delay):

        key = (deviceId, button)

        self.obligations[key] = {
            "deviceId": deviceId,
            "button": button,
            "state": state,
            "tries": tries,
            "delay": delay,
            "due": 0
        }


    def executeObligation(self, deviceId, button):

        key = (deviceId, button)
        obligation = self.obligations.get(key)

        if obligation is None:
            return

        tries = obligation["tries"]

        if tries <= 0:
            return

        state = obligation["state"]

        if button is not None and button > 0:
            # KeypadLinc LED
            indigo.dimmer.setLedState(
                deviceId,
                index=button - 1,
                value=state
            )
        else:
            # Bound device
            if state:
                indigo.device.turnOn(deviceId)
            else:
                indigo.device.turnOff(deviceId)

        obligation["tries"] -= 1
        obligation["due"] = time.time() + obligation["delay"]
        delay = obligation["delay"]

        if self.isDebugActive():

            self.logger.info(
                f"Executed obligation for device {deviceId}, "
                f"button {button}: {'ON' if state else 'OFF'}, "
                f"attempts remaining={obligation['tries']}, "
                f"next retry in {delay} seconds @={datetime.fromtimestamp(obligation['due']).strftime('%H:%M:%S')}"
            )


    def runConcurrentThread(self):

        while not self.stopThread:


            try:
                if self.isDebugActive():
                    self.dumpObligations()
                self.executeObligations()
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")

            self.sleep(15)

    def executeObligations(self):

        if not self.pluginPrefs.get("reSyncEnabled", True):
            return

        now = time.time()

        for deviceId, button in list(self.obligations.keys()):

            obligation = self.obligations.get((deviceId, button))

            if not obligation:
                continue

            if obligation["tries"] <= 0:
                continue

            if now >= obligation["due"]:
                self.executeObligation(deviceId, button)

    def dumpObligations(self):

        now = time.time()
        nowFormatted = datetime.fromtimestamp(now).strftime("%Y-%m-%d %H:%M:%S")

        self.logger.info(
            f"========== SYNCRIFY OBLIGATIONS | NOW: {nowFormatted} =========="
        )

        if not self.obligations:
            self.logger.info("No outstanding obligations.")
            return

        for key, obligation in self.obligations.items():

            deviceId = obligation["deviceId"]
            button = obligation["button"]
            state = obligation["state"]
            tries = obligation["tries"]
            due = obligation.get("due", 0)

            deviceName = indigo.devices[deviceId].name

            dueFormatted = (
                datetime.fromtimestamp(due).strftime("%Y-%m-%d %H:%M:%S")
                if due else "Not scheduled"
            )

            executable = tries > 0 and now >= due
            executionStatus = "YES" if executable else "NO"

            self.logger.info(
                f"Device: {deviceName} [{deviceId}] | "
                f"Button: {button if button else 'N/A'} | "
                f"Desired: {'ON' if state else 'OFF'} | "
                f"Attempts remaining: {tries} | "
                f"Due: {dueFormatted} | "
                f"Executable: {executionStatus}"
            )

        self.logger.info("========== END OBLIGATIONS ==========")

    def dumpKeypadMappings(self):

        self.logger.info("========== SYNCRIFY KEYPAD MAPPINGS ==========")

        for (address, button), bondId in self.bondByKeypadButton.items():

            bondName = indigo.devices[bondId].name

            self.logger.info(
                f"Keypad address: {address} | "
                f"Button: {button} | "
                f"Bond: {bondName} [{bondId}]"
            )

        self.logger.info("")

        for keypadId, buttons in self.bondedKeypads.items():

            keypadName = indigo.devices[keypadId].name

            self.logger.info(
                f"Keypad: {keypadName} [{keypadId}] | "
                f"Configured buttons: {sorted(buttons)}"
            )

        self.logger.info("========== END KEYPAD MAPPINGS ==========")

    def dumpBoundDeviceMappings(self):

        self.logger.info("========== SYNCRIFY BOUND DEVICE MAPPINGS ==========")

        if not self.bondByBoundDevice:
            self.logger.info("No bound devices mapped.")

        for deviceId, bondIds in self.bondByBoundDevice.items():

            deviceName = indigo.devices[deviceId].name

            self.logger.info(
                f"Bound device: {deviceName} [{deviceId}]"
            )

            for bondId in bondIds:
                bondName = indigo.devices[bondId].name

                self.logger.info(
                    f"    Bond: {bondName} [{bondId}]"
                )

        self.logger.info("========== END BOUND DEVICE MAPPINGS ==========")

    def updateBondDescriptions(self):
        updated = 0
        skipped = 0
        errors = 0

        self.logger.info("Updating Bond descriptions...")

        for bond in indigo.devices:
            if bond.deviceTypeId != "syncrifyBond":
                continue

            # Preserve any existing description
            if bond.description.strip():
                skipped += 1
                continue

            boundDeviceId = bond.pluginProps.get("boundDeviceId")

            if not boundDeviceId:
                skipped += 1
                continue

            try:
                boundDevice = indigo.devices[int(boundDeviceId)]

                description = (
                    f"Bound to {boundDevice.protocol} "
                    f"{boundDevice.model} "
                    f"{boundDevice.name} "
                    f"[{boundDevice.id}]"
                )

                bond.description = description
                bond.replaceOnServer()

                updated += 1

                self.logger.info(
                    f"Updated description for {bond.name}: {description}"
                )

            except Exception as e:
                errors += 1
                self.logger.error(
                    f"Unable to update description for "
                    f"{bond.name} [{bond.id}]: {e}"
                )

        self.logger.info(
            f"Bond description update complete: "
            f"{updated} updated, {skipped} skipped, {errors} errors."
        )

    def getRetrySettings(self):
        try:
            maxRetries = max(
                0, int(self.pluginPrefs.get("maxRetries", 3))
            )
        except (TypeError, ValueError):
            maxRetries = 3

        try:
            retryDelay = max(
                1, int(self.pluginPrefs.get("retryDelay", 5))
            )
        except (TypeError, ValueError):
            retryDelay = 5

        return maxRetries, retryDelay

    def closedPrefsConfigUi(self, valuesDict, userCancelled):

        if userCancelled:
            return

        autoBondEnabled = valuesDict.get(
            "autoBondEnabled",
            self.pluginPrefs.get("autoBondEnabled", False)
        )

        folderName = valuesDict.get(
            "autoBondFolder",
            self.pluginPrefs.get("autoBondFolder", "Syncrify")
        )

        if autoBondEnabled:
            self.logger.info("AutoBond enabled. Checking for missing Bonds...")
            self.createBonds(folderName)

        # Always rebuild mappings, whether AutoBond is enabled or not.
        self.mapKeypadButtons()

    def findExistingBond(self, keypadId, button, excludeBondId=None):

        for dev in indigo.devices.iter("self.syncrifyBond"):

            if excludeBondId is not None and dev.id == excludeBondId:
                continue

            props = dev.pluginProps

            if (int(props.get("keypadId", 0)) == int(keypadId)
                    and int(props.get("keypadButton", 0)) == int(button)):
                return dev

        return None


    def validateDeviceConfigUi(self, valuesDict, typeId, devId):

        keypadId = valuesDict.get("keypadId")
        button = valuesDict.get("keypadButton")

        if not keypadId or not button:
            return True, valuesDict

        keypadId = int(keypadId)
        button = int(button)

        for dev in indigo.devices.iter("self.syncrifyBond"):

            # Exclude the Bond currently being edited.
            if devId and dev.id == devId:
                continue

            props = dev.pluginProps

            existingKeypad = int(props.get("keypadId", 0))
            existingButton = int(props.get("keypadButton", 0))

            if existingKeypad == keypadId and existingButton == button:

                keypad = indigo.devices.get(keypadId)
                keypadName = keypad.name if keypad else str(keypadId)

                errorMessage = (
                    f"{keypadName}, button {button}, "
                    f"is already assigned to Bond '{dev.name}'. "
                    f"Each physical keypad button can only have one Bond."
                )

                self.logger.warning(
                    f"Bond configuration rejected: {errorMessage}"
                )

                return False, valuesDict, errorMessage

        return True, valuesDict

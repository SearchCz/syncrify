# Bond Configuration

Each Syncrify Bond represents the relationship between one physical KeypadLinc accessory button and the Indigo device you want it to control.
![[docs/images/BondConfig.png]]
Configuring a Bond is straightforward. There are just a few things to understand about the choices available.

## KeypadLinc

Select the Insteon KeypadLinc device that contains the physical button represented by this Bond.

**Important:** If you used Automatic Bond Creation, leave this field alone. Syncrify has already assigned the correct KeypadLinc to each Bond.

This field is primarily for users who prefer to create their Bonds individually rather than using AutoBond.

## Keypad Button

Select the accessory button on the selected KeypadLinc.

Again, if Syncrify created your Bonds using AutoBond, you should leave this setting unchanged.

**One Bond per button:** Syncrify allows only one Bond for each KeypadLinc/button combination. You cannot create multiple Bonds representing the same physical button.

For those creating Bonds manually, simply select the desired KeypadLinc and button combination.

## Bound Device

This is where you choose the Indigo device you want the physical button to control.

It can be a light, plug, Roomify Room, or any other compatible Indigo on/off device.

Once assigned, Syncrify keeps the Bond, physical button, and bound device synchronized. Changes can originate from any of the three participants.

## Active

Enables or disables synchronization for this particular Bond.

You can temporarily deactivate a Bond without deleting it or disturbing its configuration.

## Enable Debug Logging

Enables additional diagnostic logging for this Bond.

Normally, you can leave this disabled. It can be useful when investigating unexpected behaviour or when looking for more detail about the synchronization activity involving a particular button.

## Audit automation conflicts whenever this Bond is saved

This is a handy diagnostic, particularly if you're migrating an existing Indigo setup to Syncrify.

When enabled, Syncrify examines your Indigo triggers whenever this Bond is saved. It looks for triggers that are activated by either the specific KeypadLinc/button combination represented by this Bond or the device assigned as its Bound Device.

Any matching triggers are reported in the Indigo event log, with different levels of emphasis depending on their status and location:

- **Active triggers — Error:** Any active matching trigger is reported as an error, regardless of which folder it's in. This is a visual warning to make it stand out; it doesn't necessarily mean Indigo has encountered an actual error.
    
- **Deactivated triggers — Warning:** Deactivated matching triggers are reported as warnings unless they're already in the `deprecated` folder.
    
- **Deactivated triggers in** `**deprecated**` **— Ignored:** These are deliberately excluded from the report. Once you've reviewed and retired an old trigger, you won't keep seeing it flagged every time you save the Bond.
    

The idea is to help you find existing trigger-based automation that may now be redundant because Syncrify is handling that relationship for you.

**My recommendation:** Don't immediately delete those triggers. Deactivate them first and move them into a separate folder named `deprecated`. That way, you can see how everything behaves with Syncrify in control, while keeping the original automation available if you need to revisit it.

That's exactly what I did when migrating my own setup. Once I was satisfied that Syncrify was doing the job, the old triggers could stay retired.

---

That's it! Once you've selected the Bound Device and saved the Bond, Syncrify takes care of keeping the participants in sync.

## Pro Tip: Bond Descriptions

Once you've assigned a Bound Device to your Bonds, you can use the **plugin menu option to populate device descriptions**. 

Syncrify fills in the descriptions to make each Bond's relationship to its KeypadLinc button and controlled device easier to recognize throughout Indigo. Only Sybcrify Bonds that have no description will be included. 

This is especially useful when you've created a large number of Bonds using AutoBond, and makes each button's purpose clear in Indigo. Here's an example from my setup:

![[docs/images/kepadExample.png]]
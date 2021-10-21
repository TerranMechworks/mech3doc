# Overview

## Installer

The MW3 installer is quite flexible, allowing selection of only some features to save hard drive space. The components and sub-components listed for a custom installation are:

* Program files
  * Codec Files
* AVI files
* Software Render Files
  * Low Detail
  * Medium Detail
  * Best Detail
* 3D Accelerator Files
  * 2 MB Card
  * 4 MB Card
  * 8 MB Card+
* Sound
  * High Fidelity
  * Low Fidelity

Some files not directly installed that are discussed are ambient tracks and save games.

Please note that while many files have the ending `.zbd`, this does not mean they are in any way similar. Different `.zbd` files need to be parsed differently (they aren't even all [archive files](archive-files.md)). It's possible `.zbd` stands for Zipper Binary Data. 

## Ambient tracks

The [ambient tracks](ambient-tracks.md) are never installed, and always streamed from the CD.

## AVI files

If the [AVI/video files](avi-files.md) are not installed, they will be read from the CD. These are the game intro, and cut scenes/mission briefings.

## Sound

The high fidelity and low fidelity options installed `soundsH.zbd` and `soundsL.zbd` to the `zbd` directory, respectively. These are both [sound archives](sound-archives.md). The demo only ships with medium fidelity sounds (`soundsM.zbd`). Additionally, the 1.2 patch installs some loose `.wav` files into the `zbd` directory.

## Software render files

The software render files component installs textures for the software rendering to the `zbd` directory. They are largely campaign-specific.

For low detail `c1\texture1.zbd`, `c2\texture1.zbd`, `c3\texture1.zbd`, `c4\texture1.zbd`, `c4b\texture1.zbd`, and `t1\texture1.zbd` are installed.

For medium detail `c1\texture2.zbd`, `c2\texture2.zbd`, `c3\texture2.zbd`, `c4\texture2.zbd`, `c4b\texture2.zbd`, and `t1\texture2.zbd` are installed.

For best detail `c1\texture.zbd`, `c2\texture.zbd`, `c3\texture.zbd`, `c4\texture.zbd`, `c4b\texture.zbd`, and `t1\texture.zbd` are installed.

In each case, the 'mech textures `rmechtexs.zbd` are also installed.

All of these files are [texture packages](texture-packages.md). The textures for software rendering are largely palette-based.

## 3D accelerator files

The 3d accelerator files component installs textures for the hardware rendering to the `zbd` directory. They are largely campaign-specific.

For 2 MB cards `c1\rtexture2.zbd`, `c2\rtexture2.zbd`, `c3\rtexture2.zbd`, `c4\rtexture2.zbd`, `c4b\rtexture2.zbd`, and `t1\rtexture2.zbd` are installed.

For 4 MB cards `c1\rtexture3.zbd`, `c2\rtexture3.zbd`, `c3\rtexture3.zbd`, `c4\rtexture3.zbd`, `c4b\rtexture3.zbd`, and `t1\rtexture3.zbd` are installed.

For 8 MB+ cards `c1\rtexture.zbd`, `c2\rtexture.zbd`, `c3\rtexture.zbd`, `c4\rtexture.zbd`, `c4b\rtexture.zbd`, and `t1\rtexture.zbd` are installed.

In the 2 MB case, the 'mech textures `rmechtex16.zbd` are also installed; otherwise, the 'mech textures `rmechtex.zbd` are also installed. 

All of these files are [texture packages](texture-packages.md). The textures for 3d accelerator rendering are not palette-based, but do have a reduced bit depth. 

## Program files

The program files component installs the following files to the specified install location:

* `force_eff.ifr`: Probably force-feedback effects. I think this was a technology developed by the Immersion Corporation. The file extension `.ifr` stands for "Immersion Force Resource", which are pre-built effects authored in a tool called Immersion Studio. It's not clear how the game engine used these, and they deserve more investigation.
* `Mech3.exe`: The main game engine executable. Not further discussed.
* `Mech3.icd`: Only present for the German version, probably related to the SafeDisc DRM. Discussed tangentially in [the introduction](introduction.md); otherwise not further discussed.
* `Mech3Msg.dll`: A resource dynamic link library (DLL), which contains localised messages. Discussed in [message table/translations](mech3msg.md).
* `MSN Gaming Zone.url`: A Windows Internet Shortcut file, presumably to the MSN Gaming Zone, now known as MSN Games. Not further discussed.
* `ReadMe.doc` or `readme.doc`, `ReadMe.txt` or `readme.txt`: The READMEs for the game in both Microsoft Word (`.doc`) and plain text (`.txt`) format. Not further discussed.
* `Uninstl.ddl` and `Uninstall.isu`: Support files for the InstallShield uninstaller. Not further discussed.

These files are also installed on the system:

* `arial.ttf`, `impact.ttf`, and `lucon.ttf`: Font files the game engine needs.
* `IFORCE2.dll`: Probably force-feedback effects, see `force_eff.ifr`.
* `MSVCRT.DLL`, `msvcirt.dll`, `MSVCRT40.DLL`, and `MSVCP50.DLL`: Support the Microsoft Visual C/C++ Runtime. These could be used to determine which MSVC version was used. Not further discussed.
* `MFC40.DLL` and `MFC42.DLL`: [Microsoft Foundation Class Library](https://docs.microsoft.com/en-us/cpp/mfc/mfc-desktop-applications) (MFC) dependencies. Not further discussed.

The codec sub-component also installs `Ir50_32.dll`. This video codec is relevant for the [AVI files](avi-files.md).

The program files component also installs all the necessary game files to the `zbd` directory in the specified install location. These are called [database files](#database-files), and have their own section below.

## Database files

Database files are installed by the program files component. There are a lot of data files, and can be grouped into various categories. In general, database files are either:

* global, in the root `zbd` directory
* operation or chapter specific. The sub-directories `c1`, `c2`, `c3`, `c4`, `c4b`, and `t1` seem to correspond to the operations of the campaign. `t1` for the training operation, and `c1` to `c4` for the main campaign's operations/chapters. One oddity is `c4b`, which is possibly split off because the third and fourth operations (`c3`/`c4`) had 6 missions each (instead of four), and there was some kind of game engine limitation
* mission specific. Multiplayer or instant action scenarios are also "missions" associated with a specific operation/chapter. These are identified by the file name's suffix, e.g. `m1` for mission 1, `mp1` for multiplayer map 1, and `ia1` for instant action scenario 1.

### Texture packages

The `rimage.zbd` provides globally-used images, such as UI elements, menu backgrounds, and more. This file is a [texture package](texture-packages.md), and can be read in the same way software render files and 3D accelerator files are read.

### Reader archives

[Reader archives](reader-archives.md) contain game configuration. They can be global (`reader.zbd`), campaign-specific (`c1\reader.zbd`, `c2\reader.zbd`, `c3\reader.zbd`, `c4\reader.zbd`, `c4b\reader.zbd`, `t1\reader.zbd`), mission-specific (`<chapter directory>\readerm*.zbd`), multiplayer maps (`<chapter directory>\readermp*.zbd`), or instant action scenarios (`<chapter directory\readeria*.zbd`). This is the full list:

* `reader.zbd`
* `c1\reader.zbd`
* `c2\reader.zbd`
* `c3\reader.zbd`
* `c4\reader.zbd`
* `c4b\reader.zbd`
* `t1\reader.zbd`
* `c1\readeria1.zbd`
* `c1\readeria2.zbd`
* `c1\readeria3.zbd`
* `c1\readerm1.zbd`
* `c1\readerm2.zbd`
* `c1\readerm3.zbd`
* `c1\readerm4.zbd`
* `c1\readermp1.zbd`
* `c1\readermp2.zbd`
* `c2\readeria1.zbd`
* `c2\readeria2.zbd`
* `c2\readeria3.zbd`
* `c2\readerm1.zbd`
* `c2\readerm2.zbd`
* `c2\readerm3.zbd`
* `c2\readerm4.zbd`
* `c2\readermp1.zbd`
* `c2\readermp2.zbd`
* `c3\readeria1.zbd`
* `c3\readeria2.zbd`
* `c3\readeria3.zbd`
* `c3\readerm1.zbd`
* `c3\readerm2.zbd`
* `c3\readerm3.zbd`
* `c3\readerm4.zbd`
* `c3\readerm5.zbd`
* `c3\readerm6.zbd`
* `c3\readermp1.zbd`
* `c3\readermp2.zbd`
* `c4\readeria1.zbd`
* `c4\readeria2.zbd`
* `c4\readeria3.zbd`
* `c4\readerm1.zbd`
* `c4\readerm2.zbd`
* `c4\readerm3.zbd`
* `c4\readermp1.zbd`
* `c4\readermp2.zbd`
* `c4b\readerm4.zbd`
* `c4b\readerm5.zbd`
* `c4b\readerm6.zbd`
* `t1\readeria1.zbd`
* `t1\readerm1.zbd`
* `t1\readerm2.zbd`
* `t1\readerm3.zbd`
* `t1\readerm4.zbd`
* `t1\readermp1.zbd`

Two more multiplayer maps are provided by the 1.2 patch: `c3\readermp3.zbd` and `c3\readermp4.zbd`.

### Interpreter scripts

The [interpreter scripts](interpreter-scripts.md) (`interp.zbd`) drive how the game engine loads the game data/worlds.

### Mechlib archive

A single [mechlib archive](mechlib-archives.md) is installed, `mechlib.zbd`. This contains 'mech and mechlib model data.

### Motion archive

A single [motion archive](motion-archives.md) is installed, `motion.zbd`. This contains the animation data for 'mech motion (e.g. walking).

### Game world data

The game world data is called `gamez.zbd`, and so also known as [GameZ files](gamez-files.md). Each operation/chapter has its own game world data in the sub-directory:

* `c1\gamez.zbd`
* `c2\gamez.zbd`
* `c3\gamez.zbd`
* `c4\gamez.zbd`
* `c4b\gamez.zbd`
* `t1\gamez.zbd`

### Animation definition archives

While animation definitions are provided in some [reader archives](#reader-archives), they are also present in a compiled form in [animation definition files](anim-files.md), called `anim.zbd`. These correspond to each game world:

* `c1\anim.zbd`
* `c2\anim.zbd`
* `c3\anim.zbd`
* `c4\anim.zbd`
* `c4b\anim.zbd`
* `t1\anim.zbd`

## Save games

TODO

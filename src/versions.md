# MechWarrior 3 versions

## Base game

In the US, there seem to have been a few releases: version 1.0, 1.1, 1.2, and Gold Edition. They can all be patched to 1.2. Presumably there was also a 1.1 patch (which I have not been able to find). In a weird quirk, the Gold Edition Readme says it is version 1.2, but it is still missing two multiplayer maps, `zbd/c3/readermp3.zbd` and `zbd/c3/readermp4.zbd`. Applying the 1.2 patch will install these.

Localisations and versions:
* English (US): 1.0, 1.1, 1.2, Gold Edition
* German (DE): 1.0, 1.2 patch exists
* French (FR): 1.0, 1.2 patch exists
* Italian (IT): Unconfirmed
* Japanese (JA): 1.2 (メックウォリア３)
* Taiwanese (TW): An extremely believable big box edition exists on eBay, but is horrendously expensive (機甲爭霸戰3, see [BattleTech on zh.wikipedia.org](https://zh.wikipedia.org/zh-hant/BattleTech) or [chiuinan.github.io](https://chiuinan.github.io/game/game/intro/eng/e51/mech3.htm))
* Chinese/Hong Kong: Unconfirmed (Simplified: 机甲战士3, Traditional: 機甲戰士3, see [BattleTech on zh.wikipedia.org](https://zh.wikipedia.org/zh-hant/BattleTech) or [chiuinan.github.io](https://chiuinan.github.io/game/game/intro/eng/e51/mech3.htm))
* English (GB): Unconfirmed if this is different than US, although redumps exist
* Russian (RU): Unconfirmed, possibly a bootleg/fan translation only

Please do reach out if you have a version I'm missing. I would love to confirm the information holds for all versions.

I have installed all versions in a virtual machine, gathered the files, patched the versions to 1.2, and gathered the files again. This has allowed me to find differences, but also check that the structures, value-ranges, and methods should hold.

## Expansion

I know a lot less about the Pirate's Moon expansion. For one, I never played it, as it was never released in German.

My focus has also been mainly on the base game, and there's still enough unknown information it that. I also only own a single US version of PM. Still, the code from the base game was easy enough to apply to Pirate's Moon, so some things could be discovered. When Pirate's Moon-specific information is known, it is noted in this project.

## System requirements

MechWarrior 3 only runs on Windows, and required DirectX 6.1. It is probably a 32-bit executable, given the time frame. And it was likely programmed in C++, specifically Microsoft Visual C++ based on the dependencies. MechWarrior 3 came on a standard CD-ROM.

| Spec                  | Minimum               | Recommended           |
|-----------------------|-----------------------|-----------------------|
| Operating system (OS) | Windows 95            | Windows 98            |
| Processor (CPU)       | Intel Pentium 166 MHz | Intel Pentium 200 MHz |
| System memory (RAM)   | 32 MB                 | 64 MB                 |
| Hard disk drive (HDD) | 240 MB                | 390 MB                |
| Video card (GPU)      | 2 MB of VRAM          | 8 MB of VRAM          |

## DRM

The PC Gaming Wiki claims [MechWarrior 3 is protected by Macrovision's SafeDisc DRM](https://pcgamingwiki.com/wiki/MechWarrior_3). At the time MW3 was released, only SafeDisc version 1 was available. Instructions from [CD Media World](https://www.cdmediaworld.com/hardware/cdrom/cd_protections_safedisc.shtml) on how to detect SafeDisc protection:

> The following files should exist on every the original CD: **00000001.TMP**, **CLCD16.DLL**, **CLCD32.DLL**, **CLOKSPL.EXE**, **DPLAYERX.DLL**

> There is always a **GAME.EXE** and **GAME.ICD** file where the **.ICD** is the original game executable (in encrypted form) and the **.EXE** is a loader containing a parts of the **SafeDisc** protection.

(Formatting edited for readability.) The [Wine mailing list agrees](https://www.winehq.org/pipermail/wine-users/2002-April/007910.html) largely, sometimes `SECDRV.SYS` and `DRVMGT.DLL` are also found.

None of the US version I own have any of these files, the German version does though. It is possible the US versions have an earlier variant of SafeDisc copy protection, based on the earlier SafeAudio copy protection It uses weak sectors to detect when a disk has been copied. (For more information, see [this CD Freaks/Myce article](https://www.myce.com/article/SafeDisc-2-Explained-and-Defeated___-181/) on SafeDisc 2.)

There are indications something odd is present on US disks. When I list the `video` directory, the date of the parent directory (`..`) is always mangled:

Version 1.00 (DE):

```plain
04/06/1999  02:25    <DIR>          .
04/06/1999  02:25    <DIR>          ..
```

Version 1.00 (US):

```plain
12/05/1999  02:18    <DIR>          .
The parameter is incorrect.
<0x16>?      <DIR>          ..
```

Version 1.1 (US):

```plain
09/07/1999  12:01    <DIR>          .
The parameter is incorrect.

?      <DIR>                              ..
```

Version 1.2 (US):

```plain
05/10/1999  08:35    <DIR>          .
<0x11>?      <DIR>          ..
```

SafeDisc itself is a liability, as the driver [contains a buffer overflow vulnerability (CVE-2007-5587)](https://nvd.nist.gov/vuln/detail/CVE-2007-5587).

I don't want to comment too much on DRM, although as a customer, it has always been an annoyance and a hindrance for me. It is a concern for any effort legally examining the game. Some countries allow circumventing DRM for abandoned products or legitimate fair use. Some don't. This is why I've approached the project by installing the game, and then working on binary files. No DRM is bypassed.

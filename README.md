# Cosmote3GCPatcher aka (CosmoPatcher)

Cosmote3GCPatcher is a utility designed to patch the COSMOTE Connect 3G application, allowing you to route your connection through standard Wi-Fi instead of relying on COSMOTE's discontinued servers.

   - [**NOTE!**]
    Work in Progress (WIP): This tool currently only supports the Romanian version of COSMOTE Connect 3G. Support for Greek modem versions will be added in a future update once hardware is acquired.

Before running the script, ensure you have the following installed and prepared:

   - Python (Latest stable version i think idk)

   - COSMOTE Connect 3G (should be in the releases tab)

   - Modem Adapter (e.g., compatible Huawei/ZTE USB or wireless adapter, example: Huawei E171, E173, ZTE MF637, Cosmote Connect MF60 etc.)
   - (P.S, patch for Cosmote Connect MF60 will be made once the hardware is obtained)

   - Frida (Optional; strictly required only if you plan to modify or patch the source scripts)

   - pyserial (recommended only if you do not have a standard modem adapter connected to your PC/laptop)

ㅤㅤㅤㅤㅤ
# HOW TO RUN :

- Make sure you have COSMOTE Connect 3G installed (version doesn't matter).

- Install all the project files on your pc.

- Add the Python files inside of the COSMOTE Connect 3G folder (C:\Program Files (x86)\COSMOTE Connect 3G)

- Run the pre-init.bat file

- Open your terminal and type either init.py or tester.py (both do almost the same thing but tester has some debug stuff)

- Open COSMOTE Connect 3G and click Connect (Or Redial if you connected before).

- Pray it connects.


# What does this do exactly? (If you didn't understand)
CosmoPatcher (a.k.a Cosmote3GCPatcher) essentially revives old hardware and modems.

Since the original servers, for the COSMOTE Connect 3G network are no longer working, old modems cannot connect on their own. CosmoPatcher fixes this by sending your data through Wi‑Fi, avoiding the dead COSMOTE network and letting your system work again.

# Credits
```
XercesRe (main developer)
ST3HEN (main developer #2)

```
# Notes
 - My COSMOTE Connect 3G client is version 11.301.05.04.709, the software may vary for other versions like v16.001 – v21.003.
 - It *will* not work with ZTE USB's since the software is meant for Huawei USB's, but if it won't work with ZTE devices, i will note them for future updating
 - As shown above this note, again, for versions v2.7.2.89 (Birdstep) and/or BD_COSMOTEMF60V1.0.0B01 (WebUI), it *will* not work, but v11.1xx and above works.
 - I am not sure if this software will work below Windows 10 (e.g. Windows 8.1, Windows 7, Windows XP) but again, updates will be happening for older versions too


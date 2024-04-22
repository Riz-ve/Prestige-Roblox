import os, json, time, threading, urllib.request, shutil
from playsound import playsound
from src.prestige import Prestige
from pystyle import Colorate, Colors, Center
os.system("cls")

if not os.path.isdir("src"):
    os.makedirs("src")
if not os.path.isfile("src/data.json"):
    open("src/data.json", "x").close()
    print(Colors.dark_gray + "Successfully created file src/data.json")

Prestige = Prestige()
try:
    with open("src/data.json", "r+") as file:
        default = json.dumps({
                            "settings": {
                                "basic": {
                                    "play-sound": True,
                                    "banner": "      :::::::::  :::::::::  :::::::::: :::::::: ::::::::::: ::::::::::: ::::::::  ::::::::::\n     :+:    :+: :+:    :+: :+:       :+:    :+:    :+:         :+:    :+:    :+: :+:\n    +:+    +:+ +:+    +:+ +:+       +:+           +:+         +:+    +:+        +:+\n   +#++:++#+  +#++:++#:  +#++:++#  +#++:++#++    +#+         +#+    :#:        +#++:++#\n  +#+        +#+    +#+ +#+              +#+    +#+         +#+    +#+   +#+# +#+\n #+#        #+#    #+# #+#       #+#    #+#    #+#         #+#    #+#    #+# #+#\n###        ###    ### ########## ########     ###     ########### ########  ##########\nBy .rizve",
                                    "skip-on-valid-pattern": False # Takes less time to inject (more likely to fail)
                                },
                                "advanced": {
                                    "list-items": False, # Lists the instances as we scan through
                                    "multi-inject": False # Inject on different clients
                                }
                            },
                            "assets": {
                                "success": "https://drive.usercontent.google.com/download?id=1sHUDhicdC26hzfvUu2tDI-gQNqWzeiEE&export=download&authuser=0&confirm=t&uuid=5d893c00-ef5d-45a8-bd02-f20c09312707&at=APZUnTWfZEYOS2jPzLSiCZw_GoMR:1713808518787",
                                "fail": "https://drive.usercontent.google.com/download?id=1BOdAAvuewyPr6s2_ipNu3BEhu4cMILL5&export=download&authuser=0&confirm=t&uuid=8d72b563-70fd-428b-95c8-ffe73ce747d7&at=APZUnTW2rJmljh9xbEp_dw5DM7SK:1713809563527"
                            }
                        }, indent = 6)
        try:
            data = json.load(file)
            data["settings"]
            data["settings"]["basic"]
            data["settings"]["advanced"]
            data["assets"]
        except Exception as e:
            print(Colors.StaticRGB(49, 38, 252) + "[PRESTIGE]: Data error\n" + Colors.dark_gray + "  ↑ Loading Defaults...")
            file.seek(0)
            file.truncate()
            file.write(default)
            print("    ↑ Successfuly Loaded Defaults")
            data = json.loads(default)
except Exception as e:
    input(Colors.StaticRGB(49, 38, 252) + "[PRESTIGE]: Failed to Load Data\n  ↑ " + Colors.dark_gray + str(e))
    exit()

if os.path.exists("src/assets") and os.path.isfile("src/assets/NOT LOADED"):
    print(Colors.StaticRGB(49, 38, 252) +"We could not finish downloading our assets on the last run")
    shutil.rmtree("src/assets")

if not os.path.exists("src/assets"):
    os.mkdir("src/assets")
    open("src/assets/NOT LOADED", "x").close()
    print(Colors.dark_gray + "Successfully created folder src/assets\n"+ Colors.StaticRGB(49, 38, 252) +"Now downloading assets...")

    try:
        urllib.request.urlretrieve(data["assets"]["success"], "src/assets/success.wav")
        print(Colors.dark_gray + "  ↑ Downloaded src/assets/success.wav")

        urllib.request.urlretrieve(data["assets"]["fail"], "src/assets/fail.wav")
        print(Colors.dark_gray + "  ↑ Downloaded src/assets/fail.wav")
    except Exception as e:
        input(Colorate.Horizontal(Colors.red_to_yellow, f"Failed to download assets: {e}"))
    
    time.sleep(1)
    os.remove("src/assets/NOT LOADED")

os.system("cls")
def ReadRobloxString(ExpectedAddress: int) -> str:
    StringCount = Prestige.Pymem.read_int(ExpectedAddress + 0x10)
    if StringCount > 15:
        return Prestige.Pymem.read_string(Prestige.DRP(ExpectedAddress, True), StringCount)
    return Prestige.Pymem.read_string(ExpectedAddress, StringCount)

def GetClassName(Instance: int) -> str:
    ExpectedAddress = Prestige.DRP(Prestige.DRP(Instance + 0x18, True) + 8, True)
    return ReadRobloxString(ExpectedAddress)

def SetParent(Instance, Parent) -> None:
    Prestige.Pymem.write_longlong(Instance + parentOffset, Parent)
    newChildren = Prestige.Pymem.allocate(0x400)
    Prestige.Pymem.write_longlong(newChildren + 0, newChildren + 0x40)
    ptr = Prestige.Pymem.read_longlong(Parent + childrenOffset)
    childrenStart = Prestige.Pymem.read_longlong(ptr)
    childrenEnd = Prestige.Pymem.read_longlong(ptr + 8)
    b = Prestige.Pymem.read_bytes(childrenStart, childrenStart - childrenEnd)
    Prestige.Pymem.write_bytes(newChildren + 0x40, b, len(b))
    e = newChildren + 0x40 + (childrenEnd - childrenStart)
    Prestige.Pymem.write_longlong(e, Instance)
    Prestige.Pymem.write_longlong(e + 8, Prestige.Pymem.read_longlong(Instance + 0x10))
    e = e + 0x10
    Prestige.Pymem.write_longlong(newChildren + 0x8, e)
    Prestige.Pymem.write_longlong(newChildren + 0x10, e)

def inject(PID: int=None) -> list:
    global childrenOffset
    global parentOffset

    print(Colors.StaticRGB(78, 23, 230) + "Scanning Array of Bytes")
    results = Prestige.AOBSCANALL("50 6C 61 79 65 72 73 ?? ?? ?? ?? ?? ?? ?? ?? ?? 07 00 00 00 00 00 00 00 0F", True)

    start_time = time.time()
    total_patterns = len(results)
    current_pattern = 1
    isFirst = False
    gotBoth = False

    print(Colors.StaticRGB(49, 38, 252) + "Begin Analysis")
    for pattern in results:
        elapsed_time = time.time() - start_time
        remaining_time = remaining_time = f"{(elapsed_time / current_pattern) * (total_patterns - current_pattern):.1f}s" if current_pattern!= 1 else "?"

        hexas = Prestige.d2h(pattern)
        aobs = ""
        for i in range(1, 16 + 1):
            aobs = aobs + hexas[i - 1 : i]
        aobs = Prestige.hex2le(aobs).upper()

        print(Colorate.Horizontal(Colors.blue_to_purple, f" Analyzing Array of Bytes ({current_pattern} / {total_patterns}, Time Left: {remaining_time})"))
        current_pattern+=1
        valid = False
        try:
            results = Prestige.AOBSCANALL(aobs, True)
            if results:
                print(Colorate.Horizontal(Colors.purple_to_blue, f"  ↑ Valid ({aobs}) Now Checking..."))
                for i in results:
                    for j in range(1, 10 + 1):
                        address = i - (8 * j)
                        if not Prestige.isValidPointer(address, True):
                            continue

                        ptr = Prestige.Pymem.read_longlong(address)
                        if not Prestige.isValidPointer(address, True):
                            continue

                        address = ptr + 8
                        if not Prestige.isValidPointer(address, True):
                                continue
                            
                        ptr = Prestige.Pymem.read_longlong(address)
                        try:
                            if Prestige.Pymem.read_string(ptr) == "Players":
                                print(Colorate.Horizontal(Colors.purple_to_blue, f"      ↑ Check Successful! ({str(ptr)})"))
                                if isFirst:
                                    gotBoth = True
                                else:
                                    isFirst = True
                                valid = True
                                players = (i - (8 * j)) - 0x18
                                nameOffset = i - players
                        except:
                            continue
                    if valid:
                        break
                if not valid:
                    print(Colorate.Horizontal(Colors.red_to_purple, "      ↑ Check Failed!"))
            else:
                print(Colorate.Horizontal(Colors.red_to_purple, "  ↑ Invalid"))
        except Exception as e:
            print(Colors.StaticRGB(49, 38, 252) + " [PRESTIGE]: Error while Analyzing\n  ↑ " + Colors.dark_gray + str(e))
        if gotBoth:
            print(Colors.StaticRGB(151, 9, 252) + " Acquired all Valid Addresses")
            break
        elif valid and data["settings"]["basic"]["skip-on-valid-pattern"]:
            print(Colors.StaticRGB(151, 9, 252) + "         ↑ Got valid pattern. Closing analysis...")
            break
    print(Colors.StaticRGB(49, 38, 252) + "End Analysis\nGetting Parent Offset")

    parentOffset = None
    for i in range(0x10, 0x120 + 8, 8):
        address = players + i
        if not Prestige.isValidPointer(address, True):
            continue

        ptr = Prestige.Pymem.read_longlong(address)
        if ptr == 0 and ptr % 4 != 0:
            continue

        address = ptr + 8
        if not Prestige.isValidPointer(address, True):
            continue

        if Prestige.Pymem.read_longlong(address) == ptr:
            parentOffset = i
            print(Colors.StaticRGB(151, 9, 252) + "Successfuly got Parent Offset\n" + Colors.StaticRGB(49, 38, 252) + "Getting Data Model")
            break

    if not parentOffset:
        print(Colorate.Horizontal(Colors.red_to_purple, "[PRESTIGE]: Failed to get Parent Offset"))
        return [0, "no_parent_offset"]
    
    dataModel = Prestige.Pymem.read_longlong(players + parentOffset)
    print(Colors.StaticRGB(151, 9, 252) + "Successfuly got Data Model (Game)\n" + Colors.StaticRGB(49, 38, 252) + "Getting Children Offset")

    childrenOffset = None
    for i in range(0x10, 0x200 + 8, 8):
        ptr = Prestige.Pymem.read_longlong(dataModel + i)
        if not ptr:
            continue

        try:
            childrenStart = Prestige.Pymem.read_longlong(ptr)
            childrenEnd = Prestige.Pymem.read_longlong(ptr + 8)

            if not (childrenStart and childrenEnd):
                continue

            if (
                childrenEnd > childrenStart and
                childrenEnd - childrenStart > 1 and
                childrenEnd - childrenStart < 0x1000
            ):
                print(Colors.StaticRGB(151, 9, 252) + "Successfuly got Children Offset\n" + Colors.StaticRGB(49, 38, 252) + "Getting LocalPlayer Offset")
                childrenOffset = i
                break
        except:
            pass

    if not childrenOffset:
        print(Colorate.Horizontal(Colors.red_to_purple, "[PRESTIGE]: Failed to get Children Offset (Try restarting Roblox)"))
        return [0, "no_children_offset"]

    """
    Credits to Hyper Injector and Bloxlib for these Functions.
    """
    
    def GetNameAddress(Instance: int) -> str:
        ExpectedAddress = Prestige.DRP(Instance + nameOffset, True)
        return ExpectedAddress

    def GetName(Instance: int) -> str:
        ExpectedAddress = GetNameAddress(Instance)
        return ReadRobloxString(ExpectedAddress)
    
    def GetChildren(Instance: int) -> str:
        ChildrenInstance = []
        InstanceAddress = Instance
        if not InstanceAddress:
            return False
        ChildrenStart = Prestige.DRP(InstanceAddress + childrenOffset, True)
        if ChildrenStart == 0:
            return []
        ChildrenEnd = Prestige.DRP(ChildrenStart + 8, True)
        OffsetAddressPerChild = 0x10
        CurrentChildAddress = Prestige.DRP(ChildrenStart, True)
        for i in range(0, 9000):
            if i == 8999:
                print(Colors.yellow + "WARNING: Too many children, could be invalid")
            if CurrentChildAddress == ChildrenEnd:
                break
            ChildrenInstance.append(Prestige.Pymem.read_longlong(CurrentChildAddress))
            CurrentChildAddress += OffsetAddressPerChild
        return ChildrenInstance

    def GetDescendants(Instance: int) -> str:
        DescendantsInstance = []
        for Child in GetChildren(Instance):
            DescendantsInstance.append(Child)
            DescendantsInstance += GetDescendants(Child)
        return DescendantsInstance
    
    def GetParent(Instance: int) -> int:
        return Prestige.DRP(Instance + parentOffset, True)
    
    def FindFirstChild(Instance: int, ChildName: str) -> int:
        ChildrenOfInstance = GetChildren(Instance)
        for i in ChildrenOfInstance:
            if GetName(i) == ChildName:
                return i
            
    def FindFirstChildOfClass(Instance: int, ClassName: str) -> int:
        ChildrenOfInstance = GetChildren(Instance)
        for i in ChildrenOfInstance:
            if GetClassName(i) == ClassName:
                return i
    
    class toInstance:
        def __init__(self, address: int = 0):
            self.Address = address
            self.Self = address
            self.Name = GetName(address)
            self.ClassName = GetClassName(address)
            self.Parent = GetParent(address)

        def getChildren(self):
            return GetChildren(self.Address)
        
        def getDescendants(self):
            return GetDescendants(self.Address)

        def findFirstChild(self, ChildName):
            return FindFirstChild(self.Address, ChildName)

        def findFirstChildOfClass(self, ChildClass):
            return FindFirstChildOfClass(self.Address, ChildClass)

        def setParent(self, Parent):
            SetParent(self.Address, Parent)

        def GetChildren(self):
            return GetChildren(self.Address)
        
        def GetDescendants(self):
            return GetDescendants(self.Address)

        def FindFirstChild(self, ChildName):
            return FindFirstChild(self.Address, ChildName)

        def FindFirstChildOfClass(self, ChildClass):
            return FindFirstChildOfClass(self.Address, ChildClass)

        def SetParent(self, Parent):
            SetParent(self.Address, Parent)

    players = toInstance(players)
    game = toInstance(dataModel)
    
    localPlayerOffset = None
    for i in range(0x10, 0x600 + 4, 4):
        ptr = Prestige.Pymem.read_longlong(players.Self + i)
        if not Prestige.isValidPointer(ptr, True):
            continue
        if Prestige.Pymem.read_longlong(ptr + parentOffset) == players.Self:
            localPlayerOffset = i
            print(Colors.StaticRGB(151, 9, 252) + "Successfuly got LocalPlayer Offset")
            break

    if not localPlayerOffset:
        print(Colorate.Horizontal(Colors.red_to_purple, "[PRESTIGE]: Failed to get LocalPlayer Offset"))
        return [0, "no_localplayer_offset"]

    localPlayer = toInstance(Prestige.DRP(players.Self + localPlayerOffset, True))
    os.system(f"title Injecting for {localPlayer.Name}")
    print(Colors.StaticRGB(151, 9, 252) + "LocalPlayer: " + Colors.turquoise + localPlayer.Name + Colors.StaticRGB(49, 38, 252) + "\nGetting " +
          Colors.turquoise + localPlayer.Name + Colors.StaticRGB(49, 38, 252) + "'s Character")
    
    workspace = toInstance(game.FindFirstChildOfClass("Workspace"))
    character = None
    for _object in workspace.GetDescendants():
        if not Prestige.isValidPointer(_object, True):
            continue
        try:
            filtered_object = toInstance(_object)
            if data["settings"]["advanced"]["list-items"]:
                print(Colors.dark_gray + f"Name: {filtered_object.Name}, ClassName: {filtered_object.ClassName}")
            if filtered_object.Name == localPlayer.Name and (filtered_object.ClassName == "Model" and filtered_object.FindFirstChild("HumanoidRootPart") 
                                                             and filtered_object.FindFirstChild("Humanoid")):
                character = filtered_object
                print(Colors.StaticRGB(151, 9, 252) + "Found " + Colors.turquoise + localPlayer.Name + Colors.StaticRGB(151, 9, 252) + "'s Character\n" + 
                      Colors.StaticRGB(49, 38, 252) + "Getting LocalScript to Inject Into")
                break
        except:
            continue

    if not character:
        print(Colorate.Horizontal(Colors.red_to_purple, f"[PRESTIGE]: Failed to get {localPlayer.Name}'s Character"))
        return [0, "no_character"]
    
    localScript = None
    for _object in character.GetDescendants():
        if not Prestige.isValidPointer(_object, True):
            continue
        try:
            filtered_object = toInstance(_object)
            if data["settings"]["advanced"]["list-items"]:
                print(Colors.dark_gray + f"Name: {filtered_object.Name}, ClassName: {filtered_object.ClassName}")
            if filtered_object.ClassName == "LocalScript":
                localScript = filtered_object
                print(Colors.StaticRGB(151, 9, 252) + f"Found " + Colors.turquoise + localPlayer.Name + Colors.StaticRGB(151, 9, 252) + 
                      f"'s LocalScript: {Colors.purple + filtered_object.Name}\n" + Colors.StaticRGB(49, 38, 252) + 
                      f"Getting Hook script for Localscript of {Colors.purple + filtered_object.Name}")
                break
        except:
            continue

    if not localScript:
        print(Colorate.Horizontal(Colors.red_to_purple, f"[PRESTIGE]: Failed to get {localPlayer.Name}'s LocalScript"))
        return [0, "no_localscript"]
    
    print(Colors.StaticRGB(78, 23, 230) + "Scanning Array of Bytes")
    results = Prestige.AOBSCANALL("49 6E 6A 65 63 74 ?? ?? ?? ?? ?? ?? ?? ?? ?? ?? 06", True)

    start_time = time.time()
    total_patterns = len(results)
    current_pattern = 1
    hookScript = None

    if total_patterns <= 0:
        print(Colorate.Horizontal(Colors.red_to_purple, f"[PRESTIGE]: Scan Failed for Hooking Script! (Did you Join through the Teleporter Game First?)"))
        return [0, "hook_aobs_failed"]

    print(Colors.StaticRGB(49, 38, 252) + "Begin Analysis")
    for pattern in results:
        elapsed_time = time.time() - start_time
        remaining_time = remaining_time = f"{(elapsed_time / current_pattern) * (total_patterns - current_pattern):.1f}s" if current_pattern!= 1 else "?"

        hexas = Prestige.d2h(pattern)
        aobs = ""
        for i in range(1, 16 + 1):
            aobs = aobs + hexas[i - 1 : i]
        aobs = Prestige.hex2le(aobs).upper()

        print(Colorate.Horizontal(Colors.blue_to_purple, f" Analyzing Array of Bytes ({current_pattern} / {total_patterns}, Time Left: {remaining_time})"))
        current_pattern+=1

        try:
            results = Prestige.AOBSCANALL(aobs, True)
            valid = False
            if results:
                for i in results:
                    if (Prestige.Pymem.read_longlong(i - nameOffset + 8) == i - nameOffset):
                        print(Colors.StaticRGB(151, 9, 252) + f" Successfuly got Hooking Script: {str(Prestige.d2h(i-nameOffset))}")
                        hookScript = i - nameOffset
                        valid = True
                        break
            if valid:
                break
        except Exception as e:
            print(Colors.StaticRGB(49, 38, 252) + f" [PRESTIGE]: Error while Analyzing\n  ↑ {Colors.dark_gray + str(e)}")
    print(Colors.StaticRGB(49, 38, 252) + "End Analysis")

    if not hookScript:
        print(Colorate.Horizontal(Colors.red_to_purple, "[PRESTIGE]: Failed to get Hooking Script (Are you using a Teleporter game?)"))
        return [0, "no_hook_script"]
    
    hookScript = toInstance(hookScript)

    b = Prestige.Pymem.read_bytes(hookScript.Self + 0x100, 0x150)
    Prestige.Pymem.write_bytes(localScript.Self + 0x100, b, len(b))

    try:
        localScript.SetParent(toInstance(localPlayer.FindFirstChild("PlayerScripts")).Address)
        return [0, "this_is_not_supposed_to_happen"]
    except Exception as e:
        return [1, "successfully_written_bytes_and_injected"]


if __name__ == "__main__":
    print(Center.XCenter(Colorate.Horizontal(Colors.purple_to_blue, data["settings"]["basic"]["banner"], 2)))

    x = True
    while True:
        if Prestige.YieldForProgram("RobloxPlayerBeta.exe") or Prestige.YieldForProgram("Windows10Universal.exe"):
            break
        elif x:
            print(Colors.gray + "Waiting for Roblox (RobloxPlayerBeta.exe or Windows10Universal.exe)")
            x = False

    print(Colors.StaticRGB(160, 32, 240) + f"\nFound Roblox ({Prestige.ProgramName}, PID: {Prestige.PID})")
    if data["settings"]["advanced"]["multi-inject"]:
        print(Colors.gray + " ↑ Multi Inject is Turned On (Ignore)")
        while True:
            try:
                _pid = int(input(Colors.StaticRGB(160, 32, 240) + "[Multi-Inject] Enter PID: "))
                if Prestige.Pymem.open_process_from_id(_pid):
                    Prestige = Prestige(_pid)
                break
            except:
                print(Colorate.Horizontal(Colors.red_to_yellow, "PID is not Valid"))
    else:
        input(Colors.turquoise + "Press Enter to Begin Injection")

    while True:
        start_time = time.time()
        injection = inject()
        print(f"Took {time.time() - start_time:.1f} Seconds to Initialize\nCode: {str(injection[1])}, Success: {"True" if injection[0] != 0 else "False"}")
        if injection[0] == 1:
            if data["settings"]["basic"]["play-sound"]:
                threading.Thread(target=playsound, args=["src/assets/success.wav"]).start()
            input(Colorate.Horizontal(Colors.blue_to_red, "Successfully Injected! Please Reset your Character.\nTheres a chance of Roblox Crashing or UI not showing due to Anti Cheat"))
            break
        else:
            if data["settings"]["basic"]["play-sound"]:
                threading.Thread(target=playsound, args=["src/assets/fail.wav"]).start()
            input(Colorate.Horizontal(Colors.red_to_yellow, "Injection Failed. Retry?"))

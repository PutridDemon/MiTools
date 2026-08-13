import os
import sys
import json
import urllib.request
import subprocess
import msvcrt
import zipfile
import webbrowser

# Enable ANSI escape codes in Windows 10/11
if os.name == 'nt':
    os.system('')

# ANSI Colors
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
GRAY = "\033[90m"

# GitHub Update Configuration
GITHUB_USER = "PutridDemon"
GITHUB_REPO = "MiTools"
GITHUB_BRANCH = "main"
FOLDER_PATH = "Updates"
API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{FOLDER_PATH}"

PLATFORM_TOOLS_URL = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
PLATFORM_TOOLS_DIR = os.path.join(LOCAL_DIR, "platform-tools")
FASTBOOT_EXE = os.path.join(PLATFORM_TOOLS_DIR, "fastboot.exe")

# Base de datos global para clasificación de procesadores
DEVICE_DATABASE = {
    "Redmi Note 9 (merlin)": "MTK",
    "Redmi Note 8 Pro (mtk)": "MTK",
    "Redmi Note 5 MTK (ziyi)": "MTK",
    "Redmi Note 4 MTK (nikel)": "MTK",
    "Redmi Note 3 MTK (hennessy)": "MTK",
    "Redmi 5 Plus (vince)": "Qualcomm",
    "Redmi Note 5 (whyred)": "Qualcomm",
    "Redmi 5 (rosy)": "Qualcomm"
}

def check_github_updates():
    print("[*] Checking for updates in the GitHub 'Updates' folder...")
    req = urllib.request.Request(API_URL, headers={'User-Agent': 'MiTools-Updater'})
    try:
        with urllib.request.urlopen(req) as response:
            files_data = json.loads(response.read().decode('utf-8'))
            for file_info in files_data:
                filename = file_info.get('name', '')
                if filename.startswith("update_") and filename.endswith(".py"):
                    download_url = file_info.get('download_url')
                    target_filename = filename.replace("update_", "", 1)
                    target_path = os.path.join(LOCAL_DIR, target_filename)
                    
                    print(f"[!] Update found on GitHub: {filename}")
                    with urllib.request.urlopen(download_url) as update_resp:
                        new_code = update_resp.read().decode('utf-8')
                    with open(target_path, "w", encoding="utf-8") as f_target:
                        f_target.write(new_code)
                    print(f"[OK] Update successfully applied to '{target_filename}'!")
                    input("\nPress ENTER to exit...")
                    sys.exit(0)
    except Exception as e:
        print(f"[!] Could not check for online updates: {e}")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner(title):
    print(f"{CYAN}================================================================={RESET}")
    print(f"{BOLD}{CYAN}             XIAOMI FASTBOOT & RECOVERY UTILITY v4.0             {RESET}")
    print(f"{CYAN}================================================================={RESET}")
    print(f"{YELLOW}  [i] {title}{RESET}\n")

def run_command(cmd):
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    return process.returncode, process.stdout.strip(), process.stderr.strip()

def manage_platform_tools():
    code, _, _ = run_command("fastboot --version")
    if code == 0:
        return "fastboot"

    if os.path.isfile(FASTBOOT_EXE):
        os.environ["PATH"] += os.pathsep + PLATFORM_TOOLS_DIR
        return "fastboot"

    clear_screen()
    print_banner("DOWNLOADING DEPENDENCIES")
    print(f"{RED}[!] 'fastboot' was not found on your system.{RESET}")
    print(f"{YELLOW}[*] Downloading Android Platform-Tools...{RESET}\n")
    
    zip_path = os.path.join(LOCAL_DIR, "platform-tools-latest-windows.zip")
    try:
        def show_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(int(downloaded * 100 / total_size), 100)
            sys.stdout.write(f"\r{CYAN}[*] Download progress: {percent}% completed{RESET}")
            sys.stdout.flush()

        urllib.request.urlretrieve(PLATFORM_TOOLS_URL, zip_path, show_progress)
        print(f"\n\n{GREEN}[*] Download completed. Extracting files...{RESET}")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(LOCAL_DIR)
        os.remove(zip_path)
        os.environ["PATH"] += os.pathsep + PLATFORM_TOOLS_DIR
        input(f"{GRAY}Press ENTER to continue...{RESET}")
        return "fastboot"
    except Exception as e:
        print(f"\n{RED}[X] Critical error downloading Platform-Tools: {e}{RESET}")
        input(f"{GRAY}Press ENTER to exit...{RESET}")
        sys.exit(1)

def ensure_mtkclient_installed():
    clear_screen()
    print_banner("CHECKING DEPENDENCIES (MTKCLIENT)")
    try:
        import mtk
        return True
    except ImportError:
        print(f"{YELLOW}[!] 'mtkclient' not found. Installing directly from GitHub...{RESET}\n")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
            git_url = "https://github.com/bkerler/mtkclient/archive/refs/heads/main.zip"
            subprocess.check_call([sys.executable, "-m", "pip", "install", git_url])
            print(f"\n{GREEN}[OK] 'mtkclient' installed successfully!{RESET}")
            input(f"\n{GRAY}Press ENTER to continue...{RESET}")
            return True
        except Exception as e:
            print(f"\n{RED}[X] Failed to install mtkclient: {e}{RESET}")
            input(f"\n{GRAY}Press ENTER to return...{RESET}")
            return False

def interactive_menu(options, subtitle):
    selection = 0
    total = len(options)
    box_width = 56
    
    while True:
        clear_screen()
        print_banner(subtitle)
        print(f"{GRAY}  Use arrow keys [↑] [↓] to navigate and [ENTER] to select:{RESET}\n")
        
        print(f"  {CYAN}┌" + "─" * box_width + f"┐{RESET}")
        for i, option in enumerate(options):
            max_opt_len = box_width - 6
            display_option = option[:max_opt_len]
            if i == selection:
                content = f"{GREEN}{BOLD} ► {display_option:<{max_opt_len}}{RESET}"
                print(f"  {CYAN}│{RESET} {content} {CYAN}│{RESET}")
            else:
                content = f"{GRAY}    {display_option:<{max_opt_len}}{RESET}"
                print(f"  {CYAN}│{RESET} {content} {CYAN}│{RESET}")
        print(f"  {CYAN}└" + "─" * box_width + f"┘{RESET}")
        
        key = msvcrt.getch()
        if key == b'\xe0':
            special_key = msvcrt.getch()
            if special_key == b'H':
                selection = (selection - 1) % total
            elif special_key == b'P':
                selection = (selection + 1) % total
        elif key == b'\r':
            return selection

def get_file_path(file_type):
    clear_screen()
    while True:
        print_banner(f"SELECT {file_type.upper()} FILE")
        print(f"{GRAY}  Drag and drop your file here, type path, or type 'back' to cancel:{RESET}\n")
        path = input(f"  {CYAN}Path >> {RESET}").strip().strip('"').strip("'")
        if path.lower() in ["back", "b", "salir"]:
            return None
        if os.path.isfile(path):
            return path
        print(f"\n  {RED}[X] Error: The file '{path}' does not exist or is invalid.{RESET}")
        input(f"  {GRAY}Press ENTER to try again...{RESET}")

def detect_device():
    code, output, _ = run_command("fastboot devices")
    if code == 0 and output:
        lines = output.splitlines()
        if lines and "fastboot" in lines[0]:
            return lines[0].split()[0]
    return None

def detect_device_adb():
    code, output, _ = run_command("adb devices")
    if code == 0 and output:
        lines = output.splitlines()
        if len(lines) > 1:
            parts = lines[1].split()
            if len(parts) > 1 and parts[1] in ["device", "sideload"]:
                return parts[0]
    return None

def custom_terminal_shell():
    clear_screen()
    print_banner("CUSTOM FASTBOOT / ADB TERMINAL")
    print(f"{GRAY}  Type your commands freely. Type 'exit' to return to Main Menu.{RESET}\n")
    while True:
        try:
            cmd = input(f"{CYAN}MiTools-Shell > {RESET}").strip()
            if not cmd:
                continue
            if cmd.lower() in ["exit", "quit", "back"]:
                break
            code, out, err = run_command(cmd)
            if out: print(f"{GREEN}{out}{RESET}")
            if err: print(f"{RED}{err}{RESET}")
            print()
        except KeyboardInterrupt:
            break

def aosp_roms_downloader_flow():
    res = select_device_model_flow()
    if res is None:
        return
    nombre_modelo, codename = res
    
    rom_options = [
        "LineageOS Official Downloads",
        "PixelExperience Official Archive",
        "PixelOS Official Downloads",
        "Evolution X Official Downloads",
        "crDroid Official Downloads",
        "DerpFest Official Builds",
        "XDA Developers Forums",
        "<- Back to Main Menu"
    ]
    idx_rom = interactive_menu(rom_options, f"OFFICIAL AOSP ROMS - {nombre_modelo.upper()} ({codename})")
    if idx_rom == len(rom_options) - 1:
        return
        
    urls = [
        f"https://wiki.lineageos.org/devices/{codename}/",
        f"https://download.pixelexperience.org/{codename}",
        f"https://pixelos.net/download/{codename}",
        f"https://evolution-x.org/devices/{codename}",
        f"https://crdroid.net/{codename}",
        f"https://derpfest.org/device/{codename}",
        f"https://xdaforums.com/search/1/?q={codename}+ROM&c[node]=12270"
    ]
    if 0 <= idx_rom < len(urls):
        webbrowser.open(urls[idx_rom])
    input(f"\n{GRAY}Press ENTER to return...{RESET}")

def get_mtk_devices():
    return [d for d, arch in DEVICE_DATABASE.items() if arch == "MTK"]

def unlock_mtk_bootloader_flow():
    if not ensure_mtkclient_installed():
        return
        
    mtk_devices = get_mtk_devices() + ["<- Back to Main Menu"]
    idx_disp = interactive_menu(mtk_devices, "SELECT YOUR MTK DEVICE")
    
    if idx_disp == len(mtk_devices) - 1:
        return

    selected_device = mtk_devices[idx_disp]

    clear_screen()
    print_banner(f"MTK BOOTLOADER UNLOCK - {selected_device}")
    print(f"{RED}[!] WARNING: Uses BROM exploit. Data will be formatted!{RESET}\n")
    print("INSTRUCTIONS:")
    print("1. Turn off your device completely.")
    print("2. Hold [Vol Up] + [Vol Down] simultaneously.")
    print("3. Plug in the USB cable while holding both buttons.\n")
    
    input(f"{GRAY}Press ENTER when ready to start exploit (or Ctrl+C to cancel)...{RESET}")
    print(f"\n{CYAN}[*] Running mtkclient for {selected_device}...{RESET}")
    code, out, err = run_command(f"{sys.executable} -m mtkclient da e seccfg unlock")
    
    if code == 0:
        print(f"\n{GREEN}[OK] Bootloader successfully unlocked!{RESET}")
    else:
        print(f"\n{RED}[X] Error executing unlock:{RESET}\n{RED}{err if err else out}{RESET}")
    input(f"\n{GRAY}Press ENTER to return to menu...{RESET}")

def select_device_model_flow():
    devices = [
        "Redmi Note 9 Family",
        "Redmi Note 8 Family",
        "Redmi Note 7 Family",
        "Redmi Note 6 Pro Family",
        "Redmi Note 5 / 5 Pro Family",
        "Redmi 5 / 5 Plus Family",
        "Redmi Note 4 / 4X Family",
        "Redmi Note 3 Family",
        "Redmi Note 2 Family",
        "Redmi Note 1 / 4G Family",
        "<- Back to Main Menu"
    ]
    idx_disp = interactive_menu(devices, "SELECT YOUR DEVICE FAMILY")

    if idx_disp == len(devices) - 1:
        return None

    if idx_disp == 0:
        variants = ["Redmi Note 9 (merlin)", "Redmi Note 9S (curtana)", "Redmi Note 9 Pro (joyeuse)", "<- Back"]
        idx_var = interactive_menu(variants, "SELECT VARIANT FOR REDMI NOTE 9")
        if idx_var == len(variants) - 1: return select_device_model_flow()
        return ("Redmi Note 9", "merlin") if idx_var == 0 else ("Redmi Note 9S", "curtana") if idx_var == 1 else ("Redmi Note 9 Pro", "joyeuse")
    elif idx_disp == 1:
        variants = ["Redmi Note 8 (ginkgo)", "Redmi Note 8T (willow)", "Redmi Note 8 Pro (mtk)", "<- Back"]
        idx_var = interactive_menu(variants, "SELECT VARIANT FOR REDMI NOTE 8")
        if idx_var == len(variants) - 1: return select_device_model_flow()
        return ("Redmi Note 8", "ginkgo") if idx_var == 0 else ("Redmi Note 8T", "willow") if idx_var == 1 else ("Redmi Note 8 Pro", "mtk")
    elif idx_disp == 2:
        variants = ["Redmi Note 7 (lavender)", "Redmi Note 7 Pro (violet)", "<- Back"]
        idx_var = interactive_menu(variants, "SELECT VARIANT FOR REDMI NOTE 7")
        if idx_var == len(variants) - 1: return select_device_model_flow()
        return ("Redmi Note 7", "lavender") if idx_var == 0 else ("Redmi Note 7 Pro", "violet")
    elif idx_disp == 3:
        variants = ["Redmi Note 6 Pro (tulip)", "<- Back"]
        idx_var = interactive_menu(variants, "SELECT VARIANT FOR REDMI NOTE 6 PRO")
        if idx_var == len(variants) - 1: return select_device_model_flow()
        return "Redmi Note 6 Pro", "tulip"
    elif idx_disp == 4:
        variants = ["Redmi Note 5 / 5 Pro (whyred)", "Redmi Note 5 AI / Pro (ziyi)", "<- Back"]
        idx_var = interactive_menu(variants, "SELECT VARIANT FOR REDMI NOTE 5")
        if idx_var == len(variants) - 1: return select_device_model_flow()
        return ("Redmi Note 5", "whyred") if idx_var == 0 else ("Redmi Note 5 MTK", "ziyi")
    elif idx_disp == 5:
        variants = ["Redmi 5 Plus (Snapdragon - vince)", "Redmi 5 (Snapdragon - rosy)", "<- Back"]
        idx_var = interactive_menu(variants, "SELECT VARIANT FOR REDMI 5")
        if idx_var == len(variants) - 1: return select_device_model_flow()
        return ("Redmi 5 Plus", "vince") if idx_var == 0 else ("Redmi 5", "rosy")
    elif idx_disp == 6:
        variants = ["Redmi Note 4X (Snapdragon - mido)", "Redmi Note 4 (MediaTek - nikel)", "<- Back"]
        idx_var = interactive_menu(variants, "SELECT VARIANT FOR REDMI NOTE 4")
        if idx_var == len(variants) - 1: return select_device_model_flow()
        return ("Redmi Note 4X", "mido") if idx_var == 0 else ("Redmi Note 4 MTK", "nikel")
    elif idx_disp == 7:
        variants = ["Redmi Note 3 (Snapdragon - kenzo)", "Redmi Note 3 SE (kate)", "Redmi Note 3 (MediaTek - hennessy)", "<- Back"]
        idx_var = interactive_menu(variants, "SELECT VARIANT FOR REDMI NOTE 3")
        if idx_var == len(variants) - 1: return select_device_model_flow()
        return ("Redmi Note 3", "kenzo") if idx_var == 0 else ("Redmi Note 3 SE", "kate") if idx_var == 1 else ("Redmi Note 3 MTK", "hennessy")
    elif idx_disp == 8:
        variants = ["Redmi Note 2 (hermes)", "<- Back"]
        idx_var = interactive_menu(variants, "SELECT VARIANT FOR REDMI NOTE 2")
        if idx_var == len(variants) - 1: return select_device_model_flow()
        return "Redmi Note 2", "hermes"
    elif idx_disp == 9:
        variants = ["Redmi Note 1 / 4G (dior)", "Redmi Note 1 3G (gustave)", "<- Back"]
        idx_var = interactive_menu(variants, "SELECT VARIANT FOR REDMI NOTE 1")
        if idx_var == len(variants) - 1: return select_device_model_flow()
        return ("Redmi Note 1", "dior") if idx_var == 0 else ("Redmi Note 1 3G", "gustave")

    return None

def main():
    try:
        clear_screen()
        check_github_updates()
        manage_platform_tools()

        while True:
            main_options = [
                "Select Device & Flash Recovery/ROM",
                "ADB Sideload Mode",
                "Unlock Bootloader MTK (Real BROM Exploit - Solo MTK)",
                "Custom Fastboot/ADB Shell (Manual Commands)",
                "Download Official AOSP Custom ROMs (Web Links)",
                "Exit Program"
            ]
            
            idx_main = interactive_menu(main_options, "MAIN MENU")

            if idx_main == 5:
                clear_screen()
                print("Exiting utility. Goodbye!")
                break
            elif idx_main == 4:
                aosp_roms_downloader_flow()
                continue
            elif idx_main == 3:
                custom_terminal_shell()
                continue
            elif idx_main == 2:
                unlock_mtk_bootloader_flow()
                continue
            elif idx_main == 1:
                clear_screen()
                print_banner("ADB SIDELOAD MODE")
                res = select_device_model_flow()
                if res is None:
                    continue
                nombre_modelo, codename = res

                clear_screen()
                print_banner(f"ADB SIDELOAD - {nombre_modelo.upper()} ({codename})")
                print("1. Boot into Custom Recovery (TWRP/OrangeFox).")
                print("2. Go to Advanced -> ADB Sideload and swipe.\n")
                input(f"{GRAY}Press ENTER when ready (or Ctrl+C to cancel)...{RESET}")

                dev_adb = detect_device_adb()
                if not dev_adb:
                    print(f"\n{RED}[X] No device detected in Sideload mode.{RESET}")
                    input(f"\n{GRAY}Press ENTER to return...{RESET}")
                    continue

                rom_path = get_file_path("ROM (.zip)")
                if rom_path is None:
                    continue
                    
                code, _, error = run_command(f'adb sideload "{rom_path}"')
                if code != 0:
                    print(f"\n{RED}[X] Error:\n{error}{RESET}")
                else:
                    print(f"\n{GREEN}[OK] ROM installed successfully!{RESET}")
                input(f"\n{GRAY}Press ENTER to return...{RESET}")
                continue

            elif idx_main == 0:
                res = select_device_model_flow()
                if res is None:
                    continue
                nombre_modelo, codename = res
                
                actions = [
                    "Flash Custom Recovery (.img)",
                    "Flash Full ROM / Fastboot Auto-Script (.bat)",
                    "<- Back to Main Menu"
                ]
                idx_acc = interactive_menu(actions, f"OPTIONS FOR {nombre_modelo.upper()} ({codename})")

                if idx_acc == 2:
                    continue

                if idx_acc == 0:
                    clear_screen()
                    print_banner(f"FLASH RECOVERY - {nombre_modelo.upper()}")
                    input(f"{GRAY}Boot phone into Fastboot mode and press ENTER...{RESET}")
                    
                    if not detect_device():
                        print(f"\n{RED}[X] Fastboot device not found.{RESET}")
                        input(f"\n{GRAY}Press ENTER to return...{RESET}")
                        continue

                    img_path = get_file_path("Recovery (.img)")
                    if img_path is None:
                        continue
                        
                    code, _, error = run_command(f'fastboot flash recovery "{img_path}"')
                    if code != 0:
                        print(f"\n{RED}[X] Error:\n{error}{RESET}")
                    else:
                        print(f"{GREEN}[OK] Recovery flashed!{RESET}")
                        if input(f"\n{YELLOW}Reboot to recovery? (y/n): {RESET}").lower() in ['y', 's', 'si']:
                            run_command("fastboot reboot recovery")

                elif idx_acc == 1:
                    clear_screen()
                    print_banner(f"AUTOMATED ROM INSTALLER - {nombre_modelo.upper()}")
                    script_path = get_file_path("Fastboot ROM Script (.bat)")
                    if script_path is None:
                        continue
                    
                    if not detect_device():
                        print(f"\n{RED}[X] Fastboot device not found.{RESET}")
                        input(f"\n{GRAY}Press ENTER to return...{RESET}")
                        continue

                    working_dir = os.path.dirname(script_path)
                    rom_process = subprocess.run(f'"{script_path}"', cwd=working_dir, shell=True)
                    if rom_process.returncode == 0:
                        print(f"\n{GREEN}[OK] Script executed successfully!{RESET}")
                    else:
                        print(f"\n{YELLOW}[!] Script finished with code {rom_process.returncode}.{RESET}")

                input(f"\n{GRAY}Press ENTER to return to menu...{RESET}")

    except Exception as e:
        print(f"\n{RED}[X] Unhandled Critical Error:\n{e}{RESET}")
        input("\nPress ENTER to exit...")

if __name__ == "__main__":
    main()

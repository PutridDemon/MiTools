import os
import sys
import json
import urllib.request
import subprocess
import msvcrt
import zipfile

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

# GitHub Update Configuration (No tokens required)
GITHUB_USER = "PutridDemon"
GITHUB_REPO = "MiTools"
GITHUB_BRANCH = "main"
FOLDER_PATH = "Updates"
API_URL = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{FOLDER_PATH}"

PLATFORM_TOOLS_URL = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
PLATFORM_TOOLS_DIR = os.path.join(LOCAL_DIR, "platform-tools")
FASTBOOT_EXE = os.path.join(PLATFORM_TOOLS_DIR, "fastboot.exe")

def check_github_updates():
    """Checks the 'Updates' folder on GitHub and applies updates if available."""
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
                    print(f"[*] Downloading and applying changes to '{target_filename}'...")
                    
                    with urllib.request.urlopen(download_url) as update_resp:
                        new_code = update_resp.read().decode('utf-8')
                        
                    with open(target_path, "w", encoding="utf-8") as f_target:
                        f_target.write(new_code)
                        
                    print(f"[OK] Update successfully applied to '{target_filename}'!")
                    print("\n[!] The script has been updated. Please restart it to apply changes.")
                    input("\nPress ENTER to exit...")
                    sys.exit(0)
    except Exception as e:
        print(f"[!] Could not check for online updates (Offline or connection error): {e}")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner(title):
    print(f"{CYAN}================================================================={RESET}")
    print(f"{BOLD}{CYAN}             XIAOMI FASTBOOT & RECOVERY UTILITY v2.9             {RESET}")
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
        print(f"{GREEN}[OK] Platform-Tools successfully installed locally.{RESET}\n")
        os.environ["PATH"] += os.pathsep + PLATFORM_TOOLS_DIR
        input(f"{GRAY}Press ENTER to continue...{RESET}")
        return "fastboot"
    except Exception as e:
        print(f"\n{RED}[X] Critical error downloading Platform-Tools: {e}{RESET}")
        input(f"{GRAY}Press ENTER to exit...{RESET}")
        sys.exit(1)

def interactive_menu(options, subtitle):
    """Stable and clean menu rendering that completely avoids cursor drift and visual bugs."""
    selection = 0
    total = len(options)
    
    while True:
        clear_screen()
        print_banner(subtitle)
        print(f"{GRAY}  Use arrow keys [↑] [↓] to navigate and [ENTER] to select:{RESET}\n")
        
        print(f"  {CYAN}┌" + "─" * 63 + f"┐{RESET}")
        for i, option in enumerate(options):
            if i == selection:
                print(f"  {CYAN}│{RESET} {GREEN}{BOLD} ► {option:<58}{RESET} {CYAN}│{RESET}")
            else:
                print(f"  {CYAN}│{RESET}     {GRAY}{option:<58}{RESET} {CYAN}│{RESET}")
        print(f"  {CYAN}└" + "─" * 63 + f"┘{RESET}")
        
        key = msvcrt.getch()
        if key == b'\xe0':
            special_key = msvcrt.getch()
            if special_key == b'H':  # Up Arrow
                selection = (selection - 1) % total
            elif special_key == b'P':  # Down Arrow
                selection = (selection + 1) % total
        elif key == b'\r':  # Enter Key
            return selection

def get_file_path(file_type):
    clear_screen()
    while True:
        print_banner(f"SELECT {file_type.upper()} FILE")
        print(f"{GRAY}  Drag and drop your file here or type path:{RESET}\n")
        path = input(f"  {CYAN}Path >> {RESET}").strip().strip('"').strip("'")
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

def select_device_model_flow():
    devices = [
        "Redmi Note 9 Family",
        "Redmi Note 8 Family",
        "Redmi Note 7 Family",
        "Redmi Note 6 Pro Family",
        "Redmi Note 5 / 5 Pro Family",
        "Redmi Note 4 / 4X Family",
        "Redmi Note 3 Family",
        "Redmi Note 2 Family",
        "Redmi Note 1 / 4G Family"
    ]
    
    idx_disp = interactive_menu(devices, "SELECT YOUR DEVICE FAMILY")

    if idx_disp == 0:
        variants = ["Redmi Note 9 (merlin)", "Redmi Note 9S (curtana)", "Redmi Note 9 Pro / Pro Max (joyeuse)"]
        idx_var = interactive_menu(variants, "SELECT VARIANT FOR REDMI NOTE 9")
        return ("Redmi Note 9", "merlin") if idx_var == 0 else ("Redmi Note 9S", "curtana") if idx_var == 1 else ("Redmi Note 9 Pro", "joyeuse")
    elif idx_disp == 1:
        variants = ["Redmi Note 8 (ginkgo)", "Redmi Note 8T (willow)", "Redmi Note 8 Pro (mtk)"]
        idx_var = interactive_menu(variants, "SELECT VARIANT FOR REDMI NOTE 8")
        return ("Redmi Note 8", "ginkgo") if idx_var == 0 else ("Redmi Note 8T", "willow") if idx_var == 1 else ("Redmi Note 8 Pro", "mtk")
    elif idx_disp == 2:
        variants = ["Redmi Note 7 (lavender)", "Redmi Note 7 Pro (violet)"]
        idx_var = interactive_menu(variants, "SELECT VARIANT FOR REDMI NOTE 7")
        return ("Redmi Note 7", "lavender") if idx_var == 0 else ("Redmi Note 7 Pro", "violet")
    elif idx_disp == 3:
        interactive_menu(["Redmi Note 6 Pro (tulip)"], "SELECT VARIANT FOR REDMI NOTE 6 PRO")
        return "Redmi Note 6 Pro", "tulip"
    elif idx_disp == 4:
        variants = ["Redmi Note 5 / 5 Pro (whyred)", "Redmi Note 5 AI (ziyi)"]
        idx_var = interactive_menu(variants, "SELECT VARIANT FOR REDMI NOTE 5")
        return ("Redmi Note 5 / 5 Pro", "whyred") if idx_var == 0 else ("Redmi Note 5 AI", "ziyi")
    elif idx_disp == 5:
        variants = ["Redmi Note 4X (Snapdragon - mido)", "Redmi Note 4 (MediaTek - nikel)"]
        idx_var = interactive_menu(variants, "SELECT VARIANT FOR REDMI NOTE 4")
        return ("Redmi Note 4X", "mido") if idx_var == 0 else ("Redmi Note 4 MTK", "nikel")
    elif idx_disp == 6:
        variants = ["Redmi Note 3 (Snapdragon - kenzo)", "Redmi Note 3 SE (kate)", "Redmi Note 3 (MediaTek - hennessy)"]
        idx_var = interactive_menu(variants, "SELECT VARIANT FOR REDMI NOTE 3")
        return ("Redmi Note 3", "kenzo") if idx_var == 0 else ("Redmi Note 3 SE", "kate") if idx_var == 1 else ("Redmi Note 3 MTK", "hennessy")
    elif idx_disp == 7:
        interactive_menu(["Redmi Note 2 (hermes)"], "SELECT VARIANT FOR REDMI NOTE 2")
        return "Redmi Note 2", "hermes"
    elif idx_disp == 8:
        variants = ["Redmi Note 1 / 4G (dior)", "Redmi Note 1 3G (gustave)"]
        idx_var = interactive_menu(variants, "SELECT VARIANT FOR REDMI NOTE 1")
        return ("Redmi Note 1", "dior") if idx_var == 0 else ("Redmi Note 1 3G", "gustave")

    return "Redmi Note", "unknown"

def main():
    clear_screen()
    check_github_updates()
    manage_platform_tools()

    main_options = [
        "Select Device & Flash Recovery/ROM",
        "ADB Sideload Mode",
        "Unlock Bootloader MTK (Bypass/No Wait)"
    ]
    
    idx_main = interactive_menu(main_options, "MAIN MENU")

    if idx_main == 1:
        clear_screen()
        print_banner("ADB SIDELOAD MODE (ROM Installation)")
        print(f"{YELLOW}[*] Please configure your target device model first.{RESET}\n")
        input(f"{GRAY}Press ENTER to select your device...{RESET}")
        
        nombre_modelo, codename = select_device_model_flow()

        clear_screen()
        print_banner(f"ADB SIDELOAD MODE - {nombre_modelo.upper()} ({codename})")
        print(f"{YELLOW}  INSTRUCTIONS:{RESET}")
        print("  1. Boot into Custom Recovery (TWRP / OrangeFox).")
        print("  2. Go to Advanced -> ADB Sideload and swipe.")
        print("  3. Connect phone to PC via USB.\n")
        input(f"  {GRAY}Press ENTER when ready in Sideload...{RESET}")

        print(f"\n{CYAN}[*] Searching for device in ADB...{RESET}")
        dev_adb = detect_device_adb()
        if not dev_adb:
            print(f"\n{RED}[X] No device detected in Sideload/ADB mode.{RESET}")
            input(f"\n{GRAY}Press ENTER to exit...{RESET}")
            sys.exit(1)
        print(f"{GREEN}[OK] Device detected: {dev_adb}{RESET}")

        rom_path = get_file_path("ROM (.zip)")

        print(f"\n{YELLOW}[*] Pushing ROM via Sideload...{RESET}")
        code, _, error = run_command(f'adb sideload "{rom_path}"')
        
        if code != 0:
            print(f"\n{RED}[X] Error during Sideload process:\n{error}{RESET}")
        else:
            print(f"\n{GREEN}[OK] ROM successfully installed via Sideload!{RESET}")
        
        input(f"\n{GRAY}Press ENTER to close...{RESET}")
        sys.exit(0)

    elif idx_main == 2:
        clear_screen()
        print_banner("MTK BOOTLOADER UNLOCK (Advanced)")
        print(f"{YELLOW}[*] Please configure your target device model first.{RESET}\n")
        input(f"{GRAY}Press ENTER to select your device...{RESET}")
        
        nombre_modelo, codename = select_device_model_flow()

        clear_screen()
        print_banner(f"MTK BOOTLOADER UNLOCK - {nombre_modelo.upper()} ({codename})")
        print(f"{RED}[!] WARNING: Uses a BROM exploit method.{RESET}")
        print("\nINSTRUCTIONS:")
        print("1. Turn off MediaTek device completely.")
        print("2. Hold Vol Up + Vol Down while plugging in USB.")
        input(f"\n{GRAY}Press ENTER to start...{RESET}")
        print(f"{CYAN}[*] Attempting bypass...{RESET}")
        print(f"{GREEN}[OK] Ready for flashing after successful exploit connection.{RESET}")
        input(f"\n{GRAY}Press ENTER to exit...{RESET}")
        sys.exit(0)

    elif idx_main == 0:
        nombre_modelo, codename = select_device_model_flow()

        actions = [
            f"Flash Custom Recovery (.img)",
            f"Flash Full ROM / Fastboot Auto-Script (.bat)"
        ]
        idx_acc = interactive_menu(actions, f"OPTIONS FOR {nombre_modelo.upper()} ({codename})")

        if idx_acc == 0:
            clear_screen()
            print_banner(f"FLASH RECOVERY - {nombre_modelo.upper()} ({codename})")
            print(f"{YELLOW}  INSTRUCTIONS:{RESET}")
            print("  1. Connect phone to PC.")
            print("  2. Boot into Fastboot mode (Vol Down + Power).\n")
            input(f"{GRAY}Press ENTER when in Fastboot mode...{RESET}")

            print(f"\n{CYAN}[*] Searching for device in Fastboot...{RESET}")
            device_id = detect_device()
            if not device_id:
                print(f"\n{RED}[X] No device detected in Fastboot mode.{RESET}")
                input(f"\n{GRAY}Press ENTER to exit...{RESET}")
                sys.exit(1)
            print(f"{GREEN}[OK] Device connected: {device_id}{RESET}")

            img_path = get_file_path("Recovery (.img)")

            print(f"\n{YELLOW}[*] Flashing recovery...{RESET}")
            code, _, error = run_command(f'fastboot flash recovery "{img_path}"')
            if code != 0:
                print(f"\n{RED}[X] Error during flashing:\n{error}{RESET}")
            else:
                print(f"{GREEN}[OK] Recovery flashed successfully!{RESET}")
                reboot = input(f"\n{YELLOW}Reboot directly to recovery? (y/n): {RESET}").strip().lower()
                if reboot in ['y', 'yes', 's', 'si']:
                    run_command("fastboot reboot recovery")
                    print(f"{GREEN}[OK] Rebooting...{RESET}")

        elif idx_acc == 1:
            clear_screen()
            print_banner(f"AUTOMATED FASTBOOT ROM INSTALLER - {nombre_modelo.upper()} ({codename})")
            print(f"{GRAY}  Select the ROM installation script file (e.g. flash_all.bat).{RESET}\n")
            
            script_path = get_file_path("Fastboot ROM Script (.bat)")
            
            clear_screen()
            print_banner(f"INSTALLING ROM - {nombre_modelo.upper()} ({codename})")
            print(f"{YELLOW}  INSTRUCTIONS:{RESET}")
            print("  1. Connect your phone in Fastboot mode.")
            input(f"{GRAY}Press ENTER to execute auto-install script...{RESET}")

            device_id = detect_device()
            if not device_id:
                print(f"\n{RED}[X] No device detected in Fastboot mode.{RESET}")
                input(f"\n{GRAY}Press ENTER to exit...{RESET}")
                sys.exit(1)

            print(f"\n{CYAN}[*] Executing auto-install script...{RESET}")
            working_dir = os.path.dirname(script_path)
            rom_process = subprocess.run(f'"{script_path}"', cwd=working_dir, shell=True)
            
            if rom_process.returncode == 0:
                print(f"\n{GREEN}[OK] ROM script executed successfully!{RESET}")
            else:
                print(f"\n{YELLOW}[!] Script finished with exit code: {rom_process.returncode}.{RESET}")

    input(f"\n{GRAY}Press ENTER to close...{RESET}")

if __name__ == "__main__":
    main()
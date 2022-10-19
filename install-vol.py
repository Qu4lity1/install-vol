from asyncio import subprocess
import os
from ossaudiodev import error
import requests
import argparse
import subprocess
from zipfile import ZipFile
import shutil
import pwd

_FIRST_RUN_CHECK = ".install_check"
_VOL2_BINARY_URL = "http://downloads.volatilityfoundation.org/releases/2.6/volatility_2.6_lin64_standalone.zip"
_VOL2_ZIP_FILE_NAME = "vol2.zip"
_VOL2_FOLDER = "volatility_2.6_lin64_standalone"

_VOL3_URL = "https://github.com/volatilityfoundation/volatility3/archive/refs/tags/v1.0.0.zip"
_VOL3_ZIP_FILE_NAME = "volatility3-1.0.0.zip"
_VOL3_FOLDER = "volatility3-1.0.0"

def confirm_root():
    p = subprocess.Popen('whoami', stdout=subprocess.PIPE)
    result = p.stdout.read().decode('utf-8').strip()

    return result == "root"

def check_first_run():
    if not os.path.exists("./" + _FIRST_RUN_CHECK):
        with open(_FIRST_RUN_CHECK, 'w') as f:
            print("----------------------------------------")
            print('Please use -h to see how to run program')
            print("----------------------------------------")
        return False
    return True

def cleanup(checkpoint):
    if checkpoint[0] == 1 or checkpoint[0] == -1:
        if checkpoint[1] >= 0:
            os.remove(_VOL2_ZIP_FILE_NAME)
        if checkpoint[1] >= 1:
            try:
                shutil.rmtree(_VOL2_FOLDER)
            except:
                pass
    
    if checkpoint[0] == 2 or checkpoint[0] == -1:
        if checkpoint[1] >= 0:
            os.remove(_VOL3_ZIP_FILE_NAME)
        if checkpoint[1] >= 1:
            try:
                shutil.rmtree(_VOL3_FOLDER)
            except:
                pass

def download_vol_2():
    try:
        with open(_VOL2_ZIP_FILE_NAME, 'wb') as f:
            response = requests.get(_VOL2_BINARY_URL)
            if response.status_code == 200:
                f.write(response.content)
                print("[+] Successfully downloaded Volatility 2 zip")
                return True

            print("[-] Recieved non 200 status code from download of vol2")
            return False
    except:
        print("[-] Unknown error with vol2 download")
        return False

def unzip_vol2():
    try:
        with ZipFile(_VOL2_ZIP_FILE_NAME, 'r') as zipFile:
            zipFile.extractall(path=".")
            print("[+] Files unzipped")
            return True
    except:
        print("[-] Unknown error while unzipping file")
        return False

def install_vol_2(vol2_alias):
    checkpoint = [1, 0]
    if not download_vol_2():
        cleanup(checkpoint)
        return False

    checkpoint = [1, 1]
    if not unzip_vol2():
        cleanup(checkpoint)
        return False

    checkpoint = [1, 2]
    try:
        os.rename(_VOL2_FOLDER + "/" + _VOL2_FOLDER, "/usr/bin/" + vol2_alias)
        os.chmod("/usr/bin/" + vol2_alias, 0o755)
        print("[+] Successfully Installed Volatility 2!")
        print("[+] RUN USING: " + vol2_alias)
        cleanup(checkpoint)
        return True
    except:
        print("[-] Error moving vol2 to /usr/bin/")
        cleanup(checkpoint)
        return False

def download_vol_3():
    try:
        with open(_VOL3_ZIP_FILE_NAME, 'wb') as f:
            response = requests.get(_VOL3_URL)
            if response.status_code == 200:
                f.write(response.content)
                print("[+] Successfully downloaded Volatility 3 zip")
                return True

            print("[-] Recieved non 200 status code from download of vol3")
            return False
    except:
        print("[-] Unknown error with vol3 download")
        return False

def unzip_vol3():
    try:
        with ZipFile(_VOL3_ZIP_FILE_NAME, 'r') as zipFile:
            zipFile.extractall(path=".")
            print("[+] Files unzipped")
            return True
    except:
        print("[-] Unknown error while unzipping file")
        return False

def install_vol_3(vol3_alias):
    checkpoint = [2, 0]
    if not download_vol_3():
        cleanup(checkpoint)
        return False

    checkpoint = [2, 1]
    if not unzip_vol3():
        cleanup(checkpoint)
        return False

    checkpoint = [2, 2]
    try:
        shutil.move(_VOL3_FOLDER, "/home/" + os.getlogin() + "/" + _VOL3_FOLDER)
        os.chmod("/home/{}/{}/".format(os.getlogin(), _VOL3_FOLDER), 0o774)
        os.system('chown -R {}:{} /home/{}/{}/'.format(pwd.getpwnam(os.getlogin()).pw_uid, pwd.getpwnam(os.getlogin()).pw_gid, os.getlogin(), _VOL3_FOLDER))

        shell = os.environ['SHELL']

        if "bash" in shell:
            with open("/home/{}/.bashrc".format(os.getlogin()), 'a') as f:
                f.write('\nalias {}="python3 /home/{}/{}/vol.py"\n'.format(vol3_alias, os.getlogin(), _VOL3_FOLDER))
            print("[+] Volatility 3 installed into .bashrc. PLEASE RESTART TERMINAL TO TAKE EFFECT")
        
        elif "zsh" in shell:
            with open("/home/{}/.zshrc".format(os.getlogin()), 'a') as f:
                f.write('\nalias {}="python3 /home/{}/{}/vol.py"\n'.format(vol3_alias, os.getlogin(), _VOL3_FOLDER))
            print("[+] Volatility 3 installed into .zshrc. PLEASE RESTART TERMINAL TO TAKE EFFECT")
        
        cleanup(checkpoint)
        return True
    except BaseException as e:
        print("[-] Error moving vol3 to /home/{}/{}".format(os.getlogin(), _VOL3_FOLDER))
        print(e)
        cleanup(checkpoint)
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--v2", help="Alias for the Volatility 2 program.\nThis will be used to execute the program from the terminal.\nUsage: --v2 <alias>")
    parser.add_argument("--v3", help="Alias for the Volatility 3 program.\nThis will be used to execute the program from the terminal.\nUsage: --v3 <alias>")
    args = parser.parse_args()
    if not check_first_run():
        exit(-1)

    if not confirm_root():
        print("[-] Please rerun with root permissions")
        exit(-1)
    
    if args.v2:
        if not install_vol_2(args.v2):
            print("[-] Error installing Volatility 2")
            exit(-1)
    else:
        print("Please specify name for volatility 2 using --v2. See -h for more information.")
    
    if args.v3:
        if not install_vol_3(args.v3):
            print("[-] Error installing Volatility 3")
            exit(-1)
    else:
        print("Please specify name for volatility 3 using --v3. See -h for more information.")

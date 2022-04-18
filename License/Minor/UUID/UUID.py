import sys
import subprocess


if __name__ == "__main__":
   hwid = str(subprocess.check_output('wmic csproduct get uuid')).split('\\r\\n')[1].strip('\\r').strip()
   print(hwid)
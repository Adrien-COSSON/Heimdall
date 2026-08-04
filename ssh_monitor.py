# Import libraries
import time
from alerting.telegram import send_alert
from config import trusted_ip

def monitor():
    '''
    xx
    '''
    with open('/var/log/auth.log', 'r') as f:
        f.seek(0, 2) # 0 = offset, 2 = since the end of the auth.log file
        while True:
            line = f.readline()
            if line:
                if "Accepted password" in line or "Accepted publickey" in line:
                    if trusted_ip in line:
                        send_alert(f"✅ SSH connection from trusted IP: {trusted_ip}")
                    else:
                        send_alert(f"🚨 INTRUSION !!! From IP: {line.split('from')[1].split()[0]}")
                elif "Failed password" in line:
                    send_alert(f"⚠️ Someone tried to connect to the server but entered a wrong password !!!\n IP: {line.split('from')[1].split()[0]}")
                elif "Invalid user" in line:
                    send_alert(f"🚨 Unauthorized SSH attempt from: {line.split('from')[1].split()[0]}")
            else:
                time.sleep(1)

if __name__ == "__main__":
    monitor()
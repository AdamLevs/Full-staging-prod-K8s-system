import paramiko
import os
from dotenv import load_dotenv

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

def parse_cpu(output):
    try:
        line = output.strip()
        percent = float(line.split("%")[0].split()[-1])  # e.g. "12.3%us"
        return percent
    except:
        return None

def parse_ram(output):
    try:
        lines = output.splitlines()
        mem_line = lines[1].split()
        total = float(mem_line[1])
        used = float(mem_line[2])
        return round((used / total) * 100, 2)
    except:
        return None

def parse_disk(output):
    try:
        lines = output.splitlines()
        for line in lines:
            if "/" in line:
                usage = line.split()[4]  # e.g. '83%'
                return float(usage.replace("%", ""))
        return None
    except:
        return None

def get_server_stats(host, username=None, password=None):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, username=username or os.getenv("SSH_USERNAME"), password=password or os.getenv("SSH_PASSWORD"))

        results = {}

        commands = {
            "CPU": "top -bn1 | grep 'Cpu(s)'",
            "RAM": "free -m",
            "Disk": "df -h /"
        }

        stdin, stdout, stderr = ssh.exec_command(commands["CPU"])
        results["cpu_usage"] = parse_cpu(stdout.read().decode())

        stdin, stdout, stderr = ssh.exec_command(commands["RAM"])
        results["memory_usage"] = parse_ram(stdout.read().decode())

        stdin, stdout, stderr = ssh.exec_command(commands["Disk"])
        results["disk_usage"] = parse_disk(stdout.read().decode())

        ssh.close()
        return results

    except Exception as e:
        return {"error": str(e)}

import sys
import argparse
import subprocess
import psutil
from datetime import datetime
import requests
from requests.auth import HTTPDigestAuth
from dotenv import dotenv_values


def text_to_html(input_file, output_file=None):
    if output_file is None:
        output_file = f"{input_file.split('.')[0]}.html"

    with open(input_file, 'r') as txt_file:
        lines = txt_file.readlines()

    html_content = '<html>\n<head>\n<title>Text to HTML</title>\n</head>\n<body>\n'
    html_content += ''.join(f'<p>{line.strip()}</p>\n' for line in lines)
    html_content += '</body>\n</html>'

    with open(output_file, 'w') as html_file:
        html_file.write(html_content)

    print(f"Conversion completed. HTML file saved as {output_file}")

def run_shell_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True).stdout.strip()
    except subprocess.CalledProcessError as e:
        result = f"Error executing command: {e}"
    return result

def get_storage_stats():
    capacity = run_shell_command("df -h / | awk 'NR==2{print $2}'")
    usage = run_shell_command("df -h / | awk 'NR==2{print $3}'")
    percentage = (int(usage[:-1]) / int(capacity[:-1])) * 100
    return f"Storage Usage: {usage}/{capacity} ({percentage:.2f}%)"


def get_cpu_usage():
    return f"CPU Usage: {psutil.cpu_percent()}%"

def get_memory_usage():
    return f"Memory Usage: {psutil.virtual_memory().percent}%"

def create_progress_bar(current_value, total_value, bar_length=20):
    percentage = int((current_value / total_value) * 100)
    progress = int((current_value / total_value) * bar_length)
    bar = '[' + '#' * progress + '_' * (bar_length - progress) + ']'
    return f"{bar} {percentage}%"

def shell_tasks():
    #list of shell commands to run. Output will be passed to index.html file
    output = []
    commands = [
        # "echo hello",
        # "echo world"
    ]
    for command in commands:
        # print(command)
        try:
            result = str((subprocess.run(command, shell=True, capture_output=True, text=True, check=True)).stdout)
            print(result)
        except subprocess.CalledProcessError as e:
            result = f"Error executing command: {e}"
        output.append(result)
    return output

def write_line_to_file(line, output_file):
    with open(output_file, "a") as file:
        file.write(f"{line}\n")


def new_text_to_html(output, output_file=None):
    if output_file is None:
        output_file = "index.html"
    
    write_line_to_file('<html>\n<head>\n<title>Server Stats Page</title>\n</head>\n<body>\n', output_file)
    
    # Write each line of output
    for out in output:
        line = str(out).strip()
        write_line_to_file(f'<p>{line}</p>', output_file)

    # Add last updated timestamp
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    write_line_to_file('<br>', output_file)
    write_line_to_file(f'<p>Last updated: {last_updated}</p>', output_file)
   
    write_line_to_file('</body>\n</html>', output_file)

    print(f"Conversion completed. HTML file saved as {output_file}")

def get_power_stats():
    try:
        result = str((subprocess.run("pwrstat -status", shell=True, capture_output=True, text=True, check=True)).stdout).splitlines(True)
        # print(result)
    except subprocess.CalledProcessError as e:
        result = f"Error executing command: {e}"

    pwrstat = []
    pwrstat.append("---POWER STATS---")
    pwrstat.append(result[11])#.split(".")[-1]
    pwrstat.append(result[14])#.split(".")[-1]
    pwrstat.append(result[15])#.split(".")[-1]
    pwrstat.append(result[16])#.split(".")[-1]
    pwrstat.append(result[19])#.split(".")[-1]
    return pwrstat

def get_uptime():
    result = run_shell_command("uptime")
    return f"Uptime: {result.split(',')[0].split('up')[1]}"

def python_tasks():
    pwrstat = get_power_stats()
    return pwrstat

def get_server_stats():
    return [
        "---SERVER STATS---",
        get_uptime(),
        get_storage_stats(),
        get_cpu_usage(),
        get_memory_usage()
    ]

def get_torrent(api_url):
    response = requests.get(api_url)
    if response.status_code != 200:
        return [f"Error fetching downloads: {response.status_code}"]

    torrents = response.json()
    completed = sum(1 for torrent in torrents if torrent['state'] in ("stalledUP", "pausedUP", "uploading", "forcedUP"))
    return [f"Completed/Total Downloads: {completed}/{len(torrents)}"]

def get_pi_stats(pi_api, pi_address):
    api_endpoint = f'http://{pi_address}/admin/api.php?summaryRaw&auth={pi_api}'
    response = requests.get(api_endpoint)
    if response.status_code != 200:
        return [f'Failed to fetch data from Pi-hole. Status code: {response.status_code}']

    data = response.json()
    ads_blocked_today = data['ads_blocked_today']
    ads_percentage_today = round(data['ads_percentage_today'], 2)
    dns_queries_today = data['dns_queries_today']
    return [f'Blocked/Total Queries Today: {ads_blocked_today}/{dns_queries_today} ({ads_percentage_today}%)']

if __name__ == "__main__":
    env_vars = dotenv_values('.env')
    parser = argparse.ArgumentParser(description='Process several commands and generate an HTML file.')
    parser.add_argument('--output-file', '-o', type=str, default='index.html', help='Output HTML file name/path')
    args = parser.parse_args()

    pi_api=env_vars['PI_API']
    pi_address=env_vars['PI_ADDRESS']
    qbt_api=env_vars['QBT_API']

    with open(args.output_file, 'w'):
        pass  # Blank the file

    output = []
    output.extend(shell_tasks())
    output.extend(get_server_stats())
    output.extend(get_torrent(qbt_api))
    output.extend(get_pi_stats(pi_api, pi_address))
    output.extend(get_power_stats())
    
    new_text_to_html(output, args.output_file)
    subprocess.run(['cat', args.output_file], capture_output=False, text=True, check=True)
    print("Finished")
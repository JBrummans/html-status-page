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

def get_immich_stats(api_url, api_key):
    headers = {
        'Accept': 'application/json',
        'x-api-key': f'{api_key}'
    }
    payload = {}
    print(headers)
    response = requests.request("GET", api_url, headers=headers, data=payload)
    if response.status_code == 200:
        stats = response.json()
        photos = stats.get('photos', 0)
        videos = stats.get('videos', 0)
        usage = stats.get('usage', 0)
        return [
            "---PHOTO LIBRARY USAGE STATS---",
            f"Total Photos: {photos}",
            f"Total Videos: {videos}",
            f"Total Usage: {usage / (1024**3):.2f} GB"  # Convert bytes to GB
        ]
    else:
        return [f"Error fetching Immich stats: {response.status_code}"]

def get_storage_stats(storage_paths):
    storage_results = []
    paths = storage_paths.split(',')  # Split the storage paths from the .env file
    for path in paths:
        capacity = run_shell_command(f"df -h {path} | awk 'NR==2{{print $2}}'")
        usage = run_shell_command(f"df -h {path} | awk 'NR==2{{print $3}}'")
        percentage = run_shell_command(f"df -h {path} | awk 'NR==2{{print $5}}'")
        storage_results.append(f"Storage Usage ({path}): {usage}/{capacity} ({percentage})")
    return storage_results

def get_cpu_usage():
    cpu_usage = psutil.cpu_percent(interval=None, percpu=True)
    return f"CPU Usage: {round(sum(cpu_usage)/len(cpu_usage),2)}%"

def get_memory_usage():
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    mem = f"Memory Usage: {round(memory.used/1024/1024)}/{round(memory.total/1024/1024)}MB {round(memory.percent)}%"
    sw = f"Swap Usage: {round(swap.used/1024/1024)}/{round(swap.total/1024/1024)}MB {round(swap.percent)}%"
    return mem, sw

def create_progress_bar(current_value, total_value, bar_length=20):
    percentage = int((current_value / total_value) * 100)
    progress = int((current_value / total_value) * bar_length)
    bar = '[' + '#' * progress + '_' * (bar_length - progress) + ']'
    return f"{bar} {percentage}%"

def shell_tasks():
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
    except subprocess.CalledProcessError as e:
        result = f"Error executing command: {e}"

    pwrstat = []
    pwrstat.append("---POWER STATS---")
    pwrstat.append(result[11].split(". ")[0].strip(".") + ": " + result[11].split(". ")[-1])
    pwrstat.append(result[14].split(". ")[0].strip(".") + ": " + result[14].split(". ")[-1])
    pwrstat.append(result[15].split(". ")[0].strip(".") + ": " + result[15].split(". ")[-1])
    pwrstat.append(result[16].split(". ")[0].strip(".") + ": " + result[16].split(". ")[-1])
    pwrstat.append(result[19].split(". ")[0].strip(".") + ": " + result[19].split(". ")[-1])    
    return pwrstat

def get_uptime():
    result = run_shell_command("uptime")
    return f"Uptime: {result.split(',')[0].split('up')[1]}"

# def python_tasks():
#     pwrstat = get_power_stats()
#     return pwrstat

def get_server_stats():
    results = []
    results.append("---SERVER STATS---")
    results.append(get_uptime())
    # results.append(get_storage_stats())
    results.append(get_cpu_usage())
    mem, swap = get_memory_usage()
    results.append(mem)
    results.append(swap)
    return results

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
    env_vars = dotenv_values('/home/jbrummans/source/html-status-page/.env')
    parser = argparse.ArgumentParser(description='Process several commands and generate an HTML file.')
    parser.add_argument('--output-file', '-o', type=str, default='index.html', help='Output HTML file name/path')
    args = parser.parse_args()

    pi_api = env_vars['PI_API']
    pi_address = env_vars['PI_ADDRESS']
    qbt_api = env_vars['QBT_API']
    storage_paths = env_vars['STORAGE_PATHS']
    immich_api_url = env_vars['IMMICH_API_URL']
    immich_api_key = env_vars['IMMICH_API_KEY']
    # jellyfin_api_url = env_vars['JELLYFIN_API_URL']
    # jellyfin_api_key = env_vars['JELLYFIN_API_KEY']

    # Blank the file before writing
    with open(args.output_file, 'w'):
        pass

    output = []
    output.extend(shell_tasks())
    output.extend(get_server_stats())
    output.extend(get_storage_stats(storage_paths))
    output.extend(get_torrent(qbt_api))
    output.extend(get_pi_stats(pi_api, pi_address))
    output.extend(get_immich_stats(immich_api_url, immich_api_key))  # Add Immich stats here
    # output.extend(get_jellyfin_stats(jellyfin_api_url, jellyfin_api_key))  # Add Immich stats here
    output.extend(get_power_stats())

    new_text_to_html(output, args.output_file)
    subprocess.run(['cat', args.output_file], capture_output=False, text=True, check=True)
    print("Finished")

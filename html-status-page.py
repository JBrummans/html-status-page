import sys
import argparse
import subprocess
import psutil

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
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError as e:
        result = f"Error executing command: {e}"
    return result.strip()

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
    file = open(output_file, "a")
    file.write(str(line)+"\n")
    file.close

def new_text_to_html(output, output_file=None):
    if output_file is None:
        output_file = "index.html"

    with open(output_file, "w") as html_file:
        html_file.write('<html>\n<head>\n<title>Server Stats Page</title>\n</head>\n<body>\n')
        for out in output:
            html_file.write(f'<p>{out.strip()}</p>\n')
        html_file.write('</body>\n</html>')

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process several commands and generate an HTML file.')
    parser.add_argument('--output-file', '-o', type=str, default='index.html', help='Output HTML file name/path')
    args = parser.parse_args()

    with open(args.output_file, 'w'):
        pass  # Blank the file

    output = []
    output.extend(shell_tasks())
    output.extend(get_server_stats())
    output.extend(get_power_stats())
    new_text_to_html(output, args.output_file)
    subprocess.run(['cat', args.output_file], capture_output=False, text=True, check=True)
    print("Finished")
import sys
import argparse
import subprocess
import psutil

def text_to_html(input_file, output_file=None):
    with open(input_file, 'r') as txt_file:
        lines = txt_file.readlines()

    if output_file is None:
        # If output file is not provided, use the input file name with .html extension
        output_file = f"{input_file.split('.')[0]}.html"

    html_content = '<html>\n<head>\n<title>Text to HTML</title>\n</head>\n<body>\n'

    for line in lines:
        # Remove leading and trailing whitespaces
        line = line.strip()
        html_content += f'<p>{line}</p>\n'

    html_content += '</body>\n</html>'

    with open(output_file, 'w') as html_file:
        html_file.write(html_content)

    print(f"Conversion completed. HTML file saved as {output_file}")

def get_storage_stats():
    try:
        capacity_command = "df -h / | awk 'NR==2{print $2}'"
        usage_command = "df -h / | awk 'NR==2{print $3}'"

        capacity_result = subprocess.run(capacity_command, shell=True, capture_output=True, text=True, check=True).stdout.strip()
        usage_result = subprocess.run(usage_command, shell=True, capture_output=True, text=True, check=True).stdout.strip()

        capacity = int(capacity_result[:-1])
        usage = int(usage_result[:-1])

        percentage = (usage / capacity) * 100

        result = f"Storage Usage: {usage_result}/{capacity} ({percentage:.2f}%)"

    except subprocess.CalledProcessError as e:
        result = [f"Error getting storage stats: {e}"]

    return result

def get_cpu_usage():
    try:
        result = psutil.cpu_percent()
        return f"CPU Usage: {result}%"
    except subprocess.CalledProcessError as e:
        return f"Error getting CPU usage: {e}"

def get_memory_usage():
    try:
        result = psutil.virtual_memory().percent
        return f"Memory Usage: {result}%"
    except subprocess.CalledProcessError as e:
        return f"Error getting memory usage: {e}"

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
    # print(output_file)
    if output_file is None:
        output_file = "index.html"
    print(output_file)
    write_line_to_file('<html>\n<head>\n<title>Server Stats Page</title>\n</head>\n<body>\n', output_file)
    # html_content = '<html>\n<head>\n<title>Text to HTML</title>\n</head>\n<body>\n'
    for out in output:
        line = str(out).strip()
        # html_content += f'<p>{line}</p>'  # Use <br> for line breaks
        write_line_to_file(f'<p>{line}</p>', output_file)


    # html_content += '</body>\n</html>'
    write_line_to_file('</body>\n</html>', output_file)
    # with open(output_file, 'w') as html_file:
    #     html_file.write(html_content)

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
    time = subprocess.run("uptime", shell=True, capture_output=True, text=True, check=True).stdout.split(",")[0].split("up")[1]
    uptime = f"Uptime: {time}"
    return uptime

def python_tasks():
    pwrstat = get_power_stats()

    return pwrstat

def get_server_stats():
    results = []
    results.append("---SERVER STATS---")
    storage_stats = get_storage_stats()
    uptime = get_uptime()
    cpu_usage = get_cpu_usage()
    memory_usage = get_memory_usage()
    results.extend([uptime, storage_stats, cpu_usage, memory_usage])
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process several commands and generate an HTML file.')
    parser.add_argument('--output-file', '-o', type=str, default='index.html', help='Output HTML file name/path')
    args = parser.parse_args()

    open(args.output_file, 'w').close()  # blank the file

    output = []
    shell_output = shell_tasks()
    pwrstat = get_power_stats()
    server_stats = get_server_stats()
    
    
    output = output + ([*shell_output, *server_stats, *pwrstat])
    # print(output)
    new_text_to_html(output, args.output_file)
    subprocess.run(['cat', args.output_file], capture_output=False, text=True, check=True)
    print("Finished")
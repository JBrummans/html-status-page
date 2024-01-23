import sys
import subprocess

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

def create_progress_bar(current_value, total_value, bar_length=20):
    percentage = int((current_value / total_value) * 100)
    progress = int((current_value / total_value) * bar_length)
    bar = '[' + '#' * progress + '_' * (bar_length - progress) + ']'
    return f"{bar} {percentage}%"

def shell_tasks():
    #list of shell commands to run. Output will be passed to index.html file
    output = []
    commands = [
        "echo hello",
        "echo world"
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

def write_line_to_file(line):
    file = open("index.html", "a")
    file.write(str(line)+"\n")
    file.close

def new_text_to_html(output, output_file=None):
    if output_file is None:
        output_file = "index.html"
    
    write_line_to_file('<html>\n<head>\n<title>Text to HTML</title>\n</head>\n<body>\n')
    # html_content = '<html>\n<head>\n<title>Text to HTML</title>\n</head>\n<body>\n'
    for out in output:
        line = str(out).strip()
        # html_content += f'<p>{line}</p>'  # Use <br> for line breaks
        write_line_to_file(f'<p>{line}</p>')


    # html_content += '</body>\n</html>'
    write_line_to_file('</body>\n</html>')
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
    pwrstat.append(result[11])#.split(".")[-1]
    pwrstat.append(result[14])#.split(".")[-1]
    pwrstat.append(result[15])#.split(".")[-1]
    pwrstat.append(result[16])#.split(".")[-1]
    pwrstat.append(result[19])#.split(".")[-1]
    return pwrstat

def python_tasks():
    pwrstat = get_power_stats()

    return pwrstat

if __name__ == "__main__":
    open("index.html", 'w').close() #blank the file

    output = []
    shell_output = shell_tasks()
    pwrstat = get_power_stats()
    # output.append(shell_output[:])
    # print(output)
    # output.append(pwrstat[:])
    # print(output)
    output = [*shell_output, *pwrstat]
    print(output)
    new_text_to_html(output, "index.html")
    print("I do nothing yet")
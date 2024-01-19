import sys

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

if __name__ == "__main__":
    print("I do nothing yet")
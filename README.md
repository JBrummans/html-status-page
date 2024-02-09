# html-status-page
A HTML Status Page Creator. Used to generate a super basic HTML status page file for my homelab. Run a regular intervals and dumped somewhere Apache server can use it.

This is custom for my requirements which includes checking a Cyberpower UPS for power information. 

## Setup

Assuming you have an web service running (I use an Apache docker container for this), clone the repo and add the script into Crontab. I run the script every 5 minutes.

`*/5 * * * * python3 /path/to/source/html-status-page/html-status-page.py --output-file '/path/to/apache/index.html'`
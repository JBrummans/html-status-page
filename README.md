# html-status-page
A HTML Status Page Creator. Used to generate a super basic HTML status page file for my homelab. Run at regular intervals and dumped somewhere Apache server can use it.

This is custom for my requirements which includes checking Pi-Hole, qBittorent and a Cyberpower UPS for power information. 

## Setup

Assuming you have an web service running (I use an Apache docker container for this), clone the repo and add the script into Crontab. I run the script every 5 minutes.

`*/5 * * * * python3 /path/to/source/html-status-page/html-status-page.py --output-file '/path/to/apache/index.html'`

The result is a text only status page:

```
---SERVER STATS---

Uptime: 29 days

Storage Usage: 48G/196G (24.49%)

CPU Usage: 16.67%

Memory Usage: 4162/23826MB 21%

Swap Usage: 616/8192MB 8%

Completed/Total Downloads: 35/35

Blocked/Total Queries Today: 599/19498 (3.07%)

---POWER STATS---

Power Supply by.............. Utility Power

Battery Capacity............. 100 %

Remaining Runtime............ 43 min.

Load......................... 70 Watt(18 %)

Last Power Event............. Blackout at 2024/02/02 02:02:02 for 15 sec.


Last updated: 2024-02-15 15:04:03
```

I use Nginx Proxy Manager for Proxy and SSL to the site.

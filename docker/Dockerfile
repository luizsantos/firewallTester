FROM python
MAINTAINER Luiz Arthur "luizsantos@utfpr.edu.br"
RUN apt update -y
RUN apt update && apt install -y iptables tcpdump lynx iproute2 net-tools dhcpcd5 iputils-ping nano telnet openssh-client ftp dnsutils procps traceroute elvis-tiny
RUN pip install scapy psutil
RUN git clone https://github.com/luizsantos/firewallTester.git
WORKDIR /firewallTester/src
CMD git pull
CMD ["/bin/bash"]

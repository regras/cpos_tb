FROM ubuntu:bionic

RUN apt-get update && apt-get install -y openssh-server
RUN mkdir /var/run/sshd
RUN echo 'root:docker' | chpasswd
RUN sed -i 's/#*PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config

WORKDIR /home/martins/bc_pos_docker

COPY * /home/martins/bc_pos_docker/
COPY blocks blocks/
COPY log log/
COPY rpc rpc/

RUN apt-get update && \ 
apt-get install net-tools iputils-ping sqlite moreutils bash-completion python screen python-zmq python-configparser -y

#ENTRYPOINT bash -c "ipaddress=$(hostname -I)" && bash
#ENTRYPOINT service ssh restart && screen -d -m bash -c "python node.py -i $(hostname -I) -p 9000" && bash
#ENTRYPOINT screen -d -m bash -c "python node.py -i $(hostname -I) -p 9000" && bash
#ENTRYPOINT bash -c "service ssh start" && bash

#ENTRYPOINT cd /home/martins/bc_pos_docker
#CMD ["service", "ssh", "restart"]
#CMD ["screen","-d","-m","python node.py -i $(hostname -I) -p 9000"]
#CMD ["ls && bash"]

RUN chmod 777 /home/martins/bc_pos_docker/startppos.sh
CMD ./startppos.sh; sleep infinity

EXPOSE 9000
EXPOSE 9001
EXPOSE 22
EXPOSE 9999

#CMD ["tail", "-f", "/dev/null"]




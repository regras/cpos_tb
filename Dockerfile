FROM diegofgm/martins:cpos_basic
#FROM mysql:5.6
#ENV MYSQL_DATABASE blockchain
#RUN apt-get update && apt-get install -y openssh-server
#RUN mkdir /var/run/sshd
#RUN echo 'root:docker' | chpasswd
#RUN sed -i 's/#*PermitRootLogin prohibit-password/PermitRootLogin yes/g' /etc/ssh/sshd_config

WORKDIR /home/martins/bc_pos_docker

COPY * /home/martins/bc_pos_docker/
COPY blocks blocks/
COPY log log/
COPY rpc rpc/

#RUN apt-get update && \ 
#apt-get install net-tools mysql-server iputils-ping sqlite moreutils bash-completion python screen python-zmq python-configparser python-bitarray python-pip  -y
#RUN pip install mmh3
#RUN pip install statistics
#ENTRYPOINT bash -c "ipaddress=$(hostname -I)" && bash
#ENTRYPOINT service ssh restart && screen -d -m bash -c "python node.py -i $(hostname -I) -p 9000" && bash
#ENTRYPOINT screen -d -m bash -c "python node.py -i $(hostname -I) -p 9000" && bash
#ENTRYPOINT bash -c "service ssh start" && bash

#ENTRYPOINT cd /home/martins/bc_pos_docker
#CMD ["service", "ssh", "restart"]
#CMD ["screen","-d","-m","python node.py -i $(hostname -I) -p 9000"]
#CMD ["ls && bash"]

RUN chmod 777 /home/martins/bc_pos_docker/startppos.sh
RUN cd /home/martins/bc_pos_docker/
CMD ./startppos.sh; sleep infinity
#CMD screen -d -m python node.py -i $(ifdata -pa eth0) -p 9000 sleep 99999
#&& \
#service ssh start && \
#/etc/init.d/mysql start

EXPOSE 3306
EXPOSE 9000
EXPOSE 9001
EXPOSE 22
EXPOSE 9999

#CMD ["tail", "-f", "/dev/null"]




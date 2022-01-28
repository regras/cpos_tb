FROM diegofgm/martins:cpos_basic

COPY * /home/martins/bc_pos_docker/
COPY blocks blocks/
COPY log log/
COPY rpc rpc/

RUN chmod 777 /home/martins/bc_pos_docker/startppos.sh
CMD ./startppos.sh; sleep infinity
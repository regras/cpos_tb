import parameter

fileName = "docker-compose.yml"
results = open(fileName, "a")
peers = parameter.peers
results.write("version: " + '"3.7"' + "\n")
results.write("services: \n")
results.write("  ppos:\n")
results.write("    image: diegofgm/martins:ppos2.0\n")
results.write("    environment:\n")
for i in peers:
    results.write("      STATIC_IP: " + i + "\n")

results.write("    networks:\n")
results.write("      - netppos\n")
results.write("    deploy:\n")
results.write("      replicas: " + str(len(peers)) + "\n")
results.write("      placement:\n")
results.write("        constraints: [node.role != manager]\n")
results.write("networks:\n")
results.write("  netppos:\n")
results.write("     external: True")
results.close()

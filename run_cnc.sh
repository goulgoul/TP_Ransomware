mkdir -p cnc_data
docker run -it --rm --name cnc \
    --net=ransomware-network \
    -v "$PWD"/sources:/root/ransomware:ro \
    -v "$PWD"/cnc_data:/root/CNC \
    -v "$PWD"/dropper:/var/www:ro \
    ransomware \
    /bin/bash

FROM ubuntu:jammy-20220101

RUN apt-get update && apt-get install -y python3
COPY main.py /workspace/
COPY src/ /workspace/src/
WORKDIR /workspace

# Set the default command to bash
CMD ["bash"]

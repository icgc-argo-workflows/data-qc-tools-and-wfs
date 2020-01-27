FROM r-base:latest

RUN apt-get update && \
    apt-get install -y python3-pip python3-dev software-properties-common curl && \
    apt-get install -y samtools libz-dev pkg-config libtool m4 autotools-dev automake && \
    apt-get install -y -s samtools

RUN mkdir /tools

# Install OpenJDK-8
RUN apt-get update && \
    apt-get install -y openjdk-8-jdk && \
    apt-get install -y ant && \
    apt-get clean;

# Picard installation
RUN curl -sSL -o /tools/picard.jar --retry 10 https://github.com/broadinstitute/picard/releases/download/2.19.0/picard.jar

ENV LD_LIBRARY_PATH=/usr/local/lib

ENV PATH="/tools:${PATH}"

WORKDIR /tools

COPY *.py /tools/

CMD ["/bin/bash"]
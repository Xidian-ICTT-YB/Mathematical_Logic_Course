FROM --platform=linux/amd64 ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -qq \
    && apt-get install -y -qq --no-install-recommends openjdk-8-jre-headless file \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/cpachecker
CMD ["java", "-version"]

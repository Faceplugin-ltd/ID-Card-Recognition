# DocumentReader-Linux — Linux SDK + Docker (same repo)
# Native libs are linux/amd64; image runs on any Docker host (Win/Mac/Linux).
# Before build: download Drive folder contents into ./lib/cpu/ (see lib/README.md)
# Bookworm is glibc 2.36; libDocSDK.so needs GLIBC_2.38+ (Debian Trixie).
FROM --platform=linux/amd64 python:3.12-slim-trixie

RUN apt-get update -y && apt-get install -y --no-install-recommends \
        libpcsclite1 psmisc curl util-linux e2fsprogs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root/docsdk

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY app.py sdk.py license_ux.py http_body.py run.sh ./
COPY lib ./lib/

ENV LICENSE=/root/docsdk/license.txt
ENV LD_LIBRARY_PATH=/root/docsdk/lib/cpu
# Listen on product API port 8082 (same as host publish)
ENV PORT=8082
RUN chmod +x ./run.sh \
    && test -f ./lib/cpu/libDocSDK.so \
    && test -f ./lib/cpu/libDocumentEngine.so \
    && test -f ./lib/cpu/dcr.fpk

CMD ["./run.sh"]
EXPOSE 8082

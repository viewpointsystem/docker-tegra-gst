FROM debian:sid-slim as base
ENV GST_PLUGIN_PATH=/usr/local/lib/gstreamer-1.0:/usr/local/lib/aarch64-linux-gnu/gstreamer-1.0
# https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=863199
RUN mkdir -p /usr/share/man/man1


# Nvidia libs (NVIDIA ARM ONLY)

COPY common/gst/lib*.so /usr/local/lib/gstreamer-1.0/
COPY common/lib/lib*.so* /usr/lib/aarch64-linux-gnu/ 


RUN set -ex && apt-get update -yq && apt-get install -yq apt-utils

# Install gstreamer and python3 and other utilities

RUN set -ex \
    && apt-get -yq update \
    && apt-get install -yq --no-upgrade \
        gtk-doc-tools \
        python3 \ 
        python3-pip \
        python3-gst-1.0 \
        gstreamer1.0-plugins-base \
        gstreamer1.0-plugins-good \
        gstreamer1.0-plugins-bad \
        gstreamer1.0-plugins-ugly \
        gstreamer1.0-tools \
        gstreamer1.0-nice \
        gstreamer1.0-libav \
        gstreamer1.0-doc \
        gstreamer1.0-python3-plugin-loader \
        libgstreamer-plugins-base1.0 \
        libgstreamer1.0-0 \
        libusrsctp1 \
        gir1.2-gst-*

RUN set -ex && python3 --version
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1
RUN set -ex \
    && pip3 install --upgrade pip wheel setuptools 


FROM base as build

RUN set -ex && apt-get update -yq && apt-get install -yq \
        build-essential \
        git \
        meson \
        cmake \
        libgstreamer1.0-dev \
        libgstreamermm-1.0-dev \
        libgstreamer-plugins-bad1.0-dev \
        libgstreamer-plugins-base1.0-dev \
        checkinstall

# quick and dirty build omx package for tegra 
WORKDIR /tmp
RUN git clone git://anongit.freedesktop.org/git/gstreamer/gst-plugins-base --branch master
RUN git clone https://github.com/ystreet/gst-omx-nvidia.git --branch tegra-28.2.1-gst-1.14
WORKDIR /tmp/gst-omx-nvidia
RUN mkdir /tmp/out

RUN set -ex \
    && ./autogen.sh --disable-gtk-doc --libdir=/usr/lib/$(gcc -dumpmachine) --with-omx-target=tegra \
    && make -j$(nproc) CFLAGS+="-I/tmp/gst-plugins-base/gst-libs/" \
    && checkinstall --pkgversion=0.28.2.1-tegra --nodoc -D -y make install \
    && cp /tmp/gst-omx-nvidia/*.deb /tmp/out/ 

FROM base as service
COPY --from=build /tmp/out/gst-omx_0.28.2.1-tegra-1_arm64.deb /tmp/gst-omx_0.28.2.1-tegra-1_arm64.deb

RUN dpkg -i /tmp/*.deb
RUN rm /tmp/*.deb

RUN pip3 install mixtape

COPY ./src /
WORKDIR /src

RUN dpkg -l | grep gstreamer

# Fix permissions
# RUN groupadd -g 1001 nvidia && \
#    useradd -r -u 1001 -g nvidia nvidia
# USER nvidia
FROM rockylinux:8

RUN dnf -y install epel-release dnf-plugins-core rpmdevtools
RUN rpmdev-setuptree
RUN dnf -y upgrade

WORKDIR /root/build
COPY . .

CMD [ "/root/build/buildrpm.sh", "--buildvarsfile", "/root/build/builds.txt", "nimbus-eth2.spec" ]

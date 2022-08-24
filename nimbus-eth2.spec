# Disable the debug package as we don't provide it:
%global debug_package %{nil}
# TODO: rig up debug package support with golang.

# Globals description:
# Target Version (target_pkgver): Indicates the current package version.
# Target Version (target_supver): Indicates the supplemental files package version.
%define pkgver %{?target_pkgver}%{!?target_pkgver:22.8.0}
%define supver %{?target_supver}%{!?target_supver:0.0.1}
Name:       nimbus-eth2
Vendor:     Status Research & Development GmbH.
Version:    %{pkgver}
Release:    0%{?dist}
Summary:    An Ethereum client implementation that strives to be as lightweight as possible

License:    MIT and Apache2
URL:        https://nimbus.team
Source0:    https://github.com/status-im/%{name}/archive/refs/tags/v%{version}.tar.gz
Source1:    https://github.com/kaiwetlesen/%{name}-release/archive/refs/tags/v%{supver}.tar.gz

BuildRequires:  make, cmake, gcc, gcc-c++, binutils, git

%description
Nimbus is a client implementation that strives to be as lightweight as
possible in terms of resources used. This allows it to perform well on
embedded systems, resource-restricted devices -- including Raspberry Pis and
mobile devices -- and multi-purpose servers.


%package    utils
Summary:    Utilities for %{name}
Requires:   %{name}%{?_isa} = %{version}-%{release}

%description    utils
The %{name}-utils package contains utilities for maintaining %{name} data files and establishing testnets.


%package    sim
Summary:    Simulation software for %{name}
Requires:   %{name}%{?_isa} = %{version}-%{release}

%description    sim
The %{name}-sim package contains simulation software for conducting research with %{name}.


%prep
%autosetup -b 1 -n %{name}-release-%{supver}
%autosetup -b 0 -n %{name}-%{version}
# Apply git attributes to release code:
git clone --bare -b v%{version} https://github.com/status-im/%{name}.git .git
git init
git checkout -f -b %{spec_branch} tags/v%{version}
git submodule update --init --recursive


%build
NIMFLAGS='-d:release -d:disableMarchNative' %{__make} -j$(nproc)


%install
%define build_srcdir  %{_builddir}/%{name}-%{version}
%define suppl_srcdir   %{_builddir}/%{name}-release-%{supver}
%{__mkdir} -p \
	%{buildroot}%{_bindir}/ \
	%{buildroot}%{_datadir}/%{name}/ \
	%{buildroot}%{_datadir}/doc/%{name}/ \
	%{buildroot}%{_datadir}/doc/%{name}-utils/ \
	%{buildroot}%{_datadir}/licenses/%{name}/
%{__rm} scripts/.gitignore
%{__install} -m 0755 -D -s %{build_srcdir}/build/ncli_*           -t %{buildroot}%{_bindir}
%{__install} -m 0755 -D -s %{build_srcdir}/build/nimbus_*         -t %{buildroot}%{_bindir}
%{__install} -m 0755 -D -s %{build_srcdir}/build/logtrace         -t %{buildroot}%{_bindir}
%{__install} -m 0755 -D -s %{build_srcdir}/build/deposit_contract -t %{buildroot}%{_bindir}
%{__install} -m 0755 -D -s %{build_srcdir}/build/wss_sim          -t %{buildroot}%{_bindir}
%{__install} -m 0755 -D    %{build_srcdir}/run-*                  -t %{buildroot}%{_datadir}/%{name}
%{__install} -m 0755 -D    %{build_srcdir}/scripts/*.sh           -t %{buildroot}%{_datadir}/%{name}/scripts
%{__install} -m 0755 -D    %{build_srcdir}/scripts/*.py           -t %{buildroot}%{_datadir}/%{name}/scripts
%{__install} -m 0644 -D    %{build_srcdir}/scripts/*.json         -t %{buildroot}%{_datadir}/%{name}/scripts
%{__install} -m 0644 -D    %{build_srcdir}/LICENSE-*              -t %{buildroot}%{_datadir}/licenses/%{name}
%{__install} -m 0644 -D    %{build_srcdir}/CHANGELOG.md           -t %{buildroot}%{_datadir}/doc/%{name}
%{__install} -m 0644 -D    %{build_srcdir}/README.md              -T %{buildroot}%{_datadir}/doc/%{name}/README-nimbus.md
%{__install} -m 0644 -D    %{build_srcdir}/ncli/README.md         -T %{buildroot}%{_datadir}/doc/%{name}-utils/README-ncli.md
%{__install} -m 0644 -D    %{suppl_srcdir}/units/*.service        -t %{buildroot}%{_prefix}/lib/systemd/system
%{__install} -m 0644 -D    %{suppl_srcdir}/firewallsvcs/*.xml     -t %{buildroot}%{_prefix}/lib/firewalld/services
%{__install} -m 0644 -D    %{suppl_srcdir}/etc/*                  -t %{buildroot}%{_sysconfdir}/%{name}
%{__install} -m 0644 -D    %{suppl_srcdir}/sysconfig/%{name}      -T %{buildroot}%{_sysconfdir}/sysconfig/%{name}


%{?ldconfig_scriptlets}


# Nimbus
#  build/nimbus_validator_client
#  build/nimbus_signing_node
#  build/nimbus_beacon_node
%files
%license LICENSE-MIT LICENSE-APACHEv2
%doc README-nimbus.md CHANGELOG.md
%{_bindir}/nimbus_*
%{_datadir}/%{name}/run-*
%{_datadir}/%{name}/scripts/*
%{_sysconfdir}/%{name}/*
%{_sysconfdir}/sysconfig/%{name}
%{_prefix}/lib/systemd/system/*
%{_prefix}/lib/firewalld/services/*
%config(noreplace) %{_sysconfdir}/%{name}/* %{_sysconfdir}/sysconfig/%{name}

# Utils:
#  build/logtrace
#  build/deposit_contract
#  build/ncli
#  build/ncli_db
#  build/ncli_split_keystore
%files utils
%license LICENSE-MIT LICENSE-APACHEv2
%doc README-ncli.md CHANGELOG.md
%{_bindir}/deposit_contract
%{_bindir}/logtrace
%{_bindir}/ncli_*


# Simulator:
#  build/wss_sim
%files sim
%license LICENSE-MIT LICENSE-APACHEv2
%doc CHANGELOG.md
%{_bindir}/wss_sim


%pre
if ! getent group %{name} &> /dev/null; then
    groupadd -r %{name}
fi
if ! getent passwd %{name} &> /dev/null; then
    useradd -r -g %{name} -m -d %{_sharedstatedir}/%{name} -k /dev/null %{name}
fi


%changelog
* Tue Aug 23 2022 Kai Wetlesen <kaiw@semiotic.ai> - 22.8.0-0%{?dist}
- Bumped to to Nimbus Eth2 v22.8.0
- Enabled release mode for future Nimbus builds
* Thu Aug 18 2022 Kai Wetlesen <kaiw@semiotic.ai> - 22.7.0-0%{?dist}
- Initial specification file

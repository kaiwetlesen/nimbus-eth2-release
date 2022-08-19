# Globals description:
# Target SO Version (target_sover): Indicates the current library version.
# Target Version (target_sover): Indicates the current shared-object ABI version, should correspond to major version of the library.
# Target Version (target_ver): Indicates the current package version.
%define pkgver %{?target_pkgver} %{!?target_pkgver:22.7.0}
%define sover  %{?target_sover}  %{!?target_sover:0}
%define supver %{?target_supver} %{!?target_supver:0.1.2}
Name:       nimbus-eth2
Vendor:     Status Research & Development GmbH.
Version:    %{pkgver}
Release:    0%{?dist}
Summary:    An Ethereum client implementation that strives to be as lightweight as possible

License:    MIT and Apache2
URL:        https://nimbus.team
Source0:    https://github.com/status-im/%{name}/archive/refs/tags/v%{version}.tar.gz
Source1:    https://github.com/kaiwetlesen/%{name}-release/archive/refs/tags/v%{spec_suppl_ver}.tar.gz

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
The %{name}-utils package contains utilities for maintaining %{name} data files.


%prep
%autosetup -b 1 -n %{name}-release-%{supver}
%autosetup -b 0 -n %{name}-%{version}
# Apply git attributes to release code:
git clone --bare -b v%{version} https://github.com/status-im/%{name}.git .git
git init
git checkout -f -b %{spec_branch} tags/v%{version}


%build
%make -j16


%install
%cmake_install --config Release
%__mkdir -p %{buildroot}%{_datadir}/licenses/%{name}/ %{buildroot}%{_datadir}/doc/%{name}/
%__cp LICENSE %{buildroot}%{_datadir}/licenses/%{name}/
%__cp README.md %{buildroot}%{_datadir}/doc/%{name}/
%__cp ChangeLog.md %{buildroot}%{_datadir}/doc/%{name}/
%__gzip %{buildroot}%{_mandir}/man1/mdbx_*


%{?ldconfig_scriptlets}


%files
%license LICENSE
%doc README.md ChangeLog.md
%{_libdir}/%{name}.so.%{target_sover}
%{_libdir}/%{name}.so.%{target_ver}

%files utils
%license LICENSE
%doc README.md ChangeLog.md
%{_bindir}/*
%{_mandir}/man1/*


%changelog
* Thu Aug 18 2022 Kai Wetlesen <kaiw@semiotic.ai> - 22.7.0-0%{?dist}
- Initial specification file

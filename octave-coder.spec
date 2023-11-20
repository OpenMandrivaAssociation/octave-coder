%global octpkg coder

Summary:	A code generator and build system that converts Octave to C++
Name:		octave-coder
Version:	1.8.4
Release:	1
License:	AGPLv3+
Group:		Sciences/Mathematics
#Url:		https://packages.octave.org/coder/
Url:		https://github.com/shsajjadi/OctaveCoder
Source0:	https://github.com/shsajjadi/OctaveCoder/archive/coder-%{version}.tar.gz

BuildRequires:  octave-devel >= 4.4.0

Requires:	octave(api) = %{octave_api}

Requires(post): octave
Requires(postun): octave

%description
Coder is an Octave code generator and build system that, given a 
function name translates the function and all of its dependencies to 
C++ and builds a .oct shared module.

%files
%license COPYING
%doc NEWS
%dir %{octpkgdir}
%{octpkgdir}/*
%dir %{octpkglibdir}
%{octpkglibdir}/*

#---------------------------------------------------------------------------

%prep
%autosetup -p1 -n OctaveCoder-%{octpkg}-%{version}

%build
# force CXXFLAGS
sed -i \
	-e "s|mkoctfile ( |& '-v', `echo \'$CXXFLAGS\', |sed "s| |'\, '|g"` |" \
	-e "s|'-g0' ,||"g \
	-e "s|, '-flto'||g" \
	pre_install.m

# (mandian) this package does not provide a Makefile and it try to compile
# binaries at installation time so usual macro can't be used. We need to
# manually simulate the behaivour of octave_pkg_build macro instead.
#set_build_flags
#octave_pkg_build

# remove pre-install compilation
rm -f pre_install.m

# set useful variables
octpkg_tarfile="%{_tmppath}/%{octpkg}-%{version}.tar.gz"
octpkg_tarfile_bin="%{_tmppath}/%{octpkg}-%{version}-${octave_host}-api-%{octave_api}.tar.gz"
octave_host=$(octave-config -p CANONICAL_HOST_TYPE || echo 0)

# copy all sources into build directory
tar czf ${octpkg_tarfile} -C %{_builddir} %{buildsubdir}
mkdir -p %{_builddir}/%{buildsubdir}/build
tar xzf ${octpkg_tarfile} -C %{_builddir}/%{buildsubdir}/build

# compile and link
pushd %{_builddir}/%{buildsubdir}/build/%{buildsubdir}/src 2>/dev/null
%set_build_flags
for f in `find . -name \*cpp`; do
	mkoctfile -v -c -I. -o "`basename ${f/%.cpp/.o}`" "$f"
done
mkoctfile -v -o octave2oct.oct *.o
popd 2>/dev/null

# build the archive in the way at octave_pkg_install macro expects
tar czf $octpkg_tarfile_bin -C %{_builddir}/%{buildsubdir}/build %{buildsubdir}
mv $octpkg_tarfile_bin %{_builddir}/%{buildsubdir}/build

%install
%octave_pkg_install

%check
%octave_pkg_check

%post
%octave_cmd pkg rebuild

%preun
%octave_pkg_preun

%postun
%octave_cmd pkg rebuild


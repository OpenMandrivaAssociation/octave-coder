%undefine _ld_as_needed

%global octpkg coder

Summary:	A code generator and build system that converts Octave to C++
Name:		octave-coder
Version:	1.8.0
Release:	1
License:	AGPLv3+
Group:		Sciences/Mathematics
#Url:		https://packages.octave.org/coder/
Url:		https://github.com/shsajjadi/OctaveCoder
Source0:	https://github.com/shsajjadi/OctaveCoder/archive/coder-%{version}.tar.gz
#Patch0:		octave-coder-1.8.0-add_flags.patch

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
%set_build_flags
%before_configure
#echo \'$CXXFLAGS\' |sed "s| |'\, '|"
# force CXXFLAGS
sed -i \
	-e "s|mkoctfile ( |& '-v', `echo \'$CXXFLAGS\', |sed "s| |'\, '|g"` |" \
	-e "s|-std=gnu++11'|-std=gnu++17'|"g \
	-e "s|'-g0' ,||"g \
	-e "s|, '-flto'||g" \
	pre_install.m

#octave_pkg_build
mkdir build
pushd build 2>/dev/null
# compile
for f in `find ../src -name \*cpp`; do
	mkoctfile -v -c -I../src -std=gnu++17 -o "`basename ${f/%.cpp/.o}`" "$f"
done

# link
mkoctfile -v -std=gnu++17 -o octave2oct.oct *.o

popd 2>/dev/null

%install
#octave_pkg_install

%check
%octave_pkg_check

%post
%octave_cmd pkg rebuild

%preun
%octave_pkg_preun

%postun
%octave_cmd pkg rebuild


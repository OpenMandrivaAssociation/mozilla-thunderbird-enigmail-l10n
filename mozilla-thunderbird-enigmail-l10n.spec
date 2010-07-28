%define _enable_debug_packages %{nil}
%define debug_package %{nil}

%define name	mozilla-thunderbird-enigmail-l10n
%define oname	mozilla-thunderbird-enigmail
%define version	3.0.5

%if %mandriva_branch == Cooker
# Cooker
%define release %mkrel 1
%else
# Old distros
%define subrel 1
%define release %mkrel 0
%endif

%define _buildroot %{_tmppath}/%{name}-buildroot
%define thunderbird_version %{version}
%define enigmail_version 0.96.0
%define mozillalibdir %{_libdir}/thunderbird-%{version}
%define xpidir http://www.mozilla-enigmail.org/download/release/%{enigmail_version}

# Supported l10n language lists
%define l10n_langlist	ar ca cs de el es fi fr hu it ja ko nb nl pl pt pt_BR ru sl sv tr zh_CN zh_TW

# Disabled l10n languages, for any reason
# nl sk es_AR do not support 0.95.0 yet
#define disabled_l10n_langlist	nl sk es_AR ro
%define disabled_l10n_langlist %{nil}

# Language descriptions
%define language_ar ar
%define langname_ar Arabic
%define language_ca ca-AD
%define langname_ca Catalan
%define language_cs cs-CZ
%define langname_cs Czech
%define language_de de
%define langname_de German
%define language_el el
%define langname_el Greek
%define language_es_AR es-AR
%define langname_es_AR Spanish (Argentina)
%define language_es es-ES
%define langname_es Spanish
%define language_fi fi-FI
%define langname_fi Finnish
%define language_fr fr-FR
%define langname_fr French
%define language_hu hu-HU
%define langname_hu Hungarian
%define language_it it-IT
%define langname_it Italian
%define language_ja ja-JP
%define langname_ja Japanese
%define language_ko ko-KR
%define langname_ko Korean
%define language_nb nb-NO
%define langname_nb Norwegian Bokmaal
%define langname_nl Dutch
%define language_nl nl-NL
%define language_pl pl-PL
%define langname_pl Polish
%define langname_pt Portuguese
%define language_pt pt-PT
%define language_pt_BR pt-BR
%define langname_pt_BR Brazilian portuguese
%define language_ro ro-RO
%define langname_ro Romanian
%define language_ru ru-RU
%define langname_ru Russian
%define language_sk sk-SK
%define langname_sk Slovak
%define language_sl sl-SI
%define langname_sl Slovenian
%define language_sv sv-SE
%define langname_sv Swedish
%define language_tr tr-TR
%define langname_tr Turkish
%define langname_zh_CN Simplified Chinese
%define language_zh_CN zh-CN
%define language_zh_TW zh-TW
%define langname_zh_TW Traditional Chinese

# --- Danger line ---

# All langs
%{expand:%%define langlist %(for lang in %l10n_langlist; do echo "$lang"; done | sort -u | sed ':a;$!N;s/\n/ /;ta')}

# Defaults (all languages enabled by default)
# l10n
%{expand:%(for lang in %l10n_langlist; do echo "%%define l10n_$lang 1"; done)}
%{expand:%(for lang in %disabled_l10n_langlist; do echo "%%define l10n_$lang 0"; done)}

# Params
%{expand:%(for lang in %langlist; do echo "%%bcond_without $lang"; done)}

# Locales
%{expand:%(for lang in %l10n_langlist; do echo "%%define locale_$lang `echo $lang | cut -d _ -f 1` "; done)}

Summary:	Localizations for Enigmail (virtual package)
Name:		%{name}
Version:	%{version}
Release:	%{release}
License:	GPL
Group:		Networking/Mail
Url:		http://enigmail.mozdev.org/
# Language package template
Source0: %{name}-template.spec
# l10n sources
%{expand:%(\
	i=2;\
	for lang in %langlist; do\
		echo "%%{expand:Source$i: %{xpidir}/enigmail-%%{language_$lang}-%{enigmail_version}.xpi}";\
		i=$[i+1];\
	done\
	)
}
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires: libxml2-utils

%description
Localizations for Enigmail

# Expand all languages packages.
%{expand:%(\
	for lang in %langlist; do\
		echo "%%{expand:%%(sed "s!__LANG__!$lang!g" %{_sourcedir}/%{name}-template.spec 2> /dev/null)}";\
	done\
	)
}

%prep
%setup -q -c -T

# Convert rpm macros to bash variables
%{expand:%(for lang in %langlist; do echo "language_$lang=%%{language_$lang}"; done)}
%{expand:%(for lang in %langlist; do echo "with_$lang=%%{with $lang}"; done)}
%{expand:%(for lang in %l10n_langlist; do echo "l10n_$lang=%%{l10n_$lang}"; done)}

# Unpack all languages
for lang in %l10n_langlist; do
	with="with_$lang"
	with=${!with}
	[ $with -eq 0 ] && continue

	l10n="l10n_$lang"
	l10n=${!l10n}
	[ $l10n -eq 0 ] && continue

	language="language_$lang"
	language=${!language}
	mkdir ${language}
	cd ${language}
	unzip %{_sourcedir}/enigmail-${language}-%{enigmail_version}.xpi
	cd ..
done

# Remove some blundled trash
find -type f -name '*.spec' -exec rm -f {} \;
find -type f -name install.js -exec rm -f {} \;

# Disable version check
#sed -i -e 's/maxVersion>.*</maxVersion>2.0.*</g' */install.rdf

# Patches
#cd ${language_pt}
#patch4 -p0
#cd ..

%build
# All install.rdf files must validate
xmllint --noout */install.rdf

%install
rm -rf %buildroot

# Convert rpm macros to bash variables
%{expand:%(for lang in %langlist; do echo "language_$lang=%%{language_$lang}"; done)}
%{expand:%(for lang in %langlist; do echo "with_$lang=%%{with $lang}"; done)}
%{expand:%(for lang in %l10n_langlist; do echo "l10n_$lang=%%{l10n_$lang}"; done)}

# Install all languages
for lang in %langlist; do
	with="with_$lang"
	with=${!with}
	[ $with -eq 0 ] && continue

	l10n="l10n_$lang"
	l10n=${!l10n}
	[ $l10n -eq 0 ] && continue

	language="language_$lang"
	language=${!language}
	cd $language
	LANGPACK="enigmail-$language@enigmail.mozdev.org"
	mkdir -p %buildroot%{mozillalibdir}/extensions/$LANGPACK
	cp -f -r * %buildroot%{mozillalibdir}/extensions/$LANGPACK
	echo "%{mozillalibdir}/extensions/$LANGPACK" > %{_builddir}/%{name}-%{version}/$lang.list
	cd ..
done

%clean
rm -rf %buildroot

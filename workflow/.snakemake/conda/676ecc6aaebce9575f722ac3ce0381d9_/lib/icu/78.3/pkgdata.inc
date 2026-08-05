GENCCODE_ASSEMBLY_TYPE=-a gcc
SO=so
SOBJ=so
A=a
LIBPREFIX=lib
LIB_EXT_ORDER=.78.3
COMPILE=/home/conda/feedstock_root/build_artifacts/bld/rattler-build_icu_1784916378/build_env/bin/x86_64-conda-linux-gnu-cc -DNDEBUG -D_FORTIFY_SOURCE=2 -O2 -isystem /home/miles/moi_lab_projects/aegis/workflow/.snakemake/conda/676ecc6aaebce9575f722ac3ce0381d9_/include -D_REENTRANT  -DU_HAVE_ELF_H=1  -DU_ALL_IMPLEMENTATION -DU_ATTRIBUTE_DEPRECATED= -march=nocona -mtune=haswell -ftree-vectorize -fPIC -fstack-protector-strong -fno-plt -O2 -ffunction-sections -pipe -fno-merge-constants -isystem /home/miles/moi_lab_projects/aegis/workflow/.snakemake/conda/676ecc6aaebce9575f722ac3ce0381d9_/include -fdebug-prefix-map=/home/conda/feedstock_root/build_artifacts/bld/rattler-build_icu_1784916378/work=/usr/local/src/conda/icu-78.3 -fdebug-prefix-map=/home/miles/moi_lab_projects/aegis/workflow/.snakemake/conda/676ecc6aaebce9575f722ac3ce0381d9_=/usr/local/src/conda-prefix -std=c11 -Wall -pedantic -Wshadow -Wpointer-arith -Wmissing-prototypes -Wwrite-strings   -c
LIBFLAGS=-I/home/miles/moi_lab_projects/aegis/workflow/.snakemake/conda/676ecc6aaebce9575f722ac3ce0381d9_/include -DPIC -fPIC
GENLIB=/home/conda/feedstock_root/build_artifacts/bld/rattler-build_icu_1784916378/build_env/bin/x86_64-conda-linux-gnu-cc -march=nocona -mtune=haswell -ftree-vectorize -fPIC -fstack-protector-strong -fno-plt -O2 -ffunction-sections -pipe -fno-merge-constants -isystem /home/miles/moi_lab_projects/aegis/workflow/.snakemake/conda/676ecc6aaebce9575f722ac3ce0381d9_/include -fdebug-prefix-map=/home/conda/feedstock_root/build_artifacts/bld/rattler-build_icu_1784916378/work=/usr/local/src/conda/icu-78.3 -fdebug-prefix-map=/home/miles/moi_lab_projects/aegis/workflow/.snakemake/conda/676ecc6aaebce9575f722ac3ce0381d9_=/usr/local/src/conda-prefix -std=c11 -Wall -pedantic -Wshadow -Wpointer-arith -Wmissing-prototypes -Wwrite-strings   -Wl,-O2 -Wl,--sort-common -Wl,--as-needed -Wl,-z,relro -Wl,-z,now -Wl,--disable-new-dtags -Wl,--gc-sections -Wl,--allow-shlib-undefined -Wl,-rpath,/home/miles/moi_lab_projects/aegis/workflow/.snakemake/conda/676ecc6aaebce9575f722ac3ce0381d9_/lib -Wl,-rpath-link,/home/miles/moi_lab_projects/aegis/workflow/.snakemake/conda/676ecc6aaebce9575f722ac3ce0381d9_/lib -L/home/miles/moi_lab_projects/aegis/workflow/.snakemake/conda/676ecc6aaebce9575f722ac3ce0381d9_/lib  -shared -Wl,-Bsymbolic
LDICUDTFLAGS=-nodefaultlibs -nostdlib
LD_SONAME=-Wl,-soname -Wl,
RPATH_FLAGS=
BIR_LDFLAGS=-Wl,-Bsymbolic
AR=x86_64-conda-linux-gnu-ar
ARFLAGS=r
RANLIB=x86_64-conda-linux-gnu-ranlib
INSTALL_CMD=/usr/bin/install -c

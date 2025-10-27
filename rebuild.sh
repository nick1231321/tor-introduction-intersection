# remove most build artifacts
make clean

# (optional) remove generated configure if you want fully fresh:
# git checkout -- configure aclocal.m4 || rm -f configure aclocal.m4
# rm -rf autom4te.cache

# regenerate (if needed) and configure
./autogen.sh -f   # only if configure is missing/outdated
./configure --enable-debug --disable-asciidoc

# rebuild
make -j"$(nproc)"


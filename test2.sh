# regenerate autotools scripts using the project's helper if present:
if [ -x ./autogen.sh ]; then
  ./autogen.sh -f
else
  autoreconf -vfi
fi


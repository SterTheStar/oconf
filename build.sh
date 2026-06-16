#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
OUT="$ROOT/dist-packages"
TMP="/tmp/oconf-pack"

read -r -p "Version: " VERSION
if [[ -z "${VERSION}" ]]; then
  echo "Version is required" >&2
  exit 1
fi

rm -rf "$OUT" "$TMP" "$ROOT/dist" "$ROOT/build" "$ROOT/OConf.spec"
mkdir -p "$OUT" "$TMP/deb/DEBIAN" "$TMP/deb/usr/bin" "$TMP/deb/usr/lib/oconf" "$TMP/deb/usr/share/applications" "$TMP/deb/usr/share/pixmaps"
mkdir -p "$TMP/rpm/BUILD" "$TMP/rpm/RPMS" "$TMP/rpm/SOURCES" "$TMP/rpm/SPECS" "$TMP/rpm/SRPMS"

sed "s/__VERSION__/${VERSION}/g" "$ROOT/packaging/oconf.spec" > "$TMP/rpm/SPECS/oconf.spec"
export OCONF_VERSION="$VERSION"

"$ROOT/.venv/bin/pip" install -q pyinstaller
"$ROOT/.venv/bin/pyinstaller" --noconfirm --clean --paths "$ROOT" --name OConf --windowed --icon "$ROOT/icons/icon.png" --add-data "$ROOT/icons/icon.png:icons" "$ROOT/main.py"

cp "$ROOT/packaging/deb/control" "$TMP/deb/DEBIAN/control"
sed -i "s/^Version: .*/Version: ${VERSION}/" "$TMP/deb/DEBIAN/control"
cp -a "$ROOT/dist/OConf/." "$TMP/deb/usr/lib/oconf/"
cat > "$TMP/deb/usr/bin/oconf" <<'EOF'
#!/bin/sh
exec /usr/lib/oconf/OConf "$@"
EOF
chmod 0755 "$TMP/deb/usr/bin/oconf"
install -Dm0644 "$ROOT/packaging/oconf.desktop" "$TMP/deb/usr/share/applications/oconf.desktop"
install -Dm0644 "$ROOT/icons/icon.png" "$TMP/deb/usr/share/pixmaps/oconf.png"

dpkg-deb --root-owner-group --build "$TMP/deb" "$OUT/oconf_${VERSION}_amd64.deb"

tar -C "$ROOT/dist/OConf" -czf "$TMP/rpm/SOURCES/oconf-${VERSION}.tar.gz" .
cp "$ROOT/packaging/oconf.desktop" "$TMP/rpm/SOURCES/oconf.desktop"
cp "$ROOT/icons/icon.png" "$TMP/rpm/SOURCES/oconf.png"

rpmbuild --define "_topdir $TMP/rpm" --define "_sourcedir $TMP/rpm/SOURCES" -bb "$TMP/rpm/SPECS/oconf.spec"
cp "$TMP/rpm/RPMS"/*/*.rpm "$OUT/oconf-${VERSION}-1.x86_64.rpm"

tar -C "$ROOT/dist" -czf "$OUT/oconf-linux-x86_64-${VERSION}.tar.gz" OConf

echo "Artifacts written to $OUT"

pkgname=chocolate
pkgver=3.0.3
pkgrel=1
pkgdesc="Chocolate Project Manager for managing projects with virtual environments"
arch=('x86_64')
url="https://github.com/frchocolate/chocolate"
license=('MIT')
depends=('git' 'python')  # Adjust dependencies as needed
source=("git+https://github.com/frchocolate/chocolate.git")
md5sums=('SKIP')

pkgver() {
    cd "$srcdir/chocolate"
    if git describe --tags 2>/dev/null; then
        git describe --tags | sed 's/^v//'
    else
        echo "1.0.0"  # Default version if no tags are found
    fi
}

prepare() {
    return 0  # No preparation needed
}

build() {
    cd "$srcdir/chocolate"
    make all  # This runs the make command to build the project
}

package() {
    cd "$srcdir/chocolate"
    make all  # This runs make all again to handle installation
}

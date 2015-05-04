class Fpp < Formula
  homepage "https://facebook.github.io/PathPicker/"
  url "https://facebook.github.io/PathPicker/dist/fpp.0.5.2.tar.gz"
  sha256 "5f7f786a2a8b0fc0dce523b6ba72b95a9313699d1ce7f9fce0cbbaa22589fb3d"
  head "https://github.com/facebook/pathpicker.git"

  depends_on :python if MacOS.version <= :snow_leopard

  def install
    puts buildpath
    # we need to copy the bash file and source python files
    libexec.install Dir["*"]
    # and then symlink the bash file
    bin.install_symlink libexec/"fpp"
  end

  test do
    system bin/"fpp", "--help"
  end
end

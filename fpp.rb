class Fpp < Formula
  homepage "https://facebook.github.io/PathPicker/"
  url "https://facebook.github.io/PathPicker/dist/fpp.0.5.1.tar.gz"
  sha256 "a6cb81a10cb14f3dee7a785034073a586a1feca1f28c2a6461ab95d6dbb8dbef"
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

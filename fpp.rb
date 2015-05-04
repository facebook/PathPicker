class Fpp < Formula
  homepage "https://facebook.github.io/PathPicker/"
  url "https://facebook.github.io/PathPicker/dist/fpp.0.5.1.tar.gz"
  sha256 "550073b5cc3f4472ca0f175c3c6475077ccd5255d3230e4003e71bf031e82ac7"
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

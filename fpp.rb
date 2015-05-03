class Fpp < Formula
  homepage "https://facebook.github.io/PathPicker/"
  # TODO -- change away from gh-pages link
  url "https://facebook.github.io/PathPicker/dist/fpp.0.5.0.tar.gz"
  sha256 "25f3edddc28b7a353c407d48a74a92f9a364160de790122357a3785d9d9e8aeb"
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
    system "fpp --help"
  end

end

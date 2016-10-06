from conans import ConanFile, ConfigureEnvironment
from conans.tools import download, untargz, check_sha1, replace_in_file
import os
import shutil

class LibevConan(ConanFile):
    name = "libev"
    version = "4.22"
    url = "https://github.com/TigerZhang/conan-libev"
    license = "http://cvs.schmorp.de/libev/LICENSE?revision=1.11&view=markup&pathrev=rel-4_22"
    FOLDER_NAME = 'libev-%s' % version
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "with_openssl": [True, False],
               "disable_threads": [True, False]}
    default_options = "shared=False", "with_openssl=True", "disable_threads=False"

    def source(self):
        tarball_name = self.FOLDER_NAME + '.tar.gz'
        download("http://dist.schmorp.de/libev/libev-%s.tar.gz" % (self.version),
                 tarball_name)
        check_sha1(tarball_name, "4affcba78dc17239f2ccd84d6e3e6dec2bd1f8ba")
        untargz(tarball_name)
        os.unlink(tarball_name)

    def build(self):
        env = ConfigureEnvironment(self.deps_cpp_info, self.settings)
        if self.settings.os == "Linux" or self.settings.os == "Macos":

            env_line = env.command_line
            env_line_configure = env_line

            # compose configure options
            suffix = ''
            if not self.options.shared:
                suffix += " --disable-shared "
            if self.options.with_openssl:
                suffix += "--enable-openssl "
            else:
                suffix += "--disable-openssl "
            if self.options.disable_threads:
                suffix += "--disable-thread-support "

            cmd = 'cd %s && %s %s ./configure %s' % (self.FOLDER_NAME, env_line, env_line_configure, suffix)
            self.output.warn('Running: ' + cmd)
            self.run(cmd)

            cmd = 'cd %s && %s make' % (self.FOLDER_NAME, env_line)
            self.output.warn('Running: ' + cmd)
            self.run(cmd)
        
    def package(self):
        self.copy("ev.h", dst="include", src="%s" % (self.FOLDER_NAME))
        self.copy("ev++.h", dst="include", src="%s" % (self.FOLDER_NAME))
        if self.options.shared:
            if self.settings.os == "Macos":
                self.copy(pattern="*.dylib", dst="lib", keep_path=False)
            else:
                self.copy(pattern="*.so*", dst="lib", keep_path=False)
        else:
            self.copy(pattern="*.a", dst="lib", keep_path=False)

    def package_info(self):
       if self.settings.os == "Linux" or self.settings.os == "Macos":
            self.cpp_info.libs = ['ev']

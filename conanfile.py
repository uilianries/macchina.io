"""Conan recipe for Macchina.io project.

This recipe exports all necessary sources, build the project and create a
package with all artifacts.

"""

import os
from conans import ConanFile, AutoToolsBuildEnvironment, tools


class MacchinaioConan(ConanFile):
    name = "macchina.io"
    version = "0.7.0"
    generators = "cmake"
    license = "https://github.com/macchina-io/macchina.io/blob/master/LICENSE"
    url = "https://github.com/macchina-io/macchina.io"
    author = "Gunter Obiltschnig <guenter.obiltschnig@appinf.com>"
    description = "macchina.io is a toolkit for building IoT edge and fog device applications in JavaScript and C++"
    settings = "os", "compiler", "build_type", "arch"
    options = {"with_V8_snapshot": [True, False]}
    default_options = "with_V8_snapshot=True"
    exports = "LICENSE"
    exports_sources = "devices/*", "launcher/*", "platform/*", "protocols/*", "samples/*", "server/*", "services/*", "tools/*", "webui/*", "Makefile"
    requires = "OpenSSL/1.0.2@conan/stable"

    def build(self):
        build_args = []
        build_args.append("-s")
        build_args.append("DEFAULT_TARGET=shared_%s" % self.settings.build_type.value.lower())
        build_args.append("V8_SNAPSHOT=1" if self.options.with_V8_snapshot else "V8_NOSNAPSHOT=1")
        install_args = ["install"]
        install_args.extend(build_args)
        install_args.append("INSTALLDIR=%s" % self.package_folder)
        env_build = AutoToolsBuildEnvironment(self)
        with tools.environment_append(env_build.vars):
            env_build.make(args=build_args)
            env_build.make(args=install_args)
        os.rename(os.path.join(self.package_folder, "etc"), os.path.join(self.package_folder, "res"))

    def package(self):
        self.copy("LICENSE", dst=".", src=".")

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        if self.settings.os == "Linux":
            self.env_info.LD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))
        elif self.settings.os == "Macos":
            self.env_info.DYLD_LIBRARY_PATH.append(os.path.join(self.package_folder, "lib"))

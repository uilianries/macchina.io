"""Conan recipe for Macchina.io test package.

This test summons the macchina.io process, and check by a HTTP resquest on
port 22080.

"""

import os
import signal
import subprocess
import tempfile
import time
import sys
from conans import ConanFile, RunEnvironment, tools

if (sys.version_info > (3, 0)):
    import http.client
    httplib = http.client
else:
    import httplib

class MacchinaioTestConan(ConanFile):
    settings = "os", "compiler", "arch", "build_type"
    generators = "cmake"

    def imports(self):
        self.copy(pattern="*", dst="bin", src="bin")

    def test(self):
        config_file = os.path.join(self.deps_cpp_info["macchina.io"].res_paths[0], "macchina.properties")
        bundles_dir = os.path.join(self.deps_cpp_info["macchina.io"].lib_paths[0], "bundles")
        codecache_dir = os.path.join(os.getcwd(), "bin", "codeCache")
        _, pid_file = tempfile.mkstemp(prefix="macchinaio-pid")

        build_vars = RunEnvironment(self).vars
        build_vars["LD_LIBRARY_PATH"].append(codecache_dir)
        with tools.environment_append(build_vars):
            self.run("%s/bin/macchina --daemon -B%s -c%s --pidfile=%s" % (os.getcwd(), bundles_dir, config_file, pid_file))
            time.sleep(10)
            try:
                conn = httplib.HTTPConnection("localhost:22080")
                conn.request("GET","/macchina/login")
                res = conn.getresponse()
                assert(res.status == 200)
            finally:
                with open(pid_file) as f:
                    pid = int(f.read())
                    os.kill(pid, signal.SIGKILL)

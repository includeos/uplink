from conans import ConanFile, python_requires, CMake

conan_tools = python_requires("conan-tools/[>=1.0.0]@includeos/stable")

class UplinkConan(ConanFile):
    settings= "os","arch","build_type","compiler"
    name = "uplink"
    license = 'Apache-2.0'
    version = conan_tools.git_get_semver()
    description = 'Run your application with zero overhead'
    generators = 'cmake'
    url = "http://www.includeos.org/"
    scm = {
        "type" : "git",
        "url" : "auto",
        "subfolder": ".",
        "revision" : "auto"
    }
    default_user="includeos"
    default_channel="test"

    options={
        "liveupdate":[True,False],
        "tls": [True,False],
        "uplink_log": [True,False]
    }
    default_options={
        "liveupdate":True,
        "tls":True,
        "uplink_log":True
    }

    no_copy_source=True
    def package_id(self):
        self.info.requires.major_mode()

    def requirements(self):
        self.requires("includeos/[>=0.14.0,include_prerelease=True]@includeos/latest")
        if (self.options.liveupdate):
            self.requires("liveupdate/[>=0.14.0,include_prerelease=True]@includeos/latest")

    def _cmake_configure(self):
        cmake = CMake(self)
        cmake.definitions['UPLINK_LOG']=self.options.uplink_log
        cmake.definitions['LIVEUPDATE']=self.options.liveupdate
        cmake.definitions['TLS']=self.options.tls
        cmake.configure(source_folder=self.source_folder)
        return cmake

    def build(self):
        cmake = self._cmake_configure()
        cmake.build()

    def package(self):
        cmake = self._cmake_configure()
        cmake.install()

    def package_info(self):
        self.cpp_info.libdirs = [
            'plugins'
        ]
        self.cpp_info.libs=['uplink']
        if self.options.uplink_log:
            self.cpp_info.libdirs.append('drivers')
            self.cpp_info.libs.append('uplink_log')

    def deploy(self):
        self.copy("*.a",dst="drivers",src="drivers")
        self.copy("*.a",dst="plugins",src="plugins")
        self.copy("*",dst="include",src="include")

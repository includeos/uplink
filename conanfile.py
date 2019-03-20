from conans import ConanFile,tools,CMake

def get_version():
    git = tools.Git()
    try:
        prev_tag = git.run("describe --tags --abbrev=0")
        commits_behind = int(git.run("rev-list --count %s..HEAD" % (prev_tag)))
        # Commented out checksum due to a potential bug when downloading from bintray
        #checksum = git.run("rev-parse --short HEAD")
        if prev_tag.startswith("v"):
            prev_tag = prev_tag[1:]
        if commits_behind > 0:
            prev_tag_split = prev_tag.split(".")
            prev_tag_split[-1] = str(int(prev_tag_split[-1]) + 1)
            output = "%s-%d" % (".".join(prev_tag_split), commits_behind)
        else:
            output = "%s" % (prev_tag)
        return output
    except:
        return '0.0.0'


class UplinkConan(ConanFile):
    settings= "os","arch","build_type","compiler"
    name = "uplink"
    license = 'Apache-2.0'
    version=get_version()
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

    def requirements(self):
        self.requires("includeos/[>=0.14.0,include_prerelease=True]@{}/{}".format(self.user,self.channel))
        if (self.options.liveupdate):
            self.requires("liveupdate/[>=0.14.0,include_prerelease=True]@{}/{}".format(self.user,self.channel))
        if (self.options.tls):
            #this will put a dependency requirement on openssl
            self.requires("s2n/1.1.1@{}/{}".format(self.user,self.channel))

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

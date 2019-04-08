pipeline {
  agent { label 'ubuntu-18.04' }
  triggers { upstream( upstreamProjects: 'IncludeOS/IncludeOS/master, IncludeOS/IncludeOS/dev', threshold: hudson.model.Result.SUCCESS ) }
  options { checkoutToSubdirectory('src') }
  environment {
    CONAN_USER_HOME = "${env.WORKSPACE}"
    PROFILE_x86_64 = 'clang-6.0-linux-x86_64'
    PROFILE_x86 = 'clang-6.0-linux-x86'
    CPUS = """${sh(returnStdout: true, script: 'nproc')}"""
    CC = 'clang-6.0'
    CXX = 'clang++-6.0'
    PACKAGE = 'uplink'
    USER = 'includeos'
    CHAN_LATEST = 'latest'
    CHAN_STABLE = 'stable'
    REMOTE = "${env.CONAN_REMOTE}"
    BINTRAY_CREDS = credentials('devops-includeos-user-pass-bintray')
    SRC = "${env.WORKSPACE}/src"
  }

  stages {
    stage('Setup') {
      steps {
        sh script: "ls -A | grep -v src | xargs rm -r || :", label: "Clean workspace"
        sh script: "conan config install https://github.com/includeos/conan_config.git", label: "conan config install"
      }
    }
    stage('Unit tests') {
      when { changeRequest() }
      steps {
        dir('unittests') {
          sh script: "cmake $SRC/unit", label: "cmake configure"
          sh script: "make -j $CPUS", label: "build tests"
          sh script: "ctest --output-on-failure", label: "run unit tests"
        }
      }
    }
    stage('Build package') {
      steps {
        build_all_variations("$PROFILE_x86_64")
        script { VERSION = sh(script: "conan inspect -a version $SRC | cut -d ' ' -f 2", returnStdout: true).trim() }
      }
    }
    stage('Build starbase') {
      when { changeRequest() }
      steps {
        dir('starbase_build') {
          sh script: "conan install $SRC/starbase -pr $PROFILE_x86_64", label: "conan_install"
          sh script: ". ./activate.sh; cmake $SRC/starbase",label: "cmake configure"
          sh script: "make -j $CPUS", label: "building example"
        }
      }
    }
    stage('Upload to bintray') {
      parallel {
        stage('Latest release') {
          when { branch 'master' }
          steps {
            upload_package("$CHAN_LATEST")
          }
        }
        stage('Stable release') {
          when { buildingTag() }
          steps {
            sh script: "conan copy --all $PACKAGE/$VERSION@$USER/$CHAN_LATEST $USER/$CHAN_STABLE", label: "Copy to stable channel"
            upload_package("$CHAN_STABLE")
          }
        }
      }
    }
  }
}

def build_all_variations(String profile) {
  tls=['True','False']
  liveupdate=['True','False']
  uplink_log=['True','False']
  for (int x = 0; x < uplink_log.size(); x++) {
    for (int y = 0; y < liveupdate.size(); y++) {
      for (int z = 0; z < tls.size();z++) {
        sh script: "conan create $SRC $USER/$CHAN_LATEST -pr ${profile} -o uplink_log=${uplink_log[x]} -o liveupdate=${liveupdate[y]} -o tls=${tls[z]}", label: "Build with profile: $profile log=${uplink_log[x]} liveupdate=${liveupdate[y]} tls=${tls[z]}"
      }
    }
  }
}

def upload_package(String channel) {
  sh script: """
    conan user -p $BINTRAY_CREDS_PSW -r $REMOTE $BINTRAY_CREDS_USR
    conan upload --all -r $REMOTE $PACKAGE/$VERSION@$USER/$channel
  """, label: "Upload to bintray"
}

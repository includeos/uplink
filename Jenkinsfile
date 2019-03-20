pipeline {
  agent { label 'ubuntu-18.04' }

  triggers {
    upstream(
      upstreamProjects: 'hioa-cs-org-test/IncludeOS/dev', threshold: hudson.model.Result.SUCCESS
      )
  }

  environment {
    CONAN_USER_HOME = "${env.WORKSPACE}"
    PROFILE_x86_64 = 'clang-6.0-linux-x86_64'
    PROFILE_x86 = 'clang-6.0-linux-x86'
    CPUS = """${sh(returnStdout: true, script: 'nproc')}"""
    CC = 'clang-6.0'
    CXX = 'clang++-6.0'
    PACKAGE = 'uplink'
    USER = 'includeos'
    CHAN = 'test'
    REMOTE = "${env.CONAN_REMOTE}"
    BINTRAY_CREDS = credentials('devops-includeos-user-pass-bintray')
  }

  stages {
    stage('Setup') {
      steps {
        sh script: "conan config install https://github.com/includeos/conan_config.git", label: "conan config install"
      }
    }
    stage('Unit tests') {
      steps {
        //cmake cache is bad
        sh script: "mkdir -p unittests && rm -rf unittests/*", label: "Setup"
        sh script: "cd unittests; cmake ../unit", label: "cmake configure"
        sh script: "cd unittests; make -j $CPUS", label: "build tests"
        sh script: "cd unittests; ctest --output-on-failure", label: "run unit tests"
      }
    }

    stage('Build package') {
      steps {
      //TODO figure out if there is a better way to do this
      //TODO consider also building debug ?
        build_all_variations("$PROFILE_x86_64")
      }
    }
    /* TODO build and link starbase or some other example?
    stage('build example') {
      steps {
        sh script: "mkdir -p build_example", label: "Setup"
        sh script: "cd build_example; conan install ../starbase -pr $PROFILE_x86_64 -u", label: "conan_install"
        sh script: "cd build_example; cmake ../starbase",label: "cmake configure"
        sh script: "cd build_example; make -j $CPUS", label: "building example"
        //sh script: "cd build_example; source activate.sh; cmake ../unit/integration/simple", label: "cmake configure"
        //sh script: "cd build_example; source activate.sh; make", label: "build"
      }
    }
    */
    stage('Upload to bintray') {
      when {
        anyOf {
          branch 'master'
        }
      }
      steps {
        sh script: """
          conan user -p $BINTRAY_CREDS_PSW -r $REMOTE $BINTRAY_CREDS_USR
          VERSION=\$(conan inspect -a version . | cut -d " " -f 2)
          conan upload --all -r $REMOTE $PACKAGE/\$VERSION@$USER/$CHAN
        """, label: "Upload to bintray"
      }
    }
  }
  post {
    cleanup {
      sh script: """
        VERSION=\$(conan inspect -a version . | cut -d " " -f 2)
        conan remove $PACKAGE/\$VERSION@$USER/$CHAN -f || echo 'Could not remove. This does not fail the pipeline'
      """, label: "Cleaning up and removing conan package"
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
        sh script: "conan create . $USER/$CHAN -pr ${profile} -o uplink_log=${uplink_log[x]} -o liveupdate=${liveupdate[y]} -o tls=${tls[z]}", label: "Build with profile: $profile log=${uplink_log[x]} liveupdate=${liveupdate[y]} tls=${tls[z]}"
      }
    }
  }
}

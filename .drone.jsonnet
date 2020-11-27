local PythonVersion(pyversion='2.7') = {
  name: 'python' + std.strReplace(pyversion, '.', ''),
  image: 'python:' + pyversion,
  environment: {
    PY_COLORS: 1,
  },
  commands: [
    'pip install -r dev-requirements.txt -qq',
    'pip install -qq .',
    'pytest tests --cov=certbot_dns_corenetworks --no-cov-on-fail',
  ],
  depends_on: [
    'clone',
  ],
};

local PipelineLint = {
  kind: 'pipeline',
  image_pull_secrets: ['docker_config'],
  name: 'lint',
  platform: {
    os: 'linux',
    arch: 'amd64',
  },
  steps: [
    {
      name: 'flake8',
      image: 'python:3.8',
      environment: {
        PY_COLORS: 1,
      },
      commands: [
        'pip install -r dev-requirements.txt -qq',
        'pip install -qq .',
        'flake8 ./certbot_dns_corenetworks',
      ],
    },
  ],
  trigger: {
    ref: ['refs/heads/master', 'refs/tags/**', 'refs/pull/**'],
  },
};

local PipelineTest = {
  kind: 'pipeline',
  image_pull_secrets: ['docker_config'],
  name: 'test',
  platform: {
    os: 'linux',
    arch: 'amd64',
  },
  steps: [
    PythonVersion(pyversion='2.7'),
    PythonVersion(pyversion='3.5'),
    PythonVersion(pyversion='3.6'),
    PythonVersion(pyversion='3.7'),
    PythonVersion(pyversion='3.8'),
    {
      name: 'codecov',
      image: 'python:3.8',
      environment: {
        PY_COLORS: 1,
        CODECOV_TOKEN: { from_secret: 'codecov_token' },
      },
      commands: [
        'pip install codecov -qq',
        'codecov --required -X gcov',
      ],
      depends_on: [
        'python27',
        'python35',
        'python36',
        'python37',
        'python38',
      ],
    },
  ],
  depends_on: [
    'lint',
  ],
  trigger: {
    ref: ['refs/heads/master', 'refs/tags/**', 'refs/pull/**'],
  },
};

local PipelineSecurity = {
  kind: 'pipeline',
  image_pull_secrets: ['docker_config'],
  name: 'security',
  platform: {
    os: 'linux',
    arch: 'amd64',
  },
  steps: [
    {
      name: 'bandit',
      image: 'python:3.8',
      environment: {
        PY_COLORS: 1,
      },
      commands: [
        'pip install -r dev-requirements.txt -qq',
        'pip install -qq .',
        'bandit -r ./certbot_dns_corenetworks -x ./certbot_dns_corenetworks/test',
      ],
    },
  ],
  depends_on: [
    'test',
  ],
  trigger: {
    ref: ['refs/heads/master', 'refs/tags/**', 'refs/pull/**'],
  },
};

local PipelineBuildPackage = {
  kind: 'pipeline',
  image_pull_secrets: ['docker_config'],
  name: 'build-package',
  platform: {
    os: 'linux',
    arch: 'amd64',
  },
  steps: [
    {
      name: 'build',
      image: 'python:3.8',
      environment: {
        SETUPTOOLS_SCM_PRETEND_VERSION: '${DRONE_TAG##v}',
      },
      commands: [
        'python setup.py sdist bdist_wheel',
      ],
    },
    {
      name: 'checksum',
      image: 'alpine',
      commands: [
        'cd dist/ && sha256sum * > ../sha256sum.txt',
      ],
    },
    {
      name: 'publish-github',
      image: 'plugins/github-release',
      settings: {
        overwrite: true,
        api_key: { from_secret: 'github_token' },
        files: ['dist/*', 'sha256sum.txt'],
        title: '${DRONE_TAG}',
        note: 'CHANGELOG.md',
      },
      when: {
        ref: ['refs/tags/**'],
      },
    },
    {
      name: 'publish-pypi',
      image: 'plugins/pypi',
      settings: {
        username: { from_secret: 'pypi_username' },
        password: { from_secret: 'pypi_password' },
        repository: 'https://upload.pypi.org/legacy/',
        skip_build: true,
      },
      when: {
        ref: ['refs/tags/**'],
      },
    },
  ],
  depends_on: [
    'security',
  ],
  trigger: {
    ref: ['refs/heads/master', 'refs/tags/**', 'refs/pull/**'],
  },
};

local PipelineNotifications = {
  kind: 'pipeline',
  image_pull_secrets: ['docker_config'],
  name: 'notifications',
  platform: {
    os: 'linux',
    arch: 'amd64',
  },
  steps: [
    {
      name: 'matrix',
      image: 'plugins/matrix',
      settings: {
        homeserver: { from_secret: 'matrix_homeserver' },
        roomid: { from_secret: 'matrix_roomid' },
        template: 'Status: **{{ build.status }}**<br/> Build: [{{ repo.Owner }}/{{ repo.Name }}]({{ build.link }}) ({{ build.branch }}) by {{ build.author }}<br/> Message: {{ build.message }}',
        username: { from_secret: 'matrix_username' },
        password: { from_secret: 'matrix_password' },
      },
      when: {
        status: ['success', 'failure'],
      },
    },
  ],
  depends_on: [
    'build-package',
  ],
  trigger: {
    ref: ['refs/heads/master', 'refs/tags/**'],
    status: ['success', 'failure'],
  },
};

[
  PipelineLint,
  PipelineTest,
  PipelineSecurity,
  PipelineBuildPackage,
  PipelineNotifications,
]

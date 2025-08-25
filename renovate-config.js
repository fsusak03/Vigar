module.exports = {
  platform: 'github',
  endpoint: 'https://api.github.com/',
  repositories: ['fsusak03/Vigar'],
  onboarding: true,
  onboardingConfig: {
    extends: ['config:recommended', 'group:allNonMajor'],
  },
  dependencyDashboard: true,
  baseBranches: ['dev'],
  enabledManagers: [
    'pip_requirements',
    'dockerfile',
    'docker-compose',
    'github-actions',
    // keep npm enabled for future JS tooling; harmless if no package.json
    'npm'
  ],
  // Configure Python requirements.txt detection
  pip_requirements: {
    managerFilePatterns: ['(^|/)requirements\\.txt$']
  },
  packageRules: [
    // Python: group and automerge patch/minor
    {
      matchManagers: ['pip_requirements'],
      groupName: 'python dependencies',
      matchUpdateTypes: ['patch', 'minor'],
      automerge: true,
    },
    {
      matchManagers: ['npm'],
      matchUpdateTypes: ['patch', 'minor'],
      automerge: true,
    },
    {
      matchManagers: ['dockerfile'],
      matchUpdateTypes: ['patch', 'minor'],
      automerge: true,
    },
    {
      matchManagers: ['docker-compose'],
      matchUpdateTypes: ['patch', 'minor'],
      automerge: true,
    },
    {
      matchManagers: ['github-actions'],
      matchUpdateTypes: ['patch', 'minor'],
      automerge: true,
    },
  ],
};
# Contributing to Victreebot
Hello! Thanks you for taking the time and effort to help the development of Victreebot! There a few contributing guidelines that you should follow, they are outlined in this document!

<br>

----

<br>

## Code of conduct
To ensure everyone has a safe working environment, victreebot has a code of conduct in place. Breaking this code of conduct can lead to a ban from the project and a report to GitHub!<br><br>
The code of conduct can be read here: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md#victreebot-code-of-conduct)

<br>

----

<br>

## Versioning
Victreebot uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html). All changes will be placed in the [CHANGELOG.md](CHANGELOG.md#victreebot-changelog) file. When changing, please add this to the **[Unreleased/Working on]** section of [CHANGELOG.md](CHANGELOG.md#victreebot-changelog)! When deploying, this will be updated by the person who merged the new version!

<br>

----

<br>

## Branches
To increase the ... of the repository, please use the following branch naming schemes:
- <code>feat/issue-number</code>
    - This should be used for branches that require more tasks to merge!
    - If there is no issue number availble, please use a very small description!
- <code>bugfix/issue-number</code>
    - This should be used for branches that have a bugfix!
    - If there is no issue number availble, please use a very small description!
- <code>task/issue-number</code>
    - This should be used for branches that don't all under either a bugfix or feature!
    - If there is no issue number availble, please use a very small description!

<br>

----

<br>

## Nox and pipelines
To ensure the code is in a standard format, nox is there to help maintain this. You will need to install nox locally to run any pipelines. Nox can be installed using the following command:
```
pip install nox
```

After installing you can than run nox as you wish! Please refer to the [official nox documentation](https://nox.thea.codes/en/stable/) for furher information!

In addition to Nox, there are GitHub Actions and pipelines in place. There pipelines need to succeed before a branch can be merged!

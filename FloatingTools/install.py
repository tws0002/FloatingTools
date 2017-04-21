"""
Validate the dependencies are installed.
"""
# python imports
import os
import sys
import imp
import json
import urllib
import base64
import subprocess

# FloatingTools imports
import FloatingTools

# build the packages directory if its not there.
if not os.path.exists(FloatingTools.PACKAGES):
    os.mkdir(FloatingTools.PACKAGES)

# register the FloatingTools/packages directory with sys.path.
sys.path.append(FloatingTools.PACKAGES)

# begin checking dependency list
# pip
# flask (this brings a bit with it as well)
# PyGithub

# check if pip is installed. This is installed at the Python installs site-packages. Everything else is installed in the
# FloatingTools/packages directory.
try:
    import pip
except ImportError:
    # install pip
    downloadPath = os.path.join(FloatingTools.PACKAGES, 'get-pip.py')
    urllib.urlretrieve("https://bootstrap.pypa.io/get-pip.py", downloadPath)

    # execute the python pip install call
    subprocess.call([sys.executable, downloadPath])

    # verify pip install worked
    import pip

    # delete get-pip.py
    os.unlink(downloadPath)

# Verify the github lib exists
try:
    import github
except ImportError:
    pip.main(['install', 'PyGithub', '-t', FloatingTools.PACKAGES])

    # verify install
    import github

# Verify the flask lib exists
try:
    import flask
except ImportError:
    pip.main(['install', 'Flask', '-t', FloatingTools.PACKAGES])

    # verify install
    import flask


def cloudImport(repoAddress, serverPath, userNamespace=True):
    """
    Loads a python module from a github server without downloading it.
    :param repoAddress: 
    :param serverPath: 
    :param userNamespace: 
    :return: 
    """
    repository = FloatingTools.gitHubConnect().get_repo(repoAddress)

    # repository name
    repoOwnerName, repoName = repoAddress.split('/')

    # level variable
    level = None
    if userNamespace:
        # make python package for this repository
        if repoOwnerName not in sys.modules:
            repoModule = imp.new_module(repoOwnerName)
            sys.modules[repoOwnerName] = repoModule
        else:
            repoModule = sys.modules[repoOwnerName]

    # path to module
    modulePath = repoName + '/' + serverPath

    # begin looping over the path
    for item in modulePath.split('/'):
        if item == '':
            continue

        item = item.replace('.py', '')
        if level is None:
            if item not in sys.modules:
                level = imp.new_module(item)
                sys.modules[item] = level
            else:
                level = sys.modules[item]
            continue
        try:
            level = level.__dict__[item]
        except KeyError:
            subModule = imp.new_module(item)
            level.__dict__[item] = subModule
            level = subModule

    exec repository.get_contents(serverPath).decoded_content in level.__dict__

    return level


def cloudImportDirectory(repoAddress, serverPath, userNamespace=True):
    """
    Import a directory from a server directory.
    :param repoAddress: 
    :param serverPath: 
    :param userNamespace: 
    :return: 
    """
    repository = FloatingTools.gitHubConnect().get_repo(repoAddress)

    result = []

    for f in repository.get_dir_contents(serverPath):
        if '.py' not in f.name:
            continue
        result.append(cloudImport(repoAddress, f.path, userNamespace))

    return result


def downloadBuild(repository, sha):
    """
    Download the latest FloatingTools build from the passed sha.
    :param repository: 
    :param sha: 
    :return: 
    """
    for fo in repository.get_dir_contents('/FloatingTools/'):
        if fo.type == 'dir':
            continue

        # pull server data
        serverPath = fo.path
        localPath = os.path.join(FloatingTools.INSTALL_DIRECTORY, serverPath)
        try:
            fileContent = repository.get_contents(serverPath, ref=sha)
            fileData = base64.b64decode(fileContent.content)
            fileOut = open(localPath, "w")
            fileOut.write(fileData)
            fileOut.close()
            FloatingTools.FT_LOOGER.info('Updated: ' + localPath)
        except (github.GithubException, IOError):
            FloatingTools.FT_LOOGER.error('Failed updating: ' + localPath)


def loadVersion():
    """
    Load the build information from the Branch.json file for the FloatingTools version.
    :return: 
    """
    if not os.path.exists(FloatingTools.DATA):
        os.mkdir(FloatingTools.DATA)

    branchFile = os.path.join(FloatingTools.DATA, 'Branch.json')
    # create the file if it doesnt exists.
    if not os.path.exists(branchFile):
        # build the default release data
        branchData = {'dev': False,
                      'devBranch': 'master',
                      'release': 'latest',
                      'installed': None,
                      'collaborator': False
                      }
        # dump the data
        json.dump(branchData, open(branchFile, 'w'), indent=4, sort_keys=True)
    # load the branch data
    branchData = json.load(open(branchFile, 'r'))

    if branchData['collaborator']:
        FloatingTools.FT_LOOGER.info("Launched in Collaborator mode. You are responsible for VCS control and syncing "
                                     "with HatfieldFX, LLC repository for FloatingTools. Repository public address "
                                     "aldmbmtl/FloatingTools. Thank you for helping us make FT better!")
        return

    # connect to github and pull the FloatingTools repository.
    hub = FloatingTools.gitHubConnect()
    repository = hub.get_repo('aldmbmtl/FloatingTools')

    version = None
    message = ""

    if branchData['dev']:
        # find the branch being requested
        commit = repository.get_branch(branchData['devBranch']).commit
        version = commit.sha

        message = "Loading in DEV branch: " + branchData['devBranch']

    else:
        # load in the release data from the repository
        if branchData['release'] != branchData['installed']:

            # load all releases
            releases = {}
            for release in repository.get_tags():
                releases[release.name] = release.commit.sha

            if branchData['release'] == 'latest':
                # find the latest version
                version = releases[max(releases)]
                message = "Downloading FloatingTools " + max(releases)
            else:
                version = releases[branchData['release']]
                message = "Downloading FloatingTools " + branchData['release']

    # begin download
    if version:
        FloatingTools.FT_LOOGER.info(message)

        downloadBuild(repository, version)

        FloatingTools.FT_LOOGER.info("Download complete.")

        if not branchData['dev']:
            # update the branch data
            branchData['installed'] = branchData['release']

            # save out data
            json.dump(branchData, open(branchFile, 'w'), indent=4, sort_keys=True)

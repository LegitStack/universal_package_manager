# Requirements

Python 3.x
PyYAML (taken care of by bootstrap file)

# How to use

Modify the `requirements.yml` file:
  activate or deactivate the package managers you want to use
  list the required packages and optionally their version

Then run the `aquire.py` file with any combination of the following commands:

   verify all requirements and install missing required packages:
       `--v`, `--vr`, `--vap`, `-verify_requirements`, `-verify_all_packages | [repo name]`

   verifies one package:
       `--p`, `--vp`, `-verify_package | package name`

   changes working directory to include folder (for git):
       `--c`, `--cd`, `-change_directory`

   install yaml manually before we use yaml to read what packages are required:
       `--b`, `--y`, `--by`, `-bootstrap_yaml`

   attempt to install all required packages without checking if they exist first:
       `--i`, `-install`

   display help:
       `--h`, `-help`, `help`, `commands`

If no commands are specified these will run as default:
  `-change_directory -bootstrap_yaml -verify_requirements`

  First it will change directory to the one above this folder in case your
  requirements folder specifies downloading repositories.

  Then it will attempt to install a yml package from pypi.org

  Then it will use that yml package to install all the other active packages in
  the `requirements.yml` file if they're seen to be missing.

Typically a Dockerfile...
  would
    `RUN python /app/prod/app/lib/include/acquire.py --b --i`
  in order to set up the files upon creation, and
    `ENTRYPOINT ["python","/app/prod/app/lib/include/acquire.py","--v"]`
  or run it some other way upon start up in order to continually stay up dated.

The requirements file contains lines for verifying if packages are installed
`
  verify:
    active: True
    show:
      command: 'apt show'
      missing: 'No packages found'
    list:
      command: 'apt list --installed'
      headers: 1
      extract name: [0, '/']
      extract version: [1, '']
`
These two lines describe how to parse the line containing the package name and
version number. The first element of the list is a number indicating the
index position of name, while the second indicates how the line should be split.
  extract name: `[0, '/']`
  extract version: `[1, '']`

To extract a name from this line `'yaml/stable.now 1.6.0 [master]'` the
`requirements.yml` file indicates we should `name = split('/')[0]`. If more steps
required simply add them onto the extract process following the existing
pattern:
  `[ index to extract , string to split on , 2nd extract index, 2nd string , ]`

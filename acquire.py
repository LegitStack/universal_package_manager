import subprocess
import sys
import os

'''
this script uses an external file called requirements.yml
to install files from whatever package repository is specified.
It requires subprocess and yaml to be installed first.
'''

def change_directory_to_include(repo_folder='include', repo_path=''):
    ''' this is for pulling down repos into this directory
        change the repo_folder to specify a relative path
        change the repo_path as a path to the repos folder from root.
        this assumes this file is located in ./lib/universal_package_manager/'''
    if repo_path != '':
        os.chdir(repo_path)
    else:
        if os.path.isdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), repo_folder)):
            os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), repo_folder))


def get_yaml_file(name='requirements.yml'):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),name)


def get_yaml_data():
    import yaml
    reqs_file = get_yaml_file()
    reqs = yaml.load(open(reqs_file))
    return reqs

def extract_order(reqs):
    respect_order = reqs['acquire']['active']
    install_order = reqs['acquire']['order']
    del reqs['acquire']
    if respect_order:
        return reqs, install_order
    else:
        return reqs, reqs.key()


def grab_package(command, option, package):
    run_subprocess('{0} {1} {2}'.format(command, option, package))


def run_subprocess(command, print_oe=True):
    output = ''
    error  = ''
    try:
        print('---> command: ',command)
        result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output,error = result.communicate()
        output = output.decode("utf-8")
        error = error.decode("utf-8")
        if print_oe:
            print('---> output:  ',output)
            print('---> errors:  ',error, '\n\n')
    except Exception as e:
        print('---> command: ',command)
        print('---> errors:  ')
        print(type(e))
        print(e.args)
        print(e)
    return output, error


def grab_reqs(reqs):
    reqs, order = extract_order(reqs)
    for k in order:
        if reqs[k]['active']:
            for package in reqs[k]['install']['packages']:
                grab_package(reqs[k]['install']['command'], reqs[k]['install']['option'], package)


def verify_requirements(reqs):
    ''' verifies requirements quickly based on the list and parse list commands '''
    print('\nVerifying installation of required packages...\n')
    reqs, order = extract_order(reqs)
    for k in order:
        if reqs[k]['active'] and reqs[k]['verify']['active']:
            check_list = reqs[k]['install']['packages']
            command = '{0}'.format(reqs[k]['verify']['list']['command'])
            output, error = run_subprocess(command, print_oe=False)
            output = output.split('\n')[int(reqs[k]['verify']['list']['headers']):]
            for line in output:
                if line != '':
                    package_name    = parse_line(line, reqs[k]['verify']['list']['extract name'])
                    package_version = parse_line(line, reqs[k]['verify']['list']['extract version'])
                    for required_package in check_list:
                        required_name,required_version = parse_required_name_and_version(required_package, default_version=package_version)
                        if  package_name.lower()    == required_name.lower()    \
                        and package_version.lower() == required_version.lower() :
                            check_list.remove(required_package)
            if check_list == []:
                print('     All Packages Installed Correctly.\n')
            else:
                for thing in check_list:
                    print('    ', thing, 'missing!')
                    grab_package(reqs[k]['install']['command'], reqs[k]['install']['option'], thing)
    print('Verification and update process complete.\n')


def verify_package(reqs, package_name):
    reqs, order = extract_order(reqs)
    found_in_list = False
    for k in order:
        if reqs[k]['active'] and reqs[k]['verify']['active']:
            for required_package in reqs[k]['install']['packages']:
                required_name,required_version = parse_required_name_and_version(required_package)
                if required_name == package_name:
                    found_in_list = True
                    command = '{0} {1}'.format(reqs[k]['verify']['show']['command'], required_name)
                    output, error = run_subprocess(command)
                    if reqs[k]['verify']['show']['missing'] != '' \
                    and reqs[k]['verify']['show']['missing'] in output \
                    or output == '':
                        grab_package(reqs[k]['install']['command'], reqs[k]['install']['option'], required_package)
                    else:
                        print('Package:', package_name, 'already successfully installed.')
                        print('  Version number verification not attempted:')
                        print('    Installed version: displayed above')
                        print('    Required version:', required_version or 'latest')
            if not found_in_list:
                print('Package:', package_name, 'missing from your requirements list.')


def parse_required_name_and_version(required_package, default_version=''):
    if '>=' in required_package:
        required_name = required_package.split('>=')[0]
        required_version = required_package.split('>=')[1]
    elif '==' in required_package:
        required_name = required_package.split('==')[0]
        required_version = required_package.split('==')[1]
    elif '=' in required_package:
        required_name = required_package.split('=')[0]
        required_version = required_package.split('=')[1]
    elif '/' in required_package:
        required_name = required_package.split('/')[-1]
        required_version = default_version
    else:
        required_name = required_package
        required_version = default_version
    return required_name,required_version


def parse_line(line, steps):
    '''
    steps pattern:
    [index to isolate, characters to split on, next index to isolate, next char..]
    example call:
    line    = 'stableNow/perl-modules-5.24 v14.563  [whatever]'
    name    = parse_line(line, [0,'',1,'/',])
    version = parse_line(line, [1,''])
    '''
    index = steps[0]
    step = steps[1]
    steps = steps[2:]
    if step == '':
        line = line.split()[index]
    else:
        line = line.split(step)[index]
    if len(steps) > 0:
        line = parse_line(line, steps)
    return line


def bootstrap_yaml():
    with open(get_yaml_file('bootstrap')) as f:
        lines = f.readlines()
    for line in lines:
        output, error = run_subprocess(line)


if __name__ == '__main__':
    if [i for i in sys.argv if i in ['-h', '--help','help','commands']]:
        print()
        print('commands:')
        print()
        print(' verify all requirements and install missing required packages:')
        print('     -v, -vr, -vap, --verify_requirements, --verify_all_packages | [repo name]')
        print()
        print(' verifies one package:')
        print('     -p, -vp, --verify_package | package name')
        print()
        print(' changes working directory to include folder (for git):')
        print('     -c, -cd, --change_directory')
        print()
        print(' install yaml manually before we use yaml to read what packages are required:')
        print('     -b, -y, -by, --bootstrap_yaml')
        print()
        print(' attempt to install all required packages without checking if they exist first:')
        print('     -i, --install')
        print()
        print(' display help:')
        print('     -h, --help, help, commands')
        print()
    if [i for i in sys.argv if i in ['-c', '-cd', '--change_directory']]:
        change_directory_to_include()
    if [i for i in sys.argv if i in ['-b', '-y', '-by', '--bootstrap_yaml']]:
        bootstrap_yaml()
    if [i for i in sys.argv if i in ['-i', '--install']]:
        grab_reqs(get_yaml_data())
    if [i for i in sys.argv if i in ['-p','-vp', '--verify_package']]:
        verify_package(get_yaml_data(), package_name=sys.argv[-1])
    if [i for i in sys.argv if i in ['-v', '-vr','-vap','--verify_requirements','--verify_all_packages']]:
        verify_requirements(get_yaml_data())
    if len(sys.argv) == 1:
        change_directory_to_include()
        bootstrap_yaml()
        verify_requirements(get_yaml_data())

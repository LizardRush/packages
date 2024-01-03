import json
import subprocess
import requests
import os
import git
import shutil
from git import Repo
print('Initializing Rush Packager scripts')
class Actions:
    def jsonify(self, contents, name):
        data = {'.system': contents}
        json_data = json.dumps(data, indent=2)
        with open(f'systemConfig/{name}.json', 'r') as f:
            f.write(json_data)
class SystemConfig:
    destination_folder = "packager_files"
    def get_package_from_git(self, repo_url, folder, extract_contents):
        
        Repo.clone_from(repo_url, 'packager_files')
        if extract_contents:
            files_in_folder = os.listdir(f'packager_files/{folder}')
            for file_name in files_in_folder:
                file_path = os.path.join(self.destination_folder, file_name)
                shutil.move(file_path, file_name)
        else:
            shutil.move(f'packager_files/{folder}', folder)
    def install_pip_package(self, package_name):
        try:
            subprocess.check_call(["pip", "install", package_name])
            print(f"Successfully installed {package_name}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {package_name}: {e}")
    def write_lock_file(self, contents):
        with open('system.lock', 'w') as f:
            f.write(f'{contents}')
    def import_lizardlib(self, package):
        print(f'Rush Packager: Getting Package: {package}')
        response = requests.get(f'https://raw.githubusercontent.com/LizardRush/packages/main/lizardlibs/{package}.py')
        if response.status_code == 200:
            with open(f'lizardlibs/{package}.py', 'w') as f:
                f.write(response.text)
        elif response.status_code == 404:
            print(f'404: Did not find {package} in the GitHub repo')

    def clone_repo(self, repo_url, destination_folder):
        try:
            git.Repo.clone_from(repo_url, destination_folder)
            print(f"Repository cloned successfully to {destination_folder}")
        except git.exc.GitCommandError as e:
            print(f"Failed to clone repository: {e}")
systemconfig = SystemConfig()
actions = Actions()
def execute_actions_from_rconfig(file_path):
    start_config = False
    current_wrapper = None
    content_accumulator = []

    with open(file_path, 'r') as file:
        for line in file:
            line = line.split('#')[0].strip()
            if not line:
                continue
            if line.startswith('[[[{{{start-config}}}]]]'):
                start_config = True
            elif line.startswith('[[[{{{end-config}}}]]]'):
                start_config = False
                current_wrapper = None
                content = '\n'.join(content_accumulator)
                # Process the accumulated content based on the wrapper
                if content:
                    if current_wrapper == 'git':
                        content_lines = content.split('\n')
                        for content_line in content_lines:
                            key_value = content_line.split('=')
                            if len(key_value) == 2:
                                key, value = key_value[0].strip(), key_value[1].strip()
                                if key == 'repo':
                                    global git_repo
                                    git_repo = value
                                elif key == 'folder':
                                    global git_folder
                                    git_folder = value
                                elif key == 'extract_contents':
                                    global git_extract
                                    git_extract = value
                        systemconfig.get_package_from_git(git_repo, git_folder, git_extract)
                    elif current_wrapper == 'lock':
                        systemconfig.write_lock_file(content)
                    elif current_wrapper == 'libs.pyright':
                        content_lines = content.split('\n')
                        for current_line in content_lines:
                            line_parts = current_line.split('.')
                            if line_parts[0] == 'pylib':
                                systemconfig.install_pip_package(line_parts[1])
                            else:
                                pass
                    elif current_wrapper == 'libs.rush':
                        content_lines = content.split('\n')
                        for current_line in content_lines:
                            line_parts = current_line.split('.')
                            if line_parts[0] == 'rush':
                                systemconfig.import_lizardlib(line_parts[1])
                            else:
                                pass
                content_accumulator = []
            elif start_config:
                if line.startswith('[{') and line.endswith('}]'):
                    current_wrapper = line[2:-2]
                elif current_wrapper:
                    content_accumulator.append(line)
file_path = 'package.rconfig'
execute_actions_from_rconfig(file_path)

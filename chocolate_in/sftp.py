import os
import paramiko
from log import setup_logging
from project_manager import get_config
import hashlib
logging = setup_logging()


def get_file_hash(path):
    """Return the SHA-256 hash of the file at the given path."""
    sha256 = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except FileNotFoundError:
        return None

def ensure_config():
    if not (a := get_config()):
        logging.critical('No chocolate project found in this route.')
        quit(1)
    return a

class Sftp:
    def __init__(self, ip, username, password) -> None:
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(ip, username=username, password=password)
        self.sftp = self.ssh.open_sftp()

    def upload(self, file, dest):
        logging.info(f'Uploading {file} to {dest}')
        self._mkdir_remote(os.path.dirname(dest))
        self.sftp.put(file, dest)
        logging.info(f'Uploaded {file} to {dest}')

    def run(self, name):
        cmd = f'cd ~/{name} && bash run.sh'
        channel = self.ssh.get_transport()
        if not channel:
            return
        channel = channel.open_session()
        channel.exec_command(cmd)

        while True:
            if channel.recv_ready():
                output = channel.recv(1024).decode()
                for line in output.splitlines():
                    yield line

            if channel.recv_stderr_ready():
                error_output = channel.recv_stderr(1024).decode()
                for line in error_output.splitlines():
                    yield line

            if channel.exit_status_ready():
                break

    def get_hashes(self, name):
        cmd = f'cd ~/{name} && bash hash.sh'
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        stdout = stdout.read().decode().split('\n')
        
        res = {}
        for i in stdout:
            i = i.split('=',1)
            if len(i) == 2:
                res[i[0]]=i[1]
        return res

    def _mkdir_remote(self, path):
        path = path.replace('\\', '/')
        cmd = f'mkdir -p "{path}"'
        
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        err = stderr.read().decode()
        if err:
            logging.error(f'Failed to mkdir {path}: {err}')

    def sync(self, dest_folder):
        logging.info(f'Syncing current directory to {dest_folder}')
        logging.info('Getting hashes from server.')
        hashes = self.get_hashes(dest_folder)

        for root, dirs, files in os.walk('.'):
            # Skip logs/ and venv/ directories
            dirs[:] = [d for d in dirs if d not in ('logs', 'venv')]

            for filename in files:
                local_path = os.path.join(root, filename)
                rel_path = os.path.relpath(local_path, '.')
                remote_path = os.path.join(dest_folder, rel_path).replace('\\', '/')
                if rel_path in hashes and get_file_hash(local_path) == hashes[rel_path]:
                    logging.info(f'{local_path} is not changed. skipping...')
                    continue
                self._mkdir_remote(os.path.dirname(remote_path))
                
                self.sftp.put(local_path, remote_path)
                logging.info(f'Uploaded {rel_path} -> {remote_path}')
        logging.info('Sync completed.')


    def close(self):
        self.sftp.close()
        self.ssh.close()

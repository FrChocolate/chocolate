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
        logging.debug(f"Opening file to compute hash: {path}")
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        hash_value = sha256.hexdigest()
        logging.debug(f"Computed SHA-256 for {path}: {hash_value}")
        return hash_value
    except FileNotFoundError:
        logging.error(f"File not found for hashing: {path}")
        return None
    except Exception as e:
        logging.error(f"Error hashing file {path}: {e}")
        return None


def ensure_config():
    logging.info("Fetching project configuration.")
    if not (a := get_config()):
        logging.critical("No chocolate project found in this route.")
        quit(1)
    logging.info("Project configuration fetched successfully.")
    return a


class Sftp:
    def __init__(self, ip, username, password, port) -> None:
        logging.info(f"Initializing SFTP connection to {ip}:{port} as {username}")
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(ip, username=username, password=password, port=port)
            logging.info("SSH connection established.")
            self.sftp = self.ssh.open_sftp()
            logging.info("SFTP session opened.")
        except Exception as e:
            logging.critical(f"Failed to connect via SSH: {e}")
            raise

    def upload(self, file, dest):
        logging.info(f"Preparing to upload {file} to {dest}")
        try:
            self._mkdir_remote(os.path.dirname(dest))
            self.sftp.put(file, dest)
            logging.info(f"Uploaded {file} to {dest}")
        except Exception as e:
            logging.error(f"Upload failed for {file} to {dest}: {e}")

    def run(self, name):
        cmd = f"cd ~/{name} && bash run.sh"
        logging.info(f"Executing remote command: {cmd}")
        try:
            channel = self.ssh.get_transport()
            if not channel:
                logging.error("SSH transport is not available.")
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
            logging.info("Remote script execution completed.")
        except Exception as e:
            logging.error(f"Failed to execute remote command: {e}")

    def get_hashes(self, name):
        cmd = f"cd ~/{name} && bash hash.sh"
        logging.info(f"Fetching hashes from remote with command: {cmd}")
        try:
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            stdout = stdout.read().decode().split("\n")
            err = stderr.read().decode()
            if err:
                logging.warning(f"Remote stderr: {err}")

            res = {}
            for i in stdout:
                i = i.split("=", 1)
                if len(i) == 2:
                    logging.debug(f"Received hash: {i[0]} = {i[1]}")
                    res[i[0]] = i[1]
            logging.info(f"Fetched {len(res)} file hashes from server.")
            return res
        except Exception as e:
            logging.error(f"Error fetching remote hashes: {e}")
            return {}

    def exec(self, cmd):
        logging.info(f"Executing remote command: {cmd}")
        try:
            channel = self.ssh.get_transport()
            if not channel:
                logging.error("SSH transport is not available.")
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
            logging.info("Remote script execution completed.")
        except Exception as e:
            logging.error(f"Failed to execute remote command: {e}")
            

    def _mkdir_remote(self, path):
        path = path.replace("\\", "/")
        cmd = f'mkdir -p "{path}"'
        logging.debug(f"Creating remote directory: {path}")
        try:
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            err = stderr.read().decode()
            if err:
                logging.warning(f"Remote mkdir stderr: {err}")
        except Exception as e:
            logging.error(f"Failed to mkdir {path}: {e}")

    def sync(self, dest_folder):
        logging.info(f"Syncing current directory to {dest_folder}")
        logging.info("Getting hashes from server.")
        hashes = self.get_hashes(dest_folder)

        for root, dirs, files in os.walk("."):
            logging.debug(f"Walking through directory: {root}")
            dirs[:] = [d for d in dirs if d not in ("log", "venv")]
            for filename in files:
                local_path = os.path.join(root, filename)
                rel_path = os.path.relpath(local_path, ".")
                remote_path = os.path.join(dest_folder, rel_path).replace("\\", "/")
                local_hash = get_file_hash(local_path)
                remote_hash = hashes.get(rel_path)

                if remote_hash and local_hash == remote_hash:
                    logging.info(f"{rel_path} is not changed. skipping...")
                    continue

                logging.info(f"{rel_path} changed or new. uploading...")
                try:
                    self._mkdir_remote(os.path.dirname(remote_path))
                    self.sftp.put(local_path, remote_path)
                    logging.info(f"Uploaded {rel_path} -> {remote_path}")
                except Exception as e:
                    logging.error(f"Failed to upload {rel_path}: {e}")
        logging.info("Sync completed.")

    def close(self):
        logging.info("Closing SFTP and SSH connections.")
        try:
            self.sftp.close()
            self.ssh.close()
            logging.info("Connections closed.")
        except Exception as e:
            logging.warning(f"Error during closing connections: {e}")

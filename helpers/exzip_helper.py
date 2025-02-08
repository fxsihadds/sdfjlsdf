import os
import subprocess
import shutil
from bot import LOGGER

class ExtractZip:
    def __init__(self, path, output, password=None) -> None:
        self.path = path
        self.output = output
        self.password = password

        if not os.path.exists(self.output):
            os.mkdir(self.output)

        self._extract_with_7z_helper()

    def support_format(self):
        pass

    def _extract_with_7z_helper(self):
        LOGGER.info("7z : " + self.output + " : " + self.path) 
        command = ['7z', 'x', self.path, f'-o{self.output}', '-y']
        
        # If a password is provided, add the `-p` option
        if self.password:
            command.append(f'-p{self.password}')

        return self.__run_cmds_unzipper(command=command)
        
    def __run_cmds_unzipper(self, command):
        ext_cmd = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        
        if ext_cmd.returncode != 0:
            os.remove(self.path)
            raise RuntimeError(f"Extraction failed:")
            
        os.remove(self.path)

    def cleanup_macos_artifacts(self):
        # This can be used for cleaning any unnecessary artifacts on Linux as well
        for root, dirs, files in os.walk(self.output):
            for name in files:
                if name == ".DS_Store":  # These are macOS-specific, you can remove this if unnecessary on Linux
                    os.remove(os.path.join(root, name))
            for name in dirs:
                if name == "__MACOSX":  # These are macOS-specific, you can remove this if unnecessary on Linux
                    shutil.rmtree(os.path.join(root, name))

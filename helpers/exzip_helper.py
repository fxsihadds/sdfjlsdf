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
        command = [
        r"C:\Program Files\7-Zip\7z.exe", 'x', self.path, f'-o{self.output}', '-y'
    ]
        # If a password is provided, add the `-p` option
        if self.password:
            command.append(f'-p{self.password}')

        return self.__run_cmds_unzipper(command=command)
        

    def __run_cmds_unzipper(self, command):
        
        ext_cmd = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        #ext_out = ext_cmd.stdout.read()[:-1].decode("utf-8").rstrip("\n")
        #ext_err = ext_cmd.stderr.read()[:-1].decode("utf-8").rstrip("\n")
        #LOGGER.info("ext_out : " + ext_out)
        #LOGGER.info("ext_err : " + ext_err)

        if ext_cmd.returncode != 0:
            
            os.remove(self.path)
            #LOGGER.error(f"Command failed with error: {ext_err}")
            raise RuntimeError(f"Extraction failed:")
            
        os.remove(self.path)



    def cleanup_macos_artifacts(self):
        for root, dirs, files in os.walk(self.output):
            for name in files:
                if name == ".DS_Store":
                    os.remove(os.path.join(root, name))
            for name in dirs:
                if name == "__MACOSX":
                    shutil.rmtree(os.path.join(root, name))

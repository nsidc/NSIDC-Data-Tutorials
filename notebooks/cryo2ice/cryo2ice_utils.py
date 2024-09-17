"""Utility routines to download CryoSat-2 files"""

import os
import platform
from ftplib import FTP
import sys
from typing import Union, List

from pathlib import Path


def get_padded_count(count, max_count):
    return str(count).zfill(len(str(max_count)))


def file_byte_handler(data):
    global download_file_obj, read_byte_count, total_byte_count
    download_file_obj.write(data)
    read_byte_count = read_byte_count + len(data)
    progress_bar(read_byte_count, total_byte_count)


def progress_bar(progress, total, prefix="", size=60, file=sys.stdout):
    if total != 0:
        x = int(size * progress / total)
        x_percent = int(100 * progress / total)
        file.write(f" {prefix} [{'='*x}{' '*(size-x)}] {x_percent} % \r")
        file.flush()


def download_files(user_email: str, esa_files: List[str], dir: Union[str,Path]="."):
    """Downloads CryoSat-2 Files from ESA ftp

    Arguments
    ---------
    user_email : email to use for anonymous ftp login
    esa_files : list of paths to cryosat-2 files
    dir : output directory path.  Default is current working directory.
          If dir does not exist it is created.

    Returns
    -------
    list of paths to downloaded files
    """
    global download_file_obj, read_byte_count, total_byte_count

    if not isinstance(dir, Path):
        dir = Path(dir)
        
    if not dir.exists():
        if not dir.exists():
            print("Download path dir does not exist.  Creating dir")
            dir.mkdir(parents=True, exist_ok=True)

    print("About to connect to ESA science server")
    with FTP("science-pds.cryosat.esa.int") as ftp:
        try:
            ftp.login("anonymous", user_email)
            print("Downloading {} files".format(len(esa_files)))

            download_path_list = []
            for i, filename in enumerate(esa_files):
                padded_count = get_padded_count(i + 1, len(esa_files))
                print("{}/{}. Downloading file {}".format(padded_count, len(esa_files), 
                                                           os.path.basename(filename)))

                download_path = dir / os.path.basename(filename)
                with open(download_path, 'wb') as download_file:
                    download_file_obj = download_file
                    total_byte_count = ftp.size(filename)
                    read_byte_count = 0
                    ftp.retrbinary('RETR ' + filename, file_byte_handler, 1024)
                download_path_list.append(download_path)
                print("\n")
        finally:
            print("Exiting FTP.")
            ftp.quit()

    return download_path_list    
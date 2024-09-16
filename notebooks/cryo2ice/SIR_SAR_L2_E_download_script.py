import os
import platform
from ftplib import FTP
import sys


download_file_obj = None
read_byte_count = None
total_byte_count = None


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


def download_files(user_email, esa_files):
    global download_file_obj, read_byte_count, total_byte_count
    print("About to connect to ESA science server")
    with FTP("science-pds.cryosat.esa.int") as ftp:
        try:
            ftp.login("anonymous", user_email)
            print("Downloading {} files".format(len(esa_files)))

            for i, filename in enumerate(esa_files):
                padded_count = get_padded_count(i + 1, len(esa_files))
                print("{}/{}. Downloading file {}".format(padded_count, len(esa_files), os.path.basename(filename)))

                with open(os.path.basename(filename), 'wb') as download_file:
                    download_file_obj = download_file
                    total_byte_count = ftp.size(filename)
                    read_byte_count = 0
                    ftp.retrbinary('RETR ' + filename, file_byte_handler, 1024)
                print("\n")
        finally:
            print("Exiting FTP.")
            ftp.quit()


if __name__ == '__main__':

    esa_files = ['SIR_SAR_L2/2019/12/CS_LTA__SIR_SAR_2__20191227T110305_20191227T111751_E001.nc', 'SIR_SAR_L2/2020/03/CS_LTA__SIR_SAR_2__20200329T163208_20200329T164044_E001.nc', 'SIR_SAR_L2/2020/01/CS_LTA__SIR_SAR_2__20200114T203033_20200114T204440_E001.nc', 'SIR_SAR_L2/2019/11/CS_LTA__SIR_SAR_2__20191103T134759_20191103T135125_E001.nc', 'SIR_SAR_L2/2020/02/CS_LTA__SIR_SAR_2__20200204T191657_20200204T192558_E001.nc', 'SIR_SAR_L2/2019/12/CS_LTA__SIR_SAR_2__20191216T215645_20191216T220909_E001.nc', 'SIR_SAR_L2/2020/03/CS_LTA__SIR_SAR_2__20200315T065755_20200315T071241_E001.nc', 'SIR_SAR_L2/2019/10/CS_LTA__SIR_SAR_2__20191030T135252_20191030T135600_E001.nc', 'SIR_SAR_L2/2020/02/CS_LTA__SIR_SAR_2__20200219T081800_20200219T083303_E001.nc', 'SIR_SAR_L2/2020/01/CS_LTA__SIR_SAR_2__20200110T203717_20200110T204612_E001.nc', 'SIR_SAR_L2/2020/04/CS_LTA__SIR_SAR_2__20200409T053748_20200409T054151_E001.nc', 'SIR_SAR_L2/2020/04/CS_LTA__SIR_SAR_2__20200413T053254_20200413T053659_E001.nc', 'SIR_SAR_L2/2020/02/CS_LTA__SIR_SAR_2__20200208T191154_20200208T192117_E001.nc', 'SIR_SAR_L2/2020/03/CS_LTA__SIR_SAR_2__20200319T065300_20200319T070802_E001.nc', 'SIR_SAR_L2/2020/03/CS_LTA__SIR_SAR_2__20200304T175209_20200304T180102_E001.nc', 'SIR_SAR_L2/2019/11/CS_LTA__SIR_SAR_2__20191128T122800_20191128T123212_E001.nc', 'SIR_SAR_L2/2019/10/CS_LTA__SIR_SAR_2__20191009T150801_20191009T151142_E001.nc', 'SIR_SAR_L2/2019/11/CS_LTA__SIR_SAR_2__20191121T231659_20191121T232817_E001.nc', 'SIR_SAR_L2/2020/02/CS_LTA__SIR_SAR_2__20200215T082253_20200215T083741_E001.nc', 'SIR_SAR_L2/2020/01/CS_LTA__SIR_SAR_2__20200121T094259_20200121T095800_E001.nc', 'SIR_SAR_L2/2019/10/CS_LTA__SIR_SAR_2__20191005T151255_20191005T151621_E001.nc', 'SIR_SAR_L2/2020/04/CS_LTA__SIR_SAR_2__20200427T150701_20200427T151544_E001.nc', 'SIR_SAR_L2/2019/10/CS_LTA__SIR_SAR_2__20191024T004201_20191024T005059_E001.nc', 'SIR_SAR_L2/2020/03/CS_LTA__SIR_SAR_2__20200308T174708_20200308T175621_E001.nc', 'SIR_SAR_L2/2020/04/CS_LTA__SIR_SAR_2__20200402T162707_20200402T163602_E001.nc']

    if int(platform.python_version_tuple()[0]) < 3:
        exit("Your Python version is {}. Please use version 3.0 or higher.".format(platform.python_version()))

    email = input("Please enter your e-mail: ")

    download_files(email, esa_files)

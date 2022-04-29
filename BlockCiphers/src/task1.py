import os
import os.path as osp
import sys
from block_cipher import (
    BLOCKSIZE, ecb_encode, cbc_encode
)

BMP_HEADER_LEN = 54


def main():
    # iterate through all arguments other than the python file name
    for file in sys.argv[1:]:
        # get a key and initialization vector
        key = os.urandom(BLOCKSIZE)
        iv = os.urandom(BLOCKSIZE)

        # if the argument isn't a file that exists
        if not osp.exists(file):
            print(f"{file} does not exist, skipping...")
            continue

        # get the name and the extension separately
        name, ext = osp.splitext(osp.basename(file))

        # if it is an image...
        if ext == ".bmp":
            # read the file into a bytes object
            with open(file, "rb") as f:
                contents = f.read()

            # split into header and data
            header, data = contents[:BMP_HEADER_LEN], contents[BMP_HEADER_LEN:]
            
            # generate the ecb version
            ecb_data = ecb_encode(data, key)
            with open(f"output/{name}_ecb{ext}", "wb") as f:
                f.write(header)
                f.write(ecb_data)
            
            # generate the cbc version
            cbc_data = cbc_encode(data, key, iv)
            with open(f"output/{name}_cbc{ext}", "wb") as f:
                f.write(header)
                f.write(cbc_data)
        
        # every other type of file...
        else:
            # read the file into a bytes object
            with open(file, "rb") as f:
                data = f.read()
            
            # generate the ecb version
            ecb_data = ecb_encode(data, key)
            with open(f"output/{name}_ecb{ext}", "wb") as f:
                f.write(ecb_data)

            # generate the cbc version
            cbc_data = cbc_encode(data, key, iv)
            with open(f"output/{name}_cbc{ext}", "wb") as f:
                f.write(cbc_data)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: task1.py [file1] [file2] ...")
    main()
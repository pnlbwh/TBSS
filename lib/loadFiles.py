from tbssUtil import isfile
import numpy as np
def read_imgs(file, n):

    imgs=[]
    with open(file) as f:

        content = f.read()
        for line, row in enumerate(content.split()):
            temp = [element for element in row.split(',') if element]  # handling w/space

            if len(temp) != n:
                raise FileNotFoundError(f'Columns don\'t have same number of entries: check line {line} in {file}')

            for img in temp:
                if not isfile(img):
                    raise FileNotFoundError(f'{img} does not exist: check line {line} in {file}')

            imgs.append(temp)

    return np.array(imgs)

if __name__=='__main__':
    imgs= read_imgs('/home/tb571/Documents/TBSS/local_tests/imagelist_double.txt',2)
    print('Wait')
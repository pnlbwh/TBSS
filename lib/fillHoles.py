from tbssUtil import load, save_nifti
from plumbum import local, FG
from plumbum.cmd import fslmaths
from tempfile import TemporaryDirectory


def fillHoles(imgPath):

    with TemporaryDirectory() as tmpdir, local.cwd(tmpdir):

        img= load(imgPath)
        data= img.get_data()

        dataBin= (data>0.)*1
        save_nifti('bin.nii.gz', dataBin.astype('uint8'), affine=img.affine, hdr=img.header)

        fslmaths['bin.nii.gz', '-fillh', 'bin_filled.nii.gz'] & FG

        dataBinFilled= load('bin_filled.nii.gz').get_data()

        dataDiff= dataBinFilled - dataBin

        dataFilled= data+ dataDiff*10e-8

        save_nifti(imgPath, dataFilled, affine= img.affine, hdr= img.header)

if __name__=='__main__':
    fillHoles('')

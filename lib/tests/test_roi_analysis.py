from util import *

from roi_analysis import roi_analysis

class TestBmap(unittest.TestCase):

    def test_bvalMap(self):


        modDir = '/home/tb571/Documents/TBSS/local_tests/FA/'
        skelDir= pjoin(modDir, 'skeleton')
        roiDir = pjoin(modDir, 'roi')

        cases = ['GT_2007', 'GT_2029', 'GT_2046']
        imgs = [pjoin(skelDir, f'{c}_FA_to_target_skel.nii.gz') for c in cases]

        labelMapFile = '/home/tb571/fsl/data/atlases/JHU/JHU-ICBM-labels-1mm.nii.gz'

        modality = 'FA'

        roi_analysis(imgs, cases, modality, labelMapFile, None, modDir, roiDir, True)


if __name__ == '__main__':
    unittest.main()
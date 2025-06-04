from anre.utils import testutil
from anre.utils.modeling.timeSlice.timeSliceSchema import TimeSliceSchema
from anre.utils.parameter.parameter import Parameter


class TestTimeSliceSchema(testutil.TestCase):
    def test_smokeTest(self) -> None:
        values = list(range(100, 160))
        params = {
            'trainSizeDefault': 20,
            'testSizeDefault': 20,
            'levels': [
                {'testSize': 10, 'trainSize': 50, 'sliceCount': 1, 'shiftStep': -1},
                {
                    'testSize': 5,
                    'shiftStep': 2,
                    'testInitPoss': 10,
                    'slicingType': 'box',  # rolling, box
                },
                {
                    'testSize': 6,
                    'sliceCount': 3,
                    'shiftStep': -3,
                    'slicingType': 'box',  # rolling, box
                },
            ],
        }
        prm = Parameter(params)

        timeSliceSchema = TimeSliceSchema(values=values, prm=prm)
        rootTimeSlice = timeSliceSchema.get_rootTimeSlice()

        rootTimeSlice.plot(maxLevel=-1)
        str(rootTimeSlice)

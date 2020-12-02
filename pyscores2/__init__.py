import os
path = os.path.dirname(__file__)
exe_file_path = os.path.join(path, 'fortran', 'scores2.exe')


class UnknownError(Exception):
    default = r'Unknown error'
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = self.default

    def __str__(self):
        return '%s: %s' % (self.__class__, self.message)


class TooManySectionsError(UnknownError): default= r'Too many sections, wave lengths, wave angles, etc.'


class SumOfWeightDistributionError(UnknownError): default=r'Sum of weight distribution does not equal the displacement'


class DisplacementError(UnknownError): default=r'The calculated displacement differs from the given nominal displacement (max 2% deviation alowed)'


class LcgError(UnknownError): default=r'The calculated longitudinal centre of bouyancy differ from the nomonal value ((LCB-LCG)/L max 0.5%)'


class IncrementError(UnknownError): default=r'Error in range or increment of variable conditions'


class TDPError(UnknownError): default=r"TDP calculation incomplete. I don't know what this is but sectionfiles are created but no RAO:s so if only sections area needed this can be dissregarded"


class TDPFileError(UnknownError): default=r'TDP file label does not equal title data, col. 1-30'

class OutputFileEmptyError(UnknownError): default=r'The output file is empty'

class ZbarsMissingError(UnknownError): default=r'indata does not have zbars'
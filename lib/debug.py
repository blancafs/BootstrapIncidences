'''
Copyrights(R) Blancanator and Vanginous LTD

'''

from .configurator import DEBUG

class Debug:
    """
    Class to help with debug messages, all relevant classes subclass it to inherit the inform method.
    """

    ## DEBUG message method
    def inform(self, *text):
        Green = "\033[1;32;40m"
        White = "\033[1;37;40m"
        Norm = "\033[0;37;40m"
        if DEBUG:
            print(Green+'[DEBUG]:'+White, *text, Norm)

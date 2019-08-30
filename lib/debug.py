'''
Copyrights(R) Blancanator and Vanginous LTD

This class helps with debug messages. All relevant classes sublclass it
to inherit inform method
'''

from .configurator import DEBUG

class Debug:

    ## DEBUG message method
    def inform(self, *text):
        Green = "\033[1;32;40m"
        White = "\033[1;37;40m"
        Norm = "\033[0;37;40m"
        if DEBUG:
            print(Green+'[DEBUG]:'+White, *text, Norm)

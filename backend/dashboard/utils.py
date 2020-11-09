import os, sys

class linenum():

    def __init__(self, newline=True):
        self.newline = newline

    def __repr__(self):
        try:
            raise Exception
        except:
            frame = sys.exc_info()[2].tb_frame.f_back
            return '%s:%s:%s%s'%(
                os.path.basename(frame.f_code.co_filename), 
                frame.f_code.co_name, 
                frame.f_lineno, 
                '\n' if self.newline else ''
            )

def NoneStr2Obj(value):
    return None if value == 'None' else value

# from https://docs.djangoproject.com/en/3.1/howto/outputting-csv/#streaming-large-csv-files
class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

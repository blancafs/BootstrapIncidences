import os
import shutil
from lib.configurator import TEXT_DATABASE_PATH, VECTOR_DATABASE_PATH, GENERAL_DATABASE_PATH


def main():
    confirm = input('Are you sure you want to reset the database? (All changes will be lost) (y/n) >>')
    if confirm == 'y':
        # Create file lists
        files = [TEXT_DATABASE_PATH, VECTOR_DATABASE_PATH, GENERAL_DATABASE_PATH]
        files_backups = [x.rsplit('.',1)[0]+'_BACKUP.'+x.rsplit('.',1)[1] for x in files]

        # Overwrite databases with backups
        for i in range(3):
            try:
                shutil.copy(files_backups[i],files[i])
            except:
                print('Something went wrong while resetting:\n'+files[i]+'\nfrom backup file:\n'+files_backups[i])
                print('Aborting...')
                return

        print('Databases were reset successfully!')

    else:
        exit(0)



if __name__=='__main__':
    main()
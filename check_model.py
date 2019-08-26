import os

# Vars
path = os.path.dirname(os.path.realpath(__file__)) + '/'
model_dir = path + 'models/'
file_name = model_dir + 'model.tar.gz'
folder_name = model_dir + 'multilingual-large'
url = 'https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/1?tf-hub-format=compressed'


# Ensures the model directory is present
def checkModelDirectory():
    mkdir_request = "mkdir " + model_dir
    # Check if models dir is present
    if os.path.exists(model_dir):
        return
    else:
        os.system(mkdir_request)
        return


# Attempt to download and extract
def attemptDownload():
    print('Attempting download ...')

    # Build requests
    download_request = "wget -O "+file_name+" '"+url+"'"
    mkdir_request = "mkdir "+folder_name
    unpack_request = "tar xvzf "+file_name+" -C "+folder_name
    delete_tar = "rm "+file_name

    # Ensure model directory presence
    checkModelDirectory()

    # Perform requests
    os.system(download_request)
    print('\nDownload completed successfully!')
    os.system(mkdir_request)
    print('Unpacking files ...')
    os.system(unpack_request)
    print('\nUnpacking completed successfully!')
    os.system(delete_tar)
    return



def main():
    print('Checking models...')

    # Check if multilingual-large is in models folder
    if os.path.exists(folder_name):
        print('Multilingual model was found!.\nSearch terminating.')
        exit(0)
    else:
        print('Multilingual model was not found in the local repo.')
        ans = input('Do you want to attempt downloading it? (y/n) >> ')

    # If it does not exist and answer is no, exit
    if ans=='y':
        attemptDownload()
        print('Exiting.')
        exit(0)
    else:
        print('Exiting.')
        exit(0)

if __name__=='__main__':
    main()

# BootstrapIncidences
This is the repository for the Automatic Incidence Management Website

## Notes
- To start the server, make sure all the dependencies in 'requirements.txt' are installed and the models folder is not empty and then run 'python3 main.py'.
- If the models folder is empty (google encoder is not there), then run the 'check_model.py' script to download and save the model.
- To change the port the server runs in, open 'lib/configurator.py', and edit the PORT variable to the port of your choice.
- If for any reason the database needs to be reset to the initial training data then run 'reset_database.py'.

## Quick references
- Google Universal Sentence Encoder code is found in 'lib/processor.py'.
- ML Classifier specific code is found in 'lib/classifier.py'
- The saving/updating/extracting from the csv database files is all implemented by 'lib/incidentBase.py' and the files are in the 'data/' folder.

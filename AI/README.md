To run: ./ai_run 

--Will need to create a file (this type of file can't be copied to git)
'mkfifo ai-out'
'chmod 666 ai-out'

--May need to give this file permissions on a new system ('chmod -x ai_run')

--Once the system is running, run "ai-out_read.py" in another terminal to see the live metadata output, this is how the use case functions (rest of the backend) would read in the data.


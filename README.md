# Google Drive Security Checker 
Google Drive Security Checker is a python program that monitor your Google Drive and make sure all of your
files are private and can't be accessed publicly.

## In order to run the script you should first do the following steps:
1. Follow the instruction here to enable API and do all preparation needed:
https://developers.google.com/drive/api/quickstart/python
2. Make sure to put credentials.json inside config directory
3. Create new python virtual env 
4. Install requirements by using <code> pip install -r requirements </code>
5. Configure the time frequency you would like the script to check your drive changes on CHECK_NEW_FILES_FREQUENCY 
in google_drive_security_checker.py
6. Run the script using <code> python google_drive_security_checker.py </code>

### Interesting Stuff 
While I was working on this project, and played with the API a bit I found that I can retrieve deleted files even
though it can't be seen Google Drive UI

### Permissions, Scopes and tokens
- This scripts require permissions to you Google Drive, in this version it require permissions to read, write and edit
and delete access to your Google Drive files. It is possible that the script can do it with lower permissions and scopes 
but currently, this is how it was tested.
- Once you create credentials.json and run the script, it pops up and ask you to authenticate.
After you authenticate once, you token.json saved in config directory. it is not the best practice for security, it
can be saved in a more secure way in the next versions. make sure to delete it if you stopped using the script.

### Important to notice
- Notice that this script was written and tested in Python 3.11
- When you start the script in the first time, you should give the script the permissions it asks for

### Usage Example:
<code> python google_drive_security_checker.py </code>

### Output:
>INFO:root:Start monitoring you Google Drive\
>INFO:root:Checking for new changes...\
>INFO:root:No changes\
>INFO:root:0 files were changed\
>INFO:root:Sleeping for 10 seconds...\
>INFO:root:Checking for new changes...\
>INFO:root:1 changes\
>INFO:root:1 files were changed\
>Changing file מסמך ללא שם to private\
>INFO:root:מסמך ללא שם (15aSg9Mw8ll8kB9yRG48szjUZqOkpAtPgP-qHaLb4SA0) - added since the last check time\
>INFO:root:Checking file מסמך ללא שם permissions... \
>INFO:root:File מסמך ללא שם found as public to anyone with link\
>INFO:root:Deleting permissions anyoneWithLink for file מסמך ללא שם...\
>INFO:root:Done\
</deblock>

### Known Issues/pitfalls
- It seems that currently it is not possible to retrieve the default setting for sharing files using Google Drive API
you can read more about it in limitation of the API:
https://developers.google.com/admin-sdk/directory/v1/limits
"Groups, settings" - Groups access settings, sharing options, monitoring, and discussion archive is managed using the 
Admin console. For more information about groups settings, see the administration help center.
- In this version, the script is pulling and sleeping for configurable time. It is a better practice to use 
<code> watch</code> method and get push every time something changed. due to time consideration I didn't manage to 
use this method

### TODO: self note
- open / login to github repository and upload you solution
- check better method (watch) and get push instead of pulling

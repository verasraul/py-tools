<!-- ABOUT THE PROJECT -->
## About The Project
The purpose of this program is to add and search for the hostnames of unmonitored machines.

<!-- FEATURES -->
### Features
1. Single hostname or multiple comma separated hostnames can be added to the list.
2. Range-pattern name entry. For example, entering hostnames in this format `host[01-02].com` will add 
```
host01.com
host02.com
```
3. Allows wildcard (*) hostname searching.
4. Allows wildcard (*) removal of hostnames.
5. Comment section for each name entry.
6. The hostname(s) and comments associated with the hostname are displayed in the results.

<!-- REQUIREMENTS -->
### Requirements
1. python@3.12.
2. Tkinter (Python library).


<!-- GETTING STARTED -->
## Getting Started
1. Confirm that your machine is using `Python 3.12.*`.
    * Run `python3 --version`, the output should read: 
    ```
    Python 3.12.*
    ```
    * **If not**, then proceed to install Python 3.12 using homebrew: 
    ```
    brew install python@3.12
    ```
    * Confirm that Python 3.12 is installed by running: 
    ```
    brew search python3
    ```
    You should see `python@3.12 ✔` (with a checkmark ✔ next to it) in the ouput:
    ```
    ==> Formulae
        boost-python3            python@3.11 ✔            python@3.8               ipython                  jython
        python@3.10              python@3.12 ✔            python@3.9               bpython                  cython
    ```

    *   **NOTE**: If you are running `ansible@8` you should also see `python@3.11   ✔` with a checkmark ✔ because it's a dependancy for it.
    * Confirm that your machine is using `Python 3.12.*` by running: 
    ```
    python3 --version
    ```
    Your output should read:
    ```
    Python 3.12.*
    ```
    The asterisk (*) represents any number.

2. Confirm that you have `TKinter` Python library installed. 
    * Run: 
    ```
    brew search python-tk@3.12
    ``` 
    You should see python-tk@3.12 in your ouput (with a checkmark next to it):
    ```
    python-tk@3.12 ✔
    ```
    * **_IF NOT_**, then proceed to install TKinter library for Python 3.12:
    ```
    brew install python-tk@3.12
    ```
    You can confirm TKinter is installed by running `brew search python-tk@3.12` again and this time you should see `python-tk@3.12` with a checkmark:
    ```
    ==> Formulae
    python-tk@3.12 ✔               python-tk@3.11                 python@3.12 ✔                  python@3.11 ✔
    python-tk@3.10                 python-tk@3.9                  python-gdbm@3.12               python@3.10
    ```
    *   **_NOTE_**: Python typically comes with `TKinter` pre-installed; but, occasionally, the module may not be configured correctly during the installation process; in such scenario, you will need to manually download it via homebrew.
3. Fork the `denied_host_tool` repo to your github.
4. Clone repo to your local machine.
5. `cd` to repo:
    ```
    cd denied_host_tool
    ```
6. Set-up GitHub upstream remote:
    ```
    git remote add upstream git@github.bamtech.co:sysops/denied_host_tool.git
    ```

<!-- Usage -->
## Usage
* `cd` into repo: 
```
cd denied_host_tool
```
* Run program: 
```
python3 denied_host_gui.py
```
### Adding Hostname(s):
* Hostnames can be added in the following ways:
    * Users are able to input a single hostname: 
    ```
    example01.host.com
    ```
    * Users can input several hostnames separated by commas:
    ```
    example01.host.com, example02.host.com
    ```
    * Users can enter several hostnames in a range format by using brackets []:
    ```
    example[01-02].host.com
    ```
### Adding Comments:
* **ALWAYS** use a comment with your hostname(s) entry.
* **NEVER** use new lines in comment section.
* Provide brief explanation of why host is being removed from monitoring to the list and who made the request.
    * If applicable, add the ticket numbers (Jira, SNOW, etc.) linked to the host's removal to the comment field by placing a dash (-) after the comment.
    * Example of a good comment entry:
    ```
    Remove from monitoring per <employee-name> - <ticket-number> - thread; <thread-link>
    ```
Where `<ticket-number>` represents the ticket or request number if available/applicable.
* _Comments_ will be applied to each hostname supplied, whether they are entered as a single, comma-separated, or range format entry.
### Searching for Hostname(s):
* Users can search for a single hostname ```example01.host.com```.
* Users can utilize wildcard search pattern for mutiple hostnames ```example*.host.com```.
### Removing Hostnames:
* Hostnames can be removed singularly by entering specific hostname.
* Multiples hostnames can be removed from the list by using wildcard (*) pattern. ``` example*.host.com ``` will remove any hosts that has any amount of characters between `example` and `.host.com`.
### Saving changes:
* After adding/removing hostnames to and from the list you can save your changes by simply clicking the exit (X) button on the application's GUI.
* DO NOT exit application with `control + C` via the terminal as your changes would not be saved to the list. 
* Once the exit (X) button is clicked on the GUI the changes made to the csv file will automatically be saved and pushed to your repo.
* Open a PR to merge your changes to the shared list in the SysOps repo.


<!-- Troubleshoot and Error Messages -->
## Troubleshoot
1. When opening the program, if no updates were fetched from the main repo you will see the following message in the terminal:
```
Already up to date.
```
2. When exiting the program, if you see the following error message in the terminal:
```
An error occurred: Command 'git commit -m 'Updated denied list'' returned non-zero exit status 1.
```
* This just means that no updates were made to the list.
* For instance, when you close the application after using it to search the denied list and making no modifications, this "error" message will appear in your terminal output.

    
<p align="right">(<a href="#readme-top">back to top</a>)</p>

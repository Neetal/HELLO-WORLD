from pypsexec.client import Client
from pypsexec.exceptions import SCMRException
#import Resources.Config.variables as var
from robot.api import logger as LOGGER
import time
import logging
import random
import subprocess
import os
import paramiko
import winreg as reg
import sys
import signal

def signal_handler(signal, frame):
    print("Signal interrupt received. Exiting..." )
    sys.exit(0)
    
signal.signal(signal.SIGINT, signal_handler)

def progress_callback(current, total):
    print(f"Progress: {current}/{total}" )

def execute_windows_cmd(command, std_err=None):
    ''' This function logs into the windows OS and runs the given command.  '''

    # Comment out the below 4 lines if detailed logging by PyPsExec and SMBprotocol is required.
    pyps_logger = logging.getLogger("pypsexec")
    pyps_logger.setLevel(logging.ERROR)
    smb_logger = logging.getLogger("smbprotocol")
    smb_logger.setLevel(logging.WARNING)
    command = "dir"
    os_ip = "10.132.149.41"
    #os_ip = os_ip[1]
    os_user = "Administrator"
    #os_user = os_user[1]
    os_pass = "Swit@123"
    #os_pass = os_pass[1]
    
    print(f"Executing command on Windows IP {os_ip} for {os_user} {command}" )
    try:
        command = "/c " + command
        c = Client(server=os_ip, port=445, username=os_user, password=os_pass, encrypt=False)
        
        # track Client() progress
        #c.progress_callback = progress_callback
        #print("Command execution completed" )
        
        #c.connect(timeout=60)
        max_attempts =  5
        for attempt in range(max_attempts):
            try:
                if not c.connect():
                    print("Connection to Windows OS timed out or not responding" )
                    return
                else:
                    print("Connected to Windows OS" )
                    break    
            except Exception as ec:
                print(f"Failed to connect to windows: {e}" )
                if attempt < max_attempts - 1:
                    print(f"Retrying connection attempt {attempt + 1} of {max_attempts}" )
                    continue
                else:
                    LOGGER.error(f"Failed to connect to windows after maximum attempts: {e}" )
                    return
        print(f"Connected to Windows OS" )
            # Check if 'c' is None before calling methods on it
        if c is not None:
            print(" created a client connection" )
            try:
                c.create_service()
                c.run_executable("cmd.exe", arguments='netsh advfirewall firewall set rule name="File and Printer Sharing (SMB-In)" dir=in new enable=Yes', run_elevated=True)
                if 'reboot' in command:
                    stdout = c.run_executable("cmd.exe", arguments=command, asynchronous=True)
                    output = "reboot is executed, but the output is not captured"
                else:
                    LOGGER.trace("running command {command} on 'cmd.exe'", html=True)
                    try:
                        stdout = c.run_executable("cmd.exe", arguments=command)
                    except Exception as e:
                        errMsg = 'Error: Time limit exceeded, terminating..'
                        LOGGER.trace("timeout occurred ..,.", html=True)
                    if stdout is None:
                        print("Failed to execute command- {command}" )
                        return
                    else:
                        if std_err is None:
                            output = stdout[0].decode("utf-8")
                            error_stream = stdout[1].decode("utf-8")
                            print("stdout {0} from {command} \n", stdout )
                            print("Error Stream :\n" + error_stream )
                        else:
                            output = stdout[1].decode("utf-8")
                time.sleep(5)
                c.remove_service()
                #c.cleanup()
            except SCMRException as exc:
                    if exc.return_code == 1072:    
                        print("The specified service has been marked for deletion" )
                        pass
                    else:
                        raise exc
        else:
            print("Failed to create a client connection" )
            return
    except Exception as e:
        print(f"Error {e} occurred while executing the command: {command}" )
    
    finally:
        if c:
            c.disconnect()

    print("Command Output :\n" + output )
    output =  add_to_path_usingreg()
    return output


# Run the shutdown command with the appropriate flags to restart Windows
def restart_windows():
    ''' This function to restart windows OS and wait for it to turn up and validate.  '''
    try:
        # Run the shutdown command with the appropriate flags to restart Windows
        execute_windows_cmd("shutdown /r /t 0")
        
        # Wait for the remote host to turn up
        time.sleep(60)
        
        # Validate the remote host is up
        # Add your validation code here
        output =  execute_windows_cmd("ilorest")
        
    except Exception as e:
        print("Command Output : {e}\n"  )
    return output

def add_to_path_usingreg():
    ''' This function to add value in environment variable  '''
    # connect to remote system
    app_path = r"C:\\Program Files\\Hewlett Packard Enterprise\\RESTful Interface Tool"
    os_ip = "10.132.149.41"
    #os_ip = os_ip[1]
    os_user = "Administrator"
    #os_user = os_user[1]
    os_pass = "Swit@123"
    #os_pass = os_pass[1]
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(os_ip, 22, os_user, os_pass, auth_timeout=60, timeout=60, banner_timeout=60, allow_agent=False, look_for_keys=False)
    except paramiko.AuthenticationException:
        print("Authentication failed when connecting to {os_ip}" )
    except paramiko.SSHException as ssh_exc:
        print(f"Unable to establish SSH connection to {os_ip}: {ssh_exc}" )
    except paramiko.ssh_exception.NoValidConnectionsError:
        print(f"Unable to connect to {os_ip}. No valid connections." )
    except Exception as e:
        print(f"Error occurred while connecting to {os_ip}: {e}" )

    print(f"Adding {app_path} to the PATH environment variable on {os_ip}" )
    # Get the current value of the PATH environment variable
    stdin, stdout, stderr = ssh.exec_command("echo %PATH%")
    existing_path = stdout.read().decode("utf-8")
    #existing_path = execute_windows_cmd("echo %PATH%")

    # Check if the app_path is already in the PATH variable
    if app_path in existing_path:
        print("${app_path} is already in the PATH variable :\n" )
        return
    else:
        print("${app_path} is not in the PATH variable :\n" )
        # Append the app_path to the PATH variable
        new_path = f"{existing_path};{app_path}"


    try:
        # Open the Environment Variables registry key
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Environment", 0, reg.KEY_ALL_ACCESS)

        # Set the new PATH value in the registry
        reg.SetValueEx(key, "PATH", 0, reg.REG_EXPAND_SZ, new_path)

        # Notify the user about successful addition
        print("${app_path} added to the PATH variable successfully.\n"  )

        # Close the registry key
        reg.CloseKey(key)

        # Update the environment of the current Python process
        os.environ["PATH"] = new_path
        edited_path = os.environ.get('PATH', app_path)
        print("\n ${edited_path} \n" )
           
        restart_windows()
    except Exception as e:
        print(f"Error occurred: {e}") 
        print("Error occurred: {e}\n" )
        
if '__name__' == '__main__':
    command = "dir"
    execute_windows_cmd(command)
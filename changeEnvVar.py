import os
import winreg as reg

def restart_windows():
    try:
        # Run the shutdown command with the appropriate flags to restart Windows
        os.system("shutdown /r /t 0")
    except Exception as e:
        print(f"Error occurred: {e}")
		
def add_to_path(app_path):
    # Get the current value of the PATH environment variable
    current_path = os.environ.get('PATH', '')
    print(f"current_path:{current_path}")
    # Check if the application path is already in the PATH variable
    if app_path in current_path:
        print(f"{app_path} is already in the PATH variable.")
        return

    # Add the application path to the PATH variable
    new_path = f"{current_path};{app_path}"

    # Set the updated PATH variable
    os.environ['PATH'] = new_path
    added_path = os.environ.get('PATH', 'app_path')
    print(f"{app_path} has been added to the PATH variable.")
    restart_windows()
    #Sleep  30s



def add_to_path_usingreg(app_path):
    # Get the current value of the PATH environment variable
    existing_path = os.environ.get('PATH', '')

    # Check if the app_path is already in the PATH variable
    if app_path in existing_path:
        print(f"{app_path} is already in the PATH variable.")
        return

    # Append the app_path to the PATH variable
    new_path = f"{existing_path};{app_path}"

    try:
        # Open the Environment Variables registry key
        key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Environment", 0, reg.KEY_ALL_ACCESS)

        # Set the new PATH value in the registry
        reg.SetValueEx(key, "PATH", 0, reg.REG_EXPAND_SZ, new_path)

        # Notify the user about successful addition
        print(f"{app_path} added to the PATH variable successfully.")

        # Close the registry key
        reg.CloseKey(key)

        # Update the environment of the current Python process
        os.environ["PATH"] = new_path
        edited_path = os.environ.get('PATH', app_path)
        print(f"\n {edited_path} \n")
        
        restart_windows()
    except Exception as e:
        print(f"Error occurred: {e}") 
    

if __name__ == "__main__":
    # Provide the path of the application you want to add to the PATH variable
    app_path = r"C:\Program Files\Hewlett Packard Enterprise\RESTful Interface Tool"
    add_to_path_usingreg(app_path)
    #restart_windows()
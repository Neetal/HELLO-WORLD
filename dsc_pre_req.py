import re
import spur
import spur.ssh
import subprocess
from dsc_hpssacli import hpssacli
import paramiko
from ConfigParser import SafeConfigParser
#print "************* Going to start PRE REQUISITE TEST of Your System # %s ************"%(hostname)
result = None
cmd = r'cmd /c ver'
cmd2 = r'uname -a'
cmd3 = r'cmd /c systeminfo | findstr OS'
execution_path = r'C:\Users'
cmd4 = r'cmd /c "cd c:/Program Files/hp/hpssacli/bin & hpssacli version"'


class prerequisite(hpssacli):
    def __init__(self,hostname,username,password,filepath=None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.filepath = filepath
        self._ssh =None
        self._sftp =None
        self.shell = spur.SshShell(hostname=str(hostname), username=str(username), password=str(password),shell_type=spur.ssh.ShellTypes.sh,missing_host_key=spur.ssh.MissingHostKey.accept)
        self.linuxList = ['RHEL6', 'RHEL7', 'SUSE', 'SLES12', 'SLES11']
        self.windowsList = ['Windows2012', 'Windows2012R2', 'Windows2008', 'Windows2008R2', 'Windows2016', 'Windows']


    def hpssacli_check(self):
        os_name_list = self.os_name
        os_name = os_name_list[0]
        if (os_name) :
           if os_name in self.linuxList :
            hpssacli = self.shell.run(["rpm", "-qa", "|", "grep", "hpssacli.*"])
            installed_rpm = hpssacli.output
            hpssacli_version = re.findall(r'(hpssacli.*)',installed_rpm)

            #----------------------repetitive print statements in each if/elif conditions replaced at the end-----------
            #if hpssacli_version:
             #   print "HPSSACLI is INSTALLED and the version is %s \n\n"%(hpssacli_version)
              #  return True
            #else:
             #   print "HPSSACLI is not INSTALLED.. Please install HPSSACLI"
              #  return False
           elif os_name == 'Ubuntu':
            print "am in UBUNTU"
            hpssacli = self.shell.run(["dpkg","-s","hpssacli"])
            installed_rpm = hpssacli.output
            hpssacli_version = re.findall(r'(Version:.*)',installed_rpm)
            #if hpssacli_version:
             #   print "HPSSACLI is INSTALLED and the version is %s \n\n"%(hpssacli_version)
              #  return True
            #else:
             #   print "HPSSACLI is not INSTALLED.. Please install HPSSACLI"
              #  return False
            #return True
           elif os_name in self.windowsList :
            #print 'Am in WINDOWS'
            stdin,stdout,stderr = self._ssh.exec_command(cmd4)
            hpssacli = stdout.read()
            #print hpssacli
            hpssacli_version = re.findall(r'(HPSSACLI.*)',hpssacli)
            #if hpssacli_version:
             #   print "HPSSACLI is installed and the version is %s \n\n"%(hpssacli_version)
              #  return True
            #else:
             #   print "HPSSACLI is not INSTALLED.. Please install HPSSACLI"
              #  return False
           elif os_name == 'Vmware':
            hpssacli = self.shell.run(["esxcli","software","vib","list"])
            installed_rpm = hpssacli.output
            hpssacli_version = re.findall(r'(hpssacli.*)',installed_rpm)

           else:
            print "Unable to CHECK HPSSACLI on your %s Server"%(self.hostname)
            return False

            # ------------common for all elif os_name-------------------------------------------
            if hpssacli_version:
                print "HPSSACLI is INSTALLED and the version is %s \n\n" % (hpssacli_version)
                return True
            else:
                print "HPSSACLI is not INSTALLED.. Please install HPSSACLI"
                return False


    # THIS IS RESPONSIBLE TO CHECK WHETHER THE "SUT" HAS THE "TEST DRIVES" INSTALLED IN THE SYSTEM OR NOT
    # IT WILL RETURN A DICTIONARY CONTAINING THE LIST OF HDD AS "VALUE" AND THEIR ASSOCIATED CONTROLLER SLOT NUMBER AS "KEY"


    def search_of_specific_drive(self):
        f = open(self.filepath,'r')
        item = f.readlines()
        new_list_item = []
        for i in range(0,len(item)):
            new_list_item.append(item[i].rstrip('\n').split('_'))
        final_list =[]
        for i in range(0, len(new_list_item)):
            for j in range(0, len(new_list_item[i])):
                final_list.append(new_list_item[i][j])
        f.close()
        pd_details = self.pd_detail()
        available_drive= {}
        unavailable_drive = {}
        for i in range(0,len(final_list)):
            for key,val in pd_details.items():
                    pat = 'Model: \w+\s+'+final_list[i]
                    match = re.findall(pat,val)
                    if match:
                        available_drive.setdefault(key,[]).append(final_list[i])
                    else:
                        unavailable_drive.setdefault(key,[]).append(final_list[i])

        print "******Following are the AVAILABLE DRIVE LIST***** \n",available_drive
        print "******Following are the UNAVAILABLE DRIVE LIST***** \n",unavailable_drive
        if len(available_drive.keys()) > 1 :
            print "Drives are found in more than One slot "
            print "Drives list %s"%str(available_drive)
        try:
            parser = SafeConfigParser()
            parser.read('C:\DriveSmartAutomation\Config\global.ini')
            parser.set('HBA_Slot', 'ctrl', available_drive.keys()[0])
        except:
            pass
        return available_drive,unavailable_drive

    def pre_req(self):
        hpssacli,drives = self.hpssacli_check(),self.search_of_specific_drive()
        if hpssacli and drives:
            print "***********YOUR %s SYSTEM IS READY FOR SCRIPT EXECUTION ************"%(self.hostname)
            return True
        else:
            print "************ \n" \
            "YOUR %s SYSTEM HAS FAILED PRE-REQUISITE TEST. YOUR SCRIPT CANNOT BE EXECUTED. \n" \
            "PLEASE CHECK YOUR CONFIGURATION \n" \
            "*************"
            return False



#obj = prerequisite(r'15.162.207.168',r'root',r'Hpq12345','MB1000FCWDE','MB2000FCWDF','MB3000FCWDH','MB4000FCWD')
#obj = prerequisite(r'15.162.207.168',r'root',r'Hpq12345','MB1000GCWCV','MB2000GCWDA','MB3000GCWDB','MB4000GCWD')
#obj = prerequisite(r'15.162.207.7',r'root',r'Hpq12345',r'C:\prasit_drive_list.txt')
#obj = prerequisite(r'15.162.207.168',r'dscuser',r'Hpq12345',r'C:\prasit_drive_list.txt')
#obj = prerequisite(r'15.213.121.149',r'Administrator',r'Admin123',r'C:\prasit_drive_list.txt')

#obj.controller_check()
#obj.ctrlpdShow()
#obj.pre_req()
#obj.check_ping()
#obj.check_SSH_connection_linux()
#obj.check_SSH_connection()
#obj.os_check()
#obj.os_name()
#obj.hpssacli_check()
#obj.search_of_specific_drive('MB1000FCWDE','MB2000FCWDF','MB3000FCWDH','MB4000FCWD')
#obj.search_of_specific_drive('MB1000GCWCV','MB2000GCWDA','MB3000GCWDB','MB4000GCWD')
#obj.search_of_specific_drive('VK0400JEABD','VK0800JEABE','VO1600JEABF','MO0800JEFPB','EG0450FCHHT','EG0600JETKA')
#obj.search_of_specific_drive()
#obj.ctrlallShow()
#obj.ctrlSlotDetails()
#obj.pd_detail()
#obj.get_bootvolume_details(2)
#obj.controller_slot()
#obj.ctrlpdShow()
import spur
import spur.ssh
import re
import sys
import paramiko
import subprocess
import _collections
import copy

# print "************** HPSSACLI is going to START*****************"

#shell = spur.SshShell(hostname="192.168.191.128", username="neetal", password="12345678",shell_type=spur.ssh.ShellTypes.minimal,missing_host_key=spur.ssh.MissingHostKey.accept)
drive_dict = {'slot_num': 0, 'drive_type': 'SATA', 'num_drives': 2, 'raid': '1', 'size': 100, 'ld_id': 4,
              'drive_id': r'1I:1:25'}

result = None
cmd = r'cmd /c ver'
cmd1 = r'cmd /c "cd c:/Program Files/hp/hpssacli/bin & hpssacli ctrl all show"'
cmd1_a = r'cd / "cd /opt/hp/hpssacli/bin & ./hpssacli ctrl all show"'
# cmd1 = r'cmd.exe /c " C: && dir"'
cmd2 = r'uname -a'
cmd3 = r'cmd /c systeminfo | findstr OS'
cmd4 = r'cmd /c "cd c:/Program Files/hp/hpssacli/bin & hpssacli ctrl slot=2 pd all show"'
execution_path = r'C:\Users'


class hpssacli(object):
    # class hpssacli(prerequisite):
    def __init__(self, drive_dict):
        self.username = "root"
        self.password = "Hpq12345"
        self.hostname = "15.213.140.231"
        self.slot_num = drive_dict['slot_num']
        self.drive_type = drive_dict['drive_type']
        self.num_drives = drive_dict['num_drives']
        self.raid = drive_dict['raid']
        self.size = drive_dict['size']
        self.ld_id = drive_dict['ld_id']
        self.drive_id = drive_dict['drive_id']
        self.shell=""

    def check_ping(self):
        print "************* Going to start PRE REQUISITE TEST of Your System # %s ************" % (self.hostname)
        try:
            retcode = subprocess.Popen(['ping', self.hostname], cwd=execution_path, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, shell=True)
            out, err = retcode.communicate()
            pat = r'Lost = 0'
            matchobj = re.search(pat, out)
            if matchobj:
                print "Successfully able to ping %s Server" % self.hostname
                return True
            else:
                print "Unable to PING %s Server" % self.hostname
                return False
        except Exception, e:
            print "Unable to PING you %s Server" % self.hostname
            print e

    def check_SSH_connection(self):
        try:
            self._ssh = paramiko.SSHClient()
            self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self._ssh.connect(self.hostname, username=self.username, password=self.password)
            if self._ssh is not None:
                print "We are successfully able to perform SSH on your %s server \n" % (self.hostname)
                return True
            else:
                self.check_SSH_connection_linux()
        except Exception as e:
            print "*********SSH check failed due to following error********** \n", e
        finally:
            if self._ssh:
                self._ssh.close()

    def check_SSH_connection_linux(self):
        try:
            print self.hostname
            self.shell = spur.SshShell(hostname=self.hostname, username=self.username, password=self.password,
                                  shell_type=spur.ssh.ShellTypes.minimal,
                                  missing_host_key=spur.ssh.MissingHostKey.accept)
            # if shell:
            with self.shell:
                result = self.shell.run(["echo", "hello"])
                if result.output:
                    print "We are successfully able to perform SSH on your %s server \n" % (self.hostname)
                    # print shell
                    return True
                else:
                    return False




        except Exception, e:
            print "We are unable to perform SSH on your %s server \nPlease check your credentials/configuration..." % (
            self.hostname)
            print e
            return False
        exit(1)

    def os_check(self):
        # if self.check_ping():
        try:
            # print "Checking whether server is WINDOWS or LINUX..."
            self._ssh = paramiko.SSHClient()
            self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self._ssh.connect(self.hostname, username=self.username, password=self.password)
            if self._ssh is not None:
                stdin, stdout, stderr = self._ssh.exec_command(cmd3)
                output = stdout.read()
                error = stderr.read()
                stdin.flush()
                stdin.channel.shutdown_write()
                # print "ERROR IS:::",error
                # print "OUTPUT IS::",output
                check_output_pattern = r'bash: findstr: command not found'
                check_output_result = re.search(check_output_pattern, output)
                check_error_pattern = r'bash: cmd: command not found'  # This is for RHEL flavor OS
                check_error_pattern_1 = r'sh: cmd: not found'  # This is for VMware
                check_error_result = re.search(check_error_pattern, error)
                check_error_result_1 = re.search(check_error_pattern_1, error)
                if not (check_error_result or check_output_result or check_error_result_1):
                    # print output
                    # os_ver = re.search(r'(Microsoft *.)',output)
                    os_ver_list = re.findall(r'(OS Name:*.*)', output)
                    os_ver = str(os_ver_list)
                    cmd2 = r'wmic OS get OSArchitecture'
                    stdin, stdout, stderr = self._ssh.exec_command(cmd2)
                    os_arch = stdout.read()
                    # print "OS_Verion is::",os_ver
                    # print "OS_Acrchitecture::",os_arch
                    return os_ver, os_arch
                else:
                    try:
                        # print "******** Its not a WINDOWS OS, Now Checking for LINUX OS *******"
                        # result = self.shell.run(["cat","/etc/issue"])

                        if self._cocheck_SSHnnection_linux():
                            result = self.shell.run(["uname", "-mrs"])
                            os_arch = self.shell.run(["uname", "-m"])
                            if result.return_code == 0 and result.output == '':
                                print "Checking for VMWARE OS"
                                result = self.shell.run(["uname", "-mrs"])
                                os_ver = result.output
                                os_architecture = os_arch.output
                                return os_ver, os_architecture

                            elif result.return_code == 0 and result.output is not None:
                                os_ver = result.output
                                os_architecture = os_arch.output
                                return os_ver, os_architecture
                        else:
                            print "Unable to SSH to your %s server" % (self.hostname)
                            return 'NA', 'NONE'
                            # exit(1)

                    except Exception, e:
                        print "Am UNABLE to CHECK LINUX OS"
                        print e
                        return 'NA', 'NONE'

            else:
                print "Couldn't able to perform OS Check, as we were unable to perform SSH..."
        except Exception, e:
            print "*******FAILED while checking SSH connection becasue of following error******", e
            return 'NA', 'NONE'
            # exit(1)

    @property
    def os_name(self):
        os_check, os_arch = self.os_check()

        #pat = r'Linux.*.el6.*'
        #pat1 = r'VM *.*'
        #pat2 = r'OS Name: \s+Microsoft Windows Server 2012 R2\s+\w+'
        #pat2a = r'OS Name: \s+Microsoft Windows Server 2012 Standard'
        #pat2b = r'OS Name: \s+Microsoft Windows Server 2016 \s+\w+'
        #pat2c = r'OS Name: \s+Microsoft Windows Server 2008 R2\s+\w+'
        #pat2d = r'OS Name: \s+Microsoft Windows Server 2008\s+\w+'
        #pat3 = r'.* Ubuntu .*'
        #pat3a = r'Linux 4.2.*.-generic'
        #pat4 = r'*. SUSE *.*'
        #pat4a = r'Linux 4.*'
        #pat5 = r'Linux.*.el7.*'
        try:
            #os_match_obj = re.search(pat, os_check)
            # print os_check
            if re.search("windows", os_check ):
                os_type = "Windows"
                #check regex
                print "Windows" + re.search(os_check,"^(?=.*[a-zA-Z]\:\s+.*[a-zA-Z]20\d+[0-9]\R\d\s+\w+)&")


            else:
                if(os_check):
                    dict = {
                             'Linux.*.el6.*' : 'Linux' ,
                             'Linux 4.2.*.-generic'  : 'LINUX 4.2',
                             'Linux 4.*' : 'LINUX 4' ,
                             'Linux.*.el7.*' : 'LINUX E17' ,
                            'DICT':{
                                   'VM *.*': 'Vmware',
                                   '*. SUSE *.*': 'SUSE',
                                   '.* Ubuntu .*': 'UBUNTU'
                                }
                    }

                    if len(dict):
                        for  key,value in dict.iteritems():
                            if re.search("linux", os_check):
                                print "OS version: " + dict.get(key, default=None)
                                os_type = "linux"
                                #os_type = dict.get(key, default=None)
                            # match for linux os versions
                            else:
                                for keys1,values1 in value.iteritems():
                                    print "OS version: " + dict.get(keys1, default=None)
                                    os_type = dict.get(keys1, default=None)

                else:
                    print "Couldn't get OS version"




           #if os_match_obj:
            #    os = 'RHEL6'
                # print "AM IN RHEL6"
                # return os
            #else:
             #   os_match_obj1 = re.search(pat1, os_check)
                # print os_check
              #  if os_match_obj1:
               #     os = 'Vmware'
                    # print "AM IN VMWARE"
                    # return os
                #else:
                 #   os_match_obj2 = re.search(pat2, os_check)
                    # print "OS_match_obj:::",os_match_obj2
                  #  if os_match_obj2:
                   #     os = 'Windows2012R2'
                        # print "AM in WINDOWS_2012_R2"
                        # return os
                    #else:
                     #   os_match_obj2a = re.search(pat2a, os_check)
                        # print "OS_match_obj:::",os_match_obj2
                      #  if os_match_obj2a:
                       #     os = 'Windows2012'
                            # print "AM in WINDOWS_2012"
                        #else:
                         #   os_match_obj3 = re.search(pat3, os_check)
                            # print os_match_obj3
                          #  if os_match_obj3:
                           #     os = 'Ubuntu'
                                # print "********AM IN UBUNTU********"
                                # return os
                            #else:
                             #   os_match_obj3a = re.search(pat3a, os_check)
                                # print "PAT3a::",os_match_obj3a
                              #  if os_match_obj3a:
                               #     os = 'Ubuntu'
                                    # print "********AM IN latest UBUNTU ********"

                                #else:
                                 #   os_match_obj4 = re.search(pat4, os_check)
                                  #  if os_match_obj4:
                                   #     os = 'SLES12'
                                        # print "AM IN SLES12"
                                        # return os
                                    #else:
                                     #   os_match_obj5 = re.search(pat5, os_check)
                                        # print os_check, os_match_obj5
                                      #  if os_match_obj5:
                                       #     os = 'RHEL7'  ''''''
                                            # print "AM IN RHEL7 "
                                            # return os

                                      #else:
                                       #     print "Couldn't get OS version"
                                            # return False

            #print os
            return os_type, os_arch
        except Exception as e:
            print "Unable to fetch OS NAME due to following issue:::", e
            return False, False

    def ctrlallShow(self):
        result = None
        os_list = self.os_name
        os = os_list[0]
        if os == 'RHEL6' or os == 'SLES12' or os == 'RHEL7':
            ctrlAll = self.shell.run(["hpssacli", "ctrl", "all", "show"])
            if ctrlAll.return_code > 0:
                raise ctrlAll.to_error()
            else:
                # sys.stdout = Logger("C:\ctrlAll.txt")
                result = ctrlAll.output
                # print result
                return result

        elif os == 'Windows2012R2' or os == 'Windows2012' or os == 'Windows2008R2' or os == 'Windows2016':
            stdin, stdout, stderr = self._ssh.exec_command(cmd1)
            output = stdout.read()
            if output:
                # print output
                return output
            else:
                print "Unable to execute hpssacli command"
        elif os == 'Vmware':
            ctrlAll = self.shell.run(["./hpssacli", "ctrl", "all", "show"], cwd="/opt/hp/hpssacli/bin")
            if ctrlAll.return_code > 0:
                raise ctrlAll.to_error()
            else:
                # sys.stdout = Logger("C:\ctrlAll.txt")
                result = ctrlAll.output
                # print result
                return result
        elif os == 'Ubuntu':
            ctrlAll = self.shell.run(["sudo", "./hpssacli", "ctrl", "all", "show"], cwd="/opt/hp/hpssacli/bld")
            if ctrlAll.return_code > 0:
                raise ctrlAll.to_error()
            else:
                result = ctrlAll.output
                return result

        else:
            print "Unable to get Controller Information from your %s Server" % (self.hostname)

    def ctrlpdShow(self):
        os_list = self.os_name
        os = os_list[0]
        slot_num = self.ctrlSlotDetails()
        result = None
        if os == 'Windows2012R2' or os == 'Windows2012' or os == 'Windows2008R2' or os == 'Windows2016':
            for i in slot_num:
                try:
                    stdin, stdout, stderr = self._ssh.exec_command(
                        r'cmd /c "cd c:/Program Files/hp/hpssacli/bin & hpssacli ctrl slot=%s pd all show"' % i)
                    output = stdout.read()
                    # print "AM INSIDE IF LOOP of WINDOWS"
                    print "Slot #", i, "controller have following HDD attached.."
                    print output
                    # return output
                except Exception, e:
                    print "Slot #", i, "controller does not have any HDD attached.."
                    # ctrlpd.to_error()
            return output

        elif os == 'RHEL6' or os == 'SUSE' or os == 'RHEL7':
            for i in slot_num:
                try:
                    ctrlpd = self.shell.run(["hpssacli", "ctrl", "slot=" + i, "pd", "all", "show"])
                except Exception, e:
                    print "Slot #", i, "controller does not have any HDD attached.."
                else:
                    print "Slot #", i, "controller have following HDD attached.."
                    result = ctrlpd.output
                    print result
            return result

    def ctrlldShow(self):
        all_ld, OK_ld_list, count_of_ok_ld_list = None, None, None
        slot_num = drive_dict['slot_num']
        ctrlld = self.shell.run(["hpssacli", "ctrl", "slot=" + str(slot_num), "ld", "all", "show"])
        if ctrlld.return_code > 0:
            raise ctrlld.to_error()
        else:
            all_ld = ctrlld.output
        OK_ld_list = re.findall(r'(logicaldrive \d+)(?=.*OK.*)', all_ld)
        count_of_ok_ld_list = len(OK_ld_list)
        return all_ld, OK_ld_list, count_of_ok_ld_list

    def controllerDetails(self):
        ctrl_info = []
        ctrl_details = []
        ctrl_info = self.ctrlallShow()
        slot_num1 = re.findall(r'Smart.*Slot\s+(\d)', ctrl_info)
        for x in slot_num1:
            i = self.shell.run(["hpssacli", "ctrl", "slot=" + x, "show", "detail"])
            ctrl_details.append(i.output)

        return ctrl_details

    def ctrlSlotDetails(self):
        ctrl_info = []
        ctrl_info = self.ctrlallShow()
        slot_num1 = re.findall(r'Smart.*Slot\s+(\d)', ctrl_info)
        return slot_num1

    def getunassignedDrives(self):
        pd_details = self.ctrlpdShow()
        # print pd_details
        unassigned_pd = re.findall(r'.*(Unassigned\s*.*)', pd_details, re.DOTALL)
        if len(unassigned_pd) == 0:
            print "Couldn't find any UNASSIGNED DRIVES , hence exiting..."
            exit()
        else:
            unassigned_pd_final = [i.split('\n\n', 1)[1] for i in unassigned_pd]
            str1 = ''.join(unassigned_pd_final)
            # print str1

        SATA_SSD = re.findall(r'physicaldrive\s+(\d\w:\d:\d+) (?=.*Solid State SATA.*OK)', str1)
        num_unassignedSATA_SSD_Drives = len(SATA_SSD)

        SATA = re.findall(r'physicaldrive\s+(\d\w:\d:\d+) (?=.*SATA.*OK)', str1)
        num_unassignedSATA_Drives = len(SATA)

        SAS = re.findall(r'physicaldrive\s+(\d\w:\d:\d+) (?=.*SAS.*OK)', str1)

        num_unassignedSAS_Drives = len(SAS)

        SAS_SSD = re.findall(r'physicaldrive\s+(\d\w:\d:\d+) (?=.*Solid State SAS.*OK)', str1)

        num_unassignedSAS_SSD_Drives = len(SAS_SSD)

        return SATA_SSD, SATA, SAS, SAS_SSD

    def create_ld(self, slot_num, drive_type, num_drives, raid, size):
        sata_ssd, sata, sas, sas_ssd = self.getunassignedDrives()

        sata_string = ','.join(sata[:self.num_drives])
        sata_ssd_string = ','.join(sata_ssd[:self.num_drives])
        sas_string = ','.join(sas[:self.num_drives])
        sas_ssd_string = ','.join(sas_ssd[:self.num_drives])

#------------convert drive_type  in create_ld to drive_type_dict[]-------------------------------------------------
        drive_type_dict = {
            'SATA' : sata_string ,
            'SSD SATA' : sata_ssd_string ,
            'SAS' : sas_string ,
            'SSD SAS' : sas_ssd_string

        }
        if drive_dict['slot_num'] == 'ALL':

            if self.num_drives <= len(sata) | self.num_drives <= len(sata_ssd) | self.num_drives <= len(sas) | self.num_drives <= len(sas_ssd):
                for key,value in drive_type_dict():
                    if re.search(key.lower(),value):
                       slot_num = self.ctrlSlotDetails()
                    for i in slot_num:

                       try:
                          LD = self.shell.run(["hpssacli", "ctrl", "slot=" + i, "create", "type=ld","drives=" + drive_type_dict.get(key, default=None),
                                               "size=" + str(self.size), "raid=" + str(self.raid), "forced"])
                       except Exception, e:
                           print "Slot #", i, "Volume creation failed"

                   else:
                        result = LD.output
                        print "Slot # %s, Successfully created RAID %s Volume.." % (i, raid)
  #          if self.drive_type == 'SATA' and self.num_drives <= len(sata):
   #             slot_num = self.ctrlSlotDetails()
    #            for i in slot_num:
     #               try:
      #                  LD = self.shell.run(
       #                     ["hpssacli", "ctrl", "slot=" + i, "create", "type=ld", "drives=" + sata_string,
        #                     "size=" + str(self.size), "raid=" + str(self.raid), "forced"])
         #           except Exception, e:
          #              print "Slot #", i, "Volume creation failed"
#
 #                   else:
  #                      result = LD.output
   #                     print "Slot # %s, Successfully created RAID %s Volume.." % (i, raid)
    #        elif drive_type == 'SSD SATA' and self.num_drives <= len(sata_ssd):
     #           slot_num = self.ctrlSlotDetails()
      #          for i in slot_num:
       #             try:
        #                LD = self.shell.run(
         #                   ["hpssacli", "ctrl", "slot=" + i, "create", "type=ld", "drives=" + sata_ssd_string,
          #                   "size=" + str(size), "raid=" + str(raid), "forced"])
           #         except Exception, e:
            #            print "Slot #", i, "Volume creation failed"

#                    else:
 #                       result = LD.output
  #                      print "Slot # %s, Successfully created RAID %s Volume.." % (i, raid)
   #         elif drive_type == 'SAS' and self.num_drives <= len(sas):
    #            slot_num = self.ctrlSlotDetails()
     #           for i in slot_num:
      #              try:
       #                 LD = self.shell.run(
        #                    ["hpssacli", "ctrl", "slot=" + i, "create", "type=ld", "drives=" + sas_string,
         #                    "size=" + str(size), "raid=" + str(raid), "forced"])
          #          except Exception, e:
           #             print "Slot #", i, "Volume creation failed"

#                    else:
 #                       result = LD.output
  #                      print "Slot # %s, Successfully created RAID %s Volume.." % (i, raid)
            #elif drive_type == 'SSD SAS' and self.num_drives <= len(sas_ssd):
             #   slot_num = self.ctrlSlotDetails()
              #  for i in slot_num:
               #     try:
                #        LD = self.shell.run(
                 #           ["hpssacli", "ctrl", "slot=" + i, "create", "type=ld", "drives=" + sas_ssd_string,
                  #           "size=" + str(size), "raid=" + str(raid), "forced"])
                   # except Exception, e:
                    #    print "Slot #", i, "Volume creation failed"

#                    else:
 #                       result = LD.output
  #                      print "Slot # %s, Successfully created RAID %s Volume.." % (i, raid)

        elif drive_dict['slot_num'] != 'ALL':
            slot_num = drive_dict['slot_num']
            if self.num_drives <= len(sata) | self.num_drives <= len(sata_ssd) |self.num_drives <= len(sas) | self.num_drives <= len(sas_ssd):
               if self.drive_type == 'SATA': #and self.num_drives <= len(sata):
                try:
                    LD = self.shell.run(
                        ["hpssacli", "ctrl", "slot=" + str(slot_num), "create", "type=ld", "drives=" + sata_string,
                         "size=" + str(self.size), "raid=" + str(self.raid), "forced"])
                   except Exception, e:
                    print "Slot #", slot_num, "Volume creation failed"

                   else:
                    result = LD.output
                    print "Slot # %s, Successfully created RAID %s Volume.." % (slot_num, raid)
            elif drive_type == 'SSD SATA': # and self.num_drives <= len(sata_ssd):
                    try:
                    LD = self.shell.run(
                        ["hpssacli", "ctrl", "slot=" + str(slot_num), "create", "type=ld", "drives=" + sata_ssd_string,
                         "size=" + str(size), "raid=" + str(raid), "forced"])
                except Exception, e:
                    print "Slot #", slot_num, "Volume creation failed"

                else:
                    result = LD.output
                    print "Slot # %s, Successfully created RAID %s Volume.." % (slot_num, raid)
            elif drive_type == 'SAS': # and self.num_drives <= len(sas):
                try:
                    LD = self.shell.run(
                        ["hpssacli", "ctrl", "slot=" + str(slot_num), "create", "type=ld", "drives=" + sas_string,
                         "size=" + str(size), "raid=" + str(raid), "forced"])
                except Exception, e:
                    print "Slot #", slot_num, "Volume creation failed"

                else:
                    result = LD.output
                    print "Slot # %s, Successfully created RAID %s Volume.." % (slot_num, raid)
            elif drive_type == 'SSD SAS': # and self.num_drives <= len(sas_ssd):
                try:
                    LD = self.shell.run(
                        ["hpssacli", "ctrl", "slot=" + str(slot_num), "create", "type=ld", "drives=" + sas_ssd_string,
                         "size=" + str(size), "raid=" + str(raid), "forced"])
                except Exception, e:
                    print "Slot #", slot_num, "Volume creation failed"

                else:
                    result = LD.output
                    print "Slot # %s, Successfully created RAID %s Volume.." % (slot_num, raid)

            else:
                print "Sorry We are unable to create Volume... Please check your configuration...You don't have enough unassgined physical drives to create volumes..."
        else:
            print "Sorry We are unable to create Volume... Please check your configuration...You don't have enough unassgined physical drives to create volumes..."

    def get_bootvolume_details(self, slot_num):
        disk_name, raid_level, logical_drive = None, None, None
        # slot_num = drive_dict['slot_num']
        boot_lun = self.shell.run(["hpssacli", "ctrl", "slot=" + str(slot_num), "ld", "all", "show", "detail"])
        if boot_lun.return_code > 0:
            raise boot_lun.to_error()
        else:
            result = boot_lun.output
            if result:
                os_status = re.search("OS Status: LOCKED", result)
                if os_status:
                    raid_level = re.search("Fault Tolerance: (.*)", result)
                    disk = re.search("Disk Name: (.*)", result)
                    ld_drive = re.search("Logical Drive: (\d+)", result)
                    disk_name = disk.group(1).rstrip()
                    raid_level = raid_level.group(1).rstrip()
                    logical_drive = ld_drive.group(1).rstrip()
        print disk_name, raid_level, logical_drive

    def delete_logical_drive(self, slot_num, ld_id):
        slot_num = drive_dict['slot_num']
        ld_id = drive_dict['ld_id']
        boot_disk, boot_lun, boot_lun_id = self.get_bootvolume_details(slot_num)
        all_lun_details = self.ctrlldShow()
        all_lun_id_list = re.findall(r'logicaldrive (\d+)(?=.*)', all_lun_details[0])
        all_lun_id_string = ' '.join(all_lun_id_list)
        if str(ld_id) == boot_lun_id:
            print "Permission Denied.. Can't delete BOOT LUN.. Please choose some other DATA LUN or 'ALL' LUN"
            exit()
        elif str(ld_id) == 'ALL':
            if boot_lun_id in all_lun_id_string:
                final_deletable_lun_string = all_lun_id_string.replace(boot_lun_id, "")
                final_deletable_lun_list = final_deletable_lun_string.split()
                for item in final_deletable_lun_list:
                    try:
                        delete_lun = self.shell.run(
                            ["hpssacli", "ctrl", "slot=" + str(slot_num), "ld" + item, "delete", "forced"])
                    except Exception, e:
                        print "Slot # %s, Logical Volume %s Deletion Failed" % (slot_num, item)
                    else:
                        result = boot_lun.output
                        print "Slot # %s, Successfully deleted Logical Volume %s.." % (slot_num, item)
                        # return result
        elif str(ld_id) not in all_lun_id_string:
            print "WRONG CHOICE!!!! UNABLE TO DELETE LOGICAL VOLUME %s \n" \
                  "Please provide proper choice from following: \n" \
                  "1. Individual LUN ID \n" \
                  "2. ALL " % (ld_id)
        else:
            try:
                delete_lun = self.shell.run(
                    ["hpssacli", "ctrl", "slot=" + str(slot_num), "ld " + str(ld_id), "delete", "forced"])
            except Exception, e:
                print "Slot # %s, Logical Volume %s Deletion Failed" % (slot_num, ld_id)
            else:
                print "Slot # %s, Successfully deleted Logical Volume %s.." % (slot_num, ld_id)

    def fail_physical_drive(self, slot_num, drive_id):
        # def fail_physical_drive():
        pd_info = self.ctrlpdShow()
        result = None
        try:
            fail_pd = self.shell.run(
                ["hpssacli", "ctrl", "slot=" + str(slot_num), "physicaldrive", drive_id, "modify", "disablepd",
                 "forced"])
            # if fail_pd.return_code >0:
        except Exception, e:
            print "Unable to FAIL %s DRIVE on Slot # %s.. \n" % (drive_id, slot_num)
            print "This could be because of following things ... \n" \
                  "1. Cache board is not present \n" \
                  "2. Mentioned Drive ID is not present in the controller."
            # raise fail_pd.to_error()
        else:
            print "Successfully able to FAIL %s DRIVE on Slot # %s.." % (drive_id, slot_num)
            result = fail_pd.output
            print result
            return result

    def pd_detail(self):
        os_list = self.os_name
        os = os_list[0]
        slot_num = self.ctrlSlotDetails()
        result = None
        dict_of_pd = {}
        try:
            if "Windows" in os :

        #if os == 'Windows2012R2' or os == 'Windows2012' or os == 'Windows2008R2' or os == 'Windows2016':
                for i in slot_num:
                #try:
                    stdin, stdout, stderr = self._ssh.exec_command(
                        r'cmd /c "cd c:/Program Files/hp/hpssacli/bin & hpssacli ctrl slot=%s pd all show detail"' % i)
                    pd_all_details = stdout.read()
                  #  if pd_all_details:
                 #       dict_of_pd.update({i: pd_all_details})
                #    else:
               #         dict_of_pd.update({i: None})
              #  except Exception, e:
             #       print "Slot #", i, "controller does not have any HDD attached.."
            #return dict_of_pd

            elif os.search("RHEL") or os.search("SLES"):
        #elif os == 'RHEL6' or os == 'SLES12' or os == 'RHEL7':
                for i in slot_num:
                #try:
                    pd_detail = self.shell.run(["hpssacli", "ctrl", "slot=" + i, "pd", "all", "show", "detail"])
                    pd_all_details = pd_detail.output
                    #if pd_all_details:
                     #   dict_of_pd.update({i: pd_all_details})
                    #else:
                     #   dict_of_pd.update({i: None})

                #except Exception, e:
                #    print "Unable to fetch Physical Drives Details from your machine, as the Controller in slot #" + i + " does not have any HDD attached"
               # return dict_of_pd

            elif os == 'Vmware':
                for i in slot_num:
                #try:
                    pd_detail = self.shell.run(["./hpssacli", "ctrl", "slot=" + i, "pd", "all", "show", "detail"],
                                               cwd="/opt/hp/hpssacli/bin")
                    #pd_all_details = pd_detail.output
                    #if pd_all_details:
                   #     dict_of_pd.update({i: pd_all_details})
                  #  else:
                 #       dict_of_pd.update({i: None})

                #except Exception, e:
                 #   print "Unable to fetch Physical Drives Details from your machine, as the Controller in slot #" + i + " does not have any HDD attached"

                #return dict_of_pd

          elif os == 'Ubuntu':
            for i in slot_num:
                #try:
                    pd_detail = self.shell.run(
                        ["sudo", "./hpssacli", "ctrl", "slot=" + i, "pd", "all", "show", "detail"],
                        cwd="/opt/hp/hpssacli/bld")


                    pd_all_details = pd_detail.output
                    if pd_all_details:
                        dict_of_pd.update({i: pd_all_details})
                    else:
                        dict_of_pd.update({i: None})

        except Exception, e:
                    print "Unable to fetch Physical Drives Details from your machine, as the Controller in slot #" + i + " does not have any HDD attached"
            return dict_of_pd

        else:
        print "Couldn't get Drive Details"

obj = hpssacli(drive_dict)
generic_obj = copy.deepcopy(obj)
generic_obj.check_SSH_connection_linux()

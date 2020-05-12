/**
 ** C++ program to list contents of a directory recursively for NVMe class.
 **/
#include <iostream>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <dirent.h>
#include <fstream>
#include <fcntl.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <errno.h>
#include <map>
#include <iterator>
#include <list>

extern int errno;

void listFilesRecursively(char *path);


int main()
{
    // Directory path to list files
    char path[100];
 
	// Input path from user
	//  printf("Enter path to list files: ");
	// scanf("%s", path);

    listFilesRecursively("/sys/class/nvme");
    
   return 0;
 }
    
/**
* Lists all files and sub-directories recursively
* considering path as base path.
**/
 void listFilesRecursively(char *basePath)
 {
    char path[1000];
    std::map<std::string, std::string> nvme;
    std::list<std::string>model_list;
    std::list<std::string>fw_list;
    static int mcount = 0, fcount = 0;
    DIR *dir;
    struct dirent *dp;
    dir = opendir(basePath);
    
    // Unable to open directory stream
    if (!dir)
          return;
    
   	while ((dp = readdir(dir)) != NULL)
        {
           if ( strcmp(dp->d_name, ".") != 0 && strcmp(dp->d_name, "..") != 0 || strcmp(dp->d_name, "nvme") == 0)
           {
               //printf("%s\n", dp->d_name);
    
               // Construct new path from our base path
               strcpy(path, basePath);
               strcat(path, "/");
               strcat(path, dp->d_name);

				if( strcmp(dp->d_name, "firmware_rev") == 0 || strcmp(dp->d_name, "model") == 0){
					std::fstream fd; 
					std::string word;
		
					fd.open(path, std::ios::in);
					if(!fd.is_open()){
						printf("error in opening file\n");}
				
						getline(fd, word);

						// inserting key,value : model, Firmware_rev pair in map 'nvme'
						// after deciding model as key and firmware_rev as value
						std::string model, fw;
						std::map<std::string, std::string>::iterator it;

						if( strcmp(dp->d_name, "model") == 0) {
							mcount++; model = word;
							model_list.push_back(model);
						}
						if(strcmp(dp->d_name,  "firmware_rev") == 0){
							fcount++; fw = word;
							fw_list.push_back(fw);
						}

					 fd.close();	
				}
		
				else{
						if(dp->d_type == DT_LNK && (strncmp(dp->d_name, "nvme", 4) == 0))
						{
							listFilesRecursively(path);
						}
					}
			}
		}
    closedir(dir);

	// iterator for model and fw lists
	std::list<std::string>::iterator mtr;
	std::list<std::string>::iterator ftr;
	std::map<std::string, std::string>nvme_list;
	for( mtr = model_list.begin(); mtr != model_list.end(); ++mtr )
		for( ftr = fw_list.begin(); ftr != fw_list.end(); ++ftr ) {
			nvme_list.insert(std::pair<std::string, std::string> (*mtr, *ftr));	
			
			//std::string m = *mtr; const char* mm = m.c_str();
			//std::string f = *ftr; const char* ff = f.c_str();
			//printf("\n %s - %s\n", mm, ff);
	}

	// print mapped list in nvme_list
	std::map<std::string, std::string>::iterator mit;
	for( mit = nvme_list.begin(); mit != nvme_list.end(); ++mit  )
	{
		printf("\n key: %s \t value: %s\n", mit->first.c_str(), mit->second.c_str());
	}
}

#include <stdio.h>
#include <string.h>
#include <conio.h>
#include <direct.h>
#include <time.h>
#include <windows.h>

#define BUFFER_SIZE MAX_PATH	 	// 32,767 characters
TCHAR Current_Dir[BUFFER_SIZE + 1];	// +1 for terminator


int input_loop(int argc, char const *argv[]);

void system_cls();
void system_cd(char *dest);
void system_chdir(char *dest);
void system_copy(char *file, char *file2);
void system_move(char *file, char *dir);
void system_time();
void system_date();
void system_type(char *file);
void system_remove(char *file);
void system_dir(char *dir, int level);
void system_rename(char *old, char *new);
void system_rmdir(char *dir);
void system_mkdir(char *dir);
void system_help();

char* last(char *path);
void pause();

int main(int argc, char const *argv[]){
	// printf("%s\n", "Test");
	int exit = 0;
	TCHAR starting_directory[MAX_PATH + 1];

	GetCurrentDirectory(BUFFER_SIZE, starting_directory);

	while (exit == 0){
		system_cls();
		SetCurrentDirectory(starting_directory);

        printf(">> Interactive Shell v2 <<\n" );
        printf(">> Type 'help' for more details\n");
		exit = input_loop(argc, argv);
	}

	return 0;
}

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ //

int input_loop(int argc, char const *argv[]){
	char input[1024];
	char *string[256];            // 1) 3 is dangerously small,256 can hold a while;-)
								// You may want to dynamically allocate the pointers
								// in a general, robust case.
	char delimit[]=" \t\r\n\v\f"; // 2) POSIX whitespace characters
	int i = 0, j = 0;
	int exit = 0;

	while ( exit == 0){
		i = 0;

		GetCurrentDirectory(BUFFER_SIZE, Current_Dir);
		printf("\n%s >> ", Current_Dir);
		// Input
		if(fgets(input, sizeof input, stdin)){
			string[i]=strtok(input,delimit);
			while(string[i]!=NULL){
			  i++;
			  string[i]=strtok(NULL,delimit);
			}
		}

		// Main Procedure
		if (string[0] != NULL){
			if (strcmp(string[0], "exit") == 0){
				// printf("%s\n", "Bai");
				exit = 1;
			}
			else if(strcmp(string[0], "cls") == 0){
				system_cls();
			}
			else if(strcmp(string[0], "time") == 0){
				system_time();
			}
			else if(strcmp(string[0], "date") == 0){
				system_date();
			}
			else if(strcmp(string[0], "cd") == 0){
				system_cd(string[1]);
			}
			else if(strcmp(string[0], "chdir") == 0){
				system_chdir(string[1]);
			}
			else if(strcmp(string[0], "cmd") == 0){
				return exit;
			}
			else if(strcmp(string[0], "type") == 0){
				system_type(string[1]);
			}
			else if(strcmp(string[0], "del") == 0){
				system_remove(string[1]);
			}
			else if(strcmp(string[0], "copy") == 0){
				system_copy(string[1], string[2]);
			}
			else if(strcmp(string[0], "dir") == 0){
				system_dir(Current_Dir, 0);
			}
			else if(strcmp(string[0], "rename") == 0){
				system_rename(string[1], string[2]);
			}
			else if(strcmp(string[0], "rmdir") == 0){
				system_rmdir(string[1]);
			}
			else if(strcmp(string[0], "mkdir") == 0){
				system_mkdir(string[1]);
			}
			else if(strcmp(string[0], "move") == 0){
				system_move(string[1], string[2]);
			}
			else if(strcmp(string[0], "help") == 0){
				system_help();
			}

		    else{
		    	printf(" > '%s' is not recognized as a command\n", string[0]);
		    }
		}

	}

	return exit;
}

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ //

void system_cls()
{
	// Courtesy of Microsoft

    DWORD cCharsWritten;
    CONSOLE_SCREEN_BUFFER_INFO csbi;
    DWORD dwConSize;
    HANDLE hConsole;

    COORD coordScreen = { 0, 0 };    // home for the cursor
    hConsole = GetStdHandle(STD_OUTPUT_HANDLE);

     // Get the number of character cells in the current buffer.

    if( !GetConsoleScreenBufferInfo( hConsole, &csbi ))
    {
       return;
    }

    dwConSize = csbi.dwSize.X * csbi.dwSize.Y;

    // Fill the entire screen with blanks.

    if( !FillConsoleOutputCharacter( hConsole,        // Handle to console screen buffer
                                     (TCHAR) ' ',     // Character to write to the buffer
                                     dwConSize,       // Number of cells to write
                                     coordScreen,     // Coordinates of first cell
                                     &cCharsWritten ))// Receive number of characters written
    {
       return;
    }

    // Get the current text attribute.

    if( !GetConsoleScreenBufferInfo( hConsole, &csbi ))
    {
       return;
    }

    // Set the buffer's attributes accordingly.

    if( !FillConsoleOutputAttribute( hConsole,         // Handle to console screen buffer
                                     csbi.wAttributes, // Character attributes to use
                                     dwConSize,        // Number of cells to set attribute
                                     coordScreen,      // Coordinates of first cell
                                     &cCharsWritten )) // Receive number of characters written
    {
       return;
    }

    // Put the cursor at its home coordinates.

    SetConsoleCursorPosition( hConsole, coordScreen );
}

void system_cd(char *dest ){
	GetCurrentDirectory(BUFFER_SIZE, Current_Dir);

	if(dest == NULL){
		printf(" - Current Directory: %s\n", Current_Dir);
	}
	else{
        system_chdir(dest);
	}
}

void system_chdir(char *dest){
	if(dest == NULL){
		printf(" > No directory specified\n");
	}
	else{
		if ( !SetCurrentDirectory(dest)){
			printf(" > No such directory: '%s'\n", dest);
		}
	}
}

void system_move(char *file, char *dir){
	TCHAR last_dir[MAX_PATH + 1];
	// int dir_exist = 0

	if(file == NULL){
		printf(" > No file specified\n");
		return;
	}

	if(dir == NULL){
		printf(" > No directory specified\n");
		return;
	}

	GetCurrentDirectory(BUFFER_SIZE, last_dir);

	if(!SetCurrentDirectory){
		
	}
}

void system_rmdir(char *dir){

	if(dir == NULL){
		printf(" > No directory specified\n");
	}
	else{
		if ( !RemoveDirectory(dir)){
			printf(" > Directory cannot be removed: '%s'\n", dir);
		}
		else{
			printf(" - Directory deleted: '%s'\n", dir );
		}
	}
}

void system_mkdir(char *dir){
	// LPCWSTR directory;
	// directory = dir;

	if(dir == NULL){
		printf(" > No directory specified\n");
		return;
	}

	if(!CreateDirectory(dir, NULL)){
		printf(" > Failure to create directory: %s\n", dir);
	}
	else{
		printf(" - Created directory: %s\n", dir);
	}
}


void system_time(){
	int LEN = 150;
	char buf[LEN];
	time_t curtime;
	struct tm *loc_time;

	//Getting current time of system
	curtime = time (NULL);

	// Converting current time to local time
	loc_time = localtime (&curtime);

	// Formatting local time
	strftime(buf, LEN, " - Time: %I:%M:%S %p\n", loc_time);
	fputs(buf, stdout);
}

void system_date(){
	int LEN = 150;
	char buf[LEN];
	time_t curtime;
	struct tm *loc_time;


	//Getting current time of system
	curtime = time (NULL);

	// Converting current time to local time
	loc_time = localtime (&curtime);

	// Formatting local time
	strftime(buf, LEN, " - Date: %A, %d %b %Y\n", loc_time);
	fputs(buf, stdout);

}

void system_type(char *file_handle){
	int c;
	FILE *file;

	if (file_handle == NULL)
	{
		printf(" > No file specified\n");
	}
	else{
		file =  fopen(file_handle, "r");
		if (file) {
			while ((c = getc(file)) != EOF)
				putchar(c);
			fclose(file);

			printf("\n");
		}
		else{
			printf(" > No such file: '%s'\n", file_handle);
		}
	}

}

void system_copy(char *src , char *dest){
	int c;
	FILE *file, *file2;
	


	if (src == NULL)
	{
		printf(" > No source file specified\n");
	}

	else if (dest == NULL){
		printf(" > No destination file specified\n");
	}

	else{
		file =  fopen(src, "r");
		file2 = fopen(dest, "w");
		if (file && file2) {
			while ((c = getc(file)) != EOF)
				putc(c, file2);
			fclose(file);
			fclose(file2);

			printf(" - Files successfully copied\n");
		}
		else{
			if(file)
				fclose(file);
			if(file2)
				fclose(file2);

			printf(" > File(s) could not be opened'\n");
		}
	}

}

void system_remove(char *file_handle){
	FILE *file;
	int ret;

	if (file_handle == NULL)
	{
		printf(" > No file specified\n");
	}
	else{
		file =  fopen(file_handle, "r");
		if (file) {
			fclose(file);
			ret = remove(file_handle);

			if(ret){
				printf(" - File could not be deleted\n");
			}
			else{
				printf(" > Successfully deleted: %s\n",file_handle);
			}
		}
		else{
			printf(" > No such file: '%s'\n", file_handle);
		}
	}
}

void system_dir(char *dir, int level){
	WIN32_FIND_DATA fdFile;
    HANDLE hFind = NULL;

    char sPath[2048];
    char buffer[256];
    char *temp;

    int c;

    if (dir == NULL){
    	printf(" > No directory specified\n");
    }

    //Specify a file mask. *.* = We want everything!
    sprintf(sPath, "%s\\*.*", dir);

    if((hFind = FindFirstFile(sPath, &fdFile)) == INVALID_HANDLE_VALUE)
    {
        printf(" > Path not found: '%s'\n", dir);
        return;
    }

    do
    {
        //Find first file will always return "."
        //    and ".." as the first two directories.
        if(strcmp(fdFile.cFileName, ".") != 0
                && strcmp(fdFile.cFileName, "..") != 0)
        {
            //Build up our file path using the passed in
            //  [sDir] and the file/foldername we just found:
            sprintf(sPath, "%s\\%s", dir, fdFile.cFileName);

            //Is the entity a File or Folder?
            if(fdFile.dwFileAttributes &FILE_ATTRIBUTE_DIRECTORY)
            {
            	// temp = last(sPath);
            	strcpy(buffer, sPath);
            	for(c = 0; c < level; c++)
            		printf("  ");

                printf(" - <DIR>  %s\n", last(buffer));
                system_dir(sPath, (level + 1)); //Recursion, I love it!
            }
            else{
            	// temp = last(sPath);
            	strcpy(buffer, sPath);
            	for(c = 0; c < level; c++)
            		printf("  ");

                printf(" - <   >  %s\n", last(buffer));
            }
        }
    }
    while(FindNextFile(hFind, &fdFile)); //Find the next file.

    FindClose(hFind); //Always, Always, clean things up!

    return;
}

void system_rename(char *old, char *new){
	int ret;

	if ( old == NULL ){
		printf(" > No file specified\n" );
		return;
	}

	if ( new == NULL ){
		printf(" > New name not specified\n" );
		return;
	}

	ret = rename(old, new);

	if(ret == 0) {
		printf(" - File renamed successfully\n");
	} else {
		printf(" > Error: unable to rename the file\n");
	}

}

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ //

/* Utility Functions*/

void pause()
{
    printf("\nPress any key to Continue... \n");
    getch();
}

char* last(char *path){
	char *string[256];
	char delimit[]="\\";
	int i = 0;

	string[i]=strtok(path,delimit);
	while(string[i]!=NULL)
	{
	  i++;
	  string[i]=strtok(NULL,delimit);
	}

	return string[i - 1];


}

int tokens(char *path){
	char *string[256];
	char delimit[]=".";
	int i = 0;

	string[i]=strtok(path,delimit);
	while(string[i]!=NULL)
	{
	  i++;
	  string[i]=strtok(NULL,delimit);
	}

	return i;
}

void system_help(){
	printf("\nUser Guide\n -- Note: <> denotes optional parameters, [] means mandatory\n");

	printf("\nCommands:");
	printf("\n > cd <new directory>");
	printf("\n   --  Shows current directory; if <new directory> is supplied, current will change to <new directory>");
	printf("\n > chdir [new directory]");
	printf("\n   --  Switches current directory to [new directory]");
	printf("\n > cls");
	printf("\n   --  Clears console window");
	printf("\n > cmd");
	printf("\n   --  Reinitializes console");
	printf("\n > copy [source] [destination]");
	printf("\n   --  Copies [source] file to [destination]");
	printf("\n > date");
	printf("\n   --  Displays system date");
	printf("\n > del [file]");
	printf("\n   --  Deletes [file] specified");
	printf("\n > dir");
	printf("\n   --  Show file tree of current directory");
	printf("\n > move [file] [directory]");
	printf("\n   --  [[  W. I. P. ]]  Does not work in current version");
	printf("\n > mkdir [directory]");
	printf("\n   --  Creates [directory]");
	printf("\n > rename [old file] [new file]");
	printf("\n   --  Renames [old file] to [new file]; also works on directorieset");
	printf("\n > rmdir [directory]");
	printf("\n   --  Deletes [directory] specified");
	printf("\n > time");
	printf("\n   --  Displays system time");
	printf("\n > type [file]");
	printf("\n   --  Displays contents of [file]");

	printf("\n");
}

#include <stdio.h>
#include <stdlib.h>
#include <conio.h>
#include <dirent.h>
#include <windows.h>

// void user_input(char *input);
// void arg_tokenizer(char **arguments, char *input);

// int user_arguments(char **arguments);
int system_loop();
void system_cls();

void pause();

int main()
{
    system_loop();

    system_cls();
}

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ //

int system_loop()
{
    char input[1024];
    char *arguments[64];

    char delimit[]=" \t\r\n\v\f"; // 2) POSIX whitespace characters
    int i, j;

    int quit = 0;

    while(quit == 0){
        i = 0, j = 0;

        printf("Input: ");
        if(fgets(input, sizeof input, stdin))
        {
            arguments[i] = strtok(input, delimit);
            while(arguments[i] != NULL)
            {
                i++;
                arguments[i]=strtok(NULL,delimit);
            }

            printf("%s\n", arguments[i]);

            if (strcmp(arguments[i], "exit") == 0)
            {
                quit = 1;
            }
        }
    }
}

// int user_arguments(char **arguments)
// {
//     char input[1024];
//     char *out[256];
//     char *string[256];            // 1) 3 is dangerously small,256 can hold a while;-)
//                                   // You may want to dynamically allocate the pointers
//                                   // in a general, robust case.
//     char delimit[]=" \t\r\n\v\f"; // 2) POSIX whitespace characters
//     int i = 0, j = 0;

//     printf("Input: ");
//     if(fgets(input, sizeof input, stdin)) // 3) fgets() returns NULL on error.
//                                           // 4) Better practice to use sizeof
//                                           //    input rather hard-coding size
//     {
//         string[i]=strtok(input,delimit);    // 5) Make use of i to be explicit
//         while(string[i]!=NULL)
//         {
//           out[i] = string[i];
//           printf("string [%d]=%s\n",i,string[i]);
//           i++;
//           string[i]=strtok(NULL,delimit);
//         }

//         for (j=0;j<i;j++)
//         printf("\nString: %s", string[j]);

//         // printf("Size: %d\n", i);
//     }

//     // arguments = string;

//     return i;
// }

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ //

void system_cls()
{
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

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ //

/* Utility Functions*/

void pause()
{
    printf("\nPress any key to Continue... \n");
    getch();
}

import sys
from Minor.DB import dbclient

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print('Please input the option')
    else:
        option = sys.argv[1]
        if option == "create":
            option2 = sys.argv[2]
            if option2 == "locker":
                dbclient.createTable()
                print('Table Locker created.')
            elif option2 == "key":
                dbclient.createTableKey()
                print('Table Key created.')
            else:
                print('No Table found.')
        elif option == "setup":
            option2 = sys.argv[2]
            if option2 == "key":
                option3 = sys.argv[3]
                saved = (str(option3))
                # print(saved)
                dbclient.createKey(saved)
                print('Key inserted.')
            else:
                print('No action.')
        elif option == "clear":
            option2 = sys.argv[2]
            if option2 == "key":
                dbclient.clearKey()
                print('All Key(s) removed')
        else:
            print('Invalid input of option')

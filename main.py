from md5 import MD5
from sys import path
import os

DB_FILE = path[0] + '/db.txt'
DB_SEPARATOR = '|'

def test_md5():
    md5 = MD5()
    values = [b'', b"a", b"abc", b"message digest", b"abcdefghijklmnopqrstuvwxyz", b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789", b"12345678901234567890123456789012345678901234567890123456789012345678901234567890", b"The quick brown fox jumps over the lazy dog", b"The quick brown fox jumps over the lazy dog."]
    hashed = ['d41d8cd98f00b204e9800998ecf8427e', '0cc175b9c0f1b6a831c399e269772661', '900150983cd24fb0d6963f7d28e17f72', 'f96b697d7cb7938d525a2f31aaf161d0', 'c3fcd3d76192e4007dfb496cca67e13b', 'd174ab98d277d9f5a5611c2c9f419d9f', '57edf4a22be3c955ac49da2e2107b67a', '9e107d9d372bb6826bd81d3542a419d6', 'e4d909c290d0fb1ca068ffaddf22cbd0']
    
    print('Running tests....')
    for i in range(len(values)):
        print(f'Test {i}: {md5.hash(values[i]) == hashed[i]}')
    print('Tests finished.')


def db_save_combination(type, msg, hash):
    f = open(DB_FILE, 'a')
    if type == 0: type = 'msg'
    if type == 1: type = 'file'
    f.write(f'{type}{DB_SEPARATOR}{msg}{DB_SEPARATOR}{hash}\n')
    f.close()


def db_load():
    path_to_hash = {}
    msg_to_hashe = {}

    with open(DB_FILE, 'r') as f:
        data = f.read()

    data = data.split('\n')

    for d in data:
        d = d.split(DB_SEPARATOR)
        if d[0] == 'file': path_to_hash[d[1]] = d[2]
        if d[0] == 'msg': msg_to_hashe[d[1]] = d[2]
    
    return path_to_hash, msg_to_hashe


def hash_file(path):
    md5 = MD5()
    try:
        chunk_size = 64*10*1024*1024 #~671 mb
        filesize = os.path.getsize(path)

        with open(path, 'rb') as f:
            while (chunk := f.read(chunk_size)): 
                if len(chunk) < chunk_size:
                    chunk = md5.msg_prepare(chunk, length=filesize)
                    
                md5.hash(chunk, auto_padding=False, overwrite=False)
                hash = md5.get_digest()
        return hash

    except: 
        print('Error opening a file. Make sure the path is correct.')
        return False


def controller():
    action = -1

    while action != 4:
        md5 = MD5()
        action = int(input("\n\nSelect a desired action: \n0 - calculate hash (message)\n1 - calculate hash (file)\n2 - check file integrity\n3 - run tests\n4 - exit\n>> "))
        
        if action == 0:
            msg = input("\nEnter message to hash:\n>> ")
            hash = md5.hash(bytearray(msg, encoding="UTF-8"))
            print("MD5 hash of the message:", hash)

            if input("\nDo you want to save this combination to DB (y/n):\n>> ") == 'y':
                _, msg_to_hash = db_load()
                
                if not msg in msg_to_hash:
                    db_save_combination(0, msg, hash)
                    print('Saved!')
                else: print('This combination is already in the DB!')


        if action == 1:
            path = input("\nEnter path to file:\n>> ")
            hash = hash_file(path)

            if hash != False:
                print('MD5 hash of the selected file: ', hash)

                if input("\nDo you want to save this combination to DB (y/n):\n>> ") == 'y':
                    path_to_hash, _ = db_load()

                    if not path in path_to_hash:
                        db_save_combination(1, path, hash)
                        print('Saved!')
                    else: print('This combination is already in the DB!')


        if action == 2:
            path_to_hash, _ = db_load()
            path = input("\nEnter path to file:\n>> ")
            
            if int(input('\nWhat do you want to compare the calculated hash to?\n0 - The database\n1 - The terminal input\n>> ')) == 0:
                hash = hash_file(path)

                if hash != False:
                    print(f'Hash current: {hash}')

                    if (path in path_to_hash):
                        print(f'Hash from DB: {path_to_hash[path]}')
                        if (path_to_hash[path] == hash): print('-> The contents are the same.')
                        else: print('-> This file has been edited!!')
                    else:
                        if  input("\nThis filepath is not in the DB. Do you want to save this combination to DB (y/n):\n>> ") == 'y':
                            db_save_combination(1, path, hash)
                            print('Saved!')
            else:
                hash_entered = input('\nEnter hash to compare to:\n>> ')
                hash = hash_file(path)
                
                if hash != False:
                    if (hash == hash_entered): print('The contents are the same!')
                    else: print(f'{hash_entered} != {hash}\n-> This file has been edited!!')


        if action == 3:
           test_md5()

controller()

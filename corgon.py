#!/usr/bin/python3

import argparse
import re
import unidecode

parser = argparse.ArgumentParser(description="Turn a list of names into user names and e-mail addresses")
parser.add_argument("Infile", type=argparse.FileType("r"), help="Text File that contains names of people")
parser.add_argument("Outfile", type=argparse.FileType("w+"), help="Output file to write to")
parser.add_argument("-f", "--function", type=str, choices=["gophish_csv", "emails", "usernames"] ,help="Name List Delimiter (default is gophish_csv)", default="gophish_csv")
parser.add_argument("-d", "--delimiter", type=str, help="Name List Delimiter (default is whitespace(s))")
parser.add_argument("-m", "--maildomain", type=str, help="Name of the e-mail Domain (default is @example.com)", default="@example.com")
parser.add_argument("-s", "--schema", type=str, help="Schema for username/mailname (default is firstname.lastname for mail and only lastname for user). Provide the order of first/last and delimiter (if any). Examples: f1l->jsmith, l1f->sjohn, f1.l->j.smith, l->smith")
parser.add_argument("-a", "--ad_domain", type=str, help="Active Directory Domain. Is prepended to usernames in case of -f usernames.")
parser.add_argument("--keepcase", action='store_true', help="Keep Casing of letters in output for email addresses and usernames (default is false)")
parser.add_argument("--hyphenfn", action='store_true', help="Keep Hyphens in first name (default is not set)")
parser.add_argument("--hyphenln", action='store_true', help="Keep Hyphens in last name (default is not set)")
args = parser.parse_args()

# prepare arguments variables
infile = args.Infile
outfile = args.Outfile
if not args.delimiter:
    delim = re.compile(r"\s+")
else:
    delim = args.delimiter
mail_domain = args.maildomain
schema = args.schema
keepcase = args.keepcase
function = args.function
firstnames = []
lastnames = []

# dictionary for problematic characters. Add chars as needed
char_replace_dict = {'ö':'oe','ä':'ae','ü':'ue'}
bad_char_re = re.compile(r"[.<>/(){}[\]~`]")
allowed_name_delimiters = r"[\.\-\_\+]"

def create_name_arrays():
    print("[+] Parsing input file")
    raw_content = infile.read().splitlines()
    
    # iterate and fill name lists
    for line in raw_content:
        # remove trailing whitespaces if any
        line = line.rstrip()
        # filter out lines without normal letters
        if not re.search(r"[a-zA-Z]+", line): 
            continue
        # your titles mean nothing to me 
        line = re.sub(r"Dr.\s*", "", line)
        # filter out lines with weird special characters
        if re.search(bad_char_re, line):
            print("[!] Bad characters detected in name: Skipping " + line)
            continue
        # split
        tmpLine = re.split(delim, line)
        firstnames.append(tmpLine[0]) # assume first value is first name
        lastnames.append(tmpLine[len(tmpLine) - 1]) # last value is last name

def generate_mail_addresses():
    email_addresses = []
    if not schema:
        name_count = len(firstnames)
        for i in range(name_count):
            email_addresses.append(firstnames[i] + "." + lastnames[i] + mail_domain)
    else:
        name_count = len(firstnames)
        for i in range(name_count):
            email_addresses.append(schematize(firstnames[i], lastnames[i], mail_domain))
    return email_addresses

def generate_usernames():
    # first check for AD-Domain
    if args.ad_domain:
        domain = args.ad_domain + "\\" # one backslash
    else:
        domain = ""

    usernames = []
    if not schema:
        name_count = len(firstnames)
        for i in range(name_count):
            usernames.append(domain + firstnames[i] + "." + lastnames[i])
    else:
        name_count = len(firstnames)
        for i in range(name_count):
            usernames.append(domain + schematize(firstnames[i], lastnames[i], ""))
    return usernames

# apply schema to name entry (for email or username)
def schematize(firstname, lastname, mail_domain):
    result = ""
    firstname_part = ""
    lastname_part = ""
    schema_delim = ""

    # get firstname part if any
    first_regex = re.search(r"f[0-9]*", schema)
    if first_regex:
        num = re.search(r"\d+", first_regex.group())
        if num:
            firstname_part = firstname[0:int(num.group())]
        else:
            firstname_part = firstname
        # we probably want to remove hyphens unless --hyphenfn is set
        if not args.hyphenfn:
            firstname_part = firstname_part.split("-")[0]
    
    # get lastname part if any
    last_regex = re.search("l[0-9]*", schema)
    if last_regex:
        num = re.search(r"\d+", last_regex.group())
        if num:
            lastname_part = lastname[0:int(num.group())]
        else:
            lastname_part = lastname
        # we probably want to remove hyphens unless --hyphenln is set
        if not args.hyphenln:
            lastname_part = lastname_part.split("-")[0]            

    # sanity check: is at least one regex present?
    if not first_regex and not last_regex:
        print("Schema does not contain first or last name. Something's wrong!")

    # get the name delimiter (this only looks for the first one)
    delim_regex = re.search(allowed_name_delimiters, schema)
    if delim_regex:
        schema_delim = delim_regex.group()

    # figure out the order of first and last name
    # only necessary if both regexes exist
    if first_regex and last_regex:
        if first_regex.start() < last_regex.start():
            result = firstname_part + schema_delim + lastname_part + mail_domain
        else:
            result = lastname_part + schema_delim + firstname_part + mail_domain

    # case change or not?
    if not keepcase:
        result = result.lower()

    # fin
    return result

# replace non-standard characters, e.g. è -> e, ö -> oe, etc.
def replace_weird_chars(inputstr):
    # first replace according to the specified dictionary
    for char in char_replace_dict:
        inputstr = inputstr.replace(char, char_replace_dict[char])
    # then replace remaining characters with unidecode
    inputstr = unidecode.unidecode(inputstr)
    return inputstr

# output email results in the Gophish CSV format (leave Position blank)
def gophish_csv_output(email_addresses):
    # First Name,Last Name,Position,Email
    print("First Name,Last Name,Position,Email", file=outfile)
    name_count = len(firstnames)
    for i in range(name_count):
        print(firstnames[i] + "," + lastnames[i] + ",," + replace_weird_chars(email_addresses[i]), file=outfile)

# can be used for username or email list output (not csv)
def simple_list_output(output_data):
    data_count = len(output_data)
    for i in range(data_count):
        print(replace_weird_chars(output_data[i]), file=outfile)





# secret function
def secret_function():
    print("Having a ruff day? Here's a corgi\n")
    print("""...........................     ..  ...  .................''..','.......      ...............''.....
.................  .......                ...............................    .......................
.................. .........,cc:;'...    ..................................... ...........','.......
........ .................,dkOkkxdc........... ............................. .............','.......
.........................,xkxxkkkxxo;'.......       .    ..... ...,cllccc,..........................
.........................okxxxxxxxxxdl,....              ..... .:dxdollldo;.........................
.........................dOxxxxxxddxxdl;..        .       ....;xOxolloddddl'........................
.........................lkddxkxxxkkOkdo:.. .   ....   ..  .;dkOxolclooddxo,.....................','
........'''..............,oddxxkxdxkOOkdol;...        ....'lxkkkdollooddddl....................':cc;
..........................:dxkkkxdodxxddxkkdooooollc:::,:odooxkkxlcloddolo;.....  .............',,''
..................',;;... .okOOkxddxxdkOOOO000000OOO0Okxxkkkoloo:;cdxdooo:...............'''''',,,,;
..  ..............';;;'....cxxkOxlldxkO0OOO0000OkxxO00Oxdlloolc;,:oxxxxdl,'',;;;;;;;;;;;;,,,;::ccccc
...    ...........'''''..',lkkkkxddxkO0OO0KKKX0kxxOO0KKOd:;;:c;..;oxxxdo:;;;;::::;;;;;;;;;;:::::ccc:
',''',,'',;:lool:,...'....'cxkkkkOOOkO0KOddk0K0xxkOOOK0xol;,,;:,.;oddddl:::::::::::::::;;;:c:::ccccc
llc::c:,'',;:cc:;,''',,,,,,;okkkkkkxxO0k;...ckOkkkkkkkc...;:;';cc:ldkkdc:::::c::::cc::;,;:ccclllllll
;;;,,,,,,,,,,,;;;;;;;;;;;;;cxxxdxOkkkO0d,...:dkkOOOOx:.   .;:'.,ccloddlcccclllllllllcccccllllooodddd
,,,,,;;;;;;;::::::;;;:::cc:lxkxxOKKKXKKKkddxkO00KK0Oko'...';;,..;:;cdoccccccccccllllloodddddxxxkkOOk
;;;,;;;;::::;;:;;;;;;::::::cdOOOKXNNXXXXXKKXXXKOkOOkkkxlccccloc,,::lol:cccc::::::::cccccccccclllllll
:;;;;;;::::::::::ccc:::::::cdO0KXNNNXXNNNNNNNk;'....,dOkdooodddl;;lddc:::cc::::::::::::;;;;;;;;;;;;;
;;;;;;::ccccc::::cc::;;;;;:ok0KXNNNNNNXXNNNNXl.      :kOkkkxdddoc;cdxoc::::::;::::cc:cc::ccc::cccccc
,,,,;;;;;;,,;;;;;;;:;;;;;;cdO0KXXXNXXKkdkXNXXO;.    .lkOkolddoddollddoc;;;::;;;;;;;:::::ccc;,,:ccccc
,;;;;:;,,,,,;;;,,,,,,,;;;;cdOKKXXXXKKKKxcoOOOkl.   .;dxko;:loodxddoddlc;;;::::;;;;;::::cllc:::cooddd
,,,,,,,,,,,;;,,,,,,,,,,;;;:dO0KKXXXKK0KKd,cxo;.     .;;,':lllodddooddl:;;:::c:::;;:cccclodxxxkOOOO00
;,,,,,,;;;,,''',,,,,;;,,;;cxO0KKKKXKK00KKd;cdc'.....'. .:ccllodooooodc;;:ccccllllooddxxkO0KKKXXXXXXN
;;;;;;;;:;;,,,;;;;,,;;,;;;lxOO0KKXKKKKKKK0xooc:c::;;,',:ccclooooooooo:':dkkOOO000KKXXXXXNNXK00KKKXXX
llcclllcc::::;::;;:::;,,,;lxkkO0KKKKXXXXXKKOlc::,'',:lc:cclloooollldo:,:dO0KKK00000000000OOkkkkkO00O
:::cllccc:cclllccllooolccldxxkOO0KKXXXXXXXXKxc;,'',;clccllloooooollll:,,:odddddddddddxxxdddxxxxxxxxx
::loddddddxxkkkkO00OO0O00KKOxxxkO0XXXXXXXXXXK0xdoooolccllloooooolllc:,'.,:lllllloooooooooooooooooooo
lloxxxkkkkkkOO000000KXXNNWWXOxdxkO0KKXKKKKXKKKOkxddolllloooooollcc;'....':loooooodddxxdddddddddddddd
kkO000KXXXXXNNNNNNNNNNWWWWWN0xooodkO0KK000KKKK00Oxxdooooooooolc::,......'cxOOOOOOO0000000OOOOOkkxxdd
0KKKKKNNWWWWWWWWWWWWWWWWWWWNKxoolodxk0000000000Okkxxxddddddoc;,'........':xKXNNNXXXXKKKKKK000OOkxxdx
WWWWWWWWWWWWWWWWWWWWWWWWWWWNKkddoddxk0000000OkkkOkkkxxxxxddl:'..........,;lkKXNNXXXXXKKKKKKKK00OOOOO
WWWWWWWWWWWWWWWWMMMMMMWWWWWN0kxddxxxk0K0000OOkkOOOOkxxxxxdoc;'..........,;:oOKKKK00KKK00KKK0000OOOOO
WWWWWWWWWWWWWWMMWWMMWMMMWWWX0Okxxdxxk0KK0OOOOOkkkkkkxxxxxdoc;'.'...  ..';::cdOOOOOOOkkkxxxkkxxxddxdd
WWWWWWWWWWWWWWWWWWWWWWWWWWNK0OOkxdxkkO000OO00kxxxkkkxxxxdool:;'..  ....';ccloxxdddddoooloddollllllll
XKKXNNNNNNNNNXXXNNNNNNNXXKKKK00OOkkxkO000OO0Oxxxkxxkxxxxdoooc'.   ....',;ccllcllcllccccllolcccclcccl
0OOOOOO000OOOkkkO0OOOkxxddOKKK00OOkOkookOkOOkkxxkxxxxxdddddl,   ...'',,;:cllcclollc::;;::::;;clc::::
ollooodxxl:lol:cloolccll::xKXKKK000kolokOOOOOkxxxxxxxxdooc,.  ..',,;;::cclllccc:;:c:;;,;::;,;:;',;;;
,,,;::;cc;;:::;;:c::loxOdld0XXXXK00O00kkO000Okxkxxxddodo:.   ',;:ccclccllllll::::;;;clloolcc:;;:cclc
;cc;cooooooocloooddlldxkkddOXNNXXXKKK000KKKK0OOOkddo:,cc'.  'clloooooolooolllccllllododddooloolooool
xkkkxkOOkxdxkO0KKK0kOOOO0Ok0XNNNNNXXXKKXXXK0000OOdol;....  .;odddddddoloooooooddddxkxxxxdlodxxxkkkkk
KKXXKKKXX0KKXNNXKKXXXXXXXXXXNNNNNNNNXXXXXXK0000OOxddo:.     ;oddddoodooooodxkOOOkxxkkkxxxdddxxxxxxkk""")

# main
if args.schema == "CORGI":
    secret_function()
    exit()

# this always has to be done
create_name_arrays()

if function == "gophish_csv":
    print("[+] Selected Gophish CSV output function")
    results = generate_mail_addresses()
    gophish_csv_output(results)

if function == "emails":
    print("[+] Selected simpel email output function")
    results = generate_mail_addresses()
    simple_list_output(results)

if function == "usernames":
    print("[+] Selected username output function")
    results = generate_usernames()
    simple_list_output(results)

print("[+] Output written to " + outfile.name)
